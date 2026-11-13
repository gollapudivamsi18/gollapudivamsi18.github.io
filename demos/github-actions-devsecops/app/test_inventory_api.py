import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import inventory_api as api


def fresh():
    return api.Inventory({"KBD-1001": 5, "MON-2040": 1})


class RouteTests(unittest.TestCase):
    def test_health(self):
        self.assertEqual(api.route(fresh(), "GET", "/healthz")[0], 200)

    def test_list_and_get(self):
        inv = fresh()
        status, body = api.route(inv, "GET", "/api/items")
        self.assertEqual(status, 200)
        self.assertEqual(len(body["items"]), 2)
        self.assertEqual(api.route(inv, "GET", "/api/items/KBD-1001")[1]["available"], 5)
        self.assertEqual(api.route(inv, "GET", "/api/items/ZZZ-9999")[0], 404)

    def test_invalid_sku_rejected(self):
        for bad in ["kbd-1001", "KBD1001", "KBD-10011", "../etc", "KBD-1001;rm"]:
            self.assertEqual(api.route(fresh(), "GET", f"/api/items/{bad}")[0], 400, bad)

    def test_reserve(self):
        inv = fresh()
        status, body = api.route(inv, "POST", "/api/items/KBD-1001/reserve", b'{"quantity": 2}')
        self.assertEqual((status, body["available"]), (200, 3))
        self.assertEqual(api.route(inv, "POST", "/api/items/MON-2040/reserve", b'{"quantity": 2}')[0], 409)
        self.assertEqual(api.route(inv, "POST", "/api/items/XYZ-0001/reserve", b'{"quantity": 1}')[0], 404)

    def test_quantity_validation(self):
        for body in [b"", b"not json", b'{"quantity": 0}', b'{"quantity": 101}',
                     b'{"quantity": "3"}', b'{"quantity": true}', b"[1]", b"x" * 2000]:
            with self.assertRaises(ValueError, msg=body[:20]):
                api.parse_quantity(body)
        self.assertEqual(api.parse_quantity(b'{"quantity": 100}'), 100)

    def test_method_not_allowed(self):
        self.assertEqual(api.route(fresh(), "POST", "/api/items/KBD-1001")[0], 405)


class HttpTests(unittest.TestCase):
    """Start the real server on a free port and call it over HTTP."""

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), api.Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def test_health_over_http(self):
        with urllib.request.urlopen(self.base + "/healthz") as r:
            self.assertEqual(r.status, 200)
            self.assertEqual(r.headers["X-Content-Type-Options"], "nosniff")
            self.assertEqual(json.load(r)["status"], "ok")

    def test_oversized_body_rejected(self):
        req = urllib.request.Request(self.base + "/api/items/KBD-1001/reserve",
                                     data=b"x" * 5000, method="POST")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 413)


if __name__ == "__main__":
    unittest.main()
