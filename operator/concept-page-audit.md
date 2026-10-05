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

PR #14 merged and Pages published its verified commit with the pinned builder. The final delivery evidence is recorded in issue #13 and PR #14. This editorial audit does not qualify live infrastructure scenarios; Bot remains configuration-only.

## Manual language qualification for issue #15

A reader-level pass covered the title, description, landing card, introduction, field explanation, table, visitor message, detail label, and expected result on every English page.

The review used the managed style guide's guidance on active wording, first-use acronyms, consistent terms, sentence-case headings, and source-linked claims. These are concept pages, so the user's concept-page direction governs the how-to template sections.

| Page | Wording issue found | Resolution |
| --- | --- | --- |
| Overview | Card descriptions restated their visible titles; the topics had no reader-task grouping. | Cards now state the visitor benefit and appear under application messages, security decisions, routes and returned data, and resource examples. |
| Error responses | “Eligible,” “source body,” and the class 3/class 5 detail label obscured status behavior. | Names the mapping keys and status families, distinguishes the separate preview, and explains precedence in direct language. |
| Maintenance | “Without waiting for the origin” obscured the route behavior. | Says that the route serves the message without forwarding the request to the application. |
| Static acknowledgement | “Answers” and “normal origin body” blurred the fixed reply and application reply. | Describes each response directly and keeps the no-processing limitation beside the example. |
| WAF blocking | “Owns” and a bare 403 check were implementation-heavy and ambiguous. | Uses active attachment language, expands HTML and JSON, and directs readers to the firewall event. |
| JavaScript challenge | “Working verification script appears” implied a visible script. | Checks that the visitor completes verification and explains the cookie and test-path behavior. |
| CAPTCHA | The acronym and interaction were left unexplained. | Expands the acronym on first prose use and describes the visitor action and return-cookie experience. |
| Conditional challenges | “Correlates” and “independently” obscured the actual selection checks. | Names each selector and says which rule or mitigation event must select the request. |
| Bot Defense | “Classified request,” “confirmed field,” and a claimed live help destination mixed configuration with runtime. | Uses protected-endpoint language and limits the expected result to inactive settings. |
| Redirects | “Over HTTPS” and “chooses” hid the exact route fields. | Names the `https` value, path, status, method concern, and redirect loop. |
| Headers and cookies | “Owns the add and remove lists” and “authenticated session” read like internal shorthand. | Names `more_option` as the field and says that adding a cookie does not sign a user in. |
| Data masking | “Usual JSON structure,” “supported values,” and “attribute the change” were vague. | Names the fields and sensitive-number formats and explains the control path. |
| Configuration reference | Schema jargon and historical-demo wording distracted from use. | Gives the fragment, placeholder, and encoding rules directly; source links remain, and maintainer provenance stays in operator notes. |

The exact synthetic messages and resource snippets remain source-owned. The formal CAPTCHA expansion appears once per page where needed; subsequent text uses the short name. The landing groups are reader-task headings, not framework labels, and no unrelated section was added.

### Candidate verification

The pinned docs-builder image in the rendered-candidate section built this wording revision. The Ubuntu evidence directory is `/data/robin-GIT/evidence/custom-responses-15/`, containing the build log, test and lint logs, Playwright script, audit JSON, and desktop/mobile screenshots.

All 13 English pages passed at 1440 × 1000 and 390 × 844 with details closed and expanded (52 captures). The checks found no horizontal overflow, empty code, unloaded content image, or browser script error.

Landing groups, 33 distinct internal content links and fragments, Pagefind, and English LLM output passed. The mobile landing and CAPTCHA pages were also inspected at full size.

Snippet preparation produced 54 source-selected files. All 23 Python tests, seven managed shell test files, Terraform format and validation, Ruff, managed prose and pre-commit checks, changed-scope PII enforcement and audit, repository hygiene, and Gitleaks passed. Terraform configuration, inactive Bot sources, scenario inventory, generator code, and shared theme were not changed.

## Content and outline audit for issue #17

This pass checks the 13 English pages for empty-looking sections, repeated labels, and prose that does not help the reader. Normal titles, breadcrumbs, sidebar labels, and card order remain useful navigation. The page-specific disposition is below.

| Page | Finding | Disposition |
| --- | --- | --- |
| Overview | “Use a resource example” introduces one card, making the heading look larger than its content. | Keep the three outcome groups and their card order; link the Configuration reference in one sentence after them. |
| Error responses | Collapsed class and exact-status disclosures hide encoded values. The class `3` JSON and class `5` decoded message come from different mappings. | Show encoded JSON inline; label the separate class `5` decoded preview explicitly. Keep the status comparison and real subsection outline. |
| Maintenance | “On this page → Overview” has no subsection to list. The resource fragment repeats the encoded version in a collapsed disclosure. | Disable the outline and show exact encoded JSON followed by its escaped decoded preview. |
| Static acknowledgement | The empty outline and collapsed duplicate slow scanning. | Disable the outline and show one encoded fragment and its escaped preview; keep the backend-processing limit beside it. |
| WAF blocking | HTML and JSON body alternatives are hidden behind duplicate fragments. | Show each encoded firewall example inline, keep their different labels, and retain the attachment fragment and real subsection outline. |
| JavaScript challenge | The empty outline and collapsed body obscure the message. | Disable the outline; show encoded JSON and escaped preview inline. Keep the cookie and test-path context. |
| CAPTCHA | The empty outline and collapsed body obscure the visitor prompt. | Disable the outline; show encoded JSON and escaped preview inline. Keep the controls and returning-cookie context. |
| Conditional challenges | Three collapsed examples resemble empty alternative sections. | Show each encoded policy or mitigation example and escaped preview inline; keep the selector comparison and real subsection outline. |
| Bot Defense | The block body is hidden behind a duplicate fragment. | Show encoded block JSON and escaped preview inline; retain the distinct redirect example and configuration-only limit. |
| Redirects | The page has no subsections, so the outline displays only “Overview.” | Disable the outline; keep the single exact route JSON and redirect-chain check. |
| Headers and cookies | The page has no subsections, so the outline displays only “Overview.” | Disable the outline; keep the single exact metadata JSON and control-host comparison. |
| Data masking | The two mechanisms and their attachment are distinct, with real subsections. | Keep both source-selected fragments, their labels, and the outline; no prose added. |
| Configuration reference | Placeholder-body guidance repeats the old two-copy display. | Explain how to encode a body using the exact examples now visible in outcome pages; keep reference subsections and resource-name placeholders. |

The previous audits remain as historical records of their own revisions. This pass preserves generated snippet bytes and source validation; only the reader's choice of existing generated includes changes.

### Verification for issue #17

The pinned builder `ghcr.io/f5-sales-demo/docs-builder@sha256:5785f53f8dcbcc8786d1c255aed3beb2f0371f1fcdde8bb3f42243f53a8126a3` built the candidate.
Local evidence is retained at `/data/robin-GIT/evidence/custom-responses-17/` with build and check logs, the browser audit, and 26 desktop/mobile screenshots.
The review used 1440 × 1000 and 390 × 844 viewports. All 13 pages retained a title, sidebar entry, breadcrumb where applicable, and readable code.
No page overflow, empty code, unloaded image, script error, collapsed example, or encoded-body placeholder appeared.
The six pages without subsections omitted the “On this page” outline; pages with subsections retained it.
Contact sheets and full Maintenance and WAF mobile captures were inspected for layout and wrapping.

The rendered crawl passed 32 distinct internal links and fragments; the three distinct external source links returned HTTP 200.
Pagefind found Maintenance, and the English LLM index and full text contained the expected titles and Configuration reference.
Snippet preparation produced 54 source-selected files. All 23 Python tests, seven managed shell suites, Terraform format and validation, Ruff,
managed prose and changed-file pre-commit checks, changed-scope PII enforcement and audit, repository hygiene, and Gitleaks passed.
No source JSON, generator, scenario inventory, infrastructure, shared theme, or translation file changed.
