"""Fictional "orders" service that exposes Prometheus metrics.

Independent portfolio demo. Standard library only. Failure and latency are
injected on purpose so the alert rules and dashboard have something to show.

Environment
  PORT            listen port (default 8081)
  ERROR_RATE      fraction of /api/orders requests that return 500 (default 0.002)
  SLOW_RATE       fraction of requests delayed by ~0.8 s (default 0.02)

Endpoints
  GET /healthz       liveness probe
  GET /readyz        readiness probe (returns 503 while DRAINING=1)
  GET /api/orders    synthetic order list
  GET /metrics       Prometheus text exposition format
"""
from __future__ import annotations

import json
import os
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BUCKETS = (0.05, 0.1, 0.25, 0.5, 1.0, 2.5)
ORDERS = [
    {"id": "ORD-1001", "status": "shipped", "items": 3},
    {"id": "ORD-1002", "status": "processing", "items": 1},
    {"id": "ORD-1003", "status": "delivered", "items": 2},
]


class Metrics:
    """Minimal counter + histogram store, safe across handler threads."""

    def __init__(self):
        self._lock = threading.Lock()
        self.requests = {}          # (route, code) -> count
        self.buckets = {}           # (route, le) -> count
        self.sums = {}              # route -> seconds
        self.counts = {}            # route -> count

    def observe(self, route: str, code: int, seconds: float) -> None:
        with self._lock:
            key = (route, str(code))
            self.requests[key] = self.requests.get(key, 0) + 1
            for le in BUCKETS:
                if seconds <= le:
                    self.buckets[(route, le)] = self.buckets.get((route, le), 0) + 1
            self.sums[route] = self.sums.get(route, 0.0) + seconds
            self.counts[route] = self.counts.get(route, 0) + 1

    def render(self) -> str:
        with self._lock:
            lines = [
                "# HELP http_requests_total HTTP requests by route and status code.",
                "# TYPE http_requests_total counter",
            ]
            for (route, code), n in sorted(self.requests.items()):
                lines.append(f'http_requests_total{{route="{route}",code="{code}"}} {n}')
            lines += [
                "# HELP http_request_duration_seconds Request latency.",
                "# TYPE http_request_duration_seconds histogram",
            ]
            for route in sorted(self.counts):
                for le in BUCKETS:
                    n = self.buckets.get((route, le), 0)
                    lines.append(f'http_request_duration_seconds_bucket{{route="{route}",le="{le}"}} {n}')
                lines.append(f'http_request_duration_seconds_bucket{{route="{route}",le="+Inf"}} {self.counts[route]}')
                lines.append(f'http_request_duration_seconds_sum{{route="{route}"}} {self.sums[route]:.6f}')
                lines.append(f'http_request_duration_seconds_count{{route="{route}"}} {self.counts[route]}')
            return "\n".join(lines) + "\n"


METRICS = Metrics()


def handle(path: str, rng: random.Random, error_rate: float, slow_rate: float, draining: bool):
    """Return (status, body_dict, simulated_delay_seconds)."""
    if path == "/healthz":
        return 200, {"status": "ok"}, 0.0
    if path == "/readyz":
        return (503, {"status": "draining"}, 0.0) if draining else (200, {"status": "ready"}, 0.0)
    if path == "/api/orders":
        delay = 0.8 if rng.random() < slow_rate else 0.02
        if rng.random() < error_rate:
            return 500, {"error": "simulated upstream failure"}, delay
        return 200, {"orders": ORDERS}, delay
    return 404, {"error": "not found"}, 0.0


class Handler(BaseHTTPRequestHandler):
    rng = random.Random()

    def do_GET(self):  # noqa: N802 (stdlib naming)
        if self.path == "/metrics":
            body = METRICS.render().encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        start = time.perf_counter()
        status, payload, delay = handle(
            self.path,
            self.rng,
            float(os.environ.get("ERROR_RATE", "0.002")),
            float(os.environ.get("SLOW_RATE", "0.02")),
            os.environ.get("DRAINING") == "1",
        )
        time.sleep(delay)
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        route = self.path if self.path in ("/api/orders", "/healthz", "/readyz") else "other"
        METRICS.observe(route, status, time.perf_counter() - start)

    def log_message(self, fmt, *args):  # keep container logs quiet
        return


def main():
    port = int(os.environ.get("PORT", "8081"))
    print(f"orders-service listening on :{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()  # nosec B104 - container service


if __name__ == "__main__":
    main()
