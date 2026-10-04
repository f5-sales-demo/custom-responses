"""Synthetic fixture and isolated fault listeners for the owned showcase."""

import contextlib
import html
import json
import logging
import os
import socket
import struct
import threading
import time
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import cast
from urllib.parse import urlsplit

SYNTHETIC = {
    "card": "4111111111111111",
    "ssn": "example-ssn",
    "label": "Synthetic demonstration data",
}


LOGGER = logging.getLogger(__name__)

RESET_PORT = 8082
DELAY_PORT = 8084
ERROR_PORT = 8081
MIN_ERROR_STATUS = 300
MAX_ERROR_STATUS = 599


class Fixture(BaseHTTPRequestHandler):
    """Serve synthetic responses and dedicated bounded fault listeners."""

    # pylint: disable-next=arguments-differ
    def log_message(self, message_format: str, *args: object) -> None:
        """Write identifying request records only to the private system journal."""
        # systemd journal is private; public receipts omit client and request IDs.
        LOGGER.info(
            json.dumps(
                {
                    "port": cast("ThreadingHTTPServer", self.server).server_port,
                    "path": urlsplit(self.path).path,
                    "event": message_format % args,
                }
            )
        )

    # pylint: disable-next=invalid-name
    def do_POST(self) -> None:
        """Consume a bounded synthetic POST before serving the response."""
        length = min(int(self.headers.get("Content-Length", "0")), 65536)
        self.rfile.read(length)
        self.do_GET()

    # pylint: disable-next=invalid-name
    def do_GET(self) -> None:
        """Return the fixture body or activate this dedicated fault listener."""
        port = cast("ThreadingHTTPServer", self.server).server_port
        if port == RESET_PORT:
            self.connection.setsockopt(
                socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0)
            )
            self.connection.close()
            return
        if port == DELAY_PORT:
            time.sleep(8)
        path = urlsplit(self.path).path
        status, content_type = 200, "text/html; charset=utf-8"
        body: str | bytes = (
            '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Custom responses origin</title></head><body><main><h1>Custom responses origin</h1><p>Healthy synthetic fixture.</p>'
        )
        if path in ["/sensitive", "/sensitive-control"]:
            content_type, body = "application/json", json.dumps(SYNTHETIC)
        elif path.startswith("/status/"):
            try:
                status = int(path.rsplit("/", 1)[1])
                status = (
                    status
                    if MIN_ERROR_STATUS <= status <= MAX_ERROR_STATUS
                    else HTTPStatus.BAD_REQUEST
                )
            except ValueError:
                status = 400
            body = "<h1>Origin status " + str(status) + "</h1>"
        elif path.startswith("/httpbin/"):
            try:
                with urllib.request.urlopen(
                    "http://127.0.0.1:8085/" + self.path[len("/httpbin/") :], timeout=10
                ) as r:
                    status, content_type, body = (
                        r.status,
                        r.headers.get("Content-Type", "application/octet-stream"),
                        r.read(),
                    )
            except urllib.error.HTTPError as e:
                status, content_type, body = (
                    e.code,
                    e.headers.get("Content-Type", "application/octet-stream"),
                    e.read(),
                )
        else:
            page_body = str(body)
            inventory = Path(__file__).with_name("scenarios.json")
            if inventory.exists():
                for item in json.loads(inventory.read_text()):
                    page_body += (
                        '<p><a href="https://'
                        + html.escape(item["hostname"])
                        + html.escape(item["trigger"])
                        + '">'
                        + html.escape(item["id"])
                        + "</a></p>"
                    )
            body = page_body + "</main></body></html>"
        if port == ERROR_PORT:
            status, body = 500, "<h1>Origin status 500</h1>"
        encoded_body = body.encode() if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded_body)))
        self.send_header("X-Response-Owner", "custom-responses-origin")
        self.send_header("X-Origin-Remove", "synthetic")
        self.send_header("Set-Cookie", "origin-remove=synthetic; Path=/; SameSite=Lax")
        if status == HTTPStatus.FOUND:
            self.send_header("Location", "/new")
        self.end_headers()
        with contextlib.suppress(BrokenPipeError, ConnectionResetError):
            self.wfile.write(encoded_body)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    ports = json.loads(os.environ.get("FIXTURE_PORTS", "[8080,8081,8082,8084]"))
    for port in ports:
        server = ThreadingHTTPServer(("0.0.0.0", port), Fixture)  # noqa: S104 -- owned VM NSG restricts published listeners
        threading.Thread(target=server.serve_forever, daemon=True).start()
    threading.Event().wait()
