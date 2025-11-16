#!/bin/bash
set -e -u -o pipefail
# Check for DATALAB_ANSIBLE_TEMPLATE_DIR environment variable
# If set, use that as the TEMPLATE_ROOT directory
# Otherwise, use "src" as the default
if [ -n "${DATALAB_ANSIBLE_TEMPLATE_DIR:-}" ]; then
    TEMPLATE_ROOT="$DATALAB_ANSIBLE_TEMPLATE_DIR"
else
    TEMPLATE_ROOT="src"
fi

commit=$(cd src/datalab-ansible-terraform && git describe --tags)
rsync --exclude vaults --exclude inventory.yml -avr "$TEMPLATE_ROOT/datalab-ansible-terraform/sync-ansible-upstream.sh" "$TEMPLATE_ROOT/datalab-ansible-terraform/Makefile" "$TEMPLATE_ROOT/datalab-ansible-terraform/.vault-pass.sh" "$TEMPLATE_ROOT/datalab-ansible-terraform/README.md" "$TEMPLATE_ROOT/datalab-ansible-terraform/requirements.txt" "$TEMPLATE_ROOT/datalab-ansible-terraform/ansible" .
chmod u+x ./.vault-pass.sh
git add -p ansible
git add src/datalab-ansible-terraform
git add $(git ls-files ansible --others --exclude-standard)
git commit ansible -p -m "Sync with upstream definitions from datalab-ansible-terraform $commit"
