# Concept-page editorial audit

Issue [#13](https://github.com/f5-sales-demo/custom-responses/issues/13) revises the 13 English reader pages. URLs, sidebar order, hero, branding, generated resource examples, body bytes, and scenario inventory remain owned by their existing sources. The prior [reader audit](page-audit.md) documents the earlier walkthrough revision.

| Page | Editorial finding | Revision |
| --- | --- | --- |
| Overview | Cards used walkthrough titles and repeated resource setup. | Uses the agreed concept titles and one sentence per outcome. |
| Error responses | Procedures obscured exact-status precedence and edge-failure differences. | Compares class and exact mappings and keeps edge failure context beside its resource example. |
| Maintenance | Setup and restoration steps repeated the route example. | Explains the selected path, message and status with one expected-result check. |
| Static acknowledgement | Steps repeated the direct response fields. | Explains the fixed answer and its backend-processing limit beside the example; adjusts the long mobile heading locally. |
| WAF blocking | Alternatives were presented as procedures. | Separates HTML and JSON bodies, preserves firewall ownership and attachment, and checks the actual blocking decision and media type. |
| JavaScript challenge | Steps repeated challenge fields. | Keeps the visitor message, script and cookie behavior, and completion check together. |
| CAPTCHA | Steps repeated challenge fields. | Keeps the visitor message, interactive element and cookie behavior together. |
| Conditional challenges | Three selectors read as sequential tasks. | Names policy JavaScript, policy CAPTCHA and DDoS mitigation as separate alternatives with independent checks. |
| Bot Defense | Inactive examples repeated a review procedure. | Keeps the protected endpoint, exclusive choices and configuration-only boundary. |
| Redirects | Route procedure duplicated the JSON. | Explains status, destination and redirect-chain behavior around the example. |
| Headers and cookies | Metadata procedure duplicated four arrays. | Explains added and removed values and the control-host comparison. |
| Data masking | Two mechanisms read as one procedure. | Separates selected fields from Data Guard and keeps its firewall attachment requirement. |
| Configuration reference | Encoding and placeholders were repeated on every page. | Owns fragment scope, placeholders and body encoding in one place. |

## Source and content gates

- `scripts/prepare_snippets.py` regenerated 54 source-selected snippets. The generator and all 23 Python tests passed, including source change, schema rejection, exact decoding and complete scenario disposition.
- The editorial test checks the exact title and description on all 13 pages, card and sidebar order, every generated primary include, the exact encoded body includes, and removal of walkthrough boilerplate.
- Managed MDX prose lint, changed-file pre-commit hooks, repository hygiene, Gitleaks and changed-scope PII enforcement passed. The managed shell suites and Terraform format and validation checks also passed.

## Rendered candidate

The pinned builder image is `ghcr.io/f5-sales-demo/docs-builder@sha256:5785f53f8dcbcc8786d1c255aed3beb2f0371f1fcdde8bb3f42243f53a8126a3`. Candidate output and the Playwright script are retained outside Git at `/data/robin-GIT/evidence/custom-responses-13/` on the Ubuntu workstation.

All 13 English pages were captured at 1440 × 1000 and 390 × 844, with details closed and expanded (52 captures). DOM checks passed for one expected heading, reading order, horizontal fit, nonempty code, loaded content images, sidebar title, and no browser script errors.

Expanded examples were inspected. The mobile Static acknowledgement title was corrected after visual review. The local render passed 29 distinct internal content links and fragments; four external content sources returned HTTP 200. Pagefind returned Maintenance, and the English LLM index plus full text contained the concept titles without the removed template headings.

Publication and merged-commit evidence belong in the linked issue and PR after protected checks and Pages finish. This editorial audit does not qualify live infrastructure scenarios; Bot remains configuration-only.
