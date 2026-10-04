"""Prepare ignored code includes from authoritative JSON pointers."""

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
LB = "/resource/xcsh_http_loadbalancer/"
WAF = "/resource/xcsh_app_firewall/"


JsonValue = str | int | float | bool | None | list["JsonValue"] | dict[str, "JsonValue"]


class Snippet(TypedDict):
    """One validated source and its owned output file."""

    output: str
    source: str
    pointer: str
    decode: bool


def selection(
    output: str, pointer: str, source: str = TF, *, decode_body: bool = False
) -> Snippet:
    """Describe one source-owned fragment without line-number coupling."""
    return {
        "output": output,
        "source": source,
        "pointer": pointer,
        "decode": decode_body,
    }


SELECTIONS = [
    selection("errors-class.json", LB + "errors-3/more_option/0/custom_errors"),
    selection("errors-exact.json", LB + "exact-503/more_option/0/custom_errors"),
    selection("errors-404.json", LB + "exact-404/more_option/0/custom_errors"),
    selection(
        "errors-class.html",
        LB + "errors-5/more_option/0/custom_errors/5",
        decode_body=True,
    ),
    selection(
        "errors-exact.html",
        LB + "exact-503/more_option/0/custom_errors/503",
        decode_body=True,
    ),
    selection("errors-fault.json", LB + "fault-502/routes"),
    selection("maintenance.json", LB + "maintenance/routes"),
    selection(
        "maintenance.html",
        LB
        + "maintenance/routes/0/direct_response_route/0/route_direct_response/0/response_body_encoded",
        decode_body=True,
    ),
    selection("acknowledgement.json", LB + "acknowledgement/routes"),
    selection(
        "acknowledgement.html",
        LB
        + "acknowledgement/routes/0/direct_response_route/0/route_direct_response/0/response_body_encoded",
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
    selection("policy-js.json", LB + "policy-js/policy_based_challenge"),
    selection("policy-captcha.json", LB + "policy-captcha/policy_based_challenge"),
    selection("ddos-js.json", LB + "ddos-js/l7_ddos_action_js_challenge"),
    selection(
        "policy-js.html",
        LB + "policy-js/policy_based_challenge/0/js_challenge_parameters/0/custom_page",
        decode_body=True,
    ),
    selection(
        "policy-captcha.html",
        LB
        + "policy-captcha/policy_based_challenge/0/captcha_challenge_parameters/0/custom_page",
        decode_body=True,
    ),
    selection(
        "ddos-js.html",
        LB + "ddos-js/l7_ddos_action_js_challenge/0/custom_page",
        decode_body=True,
    ),
    selection("data-guard-attach.json", LB + "data-guard/app_firewall"),
    selection("bot-block.json", "/bot-block/bot_defense", BOT),
    selection(
        "bot-redirect.json",
        "/bot-redirect/bot_defense/0/policy/0/protected_app_endpoints/0/mitigation",
        BOT,
    ),
    selection(
        "bot-block.html",
        "/bot-block/bot_defense/0/policy/0/protected_app_endpoints/0/mitigation/0/block/0/body",
        BOT,
        decode_body=True,
    ),
    selection("redirect.json", LB + "redirect/routes"),
    selection("metadata.json", LB + "metadata/more_option"),
    selection("disclosure.json", LB + "disclosure/sensitive_data_disclosure_rules"),
    selection("data-guard.json", LB + "data-guard/data_guard_rules"),
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
        pending[name] = (
            decode(value)
            if item.get("decode")
            else json.dumps(value, indent=2, ensure_ascii=False) + "\n"
        )
    output.mkdir(parents=True, exist_ok=True)
    for name, text in pending.items():
        (output / name).write_text(text, encoding="utf-8")
    return len(pending)


if __name__ == "__main__":
    print("Prepared", prepare(), "source-selected documentation snippets")
