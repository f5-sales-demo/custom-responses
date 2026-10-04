#!/usr/bin/env bash
set -euo pipefail
repo_root=/data/robin-GIT/worktrees
python3 -m unittest discover -s "/tests" -p "test_*.py"
terraform -chdir="/terraform" fmt -check
terraform -chdir="/terraform" init -backend=false -lockfile=readonly
terraform -chdir="/terraform" validate
