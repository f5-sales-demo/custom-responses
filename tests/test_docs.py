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
                    self.assertEqual(
                        json.loads(actual),
                        self.prepare.resource_fragment(item, value, primary=True),
                    )
                    exact = output / item["output"].replace(".json", "-encoded.json")
                    self.assertEqual(
                        json.loads(exact.read_text()),
                        self.prepare.resource_fragment(item, value, primary=False),
                    )

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
            collision = dict(
                self.prepare.SELECTIONS[0], output="errors-class-encoded.json"
            )
            for selections in [
                [bad],
                [self.prepare.SELECTIONS[0]] * 2,
                [collision, self.prepare.SELECTIONS[0]],
                [self.prepare.SELECTIONS[0], collision],
            ]:
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

    def test_malformed_source_body_prevents_all_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for source in {i["source"] for i in self.prepare.SELECTIONS}:
                (root / source).parent.mkdir(parents=True, exist_ok=True)
                (root / source).write_bytes((ROOT / source).read_bytes())
            tf_path = root / "terraform/scenarios.tf.json"
            tf = json.loads(tf_path.read_text())
            mapping = tf["resource"]["xcsh_http_loadbalancer"]["errors-3"][
                "more_option"
            ][0]["custom_errors"]
            mapping["3"] = "string:///!"
            tf_path.write_text(json.dumps(tf))
            with self.assertRaises(ValueError):
                self.prepare.prepare(root, root / "out")
            self.assertFalse((root / "out").exists())

    def test_projection_preserves_arrays_and_object_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            self.prepare.prepare(ROOT, output)
            route = json.loads((output / "maintenance.json").read_text())["spec"][
                "routes"
            ]
            self.assertIsInstance(route, list)
            self.assertIsInstance(route[0]["direct_response_route"], dict)
            self.assertEqual(
                route[0]["direct_response_route"]["route_direct_response"][
                    "response_body_encoded"
                ],
                "<ENCODED_RESPONSE_BODY>",
            )
            policy = json.loads((output / "policy-js.json").read_text())["spec"][
                "policy_based_challenge"
            ]
            self.assertIsInstance(policy, dict)
            self.assertIsInstance(policy["rule_list"]["rules"], list)
            self.assertIsInstance(policy["rule_list"]["rules"][0]["spec"], dict)
            ref = json.loads((output / "waf-attach.json").read_text())["spec"][
                "app_firewall"
            ]
            self.assertEqual(
                ref, {"name": "<APP_FIREWALL_NAME>", "namespace": "<XC_NAMESPACE>"}
            )

    def test_projection_rejects_unknown_types_and_cardinality(self):
        schema = self.prepare.CONTRACT["resources"]["http_loadbalancer"]
        for value in [
            {"unknown": {}},
            {"js_challenge": []},
            {"js_challenge": [{}, {}]},
            {"js_challenge": [{"cookie_expiry": True}]},
            {"js_challenge": [{"cookie_expiry": "300"}]},
            {"routes": {}},
            {"js_challenge": [{"unknown": 1}]},
            {"js_challenge": [{"custom_page": "https://example.com"}]},
            {"more_option": [{"custom_errors": {"299": "string:///YQ=="}}]},
        ]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.prepare.project(value, schema)

    def test_multiple_genuine_array_items_survive(self):
        schema = self.prepare.CONTRACT["resources"]["http_loadbalancer"]
        route = {
            "redirect_route": [
                {"path": [{"path": "/old"}], "route_redirect": [{"response_code": 302}]}
            ]
        }
        result = self.prepare.project({"routes": [route, route]}, schema)
        self.assertEqual(len(result["routes"]), 2)
        self.assertIsInstance(result["routes"][0]["redirect_route"]["path"], dict)

    def test_example_mutation_does_not_change_sources(self):
        before = {
            source: (ROOT / source).read_bytes()
            for source in {i["source"] for i in self.prepare.SELECTIONS}
        }
        with tempfile.TemporaryDirectory() as temp:
            self.prepare.prepare(ROOT, Path(temp))
        self.assertEqual(
            before, {source: (ROOT / source).read_bytes() for source in before}
        )

    def test_contract_has_pinned_sources_and_bounded_resources(self):
        contract = self.prepare.CONTRACT
        self.assertEqual(
            set(contract["resources"]), {"http_loadbalancer", "app_firewall"}
        )
        for source in contract["sources"]:
            self.assertRegex(source["sha256"], r"^[a-f0-9]{64}$")
            self.assertTrue(source["url"].startswith("https://docs.cloud.f5.com/"))
        for schema in contract["definitions"].values():
            self.assertIn("type", schema)

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
        outputs |= {
            name.replace(".json", "-encoded.json")
            for name in outputs
            if name.endswith(".json")
        }
        for page in (ROOT / "docs/en").glob("*.mdx"):
            text = page.read_text()
            order = re.search(r"order: (\d+)", text)
            self.assertIsNotNone(order, page.name)
            assert order is not None
            ordered.append((int(order[1]), page.stem))
            if page.stem not in {"index", "configuration-reference"}:
                for heading in [
                    "Prerequisites",
                    "Configure",
                    "Verify",
                    "Clean up",
                ]:
                    self.assertIn("## " + heading, text, page.name)
            self.assertNotRegex(text, r"/resource/|/0/|Terraform JSON|## Purpose")
            if page.stem not in {"index", "configuration-reference"}:
                self.assertIn("receives application requests", text)
                self.assertRegex(text, r"minutes")
                self.assertIn("previous", text)
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
