# Configure custom response scenarios through the API

## Prerequisites

**Estimated time:** 20–40 minutes per scenario, excluding domain validation, certificates, feature activation and origin preparation.

You generate complete create bodies for isolated F5 Distributed Cloud Hypertext Transfer Protocol (HTTP) load balancers (LBs). You compare planned direct responses with engine-owned blocking and challenge responses. See [Custom responses](CUSTOM-RESPONSES.md) for taxonomy, limits and coverage boundaries.

- Complete [Define the parameters](CUSTOM-RESPONSE-5XX.md#define-the-parameters) in a private Bash shell to establish the single canonical authenticated application programming interface (API) helper `api_request` and `require_lab_targets` guard.
- Supply owned targets and authorized namespace access. The guard rejects `example.com`, reserved subdomains and TEST-NET origin addresses before any API or application request.
- Use Bash, cURL and jq 1.6 or later. Never enable shell tracing.
- Confirm entitlement for automatic certificates, the web application firewall (WAF) and selected challenge features.
- Reserve unused dedicated names. Stop on an existing object or hostname conflict; these examples are not replacements for shared objects.

**Examples only — no deployment or traffic was executed.** The procedures below produce local JavaScript Object Notation
(JSON) files and show API commands for an operator to run later. Do not execute every scenario as a single script.
Prepare and create **one selected profile** at a time with a unique owned hostname. Domain Name System (DNS)
configuration and automatic Transport Layer Security (TLS) certificate validation remain prerequisites for HTTP Secure
(HTTPS) traffic. Do not bypass certificate validation.

## Prepare the shared baseline

You keep one baseline create body free of error mappings and security profiles. Each scenario adds only its own fields. This follows Don't Repeat Yourself (DRY) without adding a generic response framework.

1. Select the scenario's dedicated names.

```bash
export LB='example-response-maintenance-lb'
export POOL='example-response-pool'
export WAF='example-response-waf'
```

Change `LB` to the semantic name in the [hub](CUSTOM-RESPONSES.md#follow-the-implementation-guides) for another scenario. Keep the owned `DOMAIN` from shared setup; use a different owned hostname when another LB already advertises it. The catalog's metadata limit is 63 characters with lowercase letters, digits and hyphens, starting with a letter and ending in a letter or digit.

2. Generate the baseline body.

```bash
jq -n \
  --arg name "$LB" \
  --arg namespace "$NS" \
  --arg domain "$DOMAIN" \
  '{metadata: {name: $name, namespace: $namespace},
    spec: {domains: [$domain], https_auto_cert: {},
           advertise_on_public_default_vip: {}}}' \
  > custom-response-base.create.json
```

This selects automatic HTTPS certificates and the public default virtual Internet Protocol (IP) address (VIP), not a separately assigned public VIP. It omits a pool; the direct-response and redirect scenarios do not need an origin. The shared guard intentionally still requires an owned `ORIGIN_IP` for consistency, but those scenarios do not create a pool or contact that origin.

3. Prepare a forwarding baseline only for WAF, challenges or metadata.

Complete [Create the origin pool](CUSTOM-RESPONSE-5XX.md#create-the-origin-pool) once with `POOL=example-response-pool`; reuse its minimal pool body and accepted-response identity check. Do not create another pool if this walkthrough already created that pool. Then generate the forwarding baseline:

```bash
jq \
  --arg pool "$POOL" \
  --arg namespace "$NS" \
  '.spec.default_route_pools = [
    {pool: {name: $pool, namespace: $namespace}, weight: 1, priority: 1}]' \
  custom-response-base.create.json \
  > custom-response-forward.create.json
```

Treat both baselines as **fresh local create bodies**, never named `GET` responses. Do not copy server defaults or
identifying metadata into examples. All later commands use `POST`, not partial `PUT`. For an existing shared LB, follow
the [existing-resource warning](CUSTOM-RESPONSE-5XX.md#create-the-load-balancer), preserve the full current spec and
review references before any authorized replacement.

## Configure other error mappings

You can extend the documented error-mapping mechanism to classes `3` and `4`, or exact statuses `300–599`. The class `5` walkthrough remains canonical for source preparation, encoding and verification.

For a branded exact `404`, prepare `custom-response-404.html` using the same small static HTML structure, with a `Not found` heading and the documented `{{request_id}}` placeholder. Follow the 5xx encoding procedure with matching `custom-response-404.*` names. Merge the encoded value into the fresh forwarding baseline:

```bash
jq \
  --slurpfile page custom-response-404.value.json \
  '.spec.more_option.custom_errors = {"404": $page[0]}' \
  custom-response-forward.create.json \
  > custom-response-selected.create.json
```

This is an exact-code body mapping, not a route that manufactures a `404`. Use a dedicated applicable edge-response
test; an origin's normal `404` is not assumed to be rewritten. For exact `503` plus class `5`, encode two separate
appropriately worded files and set both keys in **one** map; exact `503` takes precedence. Do not repeat authentication,
source templates or fault injection here. A class `3` body mapping is not a substitute for configuring a redirect
destination.

## Configure a direct response

You return a planned maintenance body when the request matches `/maintenance`, without breaking an origin or installing a timeout healthcheck. The body is an inline Uniform Resource Identifier (URI), not a raw `response_body` field. HTML means Hypertext Markup Language.

1. Save the maintenance body as `custom-response-maintenance.html`.

```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Scheduled maintenance</title></head>
<body><main><h1>Scheduled maintenance</h1>
<p>Please return after the maintenance window.</p></main></body>
</html>
```

2. Encode the body.

```bash
jq -Rs '"string:///" + @base64' \
  custom-response-maintenance.html > custom-response-maintenance.value.json
jq -e 'startswith("string:///") and length <= 65536' \
  custom-response-maintenance.value.json
```

3. Generate the complete dedicated LB body.

```bash
jq \
  --slurpfile page custom-response-maintenance.value.json \
  '.spec.routes = [{direct_response_route: {
    path: {path: "/maintenance"},
    route_direct_response: {
      response_code: 503, response_body_encoded: $page[0]}}}]' \
  custom-response-base.create.json \
  > custom-response-selected.create.json
```

`route_direct_response.response_code` is an integer (`100–599` in the schema); this guide selects `503` with a body. Do
not use informational or bodyless statuses as arbitrary page examples. A non-error static acknowledgement uses the same
mechanism with `response_code: 200`, exact path `/acknowledgement`, and a short `Request received` body in
`custom-response-static.html`, on `example-response-static-lb`. It proves the static route responds, **not** application
or origin health. No request-identifier substitution is established for direct responses; do not add the generic error
placeholder.

Sources: [direct-response
code](xcsh://api-spec/virtual?resource=http_loadbalancer&field=spec.routes[].direct_response_route.route_direct_response.response_code),
[encoded
body](xcsh://api-spec/virtual?resource=http_loadbalancer&field=spec.routes%5B%5D.direct_response_route.route_direct_response.response_body_encoded),
[exact path](xcsh://api-spec/virtual?resource=http_loadbalancer&field=spec.routes[].direct_response_route.path.path),
and [catalog description](xcsh://api-catalog/http-loadbalancers).

## Configure a WAF blocking response

You customize a denial produced by the WAF, not a generic route. Monitoring mode cannot prove blocking. SQL injection (SQLi) test data must target your owned, isolated lab only.

1. Save the body as `custom-response-waf.html`.

```html
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Request not accepted</title></head>
<body><main><h1>Request not accepted</h1>
<p>Contact support if you need assistance.</p></main></body>
</html>
```

2. Encode the body within the WAF-specific limit.

```bash
jq -Rs '"string:///" + @base64' \
  custom-response-waf.html > custom-response-waf.value.json
jq -e 'startswith("string:///") and length <= 4096 and
       (ltrimstr("string:///") | length <= 4096)' \
  custom-response-waf.value.json
```

The complete-URI check is conservative: [support guidance](xcsh://documentation/my-f5-com/K000162105/index.md#description) identifies the 4,096-byte Base64-content limit, while the API leaf has a 4,096-character URI constraint. Keep a small body; no exact live boundary is asserted here. This guide does not assume the generic error request-ID placeholder or a per-WAF JSON content-type selector.

3. Generate the application-firewall body.

```bash
jq -n \
  --arg name "$WAF" \
  --arg namespace "$NS" \
  --slurpfile page custom-response-waf.value.json \
  '{metadata: {name: $name, namespace: $namespace},
    spec: {blocking: {}, blocking_page: {
      response_code: "Forbidden", blocking_page: $page[0]}}}' \
  > custom-response-waf.create.json
```

`Forbidden` is the documented enum, not the integer `403` or string `"403"`. `blocking` conflicts with `monitoring`; `blocking_page` conflicts with `use_default_blocking_page`. Optional detection defaults are omitted. Signature staging, tuning and exclusions can affect whether a particular test blocks; the response body does not configure those detection conditions.

4. Create the dedicated WAF.

```bash
api_request POST \
  "/api/config/namespaces/$NS/app_firewalls" \
  custom-response-waf.create.response.json \
  custom-response-waf.create.json
jq -e \
  --arg name "$WAF" \
  --arg namespace "$NS" \
  --slurpfile page custom-response-waf.value.json \
  '.metadata.name == $name and .metadata.namespace == $namespace and
   .spec.blocking_page.blocking_page == $page[0] and
   .spec.blocking_page.response_code == "Forbidden"' \
  custom-response-waf.create.response.json
```

5. Generate the LB body with the WAF reference.

```bash
jq \
  --arg name "$WAF" \
  --arg namespace "$NS" \
  '.spec.app_firewall = {name: $name, namespace: $namespace}' \
  custom-response-forward.create.json \
  > custom-response-selected.create.json
```

Sources: [WAF catalog](xcsh://api-catalog/?resource=app_firewall&compact=true), [blocking-page
schema](xcsh://api-spec/virtual?resource=app_firewall), [response
enum](xcsh://api-spec/virtual?resource=app_firewall&field=spec.blocking_page.response_code), [LB WAF
reference](xcsh://api-spec/virtual?resource=http_loadbalancer&field=spec.app_firewall), and [WAF enforcement and
blocking-page
procedure](xcsh://documentation/docs-cloud-f5-com/web-app-and-api-protection/how-to/app-security/application-firewall/index.md#create-a-waf).

## Configure challenge messages

You customize a short message while the platform still performs its challenge. Never replace its security function with hand-written JavaScript or a fake CAPTCHA form. A cURL response alone cannot prove browser challenge completion.

1. Save a message as `custom-response-challenge.html`.

```html
<p>Please wait while your browser is verified.</p>
```

For the CAPTCHA profile, use `Please complete the verification to continue.` in the same message file before encoding. This is a message fragment, not a full challenge document.

2. Encode the message.

```bash
jq -Rs '"string:///" + @base64' \
  custom-response-challenge.html > custom-response-challenge.value.json
jq -e 'startswith("string:///") and length <= 65536' \
  custom-response-challenge.value.json
```

3. Generate **one** selected challenge profile.

JavaScript (JS), on `example-response-js-lb`:

```bash
jq \
  --slurpfile page custom-response-challenge.value.json \
  '.spec.js_challenge = {
    cookie_expiry: 300, js_script_delay: 1000, custom_page: $page[0]}' \
  custom-response-forward.create.json \
  > custom-response-selected.create.json
```

Completely Automated Public Turing test to tell Computers and Humans Apart (CAPTCHA), on `example-response-captcha-lb` instead:

```bash
jq \
  --slurpfile page custom-response-challenge.value.json \
  '.spec.captcha_challenge = {cookie_expiry: 300, custom_page: $page[0]}' \
  custom-response-forward.create.json \
  > custom-response-selected.create.json
```

Each profile is generated from the clean forwarding baseline, not from the other profile's result. Top-level
`js_challenge`, `captcha_challenge`, `enable_challenge`, `policy_based_challenge` and `no_challenge` are mutually
exclusive. The selected cookie lifetime is seconds (`1–86400`); the selected JS delay is milliseconds (`1000–60000`).
These are explicit lab values, not assertions of defaults. Do not reuse a challenge cookie from another profile or a
previous test.

Sources: [JS message
preparation](xcsh://documentation/docs-cloud-f5-com/multi-cloud-app-connect/how-to/adv-security/js-challenge/index.md#prepare-custom-page-for-redirection),
[challenge
configuration](xcsh://documentation/docs-cloud-f5-com/multi-cloud-app-connect/how-to/load-balance/create-http-load-balancer/index.md#configuration),
and [JS/CAPTCHA leaf constraints](xcsh://api-spec/virtual?resource=http_loadbalancer).

## Extend challenge-message coverage

Policy-based challenge parameters and Layer 7 distributed denial-of-service (DDoS) mitigation also expose custom messages. They are conditional triggers, not new arbitrary page formats.

For the documented automatic DDoS JS mitigation variant, generate a dedicated `example-response-ddos-lb` profile from the clean forwarding baseline:

```bash
jq \
  --slurpfile page custom-response-challenge.value.json \
  '.spec.l7_ddos_action_js_challenge = {
    cookie_expiry: 300, js_script_delay: 1000, custom_page: $page[0]}' \
  custom-response-forward.create.json \
  > custom-response-selected.create.json
```

This selects JS mitigation instead of `l7_ddos_action_block` or `l7_ddos_action_default`. It does **not** force every request to be challenged. Do not manufacture a DDoS flood merely to demonstrate text. Hold runtime coverage until an approved, bounded lab mitigation test establishes the actual trigger; record normal traffic as a negative control.

Policy equivalents are `spec.policy_based_challenge.js_challenge_parameters` and `.captcha_challenge_parameters`, with the same inspected `custom_page`, cookie and JS delay constraints. A policy also needs its chosen action and matching rules; no runnable policy-rule payload is supplied here. Do not transplant these parameter fragments into a LB without completing that separate policy contract.

Sources: [DDoS challenge documentation](xcsh://documentation/docs-cloud-f5-com/multi-cloud-app-connect/how-to/load-balance/create-http-load-balancer/index.md#configuration) and [LB policy/DDoS schema](xcsh://api-spec/virtual?resource=http_loadbalancer).

## Bound Bot Defense customization

Bot Defense Standard has a **separate confirmed custom-body mechanism** at `spec.bot_defense.policy.protected_app_endpoints[].mitigation.block.body`; `.status` selects a status enum. `.mitigation.redirect.uri` selects a relative or absolute redirect destination. These fields are not WAF fields or Bot Defense Advanced web/mobile references.

[Blocked: fresh runnable Bot Defense profile.] The embedded status projection reports both a 17-character length
constraint and an enum that includes shorter values such as `Forbidden`. The full catalog lists the enum but no matching
length restriction. This conflict prevents claiming a strictly validated complete example. Resolve the authoritative
validation contract before supplying a production create body; do not silently guess a status or pad an enum.

The following is a **bounded endpoint mitigation fragment, not a runnable resource**:

```json
{
  "block": {
    "body": "string:///PHA+UmVxdWVzdCBub3QgYWNjZXB0ZWQuPC9wPg=="
  }
}
```

It decodes to `<p>Request not accepted.</p>`. It deliberately omits status pending the conflict above. Do not expose the
protection engine in the message. The body URI limit is 4,096 characters; this is independently inspected, not inherited
from the generic 5xx limit. No native Standard `content_type` leaf was confirmed, despite general planning documentation
describing content-type customization on supported deployments.

To implement later, establish Bot Defense entitlement, region, protected endpoint metadata, methods and domain/path
matches, JavaScript insertion and web/mobile selection using the exact deployment contract. Initially use Continue/Flag,
inspect human/known-bot false positives, then select Block only after authorized validation. Never merge the fragment as
a top-level LB body or replace an existing full LB with it. The native Standard fragment belongs under the selected
protected endpoint's `mitigation`, exclusive with `flag` and `redirect`.

Sources: [native endpoint mitigation catalog](xcsh://api-catalog/http-loadbalancers), [block-body
leaf](xcsh://api-spec/virtual?resource=http_loadbalancer&field=spec.bot_defense.policy.protected_app_endpoints[].mitigation.block.body),
[status constraint
conflict](xcsh://api-spec/virtual?resource=http_loadbalancer&field=spec.bot_defense.policy.protected_app_endpoints[].mitigation.block.status),
[mitigation
semantics](xcsh://documentation/docs-cloud-f5-com/bot-defense/how-tos/plan-bot-defense/index.md#configure-mitigation-actions),
and [Standard prerequisites and
testing](xcsh://documentation/docs-cloud-f5-com/bot-defense/quickstarts/bot-defense-waap/index.md).

## Configure a redirect

You redirect `/old` to `/new` on the same owned hostname, rather than returning a custom page. The target application owns the destination body. No additional hostname or origin is required to inspect the redirect itself.

```bash
jq \
  '.spec.routes = [{redirect_route: {
    path: {path: "/old"}, route_redirect: {
      proto_redirect: "https", path_redirect: "/new", response_code: 302}}}]' \
  custom-response-base.create.json \
  > custom-response-selected.create.json
```

Use `example-response-redirect-lb`. Do not add a matching generic `3xx` body map or auto-follow redirects when checking
`Location`. Visiting `/new` needs a configured target route or origin; this origin-free example only demonstrates the
redirect response. A cross-host variant needs an owned hostname in `host_redirect`, its own certificate and a review of
sensitive query parameters; it is not supplied here.

Sources: [redirect
concept](xcsh://documentation/docs-cloud-f5-com/multi-cloud-app-connect/how-tos/advanced-app-nwg/virtual-hosts/index.md#create-route),
[protocol
enum](xcsh://api-spec/virtual?resource=http_loadbalancer&field=spec.routes[].redirect_route.route_redirect.proto_redirect),
[path](xcsh://api-spec/virtual?resource=http_loadbalancer&field=spec.routes[].redirect_route.route_redirect.path_redirect),
[status](xcsh://api-spec/virtual?resource=http_loadbalancer&field=spec.routes[].redirect_route.route_redirect.response_code).

## Configure response metadata

You add a synthetic diagnostic header to ordinary forwarded responses, not a body generator. Use `example-response-metadata-lb` with the forwarding baseline:

```bash
jq \
  '.spec.more_option.response_headers_to_add = [
    {name: "x-example-response-profile", value: "metadata"}]' \
  custom-response-forward.create.json \
  > custom-response-selected.create.json
```

The LB also supports response header removal and response cookie add/remove lists. Those have separate attributes and
OneOf choices; do not copy a response-header object into a cookie list. This example does not restate cookie defaults,
set a session cookie, falsify health/cache state or override security/content-type headers. Prove the marker on a normal
forwarded response; do not assume all locally generated security replies receive it.

Sources: [header and cookie schema](xcsh://api-spec/virtual?resource=http_loadbalancer) and [response-header configuration](xcsh://documentation/docs-cloud-f5-com/multi-cloud-app-connect/how-to/load-balance/create-http-load-balancer/index.md#configuration).

## Create the selected load balancer

You submit the complete selected body only after local review and prerequisite creation. The same operation serves direct, WAF, challenge, redirect and metadata profiles.

1. Check the body without printing encoded content.

```bash
jq -e \
  --arg name "$LB" \
  --arg namespace "$NS" \
  --arg domain "$DOMAIN" \
  '.metadata.name == $name and .metadata.namespace == $namespace and
   .spec.domains == [$domain] and
   (.spec.https_auto_cert | type == "object")' \
  custom-response-selected.create.json
jq '{metadata, domains: .spec.domains, selected_fields: (.spec | keys)}' \
  custom-response-selected.create.json
```

Expect `true` and only your selected profile, domain and dedicated names. This is a consistency check, not a full schema validator. Reject unexpected fields or competing challenge/WAF/advertise choices before submitting.

2. Create the selected LB once.

```bash
api_request POST \
  "/api/config/namespaces/$NS/http_loadbalancers" \
  custom-response-selected.create.response.json \
  custom-response-selected.create.json
```

3. Check its returned identity.

```bash
jq -e \
  --arg name "$LB" \
  --arg namespace "$NS" \
  '.metadata.name == $name and .metadata.namespace == $namespace' \
  custom-response-selected.create.response.json
```

Expect `true`. Inspect the returned selected field against the submitted value: route status/body, WAF reference,
challenge message/parameters, redirect fields or response-header rule, as applicable. Preserve this configuration
evidence privately. The create response is the configuration check; no redundant `GET` is required. A successful
response does not establish runtime effect. Stop on an API error, record it and avoid blind create retries.

4. Complete the owned domain's DNS and certificate-validation records through your authorized process.

5. Wait for successful automatic certificate provisioning before traffic verification.

Sources: [LB create method and path](xcsh://api-catalog/?resource=http_loadbalancer&compact=true) and [certificate/DNS guidance](CUSTOM-RESPONSE-5XX.md#references).

## Verify

You compare a positive trigger with a negative control and record actual results. These are expectations, **not observed traffic evidence**.

1. Capture one selected application response without sending API credentials.

```bash
require_lab_targets
export TEST_PATH='/maintenance'
curl \
  --silent \
  --show-error \
  --max-time 20 \
  --dump-header custom-response-public.headers.txt \
  --output custom-response-public.body.txt \
  --write-out 'HTTP status: %{http_code}\n' \
  "https://$DOMAIN$TEST_PATH"
```

Use the selected owned path only. Do not use `--fail` when error statuses are intended, `--insecure`, or `--location` for redirect inspection. The command intentionally preserves error bodies. Use unique private capture names per test or record results before overwriting. Check the headers for actual content type; do not infer it from the source filename.

| Profile | Positive test and expected evidence | Negative control and limit |
| --- | --- | --- |
| Exact/class errors | Applicable edge-generated status; selected heading and substituted request ID; exact `503` beats class `5` when both configured | Normal successful origin reply is not the error page; record edge versus origin source; follow 5xx guide for correlation |
| Direct maintenance | `/maintenance`: status `503`, heading `Scheduled maintenance`; no origin failure needed | `/different`: not the configured maintenance body; no forwarding default exists, so do not assert a particular fallback status |
| Direct static | `/acknowledgement`: status `200`, configured acknowledgement body | `/different`: not the static acknowledgement; does not establish origin health |
| WAF | Approved synthetic SQLi request on the owned lab, with an actually enforced signature: status `403`, configured denial heading, matching WAF security event | Benign request reaches the normal origin body; staged/suppressed signatures or exclusions invalidate a claimed blocking test |
| JS challenge | Fresh browser state displays message and platform challenge; successful completion subsequently reaches the origin | Non-JS client cannot be treated as successful challenge completion; verify no origin access before success; cookies change subsequent behavior |
| CAPTCHA | Fresh browser state displays instruction and genuine platform interaction; successful solve subsequently reaches origin | Unsolved/failed challenge does not reach protected origin; do not assert the interstitial's status without measuring |
| Conditional DDoS/policy challenge | Only an approved, safely established mitigation/rule trigger demonstrates the custom message | Normal non-triggered traffic; record [blocked] runtime coverage if trigger unavailable; no flood supplied |
| Bot Defense | After contract conflict resolved and false positives reviewed: engine-classified automated test gets configured block; measure body, status, content type and inference record | Legitimate human/allowed known bot is not incorrectly blocked; no new runnable profile supplied here |
| Redirect | `/old`: status `302`, `Location` points to same-host HTTPS `/new`; inspect without following | `/different`: not that redirect; destination rendering is outside this origin-free test |
| Response metadata | Normal forwarded response contains `x-example-response-profile: metadata`; origin body/status retained | Compare a dedicated uncustomized control LB on another owned hostname; do not assume security-engine replies share header behavior |

2. Check a selected static body.

For maintenance:

```bash
jq -Rrs -e 'contains("<h1>Scheduled maintenance</h1>")' \
  custom-response-public.body.txt
```

For WAF, use the same check with `<h1>Request not accepted</h1>`. Expect `true` only for the intended positive response. These markers alone do not prove the trigger owner; compare status and security/origin records. Do not apply the generic request-ID substitution check to mechanisms without a documented substitution contract.

3. Record the negative control before presenting success.

Record profile, actual status, actual content type, body/message match, engine or route, request correlation where supported, origin access and challenge-completion result. Keep request IDs and captures private. If a dependency, certificate, entitlement, signature or trigger is unavailable, mark that part [blocked]; do not promote local encoding or an accepted API body to a runtime claim.

## Clean up

You delete only resources created and confirmed in this walkthrough. Preserve prerequisites until **all** scenario LBs referencing them have been deleted. Do not run the 5xx teardown as a second cleanup of the same pool.

1. Delete each confirmed dedicated scenario LB with its actual `LB` value.

```bash
api_request DELETE \
  "/api/config/namespaces/$NS/http_loadbalancers/$LB" \
  custom-response-lb.delete.response.json
```

2. Delete the dedicated WAF only after every referring LB is removed.

```bash
api_request DELETE \
  "/api/config/namespaces/$NS/app_firewalls/$WAF" \
  custom-response-waf.delete.response.json
```

Skip this operation if no WAF was created. Confirm no unrelated references before deletion; successful LB deletion alone does not prove exclusive ownership of the WAF.

3. Delete the dedicated pool only after every referring LB is removed.

```bash
api_request DELETE \
  "/api/config/namespaces/$NS/origin_pools/$POOL" \
  custom-response-pool.delete.response.json
```

Skip this operation for origin-free scenarios or a pool you did not create. For each standard deletion, expect successful API status and `{}`; stop on failure before deleting dependencies. Do not delete an existing shared prerequisite merely because its name matches a variable.

4. Remove only DNS records created for these lab profiles through your authorized process.

5. Retain source bodies only if needed for maintenance.

6. Remove private response captures and generated payloads through your approved retention process.

No namespace, feature subscription, shared resource or cloud infrastructure is created or deleted by these examples.
