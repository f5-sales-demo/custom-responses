# Development

The scenario inventory is `scenarios.json`. It drives documentation and HTTP verification. Terraform configuration is in `terraform/`; the synthetic fixture is in `origin/`. Original prototypes remain at the repository root unchanged.

Run `python3 scripts/generate_docs.py`, `python3 -m unittest discover -s tests -p 'test_*.py'`, `terraform -chdir=terraform fmt -check` and `terraform -chdir=terraform validate`. Run managed shell tests and PII checks before committing. Plans, state, private inputs and raw acceptance captures must stay outside Git. Infrastructure applies require explicit approval of the exact saved plan.

Documentation and branding delivery uses the governed Starlight pipeline and shared theme. The user accepted the desktop/mobile visual previews. `docs/en/branding.mdx` records the published theme and immutable builder release; `/api/revision.json` identifies the deployed source and image.

Infrastructure remains partially deployed. The WAF HTML LB has a valid automatic certificate and measured benign
`200` / custom blocked `403` responses; full scenario acceptance is incomplete. Public virtual-host capacity is deferred.
Bot entries are configuration-only and excluded from deployment and required live proof. Preserve private local state
and captures. A changed recovery plan requires explicit approval before apply. Documentation publication does not
qualify full live acceptance, teardown/rebuild or zero drift.
