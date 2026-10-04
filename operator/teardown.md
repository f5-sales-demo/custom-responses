# Teardown and rebuild

The state owns only the resources listed in the reviewed project plan. The shared DNS zone, shared storage, other namespaces, origins and demo resources are outside teardown scope.

```bash
install -d -m 700 .artifacts
terraform -chdir=terraform plan -destroy -out=../.artifacts/destroy.tfplan
terraform -chdir=terraform show ../.artifacts/destroy.tfplan
```

Review every deletion and obtain explicit confirmation before applying the destroy plan. Stop if the state includes an unexpected resource, any shared DNS zone
or imported resource. Preserve a private state backup. Terraform dependencies remove scenario LBs before their referenced WAFs, pools and namespace, then delete
only the owned Azure infrastructure. Do not delete resources by a guessed name.

After teardown, verify the shared zone and unrelated resources remain unchanged, create and review a new rebuild plan, obtain approval and rebuild. Repeat [live verification](./verification.md) and a refresh-enabled zero-change plan. Retain sanitized receipts tied to both plan identities.
