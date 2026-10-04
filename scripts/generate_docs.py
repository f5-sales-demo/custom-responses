"""Generate scenario documentation from the single inventory."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
items = json.loads((ROOT / "scenarios.json").read_text())
lines = [
    "---",
    "title: Scenario inventory",
    "description: Planned hosts, triggers, owners and acceptance gates.",
    "---",
    "",
    "All endpoints below remain unverified until their live receipt passes.",
    "",
]
for item in items:
    lines += [
        "## " + item["id"],
        "",
        (
            "[Configuration example](../bot-configuration/)"
            if item["verification"] == "configuration-only"
            else "[Open planned scenario](https://"
            + item["hostname"]
            + item["trigger"]
            + ")"
        ),
        "",
        "- Live proof: "
        + (
            "required"
            if item["live_proof_required"]
            else "not required; configuration-only"
        ),
        "- Owner: " + item["owner"],
        "- Trigger: `" + item["trigger"] + "`",
        "- Expected: `" + json.dumps(item["expected"], sort_keys=True) + "`",
        "- Negative control: `"
        + json.dumps(item["negative_control"], sort_keys=True)
        + "`",
        "- Prerequisites: " + "; ".join(item["prerequisites"]),
        "- Verification: " + item["verification"],
        "",
    ]
    if item.get("activation_gate"):
        lines += ["Activation: " + item["activation_gate"], ""]
(ROOT / "docs/en/scenarios.mdx").write_text("\n".join(lines))
print("Generated documentation for", len(items), "scenarios")
