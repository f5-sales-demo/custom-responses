# ruff: noqa: PT009, PT027, S310 -- standard-library unittest and loopback fixtures
"""Exercise echo limits, exact redirect expectations and click-only panel budgets."""

import json
import shutil
import subprocess
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from tests.test_fixture import FixtureTests
from tests.test_verify_live import verify

ROOT = Path(__file__).resolve().parents[1]


class EchoTests(FixtureTests):
    """Verify selected echo data and bounded request handling."""

    def test_post_echo_retains_body_and_omits_private_headers(self):
        request = urllib.request.Request(
            self.base + "/demo/echo?sample=synthetic",
            data=b"synthetic payload",
            headers={
                "Content-Type": "text/plain",
                "X-CR-Client": "test-synthetic",
                "Authorization": "synthetic-secret",
                "Cookie": "synthetic-cookie",
            },
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            data = json.load(response)
        self.assertEqual(data["method"], "POST")
        self.assertEqual(data["query"], "sample=synthetic")
        self.assertEqual(data["body"], "synthetic payload")
        self.assertEqual(
            data["headers"],
            {"Content-Type": "text/plain", "X-CR-Client": "test-synthetic"},
        )

    def test_oversized_body_rejected_and_server_recovers(self):
        request = urllib.request.Request(self.base + "/demo/echo", data=b"x" * 65537)
        with (
            self.assertRaises(urllib.error.HTTPError) as error,
            urllib.request.urlopen(request, timeout=2),
        ):
            self.fail("Expected an oversized request rejection")
        self.assertEqual(error.exception.code, 413)
        with urllib.request.urlopen(self.base + "/demo/echo", timeout=2) as response:
            self.assertEqual(json.load(response)["body"], "")

    def test_origin_grants_no_cors_access(self):
        request = urllib.request.Request(
            self.base + "/demo/cors",
            method="OPTIONS",
            headers={"Origin": "https://f5-sales-demo.github.io"},
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            self.assertIsNone(response.headers.get("Access-Control-Allow-Origin"))


class ResponseTests(unittest.TestCase):
    """Fail qualification on incorrect semantics, even when a status is correct."""

    def test_wrong_query_or_method_fails_redirect(self):
        item = next(
            x
            for x in json.loads((ROOT / "scenarios.json").read_text())
            if x["id"] == "temporary"
        )
        positive = {"headers": "Location: " + item["expected_location"]}
        echo = {
            "status": 200,
            "headers": "Content-Type: application/json",
            "body": json.dumps(
                {
                    "method": "GET",
                    "path": "/demo/echo",
                    "query": "",
                    "body": "",
                    "headers": {},
                }
            ).encode(),
        }
        with patch.object(verify, "capture", return_value=echo):
            failures = verify.check_method_redirect(item, positive, ROOT)
        self.assertIn("redirect echo mismatch: method", failures)
        self.assertIn("redirect echo mismatch: query", failures)
        with patch.object(verify, "capture") as capture:
            self.assertEqual(
                verify.check_method_redirect(
                    item, {"headers": "Location: https://other.invalid/"}, ROOT
                ),
                ["Location mismatch"],
            )
            capture.assert_not_called()

    def test_scoped_header_leak_fails(self):
        result = verify.check_expected(
            {"headers_absent": ["X-CR-Route"]},
            {
                "status": 200,
                "headers": "Content-Type: text/html\nX-CR-Route: scoped",
                "body": b"",
            },
        )
        self.assertEqual(result, ["unexpected header: X-CR-Route"])

    def test_denied_cors_origin_fails(self):
        response = {
            "status": 200,
            "headers": "Access-Control-Allow-Origin: *",
            "body": b"{}",
        }
        with patch.object(verify, "capture", return_value=response):
            failures = verify.check_cors(
                {"cors_origin": "https://f5-sales-demo.github.io"}, ROOT
            )
        self.assertIn("disallowed origin granted browser access", failures)

    def test_rate_budget_and_recovery_sequence(self):
        item = next(
            x
            for x in json.loads((ROOT / "scenarios.json").read_text())
            if x["id"] == "rate-limit"
        )
        success = {
            "status": 200,
            "headers": "Content-Type: application/json\nX-Response-Owner: custom-responses-origin",
            "body": b"Synthetic demonstration data",
        }
        denied = {
            "status": 429,
            "headers": "Content-Type: text/html",
            "body": b"Demo request limit reached",
        }
        replies = [success] * 5 + [denied] * 3 + [success] * 5
        with (
            tempfile.TemporaryDirectory() as temp,
            patch.object(verify, "capture", side_effect=replies) as capture,
            patch.object(verify.time, "monotonic", side_effect=[0] + [70] * 50),
        ):
            self.assertEqual(verify.check_rate_limit(item, Path(temp)), [])
            self.assertEqual(capture.call_count, 13)
        with self.assertRaises(ValueError):
            verify.check_rate_limit({**item, "request_budget": 37}, ROOT)

    def test_focused_widgets_bound_clicks_and_report_transport_failure(self):
        for name, cost, budget, count in [
            ("cors-demo", 2, 12, 1),
            ("rate-limit-demo", 14, 36, 7),
        ]:
            panel = (ROOT / "docs/assets" / (name + ".html")).read_text()
            script = panel.split("<script>")[1].split("</script>")[0]
            harness = (
                """
const assert = require("node:assert/strict");
let requests=[], handler, fail=false, now=0, timer;
const Date={now:()=>now};
const setTimeout=fn=>{timer=fn;};
const location={origin:"https://f5-sales-demo.github.io"};
const crypto={randomUUID:()=>"synthetic-test"};
const fakeButton={addEventListener:(name,fn)=>{handler=fn;}};
const fakeResult={};
const document={querySelector:s=>s==="#run"?fakeButton:s==="#result"?fakeResult:{}};
const fetch=async(url,options)=>{
 requests.push({url,options});
 if(fail) throw Error("network");
 return {status:200,url,headers:{get:()=>null},text:async()=>"synthetic"};
};
"""
                + script
                + f"""
(async()=>{{
 assert.equal(requests.length,0);
 await handler(); assert.equal(requests.length,{count});
 assert.equal(remaining,{budget - cost});
 assert(requests.every(r=>r.options.credentials==="omit" && r.options.redirect==="error"));
 if(COOLDOWN){{
   await handler();assert.equal(requests.length,{count});
   now=120001;timer();assert.equal(button.disabled,false);
 }}
 fail=true;await handler();
 assert(result.textContent.includes("could not complete"));
 assert(!result.textContent.includes("access denied"));
 now=240002;
 for(let i=0;i<20;i++){{await handler();now+=120001;}}
 assert.equal(remaining, {budget} % {cost});assert.equal(button.disabled,true);
 location.origin="https://example.invalid";remaining={budget};
 const before=requests.length;await handler();assert.equal(requests.length,before);
}})().catch(error=>{{console.error(error);process.exitCode=1;}});
"""
            )
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "focused-widget.cjs"
                path.write_text(harness)
                node = shutil.which("node")
                self.assertIsNotNone(node)
                assert node is not None
                subprocess.run([node, str(path)], check=True)  # noqa: S603

    def test_panel_sends_only_after_click_and_stops_at_budget(self):
        panel = (ROOT / "origin/panel.html").read_text()
        script = panel.split("<script>")[1].split("</script>")[0]
        harness = (
            """
const assert = require("node:assert/strict");
let calls = [];
let listeners = {};
const location = {origin:"https://custom-responses.f5-sales-demo.com"};
const controls = ["temporary","permanent","headers","cors"].map(action => ({
 dataset:{action}, addEventListener:(name, fn) => {listeners[action] = fn;}}));
const document = {querySelector:() => ({}), querySelectorAll:() => controls};
const fetch = async (url, opts) => {
 calls.push({url,opts});
 return {status:200,url,headers:{get:() => null},text:async () => "synthetic"};
};
"""
            + script
            + """
(async () => {
 assert.equal(calls.length, 0);
 await run("unknown"); assert.equal(calls.length, 0);
 for (let i = 0; i < 20; i++) await run("headers");
 assert.equal(calls.length, 12);
 assert.equal(remaining, 0);
 assert(controls.every(button => button.disabled));
 assert(calls.every(call => call.url.startsWith(ACTION_ORIGIN + "/")));
})().catch(error => {console.error(error);process.exitCode = 1;});
"""
        )
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "panel.cjs"
            path.write_text(harness)
            node = shutil.which("node")
            self.assertIsNotNone(node)
            assert node is not None
            subprocess.run(  # noqa: S603 -- fixed generated test harness
                [node, str(path)], check=True, capture_output=True
            )
