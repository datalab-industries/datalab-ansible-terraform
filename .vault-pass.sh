#!/bin/bash
# This script retrieves the password for the current git repository from a Bitwarden Vault using rbw.
# The entry is looked up as "<org>/<repo>" (e.g., "datalab-industries/datalab-ansible-terraform"),
# falling back to just "<repo>" for entries created before the org was included.
# If rbw is not available, it should error out
set -e
remote="$(git remote get-url origin | sed -E 's#^.*[:/]([^/:]+/[^/]+)$#\1#')"
rbw get "$remote" 2>/dev/null || rbw get "${remote#*/}" || { read -sp "Password or Bitwarden CLI not found. Enter vault password: " password; echo "$password"; }
