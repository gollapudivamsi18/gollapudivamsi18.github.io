import random
import unittest

import orders_service as svc


class OrdersServiceTests(unittest.TestCase):
    def test_probes(self):
        rng = random.Random(1)
        self.assertEqual(svc.handle("/healthz", rng, 0, 0, False)[0], 200)
        self.assertEqual(svc.handle("/readyz", rng, 0, 0, False)[0], 200)
        self.assertEqual(svc.handle("/readyz", rng, 0, 0, True)[0], 503)

    def test_error_injection(self):
        rng = random.Random(7)
        codes = [svc.handle("/api/orders", rng, 1.0, 0, False)[0] for _ in range(20)]
        self.assertEqual(set(codes), {500})
        codes = [svc.handle("/api/orders", rng, 0.0, 0, False)[0] for _ in range(20)]
        self.assertEqual(set(codes), {200})

    def test_unknown_path(self):
        self.assertEqual(svc.handle("/nope", random.Random(), 0, 0, False)[0], 404)

    def test_metrics_exposition(self):
        m = svc.Metrics()
        m.observe("/api/orders", 200, 0.03)
        m.observe("/api/orders", 500, 0.9)
        text = m.render()
        self.assertIn('http_requests_total{route="/api/orders",code="200"} 1', text)
        self.assertIn('http_requests_total{route="/api/orders",code="500"} 1', text)
        self.assertIn('http_request_duration_seconds_bucket{route="/api/orders",le="0.05"} 1', text)
        self.assertIn('http_request_duration_seconds_bucket{route="/api/orders",le="1.0"} 2', text)
        self.assertIn('http_request_duration_seconds_count{route="/api/orders"} 2', text)


if __name__ == "__main__":
    unittest.main()
