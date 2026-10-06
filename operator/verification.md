# Detailed scenario verification

## Evidence contract

The rebuilt origin fixture and digest-pinned httpbin passed VM health checks. Both WAF load balancers have valid certificates, measured benign `200` / custom blocked `403` responses, and matching enforced security events from 2026-10-06.
Full inventory acceptance is incomplete. A green source test or saved plan is insufficient. Keep raw HTTP headers,
bodies, origin logs, security records, browser traces and request IDs in an owner-only directory. Public receipts
contain sanitized results and SHA-256 identities only.

Run `python3 scripts/verify_live.py --captures /absolute/private/captures` after deployment. The verifier checks certificate hostname and trust, measured HTTP
status, body markers, redirects, metadata and masking controls. Manual evidence remains mandatory for challenge completion, WAF event ownership and conditional
selection. Missing evidence leaves the receipt incomplete.

## HTTP and origin checks

For each [inventory entry](../scenarios.json), verify DNS, certificate chain and hostname, accepted exact configuration,
Content-Type, body, status and negative control. Do not use insecure TLS. Correlate origin and XC records to establish
the response owner. `500`, `502`, `503` and `504` expectations are independent assertions on separate `/fault/` paths. On the shared error host, exact `503` overrides class `5` for both the origin status and the upstream fault. They are not labels on a returned page. Keep error classes and exact-status precedence configuration separate from proof of applicable runtime
replacement.

## Browser and security checks

Use fresh browser contexts for JS and CAPTCHA. Capture the custom wording, actual platform completion and subsequent
origin access. A CAPTCHA needs a human participant. Prove unsolved access does not reach the protected origin. For
policy challenges, record the matching `challenge-js-path` or `challenge-captcha-path` rule. DDoS testing is deferred. Retain the documented configuration with an `un-verified` status; ordinary traffic is only a negative control.

WAF acceptance requires a genuinely blocked synthetic request and its matching enforced event. Test HTML and JSON body variants independently, and record actual Content-Type.

Bot entries are [configuration-only](../bot-configuration/). The verifier skips their network requests and proof requirements, records `pass: null`, and excludes them from aggregate live completion. Their skipped result is not a live pass. All deployed scenarios retain their existing positive, negative-control and owner evidence gates.

## Publication and lifecycle

Inspect desktop and mobile documentation, all scenario links, shared mega-menu navigation, search, hero loading and machine-readable endpoints. Verify the published revision matches the merged source and immutable builder image.

Complete one reviewed owned-resource teardown and rebuild. Compare shared DNS zone and unrelated resources before and after. Repeat all live acceptance and finish with `terraform plan -refresh=true -detailed-exitcode`; only exit 0 qualifies zero drift. Leave the rebuilt showcase online.

Unverified inventory entries remain examples, including a load balancer whose create succeeded but whose response owner is unproven. Publish a live link only after its status, body, negative control, DNS, certificate and owner evidence pass.

The JavaScript challenge has a trusted certificate, the custom first-visit page, an XC challenge cookie, origin access after browser completion, and repeat access. A unique unsolved path produced zero origin log entries before completion and one after; the protected receipt hash is in the acceptance snapshot.

The CAPTCHA host has a valid certificate and serves the custom challenge page. A unique unsolved request produced zero origin log entries.
In a fresh headed Chrome session, the reCAPTCHA iframe showed an Enterprise free-quota warning; clicking opened an image challenge, but it expired before completion and the browser never reached the origin. Keep CAPTCHA unverified and unpublished until actual completion is proven.

Both published WAF block links have matching enforced events in protected evidence. The JSON WAF body is served with `text/html; charset=UTF-8`; verify client handling of that media type. Future requests need their own status, owner, and negative-control checks.

The shared policy host selects JavaScript on `/policy-js`, CAPTCHA on `/policy-captcha`, and no challenge on `/`. Fresh Chrome completed JavaScript verification and reached the
origin; repeat access succeeded. Origin logs showed zero selected-path requests before browser completion, two JavaScript requests afterward, and zero unsolved CAPTCHA requests.
Policy CAPTCHA completion remains unverified.

The DDoS host has trusted TLS. Ordinary requests to `/` and `/challenge` return the origin with `200`; requesting the path does not trigger mitigation. The configured custom JavaScript action is present, but DDoS testing is deferred, a real mitigation event remains unverified, and its documentation is marked `un-verified`.

## Error-mapping applicability findings

The 2026-10-06 repeat matrix over HTTP/1.1 and HTTP/2 matched accepted XC mappings to source. Origin `302`, `404`, `418`, `500`, and `503` responses retained their original bodies.
`/fault/500` also retained its origin `500` body. Direct VM probes and its private journal confirmed those responses. The reset listener produced a TCP reset directly and XC
returned `503` with the exact-503 page; the `/fault/502` name is not a verified status assertion. Oversized-header `431` and malformed-method `400` responses retained generic edge
bodies despite the class-4 mapping.

Record these as measured applicability limits. Keep origin body replacement and custom `502`, class `3`/`4`, and exact `404` examples un-verified; only the qualified `503` and
`504` custom pages remain published. The inventory preserves its intended custom-page assertions, so these cases continue to fail rather than being converted to passing origin
controls. The acceptance record contains protected repeat and direct-origin receipt digests. No Terraform or origin fixture change was needed.
