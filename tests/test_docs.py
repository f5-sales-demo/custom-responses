# ruff: noqa: PT009, PT027 -- standard-library unittest assertions
"""Source preparation and reader-guide contracts."""

import base64
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentationTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location(
            "prepare_snippets", ROOT / "scripts/prepare_snippets.py"
        )
        assert spec is not None
        assert spec.loader is not None
        self.prepare = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.prepare)

    def test_output_is_deterministic_and_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            self.prepare.prepare(ROOT, output)
            first = {p.name: p.read_bytes() for p in output.iterdir()}
            self.prepare.prepare(ROOT, output)
            self.assertEqual(first, {p.name: p.read_bytes() for p in output.iterdir()})
            for item in self.prepare.SELECTIONS:
                source = json.loads((ROOT / item["source"]).read_text())
                value = self.prepare.select(source, item["pointer"])
                actual = (output / item["output"]).read_text()
                if item.get("decode"):
                    self.assertEqual(
                        actual, base64.b64decode(value[10:], validate=True).decode()
                    )
                else:
                    self.assertEqual(json.loads(actual), value)

    def test_source_change_updates_example(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "terraform").mkdir()
            (root / "examples").mkdir()
            for source in {i["source"] for i in self.prepare.SELECTIONS}:
                (root / source).write_bytes((ROOT / source).read_bytes())
            tf_path = root / "terraform/scenarios.tf.json"
            tf = json.loads(tf_path.read_text())
            tf["resource"]["xcsh_http_loadbalancer"]["redirect"]["routes"][0][
                "redirect_route"
            ][0]["route_redirect"][0]["response_code"] = 307
            tf_path.write_text(json.dumps(tf))
            self.prepare.prepare(root, root / "out")
            self.assertIn(
                '"response_code": 307', (root / "out/redirect.json").read_text()
            )

    def test_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            bad = dict(self.prepare.SELECTIONS[0], pointer="/missing")
            for selections in [[bad], [self.prepare.SELECTIONS[0]] * 2]:
                with self.assertRaises(ValueError):
                    self.prepare.prepare(ROOT, output, selections)
                self.assertEqual(list(output.iterdir()), [])
        for value in [
            "string:///!",
            "string:///YQ",
            "string:/// /w==",
            "https://example.com",
            "string:////w==",
        ]:
            with self.assertRaises(ValueError):
                self.prepare.decode(value)
        with self.assertRaises(ValueError):
            self.prepare.select({"a": [1]}, "/a/01")
        self.assertEqual(self.prepare.select({"a/b": {"~x": 2}}, "/a~1b/~0x"), 2)

    def test_all_scenarios_have_one_disposition(self):
        coverage = json.loads((ROOT / "operator/scenario-coverage.json").read_text())
        inventory = json.loads((ROOT / "scenarios.json").read_text())
        self.assertEqual(set(coverage), {i["id"] for i in inventory})
        for item in inventory:
            page = coverage[item["id"]]
            if item["group"] in {"control", "index"}:
                self.assertEqual(page, "supporting-fixture")
            else:
                self.assertTrue((ROOT / "docs/en" / (page + ".mdx")).is_file())
            if item["group"] == "bot":
                self.assertEqual(page, "bot-configuration")
                self.assertEqual(item["verification"], "configuration-only")

    def test_editorial_and_includes(self):
        ordered = []
        outputs = {i["output"] for i in self.prepare.SELECTIONS}
        for page in (ROOT / "docs/en").glob("*.mdx"):
            text = page.read_text()
            order = re.search(r"order: (\d+)", text)
            self.assertIsNotNone(order, page.name)
            assert order is not None
            ordered.append((int(order[1]), page.stem))
            if page.stem not in {"index", "configuration-reference"}:
                for heading in [
                    "Purpose",
                    "When to use it",
                    "Configure it",
                    "Expected behavior",
                    "Check the result",
                ]:
                    self.assertIn("## " + heading, text, page.name)
            self.assertNotRegex(
                text,
                r"terraform.*(?:apply|destroy)|sha256:|saved plan|private captures|live proof|zero drift",
            )
            for filename in re.findall(r"file=\.\./_data/(\S+)", text):
                self.assertIn(filename, outputs, page.name)
            self.assertNotRegex(
                text,
                r"\.\./(?:deployment|verification|branding|teardown|ownership|scenarios)/",
            )
        self.assertEqual(
            [name for _, name in sorted(ordered)],
            [
                "index",
                "error-responses",
                "maintenance",
                "acknowledgement",
                "blocked-requests",
                "browser-verification",
                "captcha-verification",
                "conditional-challenges",
                "bot-configuration",
                "redirects",
                "headers-cookies",
                "masking",
                "configuration-reference",
            ],
        )


if __name__ == "__main__":
    unittest.main()
