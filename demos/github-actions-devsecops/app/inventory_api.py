"""Fictional inventory API used by the GitHub Actions DevSecOps demo.

Independent portfolio demo; standard library only. The interesting part of
this demo is the pipeline around it, so the service is deliberately small but
written the way the pipeline expects: input validation, no shell calls, no
secrets in code, structured JSON errors.

Endpoints
  GET  /healthz                 liveness probe
  GET  /api/items               list items
  GET  /api/items/<sku>         one item
  POST /api/items/<sku>/reserve body: {"quantity": n}
"""
from __future__ import annotations

import json
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SKU_PATTERN = re.compile(r"^[A-Z]{3}-\d{4}$")
MAX_BODY_BYTES = 1024


class Inventory:
    def __init__(self, stock: dict[str, int]):
        self._stock = dict(stock)
        self._lock = threading.Lock()

    def list(self) -> list[dict]:
        with self._lock:
            return [{"sku": k, "available": v} for k, v in sorted(self._stock.items())]

    def get(self, sku: str) -> dict | None:
        with self._lock:
            return {"sku": sku, "available": self._stock[sku]} if sku in self._stock else None

    def reserve(self, sku: str, quantity: int) -> dict:
        with self._lock:
            if sku not in self._stock:
                raise KeyError(sku)
            if quantity > self._stock[sku]:
                raise ValueError("insufficient stock")
            self._stock[sku] -= quantity
            return {"sku": sku, "reserved": quantity, "available": self._stock[sku]}


def validate_sku(sku: str) -> bool:
    return bool(SKU_PATTERN.match(sku))


def parse_quantity(raw: bytes) -> int:
    """Parse and validate the reserve request body. Raises ValueError."""
    if len(raw) > MAX_BODY_BYTES:
        raise ValueError("body too large")
    try:
        data = json.loads(raw or b"{}")
    except json.JSONDecodeError as exc:
        raise ValueError("body must be JSON") from exc
    qty = data.get("quantity") if isinstance(data, dict) else None
    # bool is a subclass of int; reject it explicitly.
    if not isinstance(qty, int) or isinstance(qty, bool) or not 1 <= qty <= 100:
        raise ValueError("quantity must be an integer between 1 and 100")
    return qty


def route(inv: Inventory, method: str, path: str, body: bytes = b"") -> tuple[int, dict]:
    parts = [p for p in path.split("/") if p]
    if method == "GET" and parts == ["healthz"]:
        return 200, {"status": "ok", "version": os.environ.get("APP_VERSION", "dev")}
    if parts[:2] != ["api", "items"]:
        return 404, {"error": "not found"}
    if method == "GET" and len(parts) == 2:
        return 200, {"items": inv.list()}
    if len(parts) >= 3 and not validate_sku(parts[2]):
        return 400, {"error": "invalid sku format, expected e.g. ABC-1234"}
    if method == "GET" and len(parts) == 3:
        item = inv.get(parts[2])
        return (200, item) if item else (404, {"error": "unknown sku"})
    if method == "POST" and len(parts) == 4 and parts[3] == "reserve":
        try:
            qty = parse_quantity(body)
            return 200, inv.reserve(parts[2], qty)
        except KeyError:
            return 404, {"error": "unknown sku"}
        except ValueError as exc:
            return (409 if str(exc) == "insufficient stock" else 400), {"error": str(exc)}
    return 405, {"error": "method not allowed"}


INVENTORY = Inventory({"KBD-1001": 25, "MON-2040": 8, "USB-3300": 120})


class Handler(BaseHTTPRequestHandler):
    def _send(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        self._send(*route(INVENTORY, "GET", self.path))

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY_BYTES:
            self._send(413, {"error": "body too large"})
            return
        self._send(*route(INVENTORY, "POST", self.path, self.rfile.read(length)))

    def log_message(self, fmt, *args):
        return


def main():
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()  # noqa: S104  # nosec B104 - container service, port mapped by runtime


if __name__ == "__main__":
    main()
