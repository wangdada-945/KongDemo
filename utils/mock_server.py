from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse


DEMO_TOKEN = "demo-token"


class _Handler(BaseHTTPRequestHandler):
    server_version = "MockApi/1.0"

    def _send_json(self, code: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> Any | None:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return None

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/get":
            qs = {k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()}
            self._send_json(200, {"args": qs, "path": parsed.path})
            return

        if parsed.path == "/protected":
            auth = self.headers.get("Authorization", "")
            if auth != f"Bearer {DEMO_TOKEN}":
                self._send_json(401, {"error": "unauthorized"})
                return
            self._send_json(200, {"ok": True})
            return

        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/post":
            payload = self._read_json()
            self._send_json(200, {"json": payload, "path": parsed.path})
            return

        if parsed.path == "/login":
            payload = self._read_json() or {}
            username = payload.get("username")
            password = payload.get("password")
            if username == "admin" and password == "123456":
                self._send_json(200, {"token": DEMO_TOKEN})
            else:
                self._send_json(403, {"error": "bad credentials"})
            return

        self._send_json(404, {"error": "not found"})

    def log_message(self, fmt: str, *args) -> None:  # silence default stdout logs
        return


@dataclass(frozen=True)
class MockServer:
    host: str
    port: int

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


def start_mock_server(host: str = "127.0.0.1", port: int = 0) -> tuple[MockServer, callable]:
    httpd = HTTPServer((host, port), _Handler)
    actual_host, actual_port = httpd.server_address[0], httpd.server_address[1]

    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    def _stop() -> None:
        httpd.shutdown()
        httpd.server_close()

    return MockServer(actual_host, actual_port), _stop

