import os
import unittest

import build_report

SAMPLE = os.path.join(os.path.dirname(__file__), "sample-results.csv")


class ReportTests(unittest.TestCase):
    def test_summary_numbers(self):
        s = build_report.summarise(build_report.load(SAMPLE))
        self.assertEqual(s["total"], 8)
        self.assertEqual(s["compliant"], 6)
        self.assertEqual(s["percent"], 75.0)
        self.assertEqual(s["families"]["Linux"], (3, 4))
        self.assertEqual(s["families"]["Windows"], (3, 4))

    def test_attention_hosts_listed(self):
        text = build_report.render(build_report.load(SAMPLE))
        self.assertIn("lab-ubuntu-02", text)
        self.assertIn("lab-win-03", text)

    def test_empty_input(self):
        self.assertEqual(build_report.summarise([])["percent"], 0.0)


if __name__ == "__main__":
    unittest.main()
