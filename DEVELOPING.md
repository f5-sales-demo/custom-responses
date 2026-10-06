# Development

The scenario inventory is `scenarios.json`. It drives HTTP verification; `operator/scenario-coverage.json` maps every entry to a reader outcome or supporting fixture. Terraform configuration is in `terraform/`; the synthetic fixture is in `origin/`. Original prototypes remain at the repository root unchanged.

Run `python3 scripts/prepare_snippets.py`, `python3 -m unittest discover -s tests -p 'test_*.py'`, `terraform -chdir=terraform fmt -check` and `terraform
-chdir=terraform validate`. Run managed shell tests and PII checks before committing. Plans, state, private inputs and raw acceptance captures must stay outside
Git. Infrastructure applies require explicit approval of the exact saved plan.

Documentation and branding delivery uses the governed Starlight pipeline and shared theme. The user accepted the desktop/mobile visual previews. `operator/branding.md` records the published theme and immutable builder release; `/api/revision.json` identifies the deployed source and image.

Infrastructure remains partially deployed. Five of eight shared load balancers and the updated synthetic origin are deployed.
The JavaScript challenge passed trusted TLS, fresh-browser completion, repeat access, and unique-path origin ownership. The HTML and JSON WAF, shared errors, direct responses, redirect, metadata, and masking have bounded verified cases; origin-status mappings and challenge modes remain incomplete. Check the dated acceptance record and live public-host usage before each deployment wave.
Bot entries are configuration-only and excluded from deployment and required live proof. Preserve private local state
and captures. A changed recovery plan requires explicit approval before apply. Documentation publication does not
qualify full live acceptance, teardown/rebuild or zero drift.

Reader content lives only in `docs/en/`. Generated schema-projected resource snippets in ignored `docs/_data/` feed the existing `file=` code includes. Their bytes come from
`terraform/scenarios.tf.json` and inactive `examples/bot-defense.json`; do not copy configuration into prose. Run preparation before the governed builder.
Preparation fails on missing selectors, unknown fields, incompatible schema types, unexpected object-block cardinality, malformed bodies and duplicate outputs. The bounded official-schema contract and selector provenance live in `operator/response-schema.json` and `operator/snippet-provenance.md`. The page audit and lifecycle procedures live in [operator
instructions](operator/README.md).
