# Snippet projection provenance

The response examples are partial F5 resource specifications, not complete create or replacement requests. The authoritative Terraform and inactive Bot files
are unchanged. Preparation selects one top-level spec field, resolves pinned schema types, unwraps exactly one provider block for an object, and preserves real
arrays. Encoded values remain exact in details; primary examples use a labelled placeholder. Decoded output preserves exact UTF-8 bytes and is displayed as
escaped code, never executed.

## Official specification inputs

Retrieved from the [official F5 OpenAPI download](https://docs.cloud.f5.com/docs-v2/downloads/f5-distributed-cloud-open-api.zip) on 2026-10-04. The archive SHA-256 is `08905e501555ad45b4916a74999a6e764dc81e93db612697c960d7e3fc0b1328`. The following member digests bind the contract to exact upstream bytes.

- Resource: `http_loadbalancer`; archive member: `docs-cloud-f5-com.0080.public.ves.io.schema.views.http_loadbalancer.ves-swagger.json`; SHA-256: `326c0df9d8758fa7125a450063a962da859ee9685b87857d13e4fdf8005fed96`; spec selector: `#/components/schemas/viewshttp_loadbalancerCreateSpecType`.
- Resource: `app_firewall`; archive member: `docs-cloud-f5-com.0019.public.ves.io.schema.app_firewall.ves-swagger.json`; SHA-256: `d98233c45b3e19bab72282b1f9e12609fd6f645f2ae9174e6a6492eb3f61b664`; spec selector: `#/components/schemas/app_firewallCreateSpecType`.

## Bounded contract

`response-schema.json` retains selected top-level fields and their reachable definitions, scalar types, enums, required fields and length/cardinality/range
constraints. For custom error maps, official `x-ves-validation-rules` supply the string value type, 65,536-character limit, 16-pair limit and permitted keys
(`3`, `4`, `5`, `300`–`599`). Objects fail closed on unknown fields; this is a partial-projection contract, not a complete resource validator or a promise of
infrastructure acceptance. No network access occurs during generation. To refresh, derive the same selected schema closure from a new official archive, record
new member digests, and rerun projection and rendered acceptance.

Resource references become `<APP_FIREWALL_NAME>`, `<ORIGIN_POOL_NAME>` and `<XC_NAMESPACE>` in both projected views. Exact details preserve encoded bodies and other literal selected values; they do not make unresolved Terraform expressions executable. `<ENCODED_RESPONSE_BODY>` appears only in the primary view.

## Selector ledger

| Output | Source | Selector |
| --- | --- | --- |
| `errors-class.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/errors-3/more_option` |
| `errors-exact.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/exact-503/more_option` |
| `errors-404.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/exact-404/more_option` |
| `errors-class.html` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/errors-5/more_option/0/custom_errors/5` |
| `errors-exact.html` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/exact-503/more_option/0/custom_errors/503` |
| `errors-fault.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/fault-502/routes` |
| `maintenance.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/maintenance/routes` |
| `maintenance.html` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/maintenance/routes/0/direct_response_route/0/route_direct_response/0/response_body_encoded` |
| `acknowledgement.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/acknowledgement/routes` |
| `acknowledgement.html` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/acknowledgement/routes/0/direct_response_route/0/route_direct_response/0/response_body_encoded` |
| `waf-html.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_app_firewall/waf-html/blocking_page` |
| `waf-json.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_app_firewall/waf-json/blocking_page` |
| `waf-attach.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/waf-html/app_firewall` |
| `waf-html.html` | `terraform/scenarios.tf.json` | `/resource/xcsh_app_firewall/waf-html/blocking_page/0/blocking_page` |
| `waf-json-body.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_app_firewall/waf-json/blocking_page/0/blocking_page` |
| `js.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/js/js_challenge` |
| `js.html` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/js/js_challenge/0/custom_page` |
| `captcha.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/captcha/captcha_challenge` |
| `captcha.html` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/captcha/captcha_challenge/0/custom_page` |
| `policy-js.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/policy-js/policy_based_challenge` |
| `policy-captcha.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/policy-captcha/policy_based_challenge` |
| `ddos-js.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/ddos-js/l7_ddos_action_js_challenge` |
| `policy-js.html` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/policy-js/policy_based_challenge/0/js_challenge_parameters/0/custom_page` |
| `policy-captcha.html` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/policy-captcha/policy_based_challenge/0/captcha_challenge_parameters/0/custom_page` |
| `ddos-js.html` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/ddos-js/l7_ddos_action_js_challenge/0/custom_page` |
| `data-guard-attach.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/data-guard/app_firewall` |
| `bot-block.json` | `examples/bot-defense.json` | `/bot-block/bot_defense` |
| `bot-redirect.json` | `examples/bot-defense.json` | `/bot-redirect/bot_defense` |
| `bot-block.html` | `examples/bot-defense.json` | `/bot-block/bot_defense/0/policy/0/protected_app_endpoints/0/mitigation/0/block/0/body` |
| `redirect.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/redirect/routes` |
| `metadata.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/metadata/more_option` |
| `disclosure.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/disclosure/sensitive_data_disclosure_rules` |
| `data-guard.json` | `terraform/scenarios.tf.json` | `/resource/xcsh_http_loadbalancer/data-guard/data_guard_rules` |

## Editorial guidance

The revision follows the managed style guide and Google's [procedure guidance](https://developers.google.com/style/procedures) and [active-voice guidance](https://developers.google.com/style/voice): outcome first, second person, imperative actions, conditions before instructions, one action per step and independent alternatives.
