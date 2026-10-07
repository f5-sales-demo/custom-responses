"""Capture HTTPS controls; fail closed until independent owner evidence is supplied."""

import argparse
import hashlib
import json
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MAX_BODY_BYTES = 65536
RATE_REQUEST_BUDGET = 36
RATE_WINDOW_SECONDS = 120
RATE_ALLOWANCE = 5


def capture(
    item: dict[str, Any],
    path: str,
    directory: Path,
    method: str = "GET",
    request_headers: dict[str, str] | None = None,
    request_body: str | None = None,
) -> dict[str, Any]:
    """Capture one inventory-bound HTTPS request without following redirects."""
    if (
        not item["hostname"].endswith(".f5-sales-demo.com")
        or "/" in item["hostname"]
        or not path.startswith("/")
        or path.startswith("//")
        or method not in {"GET", "POST", "OPTIONS"}
    ):
        message = "Request must target the owned inventory"
        raise ValueError(message)
    curl = shutil.which("curl")
    if curl is None:
        message = "curl"
        raise FileNotFoundError(message)
    stem = (
        item["id"]
        + "-"
        + hashlib.sha256(
            (
                item["hostname"]
                + method
                + path
                + json.dumps(request_headers or {}, sort_keys=True)
            ).encode()
        ).hexdigest()[:12]
    )
    headers, body = directory / (stem + ".headers"), directory / (stem + ".body")
    sequence = len(list(directory.glob(item["id"] + "-*.headers")))
    headers = directory / (stem + "-" + str(sequence) + ".headers")
    body = directory / (stem + "-" + str(sequence) + ".body")
    extra = []
    for name, value in (request_headers or {}).items():
        if name not in {
            "Content-Type",
            "X-CR-Client",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers",
        } or any(c in value for c in "\r\n"):
            message = "Unsupported synthetic header"
            raise ValueError(message)
        extra += ["--header", name + ": " + value]
    if request_body is not None:
        if len(request_body.encode()) > MAX_BODY_BYTES:
            message = "Synthetic body exceeds budget"
            raise ValueError(message)
        extra += ["--data-binary", request_body]
    result = subprocess.run(  # noqa: S603 -- executable and argv validated; no shell
        [
            curl,
            "--silent",
            "--show-error",
            "--max-time",
            "30",
            "--proto",
            "=https",
            "--request",
            method,
            "--dump-header",
            str(headers),
            "--output",
            str(body),
            "--write-out",
            "%{http_code}",
            *extra,
            "https://" + item["hostname"] + path,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return {
        "status": int(result.stdout),
        "headers": headers.read_text(),
        "body": body.read_bytes(),
    }


def response_headers(response: dict[str, Any]) -> dict[str, str]:
    """Normalize measured header fields for exact comparisons."""
    return {
        key.strip().lower(): value.strip()
        for line in response["headers"].splitlines()
        if ":" in line
        for key, value in [line.split(":", 1)]
    }


def check_expected(expected: dict[str, Any], response: dict[str, Any]) -> list[str]:
    """Compare measured response with independent inventory expectations."""
    failures = []
    if expected.get("status") is not None and response["status"] != expected["status"]:
        failures.append("status mismatch")
    if (
        expected.get("body_contains")
        and expected["body_contains"].encode() not in response["body"]
    ):
        failures.append("body mismatch")
    if "content-type:" not in response["headers"].lower() and (
        response["body"] or response["status"] not in {307, 308}
    ):
        failures.append("Content-Type absent")
    headers = response_headers(response)
    for name, value in expected.get("headers", {}).items():
        if headers.get(name.lower()) != value:
            failures.append("header mismatch: " + name)
    failures.extend(
        "unexpected header: " + name
        for name in expected.get("headers_absent", [])
        if name.lower() in headers
    )
    return failures


def check_metadata(positive: dict[str, Any], control: dict[str, Any]) -> list[str]:
    """Require transformed metadata on the action host and original fields on control."""
    failures = []
    headers = positive["headers"].lower()
    if (
        "x-showcase: custom-responses" not in headers
        or "set-cookie: showcase=custom-responses" not in headers
    ):
        failures.append("added header/cookie absent")
    if "x-origin-remove:" in headers or "set-cookie: origin-remove=" in headers:
        failures.append("removed header/cookie retained")
    control_headers = control["headers"].lower()
    if (
        "x-showcase:" in control_headers
        or "set-cookie: showcase=" in control_headers
        or "x-origin-remove:" not in control_headers
        or "set-cookie: origin-remove=" not in control_headers
    ):
        failures.append("untransformed host control failed")
    return failures


def check_redirect(
    item: dict[str, Any], response: dict[str, Any], directory: Path
) -> list[str]:
    """Check the redirect destination without following the first response."""
    failures = []
    if ("location: " + item["expected_location"]).lower() not in response[
        "headers"
    ].lower():
        failures.append("Location mismatch")
    destination = capture(item, "/new", directory)
    failures += check_expected(
        {"status": 200, "body_contains": "Custom responses origin"}, destination
    )
    return failures


def check_method_redirect(
    item: dict[str, Any], positive: dict[str, Any], directory: Path
) -> list[str]:
    """Follow only an independently expected owned Location with the same payload."""
    location = response_headers(positive).get("location")
    if location != item["expected_location"]:
        return ["Location mismatch"]
    target = urlsplit(location)
    if (
        target.scheme != "https"
        or target.netloc != item["hostname"]
        or target.path != "/demo/echo"
    ):
        return ["redirect destination outside owned echo"]
    destination = capture(
        item,
        target.path + ("?" + target.query if target.query else ""),
        directory,
        item["method"],
        item["request_headers"],
        item["request_body"],
    )
    failures = check_expected({"status": 200}, destination)
    echo = json.loads(destination["body"])
    expected = {
        "method": item["method"],
        "path": "/demo/echo",
        "query": item["expected_echo_query"],
        "body": item["request_body"],
        "headers": item["request_headers"],
    }
    for key, value in expected.items():
        if echo.get(key) != value:
            failures.append("redirect echo mismatch: " + key)
    return failures


def check_cors(item: dict[str, Any], directory: Path) -> list[str]:
    """Measure allowed and denied origins, preflight, POST, and route isolation."""
    origin = item["cors_origin"]
    denied = "https://denied.example.invalid"
    failures = []
    for source in (origin, denied):
        for method in ("GET", "POST", "OPTIONS"):
            headers = {"Origin": source}
            body = None
            if method == "OPTIONS":
                headers.update(
                    {
                        "Access-Control-Request-Method": "POST",
                        "Access-Control-Request-Headers": "content-type,x-cr-client",
                    }
                )
            if method == "POST":
                headers.update(
                    {
                        "Content-Type": "application/json",
                        "X-CR-Client": "verification-synthetic",
                    }
                )
                body = '{"sample":"synthetic"}'
            response = capture(item, "/demo/cors", directory, method, headers, body)
            fields = response_headers(response)
            if source == origin:
                if fields.get("access-control-allow-origin") != origin:
                    failures.append("allowed origin missing")
                if response["status"] not in (
                    {200, 204} if method == "OPTIONS" else {200}
                ):
                    failures.append("CORS status mismatch")
                if method == "OPTIONS":
                    for field, required in [
                        ("access-control-allow-methods", {"get", "post", "options"}),
                        (
                            "access-control-allow-headers",
                            {"content-type", "x-cr-client"},
                        ),
                    ]:
                        values = {
                            x.strip().lower() for x in fields.get(field, "").split(",")
                        }
                        if values != required:
                            failures.append("preflight permissions mismatch")
                else:
                    echo = json.loads(response["body"])
                    if echo.get("method") != method or echo.get("body") != (body or ""):
                        failures.append("CORS echo mismatch")
            elif "access-control-allow-origin" in fields:
                failures.append("disallowed origin granted browser access")
    root = capture(item, "/", directory, request_headers={"Origin": origin})
    if "access-control-allow-origin" in response_headers(root):
        failures.append("CORS leaked to root")
    return failures


def check_rate_limit(item: dict[str, Any], directory: Path) -> list[str]:
    """Bound the request sequence and require custom denial, isolation and recovery."""
    if (
        item.get("request_budget") != RATE_REQUEST_BUDGET
        or item.get("window_seconds") != RATE_WINDOW_SECONDS
    ):
        message = "Unsupported rate-limit budget"
        raise ValueError(message)
    start = time.monotonic()
    count = 0
    client = "verification-synthetic-" + str(uuid.uuid4())

    def request(
        path: str, method: str = "GET", identity: str = client
    ) -> dict[str, Any]:
        nonlocal count
        if (
            count >= item["request_budget"]
            or time.monotonic() - start >= item["window_seconds"]
        ):
            message = "Rate-limit request budget exhausted"
            raise ValueError(message)
        count += 1
        return capture(
            item,
            path,
            directory,
            method,
            {"X-CR-Client": identity},
            "synthetic payload" if method == "POST" else None,
        )

    failures = []
    for index in range(8):
        response = request(item["trigger"])
        failures += check_expected(
            {"status": 200, "body_contains": "Synthetic demonstration data"}
            if index < RATE_ALLOWANCE
            else item["expected"],
            response,
        )
    for path, method, identity in [
        (item["trigger"], "GET", client + "-independent"),
        (item["trigger"], "POST", client),
        ("/", "GET", client),
        (item["trigger"] + "-other", "GET", client),
    ]:
        response = request(path, method, identity)
        failures += check_expected({"status": 200}, response)
        if (
            response_headers(response).get("x-response-owner")
            != "custom-responses-origin"
        ):
            failures.append("rate-limit isolation origin missing")
    deadline = start + item["recovery_seconds"]
    while time.monotonic() < deadline:
        time.sleep(min(30, max(0, deadline - time.monotonic())))
    failures += check_expected(
        {"status": 200, "body_contains": "Synthetic demonstration data"},
        request(item["trigger"]),
    )
    (directory / "rate-limit-budget.json").write_text(
        json.dumps(
            {
                "count": count,
                "elapsed_seconds": round(time.monotonic() - start, 2),
                "failures": failures,
            }
        )
        + "\n"
    )
    return failures


def check_masking(
    scenario_id: str, positive: dict[str, Any], control: dict[str, Any]
) -> list[str]:
    """Require selected values to disappear only from the selected response."""
    values = [b"4111111111111111"]
    if scenario_id == "disclosure":
        values.append(b"example-ssn")
    return [
        "masking or unmasked control failed"
        for value in values
        if value in positive["body"] or value not in control["body"]
    ]


def required_proof_keys(item: dict[str, Any]) -> list[str]:
    """Keep independent evidence requirements tied to each scenario type."""
    keys = [
        "config_digest",
        "origin_evidence_digest",
        "response_owner",
        "source_commit",
        "provider_digest",
        "plan_digest",
    ]
    if item["verification"] not in [
        "http",
        "headers-cookies-and-origin",
        "masked-versus-unmasked",
    ]:
        keys += ["trigger_evidence_digest", "negative_control_verified"]
    if item["group"] in ["challenge", "conditional", "bot"]:
        keys += ["browser_completion_verified", "origin_after_completion_digest"]
    return keys


# pylint: disable-next=too-many-branches
def main() -> int:
    """Capture every scenario and leave incomplete evidence failing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", required=True, type=Path)
    parser.add_argument(
        "--scenario", action="append", help="Select bounded inventory cases"
    )
    parser.add_argument(
        "--owner-evidence",
        type=Path,
        help="Private reviewed manual evidence keyed by scenario ID",
    )
    args = parser.parse_args()
    args.captures.mkdir(parents=True, exist_ok=True, mode=0o700)
    if args.captures.resolve().is_relative_to(ROOT):
        parser.error("raw captures must remain outside the repository")
    args.captures.chmod(0o700)
    evidence = (
        json.loads(args.owner_evidence.read_text()) if args.owner_evidence else {}
    )
    results = []
    for item in json.loads((ROOT / "scenarios.json").read_text()):
        if args.scenario and item["id"] not in args.scenario:
            continue
        if item["verification"] == "configuration-only":
            results.append(
                {
                    "scenario": item["id"],
                    "pass": None,
                    "outcome": "configuration-only",
                    "status": None,
                    "content_type": None,
                    "failures": [],
                }
            )
            continue
        failures = []
        try:
            positive = capture(
                item,
                item["trigger"],
                args.captures,
                item.get("method", "GET"),
                item.get("request_headers"),
                item.get("request_body"),
            )
            control_item = {
                **item,
                "hostname": item["negative_control"].get("hostname", item["hostname"]),
            }
            control = capture(
                control_item, item["negative_control"]["path"], args.captures
            )
            if item["verification"] == "bounded-rate-limit":
                failures += check_rate_limit(item, args.captures)
            else:
                failures += check_expected(item["expected"], positive)
            # Fresh challenge controls need browser and origin evidence instead of a curl 200.
            if item["group"] not in ["challenge", "conditional", "masking"]:
                failures += check_expected(item["negative_control"], control)
            if item["id"] == "redirect":
                failures += check_redirect(item, positive, args.captures)
            if item["id"] in {"temporary", "permanent"}:
                failures += check_method_redirect(item, positive, args.captures)
            if item["id"] == "cors":
                failures += check_cors(item, args.captures)
            if item["id"] == "metadata":
                failures += check_metadata(positive, control)
            if item["group"] == "masking":
                failures += check_masking(item["id"], positive, control)
            proof = evidence.get(item["id"], {})
            if not all(proof.get(k) for k in required_proof_keys(item)):
                failures.append(
                    "independent configuration, owner, trigger or browser evidence missing"
                )
            if item.get("enabled_mitigation") == "flag":
                failures.append("Bot mitigation remains flag-only")
            status = positive["status"]
            content_type = next(
                (
                    line
                    for line in positive["headers"].splitlines()
                    if line.lower().startswith("content-type:")
                ),
                "",
            )
        except (OSError, ValueError, subprocess.CalledProcessError) as error:
            failures.append(type(error).__name__)
            status, content_type = None, None
        results.append(
            {
                "scenario": item["id"],
                "pass": not failures,
                "status": status,
                "content_type": content_type,
                "failures": failures,
            }
        )
    receipt = {
        "complete": bool(results)
        and all(r["pass"] for r in results if r["pass"] is not None),
        "results": results,
    }
    (args.captures / "sanitized-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
