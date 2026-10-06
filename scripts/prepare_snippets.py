"""Project authoritative examples into bounded F5 resource JSON and exact bodies."""

from __future__ import annotations

import base64
import binascii
import json
import re
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[1]
TF = "terraform/scenarios.tf.json"
BOT = "examples/bot-defense.json"
TF_SPEC_SELECTOR_PARTS = 4
BOT_SPEC_SELECTOR_PARTS = 2
CONTRACT = json.loads(
    (ROOT / "operator/response-schema.json").read_text(encoding="utf-8")
)
LB = "/resource/xcsh_http_loadbalancer/"
WAF = "/resource/xcsh_app_firewall/"


JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


class Snippet(TypedDict):
    """One validated source and its owned output file."""

    output: str
    source: str
    pointer: str
    decode: bool
    fields: tuple[str, ...]


def selection(
    output: str,
    pointer: str,
    source: str = TF,
    *,
    decode_body: bool = False,
    fields: tuple[str, ...] = (),
) -> Snippet:
    """Describe one source-owned fragment without line-number coupling."""
    return {
        "output": output,
        "source": source,
        "pointer": pointer,
        "decode": decode_body,
        "fields": fields,
    }


SELECTIONS = [
    selection("errors.json", LB + "errors/more_option"),
    selection(
        "errors-class.html",
        LB + "errors/more_option/0/custom_errors/5",
        decode_body=True,
    ),
    selection(
        "errors-exact.html",
        LB + "errors/more_option/0/custom_errors/503",
        decode_body=True,
    ),
    selection("errors-fault.json", LB + "errors/routes"),
    selection("maintenance.json", LB + "actions/routes/0"),
    selection(
        "maintenance-fallback.json",
        LB + "actions/more_option",
        fields=("custom_errors",),
    ),
    selection(
        "maintenance.html",
        LB
        + "actions/routes/0/direct_response_route/0/route_direct_response/0/response_body_encoded",
        decode_body=True,
    ),
    selection("acknowledgement.json", LB + "actions/routes/1"),
    selection(
        "acknowledgement.html",
        LB
        + "actions/routes/1/direct_response_route/0/route_direct_response/0/response_body_encoded",
        decode_body=True,
    ),
    selection("waf-html.json", WAF + "waf-html/blocking_page"),
    selection("waf-json.json", WAF + "waf-json/blocking_page"),
    selection("waf-attach.json", LB + "waf-html/app_firewall"),
    selection(
        "waf-html.html",
        WAF + "waf-html/blocking_page/0/blocking_page",
        decode_body=True,
    ),
    selection(
        "waf-json-body.json",
        WAF + "waf-json/blocking_page/0/blocking_page",
        decode_body=True,
    ),
    selection("js.json", LB + "js/js_challenge"),
    selection("js.html", LB + "js/js_challenge/0/custom_page", decode_body=True),
    selection("captcha.json", LB + "captcha/captcha_challenge"),
    selection(
        "captcha.html", LB + "captcha/captcha_challenge/0/custom_page", decode_body=True
    ),
    selection("policy.json", LB + "policy/policy_based_challenge"),
    selection("ddos-js.json", LB + "ddos-js/l7_ddos_action_js_challenge"),
    selection(
        "policy-js.html",
        LB + "policy/policy_based_challenge/0/js_challenge_parameters/0/custom_page",
        decode_body=True,
    ),
    selection(
        "policy-captcha.html",
        LB
        + "policy/policy_based_challenge/0/captcha_challenge_parameters/0/custom_page",
        decode_body=True,
    ),
    selection(
        "ddos-js.html",
        LB + "ddos-js/l7_ddos_action_js_challenge/0/custom_page",
        decode_body=True,
    ),
    selection("data-guard-attach.json", LB + "waf-json/app_firewall"),
    selection("bot-block.json", "/bot-block/bot_defense", BOT),
    selection(
        "bot-redirect.json",
        "/bot-redirect/bot_defense",
        BOT,
    ),
    selection(
        "bot-block.html",
        "/bot-block/bot_defense/0/policy/0/protected_app_endpoints/0/mitigation/0/block/0/body",
        BOT,
        decode_body=True,
    ),
    selection("redirect.json", LB + "actions/routes/2"),
    selection(
        "metadata.json",
        LB + "actions/more_option",
        fields=(
            "response_headers_to_add",
            "response_headers_to_remove",
            "response_cookies_to_add",
            "response_cookies_to_remove",
        ),
    ),
    selection("disclosure.json", LB + "waf-json/sensitive_data_disclosure_rules"),
    selection("data-guard.json", LB + "waf-json/data_guard_rules"),
]


def select(document: JsonValue, pointer: str) -> JsonValue:
    """Resolve RFC 6901 object keys and canonical array indices, failing closed."""
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        message = "JSON pointer must start with /"
        raise ValueError(message)
    value = document
    for raw in pointer[1:].split("/"):
        if re.search(r"~(?![01])", raw):
            message = "Malformed JSON pointer escape"
            raise ValueError(message)
        key = raw.replace("~1", "/").replace("~0", "~")
        try:
            if isinstance(value, list):
                if not re.fullmatch(r"0|[1-9][0-9]*", key):
                    message = "Invalid JSON pointer array index"
                    raise ValueError(message)
                value = value[int(key)]
            elif isinstance(value, dict):
                value = value[key]
            else:
                message = "JSON pointer traverses a scalar"
                raise TypeError(message)
        except (KeyError, IndexError) as error:
            message = "Missing selector: " + pointer
            raise ValueError(message) from error
    return value


def decode(value: JsonValue) -> str:
    """Decode canonical padded string:/// Base64 and strict UTF-8 exactly."""
    if not isinstance(value, str) or not value.startswith("string:///"):
        message = "Response body must use string:///"
        raise ValueError(message)
    payload = value[10:]
    try:
        decoded = base64.b64decode(payload, validate=True)
        if base64.b64encode(decoded).decode("ascii") != payload:
            message = "Response body encoding is not canonical padded Base64"
            raise ValueError(message)
        return decoded.decode("utf-8")
    except (binascii.Error, UnicodeError) as error:
        message = "Malformed response-body encoding"
        raise ValueError(message) from error


def validate_bodies(value: JsonValue) -> None:
    """Reject malformed encodings even in fragments kept collapsed."""
    if isinstance(value, str) and value.startswith("string:"):
        decode(value)
    elif isinstance(value, dict):
        for child in value.values():
            validate_bodies(child)
    elif isinstance(value, list):
        for child in value:
            validate_bodies(child)


def resolved(schema: dict) -> dict:
    """Resolve a pinned contract reference without network access."""
    return CONTRACT["definitions"][schema["$ref"]] if "$ref" in schema else schema


def project(value: JsonValue, schema: dict) -> JsonValue:
    """Convert single provider object blocks using API types, keeping true arrays."""
    schema = resolved(schema)
    kind = schema["type"]
    if kind == "object":
        if isinstance(value, list):
            if len(value) != 1:
                message = "Object block must contain exactly one item"
                raise ValueError(message)
            value = value[0]
        if not isinstance(value, dict):
            message = "Expected object"
            raise ValueError(message)
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", False)
        if len(value) > schema.get("maxProperties", len(value)) or any(
            not re.fullmatch(schema.get("propertyPattern", ".*"), key) for key in value
        ):
            message = "Map keys or cardinality outside schema bounds"
            raise ValueError(message)
        result = {}
        for key, child in value.items():
            child_schema = properties.get(key, additional)
            if child_schema is False or child_schema is True:
                message = "Unknown or unbounded schema field: " + key
                raise ValueError(message)
            result[key] = project(child, child_schema)
        if not set(schema.get("required", [])) <= result.keys():
            message = "Missing required schema field"
            raise ValueError(message)
        return result
    if kind == "array":
        if not isinstance(value, list):
            message = "Expected array"
            raise ValueError(message)
        if (
            not schema.get("minItems", 0)
            <= len(value)
            <= schema.get("maxItems", len(value))
        ):
            message = "Array cardinality outside schema bounds"
            raise ValueError(message)
        return [project(child, schema["items"]) for child in value]
    return scalar(value, schema)


def scalar(value: JsonValue, schema: dict) -> JsonValue:
    """Validate scalar API types and body encodings without accepting bool numbers."""
    kind = schema["type"]
    valid = {
        "string": isinstance(value, str),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }
    if not valid.get(kind, False):
        message = "Incompatible schema type: " + kind
        raise ValueError(message)
    if schema.get("encodedBody"):
        decode(value)
    if "enum" in schema and value not in schema["enum"]:
        message = "Value outside schema enum"
        raise ValueError(message)
    if isinstance(value, str) and not schema.get("minLength", 0) <= len(
        value
    ) <= schema.get("maxLength", len(value)):
        message = "String length outside schema bounds"
        raise ValueError(message)
    if (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and not schema.get("minimum", value) <= value <= schema.get("maximum", value)
    ):
        message = "Number outside schema bounds"
        raise ValueError(message)
    return value


def placeholders(value: JsonValue, *, primary: bool) -> JsonValue:
    """Label source references and hide encoded bodies only in primary examples."""
    if isinstance(value, dict):
        return {
            key: placeholders(child, primary=primary) for key, child in value.items()
        }
    if isinstance(value, list):
        return [placeholders(child, primary=primary) for child in value]
    if isinstance(value, str):
        if primary and value.startswith("string:///"):
            value = "<ENCODED_RESPONSE_BODY>"
        elif value == "${xcsh_namespace.showcase.name}":
            value = "<XC_NAMESPACE>"
        elif re.fullmatch(r"\$\{xcsh_app_firewall\.[a-z-]+\.name\}", value):
            value = "<APP_FIREWALL_NAME>"
        elif re.fullmatch(r"\$\{xcsh_origin_pool\.[a-z0-9-]+\.name\}", value):
            value = "<ORIGIN_POOL_NAME>"
        if "${" in value:
            message = "Unrecognized resource reference"
            raise ValueError(message)
    return value


def resource_fragment(item: Snippet, value: JsonValue, *, primary: bool) -> JsonValue:
    """Wrap a selected top-level configuration field in the owning resource spec."""
    parts = item["pointer"].split("/")[1:]
    if item["source"] == TF:
        resource = parts[1].removeprefix("xcsh_")
        field = parts[3]
        if len(parts) == TF_SPEC_SELECTOR_PARTS + 1 and field == "routes":
            if not re.fullmatch(r"0|[1-9][0-9]*", parts[4]):
                message = "Route selector must use a canonical array index"
                raise ValueError(message)
            value = [value]
        elif len(parts) != TF_SPEC_SELECTOR_PARTS:
            message = (
                "Resource fragment must select a top-level spec field or one route"
            )
            raise ValueError(message)
    else:
        resource, field = "http_loadbalancer", parts[1]
        if len(parts) != BOT_SPEC_SELECTOR_PARTS:
            message = "Bot fragment must select a top-level spec field"
            raise ValueError(message)
    if item["fields"]:
        if (
            item["source"] != TF
            or field != "more_option"
            or not isinstance(value, list)
            or len(value) != 1
            or not isinstance(value[0], dict)
        ):
            message = "Field projection requires one more_option object block"
            raise ValueError(message)
        try:
            value = [{key: value[0][key] for key in item["fields"]}]
        except KeyError as error:
            message = "Missing projected source field"
            raise ValueError(message) from error
    projected = project({field: value}, CONTRACT["resources"][resource])
    return {"spec": placeholders(projected, primary=primary)}


def prepare(
    root: Path = ROOT,
    output: Path | None = None,
    selections: list[Snippet] | None = None,
) -> int:
    """Validate all outputs before writing; reruns replace only owned files."""
    output = output or root / "docs/_data"
    pending = {}
    documents = {}
    for item in SELECTIONS if selections is None else selections:
        name = item["output"]
        if not re.fullmatch(r"[a-z0-9-]+\.(json|html)", name) or name in pending:
            message = "Unsafe or duplicate snippet output: " + name
            raise ValueError(message)
        source = item["source"]
        if source not in {TF, BOT}:
            message = "Unrecognized configuration source"
            raise ValueError(message)
        if source not in documents:
            documents[source] = json.loads((root / source).read_text(encoding="utf-8"))
        value = select(documents[source], item["pointer"])
        validate_bodies(value)
        if item.get("decode"):
            pending[name] = decode(value)
        else:
            encoded_name = name.replace(".json", "-encoded.json")
            if encoded_name in pending:
                message = "Duplicate projected snippet output: " + encoded_name
                raise ValueError(message)
            pending[name] = (
                json.dumps(
                    resource_fragment(item, value, primary=True),
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n"
            )
            pending[encoded_name] = (
                json.dumps(
                    resource_fragment(item, value, primary=False),
                    indent=2,
                    ensure_ascii=False,
                )
                + "\n"
            )
    output.mkdir(parents=True, exist_ok=True)
    for name, text in pending.items():
        (output / name).write_text(text, encoding="utf-8")
    return len(pending)


if __name__ == "__main__":
    print("Prepared", prepare(), "source-selected documentation snippets")
