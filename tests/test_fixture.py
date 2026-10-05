# ruff: noqa: PT009, PT027, S310 -- unittest with exclusively loopback HTTP fixture URLs
"""Exercise healthy and fault paths independently without cloud resources."""

import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

from origin import fixture


class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), fixture.Fixture)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:" + str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_origin_status_does_not_break_health(self):
        for status in [404, 500, 502, 503, 504]:
            with (
                self.assertRaises(urllib.error.HTTPError) as error,
                urllib.request.urlopen(self.base + "/status/" + str(status), timeout=2),
            ):
                self.fail("Expected an origin error")
            self.assertEqual(error.exception.code, status)
            self.assertIn(
                ("Origin status " + str(status)).encode(), error.exception.read()
            )
        with urllib.request.urlopen(self.base + "/healthy", timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"Custom responses origin", response.read())

    def test_unmasked_control_is_identical_at_origin(self):
        bodies = []
        for path in [
            "/disclosure",
            "/disclosure-control",
            "/data-guard",
            "/data-guard-control",
        ]:
            with urllib.request.urlopen(self.base + path, timeout=2) as response:
                self.assertEqual(response.headers["Content-Type"], "application/json")
                bodies.append(response.read())
        self.assertTrue(all(body == bodies[0] for body in bodies[1:]))
        self.assertIn(b"4111111111111111", bodies[0])
        self.assertIn(b"example-ssn", bodies[0])

    def test_metadata_fixture_has_removable_fields(self):
        with urllib.request.urlopen(self.base + "/", timeout=2) as response:
            self.assertEqual(response.headers["X-Origin-Remove"], "synthetic")
            self.assertIn("origin-remove=", response.headers["Set-Cookie"])

    def test_reset_listener_keeps_healthy_server_available(self):
        original = fixture.RESET_PORT
        fixture.RESET_PORT = self.server.server_port
        try:
            with (
                self.assertRaises(
                    (ConnectionResetError, urllib.error.URLError, OSError)
                ),
                urllib.request.urlopen(self.base + "/", timeout=2),
            ):
                self.fail("Expected a connection reset")
        finally:
            fixture.RESET_PORT = original
        with urllib.request.urlopen(self.base + "/healthy", timeout=2) as response:
            self.assertEqual(response.status, 200)


if __name__ == "__main__":
    unittest.main()
