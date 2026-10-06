# Deployment

## Prerequisites

Use the authorized `f5-sales-demo` tenant and Azure lab subscription. The operator needs Azure resource permissions and a private XC API context. Keep credentials in private sources or process environment, never in committed files or chat.

The root configuration pins `f5-sales-demo/xcsh` 13.0.3 and `hashicorp/azurerm` 4.51.0. Commit the lockfile. Verify the provider archive against its release checksum and signature before planning.

## State and resource scope

The current backend is **local**, as requested. On the deployment workstation, initialize the backend at an absolute owner-only path outside the checkout:

```bash
install -d -m 700 "$HOME/.local/state/custom-responses"
terraform -chdir=terraform init \
  -backend-config="path=$HOME/.local/state/custom-responses/custom-responses.tfstate"
```

Retain and back up this state privately. Never initialize against another project's state. Do not run concurrent operators against the local file. The shared Azure storage account is preserved; a future remote-state migration needs a reviewed, separately authorized change.

The project owns `rg-custom-responses` in `eastus2`, a `Standard_B2s` Ubuntu VM, network, subnet, static IP, security
group and interface. SSH permits the operator's IPv4 `/32`. Origin listeners permit the provider's pinned Regional Edge
networks plus the operator address. httpbin binds only on VM loopback behind the fixture service. The shared DNS zone is
consumed through LB-managed records and is not a Terraform resource here.

## Private inputs

Create ignored `terraform/terraform.tfvars.json` containing `subscription_id`, `operator_cidr`, `ssh_public_key`, and `httpbin_image`. The image must use the verified `mccutchen/go-httpbin@sha256:...` digest. No private key is uploaded. Provider authentication reads `XCSH_API_URL` and `XCSH_API_TOKEN` from the process environment.

## Validate and plan

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
terraform -chdir=terraform fmt -check
terraform -chdir=terraform validate
install -d -m 700 "$HOME/.local/state/custom-responses/plans"
terraform -chdir=terraform plan -parallelism=1 \
  -out="$HOME/.local/state/custom-responses/plans/full.tfplan"
terraform -chdir=terraform show "$HOME/.local/state/custom-responses/plans/full.tfplan"
sha256sum "$HOME/.local/state/custom-responses/plans/full.tfplan"
```

The current default configuration contains 24 resources: eight Azure resources, one XC namespace, five origin pools,
two WAFs and eight HTTPS load balancers. The originally approved plan contained two additional Bot LBs; it has already
been consumed by the partial apply. Generate and review a new plan for the current configuration. Costs include B2s VM hours, a 32-GiB Standard LRS disk,
static public IP, outbound traffic, and tenant-specific XC feature charges. Automatic certificates and security features
depend on tenant entitlement. Use Azure's current estimate for the selected subscription and currency; no unverified
fixed monthly price is implied.

The full plan may replace the origin VM because `custom_data` changed. Review that replacement explicitly. For the first serial wave, save a separate plan targeted only at `xcsh_http_loadbalancer.errors` and inspect its exact actions:

```bash
terraform -chdir=terraform plan -parallelism=1 \
  -target=xcsh_http_loadbalancer.errors \
  -out="$HOME/.local/state/custom-responses/plans/errors.tfplan"
terraform -chdir=terraform show "$HOME/.local/state/custom-responses/plans/errors.tfplan"
sha256sum "$HOME/.local/state/custom-responses/plans/errors.tfplan"
```

Obtain explicit user approval of the **exact saved wave plan** before applying it. A changed plan needs another review. Check the effective `virtual_host.public` limit and usage, as well as the broader Virtual Host limit and usage, in the same XC tenant. If public capacity is full, stop and address that concrete limit before creating a load balancer. After approval and available capacity:

```bash
terraform -chdir=terraform apply -parallelism=1 \
  "$HOME/.local/state/custom-responses/plans/errors.tfplan"
```

Verify DNS, certificate, status, body, negative control and response owner for the shared error host. Plan and review the next serial wave only after that evidence is complete.

A targeted plan excludes unrelated changes in the full plan. Review those changes in later waves. The origin VM replacement needs separate exact-plan approval before apply. Use [verification](./verification.md) to qualify each deployed case.

## Current serial state

The dated [acceptance snapshot](../acceptance/current-iteration.json) records four created load balancers, the approved origin VM replacement, current quota evidence, and the remaining unverified examples. The initial and pre-replacement full plans are consumed or stale. Review a fresh saved plan for each remaining challenge load balancer; retain `-parallelism=1` and the exact-plan approval gate.

## Resume the partial deployment

The initial approved apply created the owned origin resources, namespace, pools, WAFs and one LB. Public virtual-host
usage updates rejected the remaining LBs, and Bot Standard is now documented as configuration-only. The previous recovery plan is obsolete. The current source shares compatible scenarios across eight load balancers and preserves the working WAF HTML resource.

Back up the protected local state, verify tenant quota and usage, and save a fresh plan. Review every proposed replacement, especially the origin VM because cloud-init content changed, and obtain approval of that exact plan before applying. Preserve private local state; never reapply the consumed initial plan.

On a single-create 429, wait five minutes, review a fresh plan, and retry once only if capacity is available. A second 429 requires a sanitized support case for HTTP load-balancer create rate or `virtual_host.public` usage updates. Request a quota increase only if XC reports a lower effective public-host limit than the broader Virtual Host limit.
