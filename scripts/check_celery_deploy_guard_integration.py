"""Run only in an isolated app container with PROBE_QUEUE=deployguard-probe-... .

Start this file with `worker` to serve the dedicated probe queue; execute it
again without arguments in that container to verify draining against Redis.
"""

import os
from pathlib import Path
import socket
import sys
import threading
import time

from celery_deploy_guard import Guard, GuardError
from main.celery import app


QUEUE = os.environ["PROBE_QUEUE"]
assert QUEUE.startswith("deployguard-probe-")
NODE = f"celery@{socket.gethostname()}"
TASK = "metateks.deploy_guard_probe"


@app.task(name=TASK)
def probe(seconds):
    time.sleep(seconds)
    return "completed"


def send(seconds):
    return app.send_task(TASK, args=[seconds], queue=QUEUE)


def wait_active(guard):
    deadline = time.monotonic() + 30
    while not guard.inspect("active"):
        assert time.monotonic() < deadline, "Probe task did not start"
        time.sleep(0.1)


def verify():
    state = Path("/tmp/metateks-deploy-probe-state.json")
    guard = Guard(app, NODE, state, reply_timeout=5)
    assert guard.queues() == [QUEUE], "Refusing to test a worker with non-probe consumers"
    running = send(15)
    wait_active(guard)
    waiting = []
    errors = []

    def enqueue_while_paused():
        try:
            deadline = time.monotonic() + 30
            while guard.queues():
                assert time.monotonic() < deadline, "Worker did not pause"
                time.sleep(0.1)
            waiting.append(send(0))
        except BaseException as exc:
            errors.append(exc)

    producer = threading.Thread(target=enqueue_while_paused, daemon=True)
    producer.start()
    try:
        guard.drain(wait_seconds=60, poll_seconds=0.5)
        producer.join(timeout=10)
        assert not producer.is_alive() and not errors and len(waiting) == 1, errors
        assert running.get(timeout=10) == "completed"
        assert waiting[0].state == "PENDING", "A new task ran while consumption was paused"
        assert guard.queues() == []
        print("PASS: running task finished; newly queued task stayed in Redis", flush=True)
    finally:
        guard.resume()
    assert waiting[0].get(timeout=30) == "completed"
    running.forget()
    print("PASS: queued task ran after consumers resumed", flush=True)

    running = send(10)
    wait_active(guard)
    try:
        guard.drain(wait_seconds=1, poll_seconds=0.2)
        raise AssertionError("Busy worker was reported safe to restart")
    except GuardError as exc:
        assert "timed out" in str(exc), str(exc)
    assert guard.queues() == [QUEUE] and not state.exists()
    assert running.get(timeout=30) == "completed"
    for result in [running, *waiting]:
        result.forget()
    print("PASS: timeout restored consumption without interrupting running task", flush=True)


if __name__ == "__main__":
    if sys.argv[1:] == ["worker"]:
        app.worker_main(["worker", "--queues=" + QUEUE, "--concurrency=1",
                         "--loglevel=WARNING", "--without-gossip", "--without-mingle"])
    else:
        verify()
