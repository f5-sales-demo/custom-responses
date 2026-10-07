# ruff: noqa: PT009 -- standard-library unittest assertions
"""Keep configuration-only Bot entries outside live proof and deployment."""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "verify_live", ROOT / "scripts/verify_live.py"
)
assert spec is not None
assert spec.loader is not None
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


class BotScopeTests(unittest.TestCase):
    def test_bot_examples_are_excluded_from_default_resources(self):
        inventory = json.loads((ROOT / "scenarios.json").read_text())
        resources = json.loads((ROOT / "terraform/scenarios.tf.json").read_text())[
            "resource"
        ]["xcsh_http_loadbalancer"]
        examples = json.loads((ROOT / "examples/bot-defense.json").read_text())
        for item in inventory:
            if item["group"] == "bot":
                self.assertEqual(item["verification"], "configuration-only")
                self.assertFalse(item["live_proof_required"])
                self.assertNotIn(item["id"], resources)
                self.assertIn(item["id"], examples)

    def test_required_scenario_failure_still_blocks_completion(self):
        inventory = json.loads((ROOT / "scenarios.json").read_text())
        original = Path.read_text

        def read(path, *args, **kwargs):
            if path == ROOT / "scenarios.json":
                return json.dumps(inventory)
            return original(path, *args, **kwargs)

        with tempfile.TemporaryDirectory() as temp:
            with (
                patch.object(Path, "read_text", read),
                patch.object(
                    verify, "capture", side_effect=OSError("fixture unavailable")
                ) as capture,
                patch("sys.argv", ["verify", "--captures", temp]),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(verify.main(), 1)
            self.assertEqual(
                capture.call_count,
                sum(
                    item["live_proof_required"]
                    for item in json.loads((ROOT / "scenarios.json").read_text())
                ),
            )
            receipt = json.loads((Path(temp) / "sanitized-receipt.json").read_text())
        self.assertFalse(receipt["complete"])
        self.assertEqual(sum(item["pass"] is None for item in receipt["results"]), 2)

    def test_configuration_only_items_make_no_requests_and_are_not_passes(self):
        inventory = [
            item
            for item in json.loads((ROOT / "scenarios.json").read_text())
            if item["group"] == "bot"
        ]
        original = Path.read_text

        def read(path, *args, **kwargs):
            if path == ROOT / "scenarios.json":
                return json.dumps(inventory)
            return original(path, *args, **kwargs)

        with tempfile.TemporaryDirectory() as temp:
            with (
                patch.object(Path, "read_text", read),
                patch.object(verify, "capture") as capture,
                patch("sys.argv", ["verify", "--captures", temp]),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(verify.main(), 0)
            capture.assert_not_called()
            receipt = json.loads((Path(temp) / "sanitized-receipt.json").read_text())
        self.assertTrue(receipt["complete"])
        self.assertTrue(
            all(
                item["outcome"] == "configuration-only" and item["pass"] is None
                for item in receipt["results"]
            )
        )


if __name__ == "__main__":
    unittest.main()
