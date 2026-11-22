"""Run via docker exec -i <worker> python - <command> < this_file.

The state stays in the old worker until it resumes or is replaced. A failed
deployment must run `resume` against that same container ID.
"""

import argparse
import json
import os
from pathlib import Path
import signal
import socket
import sys
import time


class GuardError(RuntimeError):
    pass


class Guard:
    def __init__(self, app, worker, state_path, reply_timeout=10,
                 clock=time.monotonic, sleep=time.sleep):
        self.control = app.control
        self.worker = worker
        self.state_path = Path(state_path)
        self.reply_timeout = reply_timeout
        self.clock = clock
        self.sleep = sleep

    def inspect(self, command):
        inspector = self.control.inspect(destination=[self.worker],
                                         timeout=self.reply_timeout)
        replies = getattr(inspector, command)()
        if not isinstance(replies, dict) or set(replies) != {self.worker}:
            raise GuardError(f"No unambiguous {command} reply from {self.worker}")
        result = replies[self.worker]
        if not isinstance(result, list):
            raise GuardError(f"Invalid {command} reply from {self.worker}")
        return result

    def queues(self):
        result = self.inspect("active_queues")
        if any(not isinstance(q, dict) or not isinstance(q.get("name"), str)
               or not q["name"] for q in result):
            raise GuardError("Invalid active_queues payload")
        names = [q["name"] for q in result]
        if len(names) != len(set(names)):
            raise GuardError("Duplicate queues in active_queues reply")
        return names

    def counts(self):
        # Read active last: a reserved task may start between these requests.
        return {kind: len(self.inspect(kind))
                for kind in ("reserved", "scheduled", "active")}

    def change_consumer(self, command, queue):
        replies = getattr(self.control, command)(
            queue, destination=[self.worker], reply=True,
            timeout=self.reply_timeout)
        if (not isinstance(replies, list) or len(replies) != 1
                or not isinstance(replies[0], dict)
                or set(replies[0]) != {self.worker}):
            raise GuardError(f"Missing {command} acknowledgement for {queue}")
        result = replies[0][self.worker]
        if (not isinstance(result, dict) or not isinstance(result.get("ok"), str)
                or not result["ok"] or "error" in result):
            raise GuardError(f"Failed {command} for {queue}")

    def wait_for_queues(self, expected, exact=True):
        deadline = self.clock() + 30
        while True:
            actual = set(self.queues())
            matches = actual == set(expected) if exact else set(expected).issubset(actual)
            if matches:
                return
            if self.clock() >= deadline:
                raise GuardError("Consumer change did not take effect")
            self.sleep(1)

    def resume(self):
        if not self.state_path.exists():
            return
        state = json.loads(self.state_path.read_text())
        queues = state.get("queues")
        if (state.get("worker") != self.worker or not isinstance(queues, list)
                or not queues or any(not isinstance(q, str) or not q for q in queues)):
            raise GuardError("Invalid saved consumer state; manual recovery required")
        errors = []
        for queue in queues:
            try:
                self.change_consumer("add_consumer", queue)
            except Exception as exc:
                errors.append(str(exc))
        if errors:
            raise GuardError("; ".join(errors))
        self.wait_for_queues(queues, exact=False)
        self.state_path.unlink()
        print("Original consumers resumed", file=sys.stderr, flush=True)

    def drain(self, wait_seconds=2400, poll_seconds=5):
        if self.state_path.exists():
            raise GuardError("Previous drain state exists; run resume first")
        queues = self.queues()
        if not queues:
            raise GuardError("Worker already has no consumers; refusing deployment")
        self.counts()  # Prove all inspection commands work before changing anything.
        fd = os.open(self.state_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump({"worker": self.worker, "queues": queues}, stream)
                stream.flush()
                os.fsync(stream.fileno())
        except BaseException:
            self.state_path.unlink(missing_ok=True)
            raise
        try:
            for queue in queues:
                self.change_consumer("cancel_consumer", queue)
            self.wait_for_queues([])
            deadline = self.clock() + wait_seconds
            idle_checks = 0
            while True:
                if self.queues():
                    raise GuardError("Worker resumed consumption during drain")
                counts = self.counts()
                idle_checks = idle_checks + 1 if not any(counts.values()) else 0
                print(f"Draining {self.worker}: {counts}", file=sys.stderr, flush=True)
                if idle_checks >= 2:
                    if self.queues():
                        raise GuardError("Worker resumed consumption during drain")
                    return
                if self.clock() >= deadline:
                    raise GuardError("Drain timed out; deployment must not restart worker")
                self.sleep(min(poll_seconds, max(0, deadline - self.clock())))
        except BaseException:
            try:
                self.resume()
            except Exception as exc:
                print(f"RESUME FAILED: {exc}; saved state retained", file=sys.stderr)
            raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "drain", "resume"))
    parser.add_argument("--state-path", default="/tmp/metateks-deploy-consumers.json")
    parser.add_argument("--wait-seconds", type=int, default=2400)
    args = parser.parse_args()
    if args.wait_seconds < 1:
        parser.error("wait-seconds must be positive")

    from main.celery import app

    def interrupted(signum, frame):
        raise InterruptedError(f"Interrupted by signal {signum}")

    signal.signal(signal.SIGTERM, interrupted)
    guard = Guard(app, f"celery@{socket.gethostname()}", args.state_path)
    try:
        if args.command == "check":
            queues = guard.queues()
            if not queues:
                raise GuardError("Worker has no active consumers")
            print(json.dumps({"worker": guard.worker, "queues": queues,
                              "tasks": guard.counts()}))
        elif args.command == "drain":
            guard.drain(wait_seconds=args.wait_seconds)
        else:
            guard.resume()
    except Exception as exc:
        print(f"DEPLOY BLOCKED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
