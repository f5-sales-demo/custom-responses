# Development

The scenario inventory is `scenarios.json`. It drives documentation and HTTP verification. Terraform configuration is in `terraform/`; the synthetic fixture is in `origin/`. Original prototypes remain at the repository root unchanged.

Run `python3 scripts/generate_docs.py`, `python3 -m unittest discover -s tests -p 'test_*.py'`, `terraform -chdir=terraform fmt -check` and `terraform -chdir=terraform validate`. Run managed shell tests and PII checks before committing. Plans, state, private inputs and raw acceptance captures must stay outside Git. Infrastructure applies require explicit approval of the exact saved plan.

Task status: infrastructure source and initial plan prepared; governance enrollment under CI; hero generated and visually inspected; deployment, live qualification, publication and teardown/rebuild pending.

Current handoff: approved plan partially applied; one WAF LB is present and awaiting automatic certificate issuance. Public virtual-host capacity and Bot Standard entitlement are deferred by the user to the next iteration. Preserve private local state and captures. A changed recovery plan requires explicit approval before apply. Source delivery and documentation publication do not qualify full live acceptance.
