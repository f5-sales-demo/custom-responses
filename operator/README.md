# Repository operator instructions

The [reader guide](../docs/en/index.mdx) explains response outcomes and configuration. This directory is outside the Pages content root and its search and language-model corpus.

- [Page audit](page-audit.md) records the original guide's findings and disposition.
- [Deployment](deployment.md) retains provider, private state, saved-plan and recovery requirements.
- [Detailed verification](verification.md) retains all HTTP, browser and security-event requirements. `scenarios.json` and `scripts/verify_live.py` remain authoritative.
- [Teardown and rebuild](teardown.md) retains infrastructure ownership and approval boundaries.
- [Historical branding delivery](branding.md) retains accepted artwork and release receipts as historical evidence.
- [Scenario coverage](scenario-coverage.json) maps every inventory entry to one outcome or a supporting fixture. Control/index support comparisons; Bot remains configuration-only.

## Prepare documentation

Run `python3 scripts/prepare_snippets.py` from the repository root before the governed Pages builder. The script reads JSON pointers from the Terraform source
and inactive Bot examples, validates canonical padded Base64 and UTF-8, and writes only ignored `docs/_data/` fragments. Body files preserve exact decoded
bytes; the builder escapes them as code. Exact encoded configuration appears inline with its decoded preview where available. No infrastructure command runs during preparation.

Use `python3 -m unittest discover -s tests -p 'test_*.py'` to check source consistency, inventory scope, deterministic output and editorial boundaries. Follow `DEVELOPING.md` for managed lint, security and PII checks.

## Optional Bot activation

Bot examples remain outside the Terraform configuration directory. Future activation requires Bot Defense Standard entitlement, private API access, a reviewed
complete configuration, an approved saved plan, genuine classification evidence and legitimate-browser comparison checks. Verify the redirect destination. These
requirements do not qualify Bot runtime in the current guide or change the remaining live-verification requirements.
