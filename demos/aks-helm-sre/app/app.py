"""Clinic Slots API - a tiny fictional service used by the AKS + Helm SRE demo.

Independent portfolio demo. All data is synthetic. Uses only the Python
standard library so it runs anywhere with Python 3.10+.

Endpoints
  GET /healthz           liveness/readiness probe
  GET /api/slots         synthetic appointment slots for a fictional clinic
  GET /metrics           Prometheus text format counters
"""
import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.environ.get("APP_VERSION", "1.0.0")
SLOTS = [
    {"id": "S-1001", "clinic": "Demo Clinic North", "time": "09:30", "available": True},
    {"id": "S-1002", "clinic": "Demo Clinic North", "time": "10:00", "available": False},
    {"id": "S-1003", "clinic": "Demo Clinic South", "time": "11:15", "available": True},
]
METRICS = {"requests_total": 0, "errors_total": 0}
STARTED = time.time()


def route(path):
    """Return (status, content_type, body) for a request path."""
    if path == "/healthz":
        return 200, "application/json", {"status": "ok", "version": VERSION}
    if path == "/api/slots":
        return 200, "application/json", {"slots": SLOTS, "count": len(SLOTS)}
    if path == "/metrics":
        lines = [
            "# TYPE http_requests_total counter",
            f"http_requests_total {METRICS['requests_total']}",
            "# TYPE http_errors_total counter",
            f"http_errors_total {METRICS['errors_total']}",
            "# TYPE process_uptime_seconds gauge",
            f"process_uptime_seconds {int(time.time() - STARTED)}",
        ]
        return 200, "text/plain; version=0.0.4", "\n".join(lines) + "\n"
    return 404, "application/json", {"error": "not found"}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802 (stdlib naming)
        METRICS["requests_total"] += 1
        status, ctype, body = route(self.path)
        if status >= 500:
            METRICS["errors_total"] += 1
        data = body if isinstance(body, str) else json.dumps(body)
        payload = data.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, fmt, *args):
        print(json.dumps({"path": self.path, "msg": fmt % args}))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    print(f"Clinic Slots API {VERSION} listening on :{port}")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
