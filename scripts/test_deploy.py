"""Exercise deployment ordering and recovery with fake Docker commands."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("deploy.sh")


class DeploymentTest(unittest.TestCase):
    def run_deploy(self, failure="", same_worker=False):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            docker = root / "docker"
            docker.write_text("""#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
root = Path(os.environ['FAKE_ROOT'])
with (root / 'calls').open('a') as stream:
    stream.write(json.dumps(args) + '\\n')
failure = os.environ.get('FAILURE', '')
if args[:3] == ['compose', 'ps', '-q']:
    print('old' if os.environ['SAME_WORKER'] == '1' or not (root/'new').exists() else 'new')
elif args[0] == 'inspect':
    if (root/'new').exists() and os.environ['SAME_WORKER'] != '1':
        sys.exit(1)
    print('true')
elif args[:2] == ['compose', 'build']:
    sys.exit(1 if failure == 'build' else 0)
elif args[:2] == ['compose', 'up']:
    service = args[-1]
    if failure == service:
        sys.exit(1)
    if service == 'celery':
        (root/'new').touch()
elif args[0] == 'exec':
    if args[-1] == failure:
        sys.exit(1)
""")
            docker.chmod(0o755)
            for name, source in {
                "df": 'printf "Filesystem Blocks Used Available Use%% Mounted\\nmock 10000 0 9000 0%% /\\n"',
                "sleep": "exit 0",
                "curl": '[ "$FAILURE" != health ]',
            }.items():
                path = root / name
                path.write_text("#!/bin/sh\n" + source + "\n")
                path.chmod(0o755)
            result = subprocess.run(["bash", str(SCRIPT)], capture_output=True,
                                    env=dict(os.environ, PATH=f"{root}:{os.environ['PATH']}",
                                             FAKE_ROOT=temp, FAILURE=failure,
                                             SAME_WORKER="1" if same_worker else "0"))
            calls = [json.loads(line) for line in (root / "calls").read_text().splitlines()]
            return result, calls

    def test_success_migrates_web_before_replacing_worker(self):
        result, calls = self.run_deploy()
        self.assertEqual(result.returncode, 0, result.stderr)
        drain = next(i for i, cmd in enumerate(calls) if cmd[-1] == "drain")
        web = calls.index(["compose", "up", "-d", "--no-deps", "web"])
        worker = calls.index(["compose", "up", "-d", "--no-deps", "celery"])
        ready = next(i for i, cmd in enumerate(calls) if cmd[-1] == "check")
        nginx = calls.index(["compose", "up", "-d", "--no-deps", "nginx"])
        self.assertLess(drain, web)
        self.assertLess(web, worker)
        self.assertLess(worker, ready)
        self.assertLess(ready, nginx)
        self.assertNotIn("resume", [cmd[-1] for cmd in calls])

    def test_failure_never_restarts_undrained_worker_and_resumes_if_needed(self):
        for failure in ("build", "drain", "web", "health", "celery"):
            with self.subTest(failure=failure):
                result, calls = self.run_deploy(failure)
                self.assertNotEqual(result.returncode, 0)
                if failure != "build":
                    self.assertIn(["exec", "-i", "old", "python", "-", "resume"], calls)
                if failure in ("build", "drain", "web", "health"):
                    self.assertNotIn(["compose", "up", "-d", "--no-deps", "celery"], calls)

    def test_unchanged_worker_is_resumed(self):
        result, calls = self.run_deploy(same_worker=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(["exec", "-i", "old", "python", "-", "resume"], calls)

    def test_unready_replacement_fails_before_nginx_update(self):
        result, calls = self.run_deploy("check")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(["compose", "up", "-d", "--no-deps", "nginx"], calls)


if __name__ == "__main__":
    unittest.main()
