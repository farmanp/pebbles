"""Transport regressions: authentication, validation order and error responses."""
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from pebbles.web import Handler


class HandlerContracts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.storage = Path(self.tmp.name)

    def request(self, path, body=b"{}", headers=None, method="POST"):
        handler = Handler.__new__(Handler)
        handler.server = SimpleNamespace(
            storage=self.storage, server_port=8848, token="secret"
        )
        handler.path = path
        handler.rfile = io.BytesIO(body)
        handler.headers = {
            "Host": "127.0.0.1:8848",
            "X-Pebbles-Token": "secret",
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
            **(headers or {}),
        }
        responses = []
        handler.send = lambda value, status=200, **kwargs: responses.append(
            (status, value)
        )
        getattr(handler, "do_" + method)()
        self.assertEqual(len(responses), 1)
        return responses[0]

    def test_security_checks_precede_body_validation(self):
        for headers, message in [
            ({"Host": "evil.example"}, "Use the local Pebbles address."),
            (
                {"Origin": "http://evil.example"},
                "Requests must originate from this local app.",
            ),
            (
                {"X-Pebbles-Token": "wrong"},
                "Reload the app before running an investigation.",
            ),
        ]:
            with self.subTest(headers=headers):
                self.assertEqual(
                    self.request("/api/investigate", b"{", headers),
                    (403, {"error": message}),
                )

    def test_size_errors_precede_content_type_errors(self):
        for path, limit, message in [
            ("/api/workspace", 6_100_000, "Received evidence request is too large."),
            ("/api/intake/preview", 60_000_000, "CSV request too large."),
            (
                "/api/investigate",
                60_000_000,
                "Choose a package under 50 MB, with no more than 10 files.",
            ),
        ]:
            with self.subTest(path=path):
                self.assertEqual(
                    self.request(
                        path,
                        headers={
                            "Content-Length": str(limit + 1),
                            "Content-Type": "text/plain",
                        },
                    ),
                    (400, {"error": message}),
                )

    def test_workspace_action_limit_is_distinct_from_received_file_limit(self):
        body = json.dumps(
            {"action": "create", "name": "Example", "padding": "x" * 64_000}
        ).encode()
        self.assertEqual(
            self.request("/api/workspace", body),
            (400, {"error": "Workspace request exceeds 64 KB."}),
        )
        self.assertFalse((self.storage / "workspace.sqlite").exists())

    def test_preview_does_not_gain_a_content_type_restriction(self):
        body = json.dumps(
            {"content": "user,group,outcome\nu1,control,1\nu2,treatment,0\n"}
        ).encode()
        status, result = self.request(
            "/api/intake/preview", body, {"Content-Type": "text/plain"}
        )
        self.assertEqual(status, 200)
        self.assertNotIn("error", result)

    def test_unknown_routes_do_not_parse_the_body(self):
        self.assertEqual(
            self.request("/api/unknown", b"{"), (404, {"error": "Not found."})
        )

    def test_unexpected_engine_error_never_returns_an_analysis(self):
        with patch(
            "pebbles.web.investigate", side_effect=RuntimeError("private details")
        ):
            status, result = self.request("/api/investigate", b'{"example":"checkout"}')
        self.assertEqual(status, 500)
        self.assertIn("No analytical result is being claimed.", result["error"])
        self.assertNotIn("private details", result["error"])
        self.assertEqual(list(self.storage.iterdir()), [])
