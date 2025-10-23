#!/bin/bash
# This script retrieves the password for the current git repository from a Bitwarden Vault.
# If bw is not available, it should error out
set -e
bw get password "$(git remote get-url origin | awk '{split($0, a, "/"); print a[length(a)]}')" || { read -sp "Password or Bitwarden CLI not found. Enter vault password: " password; echo "$password"; }
