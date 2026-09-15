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
UPSTREAM="$TEMPLATE_ROOT/datalab-ansible-terraform"

commit=$(cd src/datalab-ansible-terraform && git describe --tags)

# Files owned by the upstream template.
# Deployment-specific files (vaults, inventory, CHECKLIST.md, deployment-notes/) are never synced.
rsync --exclude vaults --exclude inventory.yml -avr "$UPSTREAM/sync-ansible-upstream.sh" "$UPSTREAM/Makefile" "$UPSTREAM/.vault-pass.sh" "$UPSTREAM/README.md" "$UPSTREAM/requirements.in" "$UPSTREAM/requirements.txt" "$UPSTREAM/zensical.toml" "$UPSTREAM/ansible" .
# docs/ is fully owned by upstream, so also remove pages that were removed upstream.
# docs/deployment-notes is generated locally by `make docs` and is left alone.
rsync --delete --exclude deployment-notes -avr "$UPSTREAM/docs/" docs/
chmod u+x ./.vault-pass.sh

# Ignore built docs
for pattern in "site/" "docs/deployment-notes/"; do
    grep -qxF "$pattern" .gitignore 2>/dev/null || echo "$pattern" >> .gitignore
done

git add -p ansible
git add $(git ls-files ansible --others --exclude-standard)
git add src/datalab-ansible-terraform docs zensical.toml .gitignore
git commit -m "Sync with upstream definitions from datalab-ansible-terraform $commit"
echo "Review and commit any remaining changes to Makefile, README.md, requirements.* and .vault-pass.sh separately."
