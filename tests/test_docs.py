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
BODY_EXAMPLES = {
    "errors",
    "maintenance",
    "acknowledgement",
    "waf-html",
    "waf-json",
    "js",
    "captcha",
    "policy",
    "ddos-js",
    "bot-block",
}
NO_SUBSECTIONS = {
    "maintenance",
    "acknowledgement",
    "browser-verification",
    "captcha-verification",
    "redirects",
    "headers-cookies",
}


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
            tf["resource"]["xcsh_http_loadbalancer"]["actions"]["routes"][2][
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
            collision = dict(self.prepare.SELECTIONS[0], output="errors-encoded.json")
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
            mapping = tf["resource"]["xcsh_http_loadbalancer"]["errors"]["more_option"][
                0
            ]["custom_errors"]
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
            policy = json.loads((output / "policy.json").read_text())["spec"][
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

    def test_selector_ledger_tracks_current_sources(self):
        ledger = (ROOT / "operator/snippet-provenance.md").read_text()
        for item in self.prepare.SELECTIONS:
            row = f"| `{item['output']}` | `{item['source']}` | `{item['pointer']}` |"
            self.assertIn(row, ledger)
        self.assertEqual(
            ledger.count(" | `terraform/scenarios.tf.json` | ")
            + ledger.count(" | `examples/bot-defense.json` | "),
            len(self.prepare.SELECTIONS),
        )

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

    def test_only_verified_live_paths_are_linked(self):
        record = json.loads((ROOT / "acceptance/current-iteration.json").read_text())
        inventory = json.loads((ROOT / "scenarios.json").read_text())
        verified = set(record["verified_live_scenarios"])
        expected = {
            f"https://{item['hostname']}{item['trigger']}"
            for item in inventory
            if item["id"] in verified
        }
        linked = set()
        for page in (ROOT / "docs/en").glob("*.mdx"):
            linked.update(
                re.findall(
                    r"\]\((https://[a-z0-9.-]+\.f5-sales-demo\.com/[^)\s]*)\)",
                    page.read_text(),
                )
            )
        self.assertEqual(linked, expected)

    def test_editorial_and_includes(self):
        pages = [
            ("index", "Custom Responses"),
            ("error-responses", "Error responses"),
            ("maintenance", "Maintenance"),
            ("acknowledgement", "Static acknowledgement"),
            ("blocked-requests", "WAF blocking"),
            ("browser-verification", "JavaScript challenge"),
            ("captcha-verification", "CAPTCHA"),
            ("conditional-challenges", "Conditional challenges"),
            ("bot-configuration", "Bot Defense"),
            ("redirects", "Redirects"),
            ("headers-cookies", "Headers and cookies"),
            ("masking", "Data masking"),
            ("configuration-reference", "Configuration reference"),
        ]
        outputs = {item["output"] for item in self.prepare.SELECTIONS}
        valid_includes = outputs | {
            name.replace(".json", "-encoded.json")
            for name in outputs
            if name.endswith(".json")
        }
        used_includes = set()
        for order, (slug, title) in enumerate(pages, start=1):
            text = (ROOT / "docs/en" / (slug + ".mdx")).read_text()
            self.assertIn(f"title: {title}\n", text, slug)
            self.assertIn(f"description: {title}", text, slug)
            self.assertIn(f"  order: {order}\n", text, slug)
            self.assertEqual(
                "tableOfContents: false\n" in text,
                slug in NO_SUBSECTIONS,
                slug,
            )
            if slug in NO_SUBSECTIONS:
                self.assertNotIn("\n## ", text, slug)
            elif slug != "index":
                self.assertIn("\n## ", text, slug)
            self.assertNotIn("<details>", text, slug)
            self.assertNotIn("<ENCODED_RESPONSE_BODY>", text, slug)
            self.assertNotRegex(
                text, r"(?m)^## (?:Prerequisites|Configure|Verify|Clean up)$"
            )
            self.assertNotRegex(text, r"(?m)^\d+\. ")
            self.assertNotRegex(
                text,
                r"(?i)save the previous|restore the previous|allow about "
                r"|receives application requests",
            )
            self.assertNotRegex(text, r"/resource/|/0/|Terraform JSON|## Purpose")
            self.assertNotRegex(
                text,
                r"terraform.*(?:apply|destroy)|sha256:|saved plan|private captures"
                r"|live proof|zero drift",
            )
            includes = re.findall(r"file=\.\./_data/([^\s]+)", text)
            for filename in includes:
                self.assertIn(filename, valid_includes, slug)
            used_includes.update(includes)
            if slug not in {"index", "configuration-reference"}:
                self.assertIn("Visitor", text, slug)
                self.assertRegex(text, r"\*\*Expected (?:result|configuration):\*\*")
                self.assertTrue(any(name.endswith(".json") for name in includes))
            self.assertNotRegex(
                text,
                r"\.\./(?:deployment|verification|branding|teardown|ownership|scenarios)/",
            )
        self.assertEqual(
            {path.stem for path in (ROOT / "docs/en").glob("*.mdx")},
            {slug for slug, _ in pages},
        )
        expected_includes = {
            name for name in outputs if name.removesuffix(".json") not in BODY_EXAMPLES
        } | {name + "-encoded.json" for name in BODY_EXAMPLES}
        self.assertEqual(used_includes, expected_includes)
        self.assertEqual(
            {name for name in used_includes if name.endswith("-encoded.json")},
            {name + "-encoded.json" for name in BODY_EXAMPLES},
        )
        for slug in {slug for slug, _ in pages} - {"index", "configuration-reference"}:
            text = (ROOT / "docs/en" / (slug + ".mdx")).read_text()
            for name in BODY_EXAMPLES:
                encoded = f"file=../_data/{name}-encoded.json"
                if encoded not in text:
                    continue
                self.assertEqual(text.count(encoded), 1, slug)
                self.assertNotIn(f"file=../_data/{name}.json", text, slug)
                preview = f"file=../_data/{name}.html"
                if preview in text:
                    self.assertLess(text.index(encoded), text.index(preview), slug)
                    self.assertIn("decoded preview", text.lower(), slug)

        landing = (ROOT / "docs/en/index.mdx").read_text()
        cards = re.findall(
            r'<LinkCard title="([^"]+)" description="([^"]+)" '
            r'href="\./([^/]+)/" />',
            landing,
        )
        self.assertEqual(
            [(slug, title) for title, _, slug in cards],
            pages[1:-1],
        )
        self.assertEqual(
            re.findall(r"(?m)^## (.+)$", landing),
            [
                "Application messages",
                "Security checks and blocks",
                "Routes and response data",
            ],
        )
        self.assertEqual(
            landing.count("[Configuration reference](./configuration-reference/)"), 1
        )
        blocking = (ROOT / "docs/en/blocked-requests.mdx").read_text()
        self.assertLess(
            blocking.index("file=../_data/waf-json-encoded.json"),
            blocking.index("file=../_data/waf-json-body.json"),
        )
        for _, description, _ in cards:
            self.assertTrue(description.endswith("."), description)


if __name__ == "__main__":
    unittest.main()
