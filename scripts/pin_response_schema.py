"""Derive the bounded documentation contract from two official F5 specifications."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

OFFICIAL_URL = (
    "https://docs.cloud.f5.com/docs-v2/downloads/f5-distributed-cloud-open-api.zip"
)
MEMBERS = {
    "http_loadbalancer": "docs-cloud-f5-com.0080.public.ves.io.schema.views.http_loadbalancer.ves-swagger.json",
    "app_firewall": "docs-cloud-f5-com.0019.public.ves.io.schema.app_firewall.ves-swagger.json",
}
MEMBERS.update(
    {
        "rate_limiter": "docs-cloud-f5-com.0202.public.ves.io.schema.rate_limiter.ves-swagger.json",
        "user_identification": "docs-cloud-f5-com.0266.public.ves.io.schema.user_identification.ves-swagger.json",
    }
)
FIELDS = {
    "http_loadbalancer": [
        "more_option",
        "routes",
        "app_firewall",
        "js_challenge",
        "captcha_challenge",
        "policy_based_challenge",
        "l7_ddos_action_js_challenge",
        "bot_defense",
        "sensitive_data_disclosure_rules",
        "data_guard_rules",
        "api_rate_limit",
        "user_identification",
    ],
    "app_firewall": ["blocking_page"],
    "rate_limiter": ["limits", "user_identification"],
    "user_identification": ["rules"],
}
CONSTRAINTS = {
    "type",
    "enum",
    "minimum",
    "maximum",
    "minLength",
    "maxLength",
    "minItems",
    "maxItems",
    "required",
    "pattern",
}
BODY_FIELDS = {"custom_page", "blocking_page", "response_body_encoded"}


def reduce_schema(schema: dict, resource: str, schemas: dict, contract: dict) -> dict:
    """Recursively retain bounded schema structure with explicit source context."""
    if "$ref" in schema:
        name = schema["$ref"].split("/")[-1]
        key = resource + ":" + name
        if key not in contract["definitions"]:
            contract["definitions"][key] = {}
            contract["definitions"][key] = reduce_schema(
                schemas[name], resource, schemas, contract
            )
        return {"$ref": key}
    result = {key: value for key, value in schema.items() if key in CONSTRAINTS}
    rules = schema.get("x-ves-validation-rules", {})
    if "ves.io.schema.rules.map.values.string.max_len" in rules:
        result["additionalProperties"] = {
            "type": "string",
            "maxLength": int(rules["ves.io.schema.rules.map.values.string.max_len"]),
            "encodedBody": True,
        }
        result["maxProperties"] = int(rules["ves.io.schema.rules.map.max_pairs"])
        if rules["ves.io.schema.rules.map.keys.uint32.ranges"] != "3,4,5,300-599":
            message = "Unexpected official error-map key ranges"
            raise ValueError(message)
        result["propertyPattern"] = "^(?:[345]|[345][0-9]{2})$"
    if "properties" in schema:
        result["properties"] = {}
        for key, value in schema["properties"].items():
            child = reduce_schema(value, resource, schemas, contract)
            if key in BODY_FIELDS or (key == "body" and child.get("type") == "string"):
                child["encodedBody"] = True
            result["properties"][key] = child
    if "items" in schema:
        result["items"] = reduce_schema(schema["items"], resource, schemas, contract)
    if "additionalProperties" in schema:
        extra = schema["additionalProperties"]
        result["additionalProperties"] = (
            reduce_schema(extra, resource, schemas, contract)
            if isinstance(extra, dict)
            else extra
        )
    if "type" not in result:
        result["type"] = (
            "object"
            if "properties" in result or "format" not in schema
            else schema["format"]
        )
    return result


def derive(specifications: dict[str, bytes]) -> dict:
    """Keep selected fields, reachable definitions and official validation bounds."""
    contract: dict = {"resources": {}, "definitions": {}, "sources": []}
    for resource, raw in specifications.items():
        schemas = json.loads(raw)["components"]["schemas"]
        request = schemas[resource + "CreateRequest"]
        reference = request["properties"]["spec"]["$ref"].split("/")[-1]

        contract["resources"][resource] = {
            "type": "object",
            "properties": {
                key: reduce_schema(
                    schemas[reference]["properties"][key], resource, schemas, contract
                )
                for key in FIELDS[resource]
            },
        }
        contract["sources"].append(
            {
                "resource": resource,
                "url": OFFICIAL_URL,
                "member": MEMBERS[resource],
                "sha256": hashlib.sha256(raw).hexdigest(),
                "spec_ref": "#/components/schemas/" + reference,
            }
        )
    return contract


def main() -> None:
    """Read exact unmodified archive members and write a deterministic contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec_directory", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    specifications = {
        resource: (args.spec_directory / member).read_bytes()
        for resource, member in MEMBERS.items()
    }
    args.output.write_text(
        json.dumps(derive(specifications), indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
