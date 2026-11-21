"""Run on Linux: python3 scripts/test_pg_backup.py (no Docker/production DB needed)."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("pg_backup.sh")


class BackupTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.backups = self.root / "backups"
        self.backups.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.command("df", '#!/bin/sh\nprintf "Filesystem 1M-blocks Used Available Use%% Mounted\\nmock 10000 1000 %s 10%% /\\n" "${FREE_MB:-9000}"\n')
        self.command("docker", """#!/usr/bin/env python3
import os, sys
from pathlib import Path
args = sys.argv[1:]
if args[0] == 'inspect':
    print('true')
elif 'pg_restore' in args:
    sys.stdin.buffer.read()
    sys.exit(int(os.environ.get('RESTORE_FAIL', '0')))
else:
    marker = os.environ.get('MARKER')
    if marker:
        Path(marker).touch()
        import time
        time.sleep(2)
    sys.stdout.buffer.write(b'x' * int(os.environ.get('DUMP_SIZE', '1048576')))
    sys.exit(int(os.environ.get('DUMP_FAIL', '0')))
""")
        self.env = dict(os.environ, BACKUP_DIR=str(self.backups), KEEP="2",
                        PATH=f"{self.bin}:{os.environ['PATH']}")
        for n in range(3):
            old = self.backups / f"metateks_2026010{n+1}_033001.dump"
            old.write_bytes(b"old backup")
            os.utime(old, (n + 1, n + 1))
        self.legacy = self.backups / "metateks_backup_20251231.tar.gz"
        self.legacy.write_bytes(b"legacy archive")

    def command(self, name, contents):
        path = self.bin / name
        path.write_text(contents)
        path.chmod(0o755)

    def run_backup(self, **env):
        return subprocess.run(["bash", str(SCRIPT)], env=dict(self.env, **env),
                              capture_output=True, text=True)

    def dumps(self):
        return sorted(self.backups.glob("*.dump"))

    def test_success_rotates_only_after_validation_and_protects_dump(self):
        result = self.run_backup()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(self.dumps()), 2)
        new = max(self.dumps(), key=lambda p: p.stat().st_mtime)
        self.assertEqual(new.stat().st_mode & 0o777, 0o600)
        self.assertEqual(new.stat().st_size, 1048576)
        self.assertTrue(self.legacy.exists())
        self.assertEqual(list(self.backups.glob("*.tmp.*")), [])

    def test_failures_preserve_previous_backups_and_remove_partial_files(self):
        for env in ({"FREE_MB": "100"}, {"DUMP_FAIL": "1"},
                    {"DUMP_SIZE": "100"}, {"RESTORE_FAIL": "1"},
                    {"KEEP": "0"}, {"KEEP": "invalid"}):
            with self.subTest(env=env):
                result = self.run_backup(**env)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(len(self.dumps()), 3)
                self.assertEqual(list(self.backups.glob("*.tmp.*")), [])
                self.assertTrue(self.legacy.exists())

    def test_concurrent_backup_is_rejected(self):
        marker = self.root / "started"
        first = subprocess.Popen(["bash", str(SCRIPT)],
                                 env=dict(self.env, MARKER=str(marker)),
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            import time
            for _ in range(100):
                if marker.exists():
                    break
                time.sleep(0.02)
            self.assertTrue(marker.exists())
            second = self.run_backup()
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("другой бэкап", second.stdout)
            stdout, stderr = first.communicate(timeout=10)
            self.assertEqual(first.returncode, 0, stdout + stderr)
            self.assertEqual(len(self.dumps()), 2)
        finally:
            if first.poll() is None:
                first.kill()
                first.wait()


if __name__ == "__main__":
    unittest.main()
