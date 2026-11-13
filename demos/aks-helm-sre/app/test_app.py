import unittest

import app


class RouteTests(unittest.TestCase):
    def test_health(self):
        status, _, body = app.route("/healthz")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_slots(self):
        status, _, body = app.route("/api/slots")
        self.assertEqual(status, 200)
        self.assertEqual(body["count"], len(body["slots"]))

    def test_metrics_format(self):
        status, ctype, body = app.route("/metrics")
        self.assertEqual(status, 200)
        self.assertIn("text/plain", ctype)
        self.assertIn("http_requests_total", body)

    def test_unknown_path(self):
        status, _, _ = app.route("/nope")
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
