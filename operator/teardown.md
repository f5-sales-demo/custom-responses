# Teardown and rebuild

The state owns only the resources listed in the reviewed project plan. The shared DNS zone, shared storage, other namespaces, origins and demo resources are outside teardown scope.

```bash
install -d -m 700 .artifacts
terraform -chdir=terraform plan -destroy -out=../.artifacts/destroy.tfplan
terraform -chdir=terraform show ../.artifacts/destroy.tfplan
```

Review every deletion before applying the saved destroy plan under the user's standing Terraform authorization for this prototype, granted on 2026-10-06. Stop if the state includes an unexpected resource, any shared DNS zone
or imported resource. Preserve a private state backup. Terraform dependencies remove scenario LBs before their referenced WAFs, pools and namespace, then delete
only the owned Azure infrastructure. Do not delete resources by a guessed name.

After teardown, verify the shared zone and unrelated resources remain unchanged, create and review a new rebuild plan, apply the reviewed saved plan and rebuild. Repeat [live verification](./verification.md) and a refresh-enabled zero-change plan. Retain sanitized receipts tied to both plan identities.

## Completed lifecycle exercise

The 2026-10-06 teardown deleted the 24 owned resources and eight LB-managed DNS records. Shared-zone unrelated records, namespaces, and Azure resources matched their baselines. The
serial rebuild restored all 24 resources and eight hosts with trusted TLS. The VM, OS disk, and origin IP were recreated. Qualified HTTP/browser checks and matching enforced WAF
events were repeated, and the aggregate refresh returned zero changes. The acceptance snapshot records protected receipt and saved-plan digests. DDoS remains deferred and
un-verified; origin mapping and CAPTCHA limitations remain explicit.
