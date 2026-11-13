"""Run the Linux scripts against fixture files and check their output.

  python3 -m unittest discover -s demos/server-ops-toolkit/tests -v
"""
import json
import os
import subprocess
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
LINUX = os.path.join(HERE, "..", "linux")
FIX = os.path.join(HERE, "fixtures")


def run(script, *args, env=None):
    e = dict(os.environ, **(env or {}))
    return subprocess.run(["bash", os.path.join(LINUX, script), *args],
                          capture_output=True, text=True, env=e, check=False)


class HealthCheckTests(unittest.TestCase):
    def test_healthy_fixture_json(self):
        # Disk thresholds at 100% so the result depends only on the fixture files.
        r = run("health-check.sh", "--json", "--disk-warn", "100", "--disk-crit", "100",
                env={"PROC_ROOT": os.path.join(FIX, "proc")})
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        data = json.loads(r.stdout)
        checks = {c["name"]: c for c in data["checks"]}
        self.assertEqual(checks["cpu_load"]["state"], "OK")
        self.assertIn("2 cores", checks["cpu_load"]["detail"])
        self.assertEqual(checks["memory"]["detail"], "75% used")

    def test_busy_fixture_warns(self):
        r = run("health-check.sh", "--disk-warn", "100", "--disk-crit", "100",
                env={"PROC_ROOT": os.path.join(FIX, "proc_busy")})
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertIn("WARNING", r.stdout)
        self.assertIn("95% used", r.stdout)

    def test_disk_critical_threshold(self):
        # Any mounted filesystem is >= 0% used, so a 0% critical threshold must trip.
        r = run("health-check.sh", "--disk-warn", "0", "--disk-crit", "0",
                env={"PROC_ROOT": os.path.join(FIX, "proc")})
        self.assertEqual(r.returncode, 2, r.stdout)

    def test_bad_option(self):
        self.assertEqual(run("health-check.sh", "--nope").returncode, 64)


class SshCheckTests(unittest.TestCase):
    def test_good_config_passes(self):
        r = run("ssh-hardening-check.sh", os.path.join(FIX, "sshd_good"))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertNotIn("FAIL", r.stdout)

    def test_bad_config_fails_and_first_value_wins(self):
        r = run("ssh-hardening-check.sh", os.path.join(FIX, "sshd_bad"))
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stdout, r"FAIL\s+permitrootlogin\s+yes")
        # The later "PasswordAuthentication no" must be ignored, as sshd does.
        self.assertRegex(r.stdout, r"FAIL\s+passwordauthentication\s+yes")
        # Unset MaxAuthTries falls back to sshd's default of 6, which fails.
        self.assertRegex(r.stdout, r"FAIL\s+maxauthtries\s+6")


class UserAuditTests(unittest.TestCase):
    def test_flags_empty_password_and_sudo(self):
        r = run("user-audit.sh", env={
            "PASSWD_FILE": os.path.join(FIX, "passwd"),
            "SHADOW_FILE": os.path.join(FIX, "shadow"),
            "GROUP_FILE": os.path.join(FIX, "group"),
        })
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = {l.split()[0]: l for l in r.stdout.splitlines()[1:]}
        self.assertEqual(set(lines), {"root", "alice", "bob"})  # nologin users skipped
        self.assertIn("yes", lines["alice"].split())
        self.assertIn("EMPTY", lines["bob"])
        self.assertIn("locked", lines["root"])


if __name__ == "__main__":
    unittest.main()
