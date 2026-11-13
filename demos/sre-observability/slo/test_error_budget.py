import csv
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

import error_budget as eb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "data"))
import generate  # noqa: E402  (deterministic synthetic data)

# Write the synthetic CSV once per test run instead of committing 4,000 rows.
_tmp = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
csv.writer(_tmp, lineterminator="\n").writerows([["timestamp", "total", "errors"], *generate.rows()])
_tmp.close()
SAMPLE = _tmp.name


def make(minutes, total, errors_fn):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [eb.Sample(start + timedelta(minutes=i), total, errors_fn(i)) for i in range(minutes)]


class ErrorBudgetTests(unittest.TestCase):
    def test_no_errors_means_full_budget(self):
        r = eb.build_report(make(60, 100, lambda i: 0), 99.5)
        self.assertEqual(r.budget_used_percent, 0.0)
        self.assertEqual(r.availability_percent, 100.0)
        self.assertEqual(r.alerts, [])

    def test_budget_math(self):
        # 10,000 requests at 99.5% allow 50 failures; 25 failures use half.
        r = eb.build_report(make(100, 100, lambda i: 1 if i < 25 else 0), 99.5)
        self.assertEqual(r.budget_requests, 50.0)
        self.assertEqual(r.budget_used_percent, 50.0)
        self.assertEqual(r.budget_remaining_percent, 50.0)

    def test_burn_rate(self):
        samples = make(60, 1000, lambda i: 5)  # 0.5% errors against 0.5% allowed
        end = samples[-1].ts
        self.assertAlmostEqual(eb.burn_rate(samples, end, timedelta(hours=1), 99.5), 1.0)

    def test_fast_burn_pages_only_when_both_windows_burn(self):
        # Errors stopped 35 minutes ago: both short windows (5m, 30m) are clean.
        samples = make(60, 1000, lambda i: 100 if i < 25 else 0)
        self.assertFalse([a for a in eb.evaluate_alerts(samples, 99.5) if a["severity"] == "page"])
        # Errors still happening: both windows burn, so it pages.
        samples = make(60, 1000, lambda i: 100)
        self.assertTrue([a for a in eb.evaluate_alerts(samples, 99.5) if a["severity"] == "page"])

    def test_rejects_bad_input(self):
        with self.assertRaises(ValueError):
            eb.build_report(make(5, 10, lambda i: 0), 100)
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            fh.write("timestamp,total,errors\n2026-01-01T00:00:00Z,5,9\n")
        try:
            with self.assertRaises(ValueError):
                eb.load_samples(fh.name)
        finally:
            os.unlink(fh.name)

    def test_sample_data_scenario(self):
        r = eb.build_report(eb.load_samples(SAMPLE), 99.5)
        self.assertEqual(r.total_requests > 0, True)
        # The synthetic incident should consume a large share of the budget and page.
        self.assertGreater(r.budget_used_percent, 40)
        self.assertTrue(any(a["severity"] == "page" for a in r.alerts))

    def test_cli_exit_code(self):
        self.assertEqual(eb.main([SAMPLE, "--slo", "99.5", "--json"]), 2)


if __name__ == "__main__":
    unittest.main()
