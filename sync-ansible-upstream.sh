#!/bin/bash
set -e -u -o pipefail
commit=$(cd src/datalab-ansible-terraform && git describe --tags)
rsync --exclude vaults --exclude inventory.yml -avr src/datalab-ansible-terraform/sync-ansible-upstream.sh src/datalab-ansible-terraform/Makefile src/datalab-ansible-terraform/.vault-pass.sh src/datalab-ansible-terraform/README.md src/datalab-ansible-terraform/requirements.txt src/datalab-ansible-terraform/ansible .
git add -p ansible
git add src/datalab-ansible-terraform
git add $(git ls-files ansible --others --exclude-standard)
git commit ansible -p -m "Sync with upstream definitions from datalab-ansible-terraform $commit"
