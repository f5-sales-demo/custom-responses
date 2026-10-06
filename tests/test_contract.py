# ruff: noqa: PT009 -- standard-library unittest keeps tests runnable without extra packages
"""Shared load-balancer ownership and bounded scenario contracts."""

import base64
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED_LBS = {
    "errors",
    "actions",
    "waf-html",
    "waf-json",
    "js",
    "captcha",
    "policy",
    "ddos-js",
}


class Contract(unittest.TestCase):
    def setUp(self):
        self.items = json.loads((ROOT / "scenarios.json").read_text())
        self.tf = json.loads((ROOT / "terraform/scenarios.tf.json").read_text())
        self.lbs = self.tf["resource"]["xcsh_http_loadbalancer"]
        self.by_id = {item["id"]: item for item in self.items}

    def test_shared_hosts_and_distinct_routes(self):
        self.assertEqual(len(self.items), len(self.by_id))
        self.assertEqual(set(self.lbs), EXPECTED_LBS)
        hosts = {lb["domains"][0] for lb in self.lbs.values()}
        self.assertEqual(len(hosts), len(self.lbs))
        self.assertEqual(
            {item["hostname"] for item in self.items if item["live_proof_required"]},
            hosts,
        )
        self.assertEqual(
            {
                self.by_id[key]["hostname"]
                for key in (
                    "errors-3",
                    "errors-4",
                    "errors-5",
                    "exact-404",
                    "exact-503",
                    "fault-500",
                    "fault-502",
                    "fault-503",
                    "fault-504",
                )
            },
            {"cr-errors.f5-sales-demo.com"},
        )
        self.assertEqual(
            {
                self.by_id[key]["hostname"]
                for key in (
                    "control",
                    "index",
                    "maintenance",
                    "acknowledgement",
                    "redirect",
                    "metadata",
                )
            },
            {"custom-responses.f5-sales-demo.com"},
        )
        self.assertEqual(
            {
                self.by_id[key]["hostname"]
                for key in ("waf-json", "disclosure", "data-guard")
            },
            {"cr-waf-json.f5-sales-demo.com"},
        )
        self.assertEqual(
            {self.by_id[key]["hostname"] for key in ("policy-js", "policy-captcha")},
            {"cr-policy.f5-sales-demo.com"},
        )
        for item in self.items:
            if item["live_proof_required"]:
                self.assertEqual(
                    item["delivery_state"], "example; live verification pending"
                )
                self.assertIn(item["hostname"], hosts)
                self.assertTrue(item["hostname"].endswith(".f5-sales-demo.com"))
            control_host = item["negative_control"].get("hostname")
            if control_host:
                self.assertIn(control_host, hosts)
                self.assertNotEqual(control_host, item["hostname"])
        self.assertEqual(
            self.by_id["metadata"]["negative_control"]["hostname"],
            "cr-errors.f5-sales-demo.com",
        )

    def test_error_mapping_and_fault_ownership(self):
        error = self.lbs["errors"]
        mapping = error["more_option"][0]["custom_errors"]
        self.assertEqual(set(mapping), {"3", "4", "5", "404", "503"})
        self.assertNotEqual(mapping["503"], mapping["5"])
        self.assertNotEqual(mapping["404"], mapping["4"])
        routes = [route["simple_route"][0] for route in error["routes"]]
        self.assertEqual(
            [route["path"][0]["path"] for route in routes],
            ["/fault/500", "/fault/502", "/fault/503", "/fault/504"],
        )
        self.assertEqual(
            [route["origin_pools"][0]["pool"][0]["name"] for route in routes],
            [
                "${xcsh_origin_pool.status500.name}",
                "${xcsh_origin_pool.reset.name}",
                "${xcsh_origin_pool.closed.name}",
                "${xcsh_origin_pool.delay.name}",
            ],
        )
        self.assertEqual(routes[-1]["advanced_options"][0]["timeout"], 2000)
        self.assertEqual([route["http_method"] for route in routes], ["ANY"] * 4)
        self.assertEqual(routes[-1]["advanced_options"][0]["priority"], "DEFAULT")
        self.assertEqual(
            self.by_id["fault-503"]["expected"]["body_contains"], "Exact 503"
        )
        for code in (500, 502, 503, 504):
            self.assertEqual(self.by_id[f"fault-{code}"]["trigger"], f"/fault/{code}")

    def test_actions_and_masking_paths(self):
        actions = self.lbs["actions"]
        routes = actions["routes"]
        self.assertEqual(
            [next(iter(route)) for route in routes],
            ["direct_response_route", "direct_response_route", "redirect_route"],
        )
        self.assertEqual(
            [next(iter(route.values()))[0]["http_method"] for route in routes],
            ["ANY", "ANY", "ANY"],
        )
        self.assertEqual(
            [
                routes[0]["direct_response_route"][0]["path"][0]["path"],
                routes[1]["direct_response_route"][0]["path"][0]["path"],
                routes[2]["redirect_route"][0]["path"][0]["path"],
            ],
            ["/maintenance", "/acknowledgement", "/old"],
        )
        self.assertEqual(
            self.by_id["redirect"]["expected_location"],
            "https://custom-responses.f5-sales-demo.com/new",
        )
        self.assertIn("response_headers_to_add", actions["more_option"][0])
        json_waf = self.lbs["waf-json"]
        disclosure = json_waf["sensitive_data_disclosure_rules"][0][
            "sensitive_data_types_in_response"
        ][0]["api_endpoint"][0]["path"]
        guard = json_waf["data_guard_rules"][0]["path"][0]["path"]
        self.assertEqual((disclosure, guard), ("/disclosure", "/data-guard"))
        for key in ("disclosure", "data-guard"):
            self.assertEqual(self.by_id[key]["trigger"], "/" + key)
            self.assertEqual(
                self.by_id[key]["negative_control"]["path"], "/" + key + "-control"
            )
        self.assertEqual(
            json_waf["app_firewall"][0]["name"], "${xcsh_app_firewall.waf-json.name}"
        )

        policy = self.lbs["policy"]["policy_based_challenge"][0]
        self.assertIn("js_challenge_parameters", policy)
        self.assertIn("captcha_challenge_parameters", policy)
        rules = policy["rule_list"][0]["rules"]
        self.assertEqual(
            [rule["spec"][0]["path"][0]["exact_values"][0] for rule in rules],
            ["/policy-js", "/policy-captcha"],
        )
        self.assertEqual(len({rule["metadata"][0]["name"] for rule in rules}), 2)

    def test_working_waf_html_remains_isolated(self):
        html = self.lbs["waf-html"]
        self.assertEqual(html["name"], "cr-waf-html")
        self.assertEqual(html["domains"], ["cr-waf-html.f5-sales-demo.com"])
        self.assertEqual(
            html["app_firewall"][0]["name"], "${xcsh_app_firewall.waf-html.name}"
        )
        self.assertFalse(
            {
                "routes",
                "more_option",
                "data_guard_rules",
                "sensitive_data_disclosure_rules",
            }
            & html.keys()
        )
        self.assertNotIn("<a href=", (ROOT / "origin/fixture.py").read_text())

    def test_completeness_and_encoding(self):
        groups = set()
        for item in self.items:
            groups.add(item["group"])
            for key in (
                "hostname",
                "owner",
                "trigger",
                "expected",
                "negative_control",
                "prerequisites",
                "verification",
            ):
                self.assertTrue(item[key], (item["id"], key))
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
        for lb in self.lbs.values():
            for options in lb.get("more_option", []):
                for uri in options.get("custom_errors", {}).values():
                    self.assertLessEqual(len(uri), 65536)
                    base64.b64decode(uri.removeprefix("string:///"), validate=True)
        for waf in self.tf["resource"]["xcsh_app_firewall"].values():
            uri = waf["blocking_page"][0]["blocking_page"]
            self.assertLessEqual(len(uri), 4096)
            base64.b64decode(uri.removeprefix("string:///"), validate=True)

    def test_acceptance_record_does_not_promote_examples(self):
        record = json.loads((ROOT / "acceptance/current-iteration.json").read_text())
        self.assertEqual(record["source_load_balancer_count"], len(self.lbs))
        self.assertEqual(record["source_scenario_count"], len(self.items))
        self.assertEqual(
            record["live_proof_required_count"],
            sum(item["live_proof_required"] for item in self.items),
        )
        self.assertEqual(
            record["created_scenario_lbs"], ["cr-waf-html", "cr-errors", "cr-index"]
        )
        self.assertEqual(record["verified_live_scenarios"], ["fault-503", "fault-504"])
        self.assertTrue(record["actions_wave_plan_approved"])
        self.assertTrue(record["actions_wave_plan_applied"])
        self.assertTrue(record["actions_wave_plan_apply_complete"])
        self.assertTrue(record["unverified_scenarios_are_examples"])
        self.assertTrue(record["first_wave_plan_approved"])
        self.assertTrue(record["first_wave_plan_applied"])
        self.assertFalse(record["first_wave_plan_apply_complete"])
        self.assertTrue(record["first_wave_plan_consumed"])
        self.assertTrue(record["full_plan_stale_after_first_wave"])

    def test_teardown_and_state(self):
        self.assertNotIn("xcsh_dns_zone", self.tf["resource"])
        self.assertEqual(
            self.tf["resource"]["xcsh_namespace"]["showcase"]["name"],
            "custom-responses",
        )
        self.assertTrue(
            all(
                lb["namespace"] == "${xcsh_namespace.showcase.name}"
                for lb in self.lbs.values()
            )
        )
        self.assertIn('backend "local"', (ROOT / "terraform/versions.tf").read_text())
        self.assertIn(
            "custom-responses.tfstate",
            (ROOT / "terraform/backend.hcl.example").read_text(),
        )
        pools = self.tf["resource"]["xcsh_origin_pool"]
        self.assertEqual(
            {x["port"] for x in pools.values()}, {8080, 8081, 8082, 8083, 8084}
        )


if __name__ == "__main__":
    unittest.main()
