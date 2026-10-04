"""Capture HTTPS controls; fail closed until independent owner evidence is supplied."""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def capture(
    item: dict[str, Any], path: str, directory: Path, method: str = "GET"
) -> dict[str, Any]:
    """Capture one inventory-bound HTTPS request without following redirects."""
    if not item["hostname"].endswith(".f5-sales-demo.com") or not path.startswith("/"):
        message = "Request must target the owned inventory"
        raise ValueError(message)
    curl = shutil.which("curl")
    if curl is None:
        message = "curl"
        raise FileNotFoundError(message)
    stem = item["id"] + "-" + hashlib.sha256((method + path).encode()).hexdigest()[:12]
    headers, body = directory / (stem + ".headers"), directory / (stem + ".body")
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
    if "content-type:" not in response["headers"].lower():
        failures.append("Content-Type absent")
    return failures


# pylint: disable-next=too-many-branches
def main() -> int:
    """Capture every scenario and leave incomplete evidence failing."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--captures", required=True, type=Path)
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
                item, item["trigger"], args.captures, item.get("method", "GET")
            )
            control = capture(item, item["negative_control"]["path"], args.captures)
            failures += check_expected(item["expected"], positive)
            # Fresh challenge controls need browser and origin evidence instead of a curl 200.
            if item["group"] not in ["challenge", "conditional", "masking"]:
                failures += check_expected(item["negative_control"], control)
            if item["id"] == "redirect":
                if ("location: " + item["expected_location"]).lower() not in positive[
                    "headers"
                ].lower():
                    failures.append("Location mismatch")
                destination = capture(item, "/new", args.captures)
                failures += check_expected(
                    {"status": 200, "body_contains": "Custom responses origin"},
                    destination,
                )
            if item["id"] == "metadata":
                headers = positive["headers"].lower()
                if (
                    "x-showcase: custom-responses" not in headers
                    or "set-cookie: showcase=custom-responses" not in headers
                ):
                    failures.append("added header/cookie absent")
                if (
                    "x-origin-remove:" in headers
                    or "set-cookie: origin-remove=" in headers
                ):
                    failures.append("removed header/cookie retained")
            if item["group"] == "masking":
                values = [b"4111111111111111"]
                if item["id"] == "disclosure":
                    values.append(b"example-ssn")
                for value in values:
                    if value in positive["body"] or value not in control["body"]:
                        failures.append("masking or unmasked control failed")
            proof = evidence.get(item["id"], {})
            required = [
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
                required += ["trigger_evidence_digest", "negative_control_verified"]
            if item["group"] in ["challenge", "conditional", "bot"]:
                required += [
                    "browser_completion_verified",
                    "origin_after_completion_digest",
                ]
            if not all(proof.get(k) for k in required):
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
        "complete": all(r["pass"] for r in results if r["pass"] is not None),
        "results": results,
    }
    (args.captures / "sanitized-receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n"
    )
    print(json.dumps(receipt, indent=2))
    return 0 if receipt["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
