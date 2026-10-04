# End user comprehension audit

Issue [#11](https://github.com/f5-sales-demo/custom-responses/issues/11) follows the structural rewrite in #7. The supplied baseline scan covered 13 English pages and 107 unique links without broken links/fragments, empty code, unloaded images, browser errors or page overflow. This revision addresses editorial findings; the original audit remains in Git history.

## Findings and disposition

| English page | Severity and finding | Disposition | Rendered evidence and verification |
| --- | --- | --- | --- |
| `index` | Medium: repeated inventory caveats distract from choosing an outcome. | Preserve hero/cards and sidebar; describe resource access and link the reference. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `error-responses` | High: hidden encoded maps obscure error precedence and ownership. | Show class/exact comparisons, message first, load-balancer JSON and independent procedures. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `maintenance` | High: provider arrays hide the route; missing estimate and cleanup. | Show the maintenance message and direct-response spec; scope path and restore route settings. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `acknowledgement` | High: hidden route and minified body slow comprehension. | Show fixed message and direct-response spec; retain backend limitation beside instructions. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `blocked-requests` | High: HTML/JSON alternatives resemble a single procedure. | Define firewall ownership, compare formats and separate procedures with attachment placeholders. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `browser-verification` | Medium: body markup precedes a hidden provider fragment. | Show wording first, challenge resource fields, cookie/script values and completion checks. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `captcha-verification` | Medium: provider details obscure the human-verification settings. | Show wording first, resource JSON and independent completion/returning-cookie checks. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `conditional-challenges` | High: three alternatives appear as sequential actions. | Compare selectors and give each variant its own numbered procedure and verification. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `bot-configuration` | Medium: inactive status and runtime caveats repeat. | Keep one configuration-only boundary; show complete endpoint context for block and redirect. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `redirects` | Medium: provider block representation interrupts the resource procedure. | Show route JSON under spec, preserve destination and redirect-chain checks. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `headers-cookies` | Medium: outer provider array obscures advanced-option ownership. | Show more_option object with real cookie/header arrays and control-host comparison. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `masking` | High: two mechanisms appear as one procedure. | Compare mechanisms, split procedures, preserve firewall attachment and independent checks. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |
| `configuration-reference` | Medium: repeated provider explanation and raw pointer prose. | Explain partial spec scope and encoding once; link repository-only selector provenance. | Passed at 1440 × 1000 and 390 × 844; closed/expanded screenshots and DOM checks retained. |

## Acceptance tasks

- [x] Read managed style guide and Google procedure/voice guidance.
- [x] Confirm regression tests fail before projection/editorial implementation.
- [x] Rewrite all 13 pages while preserving inventory, URLs, hero and sidebar order.
- [x] Pin official bounded schema and document member digests and selector provenance.
- [x] Verify deterministic projection, object-block rejection, genuine arrays, placeholders and exact decoding.
- [x] Changed-file pre-commit/prose/lint/secrets checks, Ruff, mypy, all managed shell tests and PII checks passed. Full Python suite: 23 tests passed. Terraform format/init/validate passed without applying infrastructure.
- [x] Rendered all 13 English pages on desktop/mobile, with details closed and expanded (52 captures). DOM gates: one heading, correct reading order, no page overflow, empty code, unloaded content images or browser errors. Visual review covered mobile layouts and expanded desktop blocking examples. Search returned the revised maintenance page; LLM content contains the new headings and placeholders.
- [x] Crawled 123 unique rendered links/fragments with three external attempts. All existing targets pass; the newly added provenance file is pending publication on main and must be rechecked after merge.
- [ ] Merge linked PR with required checks passing and verify Pages commit and pinned builder.
- [ ] Preserve evidence and retire task worktrees.

Historical demonstration results and infrastructure limits remain in `deployment.md`, `verification.md` and `branding.md`. Bot remains configuration-only; this revision does not apply infrastructure or qualify live scenario acceptance.

## Evidence notes

Candidate evidence is retained outside Git in a task-specific evidence directory: `audit-local.json`, desktop/mobile closed and expanded screenshots, search captures, builder log, changed-file pre-commit log and shell-test logs. The immutable builder is the image recorded in `branding.md`. The full repository hook pass also reports pre-existing formatting issues in unchanged prototype Markdown; those prototypes remain preserved as scoped. Changed-file gates all pass. Existing shared-theme locale links remain outside this content revision; no translations were generated.
