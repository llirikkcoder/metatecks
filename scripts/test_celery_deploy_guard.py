"""python3 scripts/test_celery_deploy_guard.py; no broker or Docker required."""

from collections import deque
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from celery_deploy_guard import Guard, GuardError


NODE = "celery@test"


class Control:
    def __init__(self):
        self.queues = ["celery", "other"]
        self.tasks = {kind: [] for kind in ("active", "reserved", "scheduled")}
        self.overrides = {}
        self.replies = {}
        self.calls = []
        self.samples = deque()

    def inspect(self, **kwargs):
        assert kwargs["destination"] == [NODE]
        return SimpleNamespace(**{kind: lambda kind=kind: self.read(kind)
                                  for kind in (*self.tasks, "active_queues")})

    def read(self, kind):
        if kind in self.overrides:
            return self.overrides[kind]
        if kind == "reserved" and self.samples:
            self.tasks = self.samples.popleft()
        payload = ([{"name": q} for q in self.queues] if kind == "active_queues"
                   else self.tasks[kind])
        return {NODE: payload}

    def cancel_consumer(self, queue, **kwargs):
        self.calls.append(("cancel", queue))
        if queue in self.queues:
            self.queues.remove(queue)
        return self.replies.get(("cancel", queue), [{NODE: {"ok": "cancelled"}}])

    def add_consumer(self, queue, **kwargs):
        self.calls.append(("add", queue))
        if queue not in self.queues:
            self.queues.append(queue)
        return self.replies.get(("add", queue), [{NODE: {"ok": "added"}}])


class GuardTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.state = Path(self.temp.name) / "state.json"
        self.control = Control()
        self.now = 0
        self.on_sleep = lambda: None
        self.guard = Guard(SimpleNamespace(control=self.control), NODE, self.state,
                           clock=lambda: self.now, sleep=self.sleep)

    def sleep(self, seconds):
        self.now += seconds
        self.on_sleep()

    def test_drain_retains_paused_state_until_explicit_resume(self):
        self.guard.drain(poll_seconds=1)
        self.assertEqual(self.control.queues, [])
        self.assertTrue(self.state.exists())
        self.assertEqual(self.state.stat().st_mode & 0o777, 0o600)
        self.guard.resume()
        self.assertCountEqual(self.control.queues, ["celery", "other"])
        self.assertFalse(self.state.exists())

    def test_waits_for_active_reserved_and_scheduled_work(self):
        for kind in ("active", "reserved", "scheduled"):
            with self.subTest(kind=kind):
                self.control.tasks[kind] = [{"id": "running"}]
                def finish():
                    self.assertEqual(self.control.queues, [])
                    self.control.tasks[kind] = []
                self.on_sleep = finish
                self.guard.drain(poll_seconds=1)
                self.assertGreater(self.now, 0)
                self.guard.resume()

    def test_missing_or_malformed_replies_block_before_pausing(self):
        bad = (None, {}, {"other-worker": []}, {NODE: [], "extra": []},
               {NODE: {"error": "failed"}})
        for command in ("active", "reserved", "scheduled", "active_queues"):
            for reply in bad:
                with self.subTest(command=command, reply=reply):
                    self.control.overrides = {command: reply}
                    with self.assertRaises(GuardError):
                        self.guard.drain()
                    self.assertEqual(self.control.calls, [])
                    self.assertFalse(self.state.exists())

    def test_missing_cancel_ack_restores_every_original_consumer(self):
        self.control.replies[("cancel", "celery")] = []
        with self.assertRaises(GuardError):
            self.guard.drain()
        self.assertCountEqual(self.control.queues, ["celery", "other"])
        self.assertFalse(self.state.exists())

    def test_timeout_resumes_without_losing_running_work(self):
        task = {"id": "exchange"}
        self.control.tasks["active"] = [task]
        with self.assertRaisesRegex(GuardError, "timed out"):
            self.guard.drain(wait_seconds=2, poll_seconds=1)
        self.assertEqual(self.control.tasks["active"], [task])
        self.assertCountEqual(self.control.queues, ["celery", "other"])
        self.assertFalse(self.state.exists())

    def test_inspection_failure_after_pause_resumes_original_queues(self):
        self.on_sleep = lambda: self.control.overrides.update(active=None)
        with self.assertRaises(GuardError):
            self.guard.drain(poll_seconds=1)
        self.assertCountEqual(self.control.queues, ["celery", "other"])
        self.assertFalse(self.state.exists())

    def test_failed_resume_retains_state_and_attempts_other_queues(self):
        self.guard.drain(poll_seconds=1)
        self.control.replies[("add", "celery")] = []
        with self.assertRaises(GuardError):
            self.guard.resume()
        self.assertIn(("add", "other"), self.control.calls)
        self.assertTrue(self.state.exists())
        del self.control.replies[("add", "celery")]
        self.guard.resume()
        self.assertFalse(self.state.exists())

    def test_reenabled_consumer_blocks_drain(self):
        self.on_sleep = lambda: self.control.queues.append("unexpected")
        with self.assertRaisesRegex(GuardError, "resumed consumption"):
            self.guard.drain(poll_seconds=1)
        self.assertIn("celery", self.control.queues)

    def test_interruption_resumes_before_propagating(self):
        def interrupt():
            raise KeyboardInterrupt()
        self.on_sleep = interrupt
        with self.assertRaises(KeyboardInterrupt):
            self.guard.drain(poll_seconds=1)
        self.assertCountEqual(self.control.queues, ["celery", "other"])
        self.assertFalse(self.state.exists())

    def test_existing_state_blocks_another_drain(self):
        self.guard.drain(poll_seconds=1)
        calls = list(self.control.calls)
        with self.assertRaisesRegex(GuardError, "Previous drain"):
            self.guard.drain()
        self.assertEqual(self.control.calls, calls)
        self.guard.resume()

    def test_one_idle_snapshot_is_insufficient(self):
        empty = {kind: [] for kind in self.control.tasks}
        busy = dict(empty, active=[{"id": "late-accepted-task"}])
        self.control.samples.extend([empty, empty, busy, empty, empty])
        self.guard.drain(poll_seconds=1)
        self.assertEqual(self.now, 3)
        self.guard.resume()


if __name__ == "__main__":
    unittest.main()
