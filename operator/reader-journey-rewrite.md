# Collection rewrite for issue #58

The English collection follows choose → configure → verify through focused concept guides. The retained sequence is Overview, Maintenance, Missing and retired resources, Static
acknowledgement, Error responses, Redirects, Headers and cookies, Cross-origin access (CORS), Data masking, WAF blocking, Rate limits, JavaScript challenge, CAPTCHA verification,
Conditional challenges, Bot Defense configuration, and Configuration reference.

Homepage cards, sidebar order and pagination share this sequence. The documentation Demo panel page and mixed widget are removed. Redirect and header guides link to the working application panel; CORS and Rate limits each own a focused widget. All other guide URLs remain stable.

## Configuration and qualification

The generator validates source schema types before narrowing display fields, error keys or route arrays. Maintenance shows only its `503` mapping; missing and retired resources
show `404` and `410`; the error guide displays its qualified fault routes. A new source-selected rate-limiter identification reference completes the identification → limiter →
load-balancer attachment → custom-body relationship.

CAPTCHA and policy CAPTCHA completion remain un-verified. DDoS remains un-verified and deferred. Bot Defense remains inactive and configuration-only. The WAF JSON media-type
limitation stays beside its example. Error-mapping investigation is retained in [operator observations](error-mapping-observations.md), and the deferred VM-fixture inaccuracies are
recorded in [runtime panel corrections](runtime-panel-corrections.md).

## Verification evidence

- The changed contracts failed on the old collection and incomplete projections before implementation. All 46 Python tests pass, including deterministic projections, required references, page purposes, card order, live-link qualification, click-only widget execution, request budgets, cooldown and incomplete-test reporting.
- Snippet preparation produces 76 source-selected files. The official schema contract, provider pins, infrastructure, fixture bytes, translations and existing protected acceptance record are unchanged.
- The 7 managed shell suites, Terraform format and validation, Ruff, MDX prose, changed-file pre-commit, staged PII enforcement, changed-scope PII audit and secrets checks pass.
- The same immutable builder as the governed Pages workflow builds the candidate: `ghcr.io/f5-sales-demo/docs-builder@sha256:988e1fbf4e5acdbb15eb0c9aa6430f7968603d4fc96e713a28ca09846eedadd4`.

The rendered audit covers all 16 English pages at 1440 × 1000 and 390 × 844. It checks headings, code, images, overflow, ordered sidebar and pagination, breadcrumbs, meaningful
outlines, all internal content links and anchors, Pagefind search, keyboard interaction, and English text indices. Each focused widget is exercised from the allowed documentation
origin: CORS returns a readable synthetic response; the limiter returns five `200` responses then two custom `429` responses and enters cooldown. No demo requests run on page load.

Visual review covers desktop and mobile captures of every page. The redirect comparison was reduced to three columns after mobile review; query handling is explained alongside it. Private raw captures remain outside Git; screenshots and a static candidate are available as review artifacts. This is editorial acceptance evidence, not a new qualification of deferred infrastructure scenarios.

## Delivery status

Source implementation and candidate verification are complete. Publication awaits explicit human acceptance of the reviewable PR under CONTRIBUTING.md. After acceptance, enable squash merge, confirm green CI and the merged state, verify `/api/revision.json` against the merged commit and immutable builder, rerun published-page checks, and retire only the task worktree and confirmed-merged branch.
