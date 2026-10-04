# Reader guide audit

Recorded before the reader rewrite for issue [#7](https://github.com/f5-sales-demo/custom-responses/issues/7).

| Original page | Finding | Disposition |
| --- | --- | --- |
| Overview (`index.mdx`) | Cards prioritize ownership, inventory, deployment and verification; operational status dominates the reader entry point. | Preserve hero and shared branding; link cards to eleven customer outcomes and order the sidebar explicitly. |
| Response ownership | Useful distinctions lack a customer problem or procedure. | Place ownership and limitations beside the relevant outcome; retire the standalone page. |
| Scenario inventory | Repeats internal IDs, raw expectations and prerequisites without explaining why or how. | Replace generated prose with authored outcome pages; retain inventory unchanged and record complete coverage here in operator documentation. |
| Deploy with Terraform | Provider versions, state paths and saved-plan approval are operator procedures. | Move intact to `operator/deployment.md`; reference from repository configuration instructions. |
| Verify every scenario | Private captures and detailed evidence requirements obscure focused reader checks. | Move intact to `operator/verification.md`; retain the verifier and historical claims unchanged. |
| Tear down and rebuild | Billable infrastructure lifecycle belongs to operators. | Move intact to `operator/teardown.md`; fix repository-relative links. |
| Bot Defense configuration | Inactive examples are useful, but encoded prose is duplicated and optional activation dominates. | Author the Bot outcome with source includes, readable body and explicit configuration-only status; retain activation requirements in operator instructions. |
| Branding and documentation delivery | Theme versions, image digests and publication receipts describe delivery rather than response customization. | Move intact to `operator/branding.md`; preserve historical evidence outside the published corpus. |

The response-body bytes, Terraform configuration, inventory expectations and verification requirements remain authoritative. Snippet preparation replaces inventory-to-prose generation; it does not alter those sources. Control and index inventory entries support comparisons and do not become reader outcomes.
