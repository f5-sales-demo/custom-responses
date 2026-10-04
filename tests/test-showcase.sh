#!/usr/bin/env bash
set -euo pipefail
repo_root=$(cd "$(dirname "$0")/.." && pwd)
python3 -m unittest discover -s "$repo_root/tests" -p 'test_*.py'
terraform -chdir="$repo_root/terraform" fmt -check
terraform -chdir="$repo_root/terraform" init -backend=false -lockfile=readonly
terraform -chdir="$repo_root/terraform" validate
