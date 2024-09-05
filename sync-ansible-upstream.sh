#!/bin/bash
set -e -u -o pipefail
commit=$(cd src/datalab-ansible-terraform && git describe --tags)
rsync --exclude vaults --exclude inventory.yml -avr src/datalab-ansible-terraform/ansible .
git add -p ansible
git add $(git ls-files ansible --others --exclude-standard)
git commit ansible -p -m "Sync with upstream definitions from datalab-ansible-terraform $commit"
