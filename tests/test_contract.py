# ruff: noqa: PT009 -- standard-library unittest keeps tests runnable without extra packages
"""Infrastructure ownership and bounded scenario contracts."""

import base64
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class Contract(unittest.TestCase):
    def setUp(self):
        self.items = json.loads((ROOT / "scenarios.json").read_text())
        self.tf = json.loads((ROOT / "terraform/scenarios.tf.json").read_text())

    def test_isolation(self):
        self.assertEqual(len(self.items), len({x["id"] for x in self.items}))
        hosts = {x["hostname"] for x in self.items}
        self.assertTrue(all(h.endswith(".f5-sales-demo.com") for h in hosts))
        self.assertEqual(len(hosts), len(self.tf["resource"]["xcsh_http_loadbalancer"]))

    def test_completeness(self):
        for x in self.items:
            for k in [
                "hostname",
                "owner",
                "trigger",
                "expected",
                "negative_control",
                "prerequisites",
                "verification",
            ]:
                self.assertTrue(x[k], (x["id"], k))
        groups = {x["group"] for x in self.items}
        self.assertEqual(
            groups,
            {
                "errors",
                "direct",
                "waf",
                "challenge",
                "conditional",
                "bot",
                "redirect",
                "metadata",
                "masking",
                "control",
                "index",
            },
        )

    def test_encoding_and_precedence(self):
        for lb in self.tf["resource"]["xcsh_http_loadbalancer"].values():
            for options in lb.get("more_option", []):
                mapping = options.get("custom_errors", {})
                for uri in mapping.values():
                    self.assertLessEqual(len(uri), 65536)
                    base64.b64decode(uri.removeprefix("string:///"), validate=True)
                if "503" in mapping:
                    self.assertIn("5", mapping)
                    self.assertNotEqual(mapping["503"], mapping["5"])
        for waf in self.tf["resource"]["xcsh_app_firewall"].values():
            uri = waf["blocking_page"][0]["blocking_page"]
            self.assertLessEqual(len(uri), 4096)
            base64.b64decode(uri.removeprefix("string:///"), validate=True)

    def test_teardown_and_state(self):
        self.assertNotIn("xcsh_dns_zone", self.tf["resource"])
        self.assertEqual(
            self.tf["resource"]["xcsh_namespace"]["showcase"]["name"],
            "custom-responses",
        )
        self.assertTrue(
            all(
                v["namespace"] == "${xcsh_namespace.showcase.name}"
                for v in self.tf["resource"]["xcsh_http_loadbalancer"].values()
            )
        )
        self.assertIn('backend "local"', (ROOT / "terraform/versions.tf").read_text())
        self.assertIn(
            "custom-responses.tfstate",
            (ROOT / "terraform/backend.hcl.example").read_text(),
        )

    def test_faults_have_dedicated_pools(self):
        pools = self.tf["resource"]["xcsh_origin_pool"]
        self.assertEqual(
            {x["port"] for x in pools.values()}, {8080, 8081, 8082, 8083, 8084}
        )
        self.assertEqual(pools["healthy"]["port"], 8080)


if __name__ == "__main__":
    unittest.main()
