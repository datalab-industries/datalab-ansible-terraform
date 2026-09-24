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
# Deployment-specific files (vaults, inventory, deployment-notes/) are never synced;
# CHECKLIST.md is merged rather than overwritten, see below.
rsync --exclude vaults --exclude inventory.yml -avr "$UPSTREAM/sync-ansible-upstream.sh" "$UPSTREAM/Makefile" "$UPSTREAM/.vault-pass.sh" "$UPSTREAM/README.md" "$UPSTREAM/requirements.in" "$UPSTREAM/requirements.txt" "$UPSTREAM/zensical.toml" "$UPSTREAM/ansible" .
# docs/ is fully owned by upstream, so also remove pages that were removed upstream.
# docs/reference is generated locally by `make docs` and is left alone.
rsync --delete --exclude reference -avr "$UPSTREAM/docs/" docs/
chmod u+x ./.vault-pass.sh

# Ignore built docs
for pattern in "site/" "docs/reference/"; do
    grep -qxF "$pattern" .gitignore 2>/dev/null || echo "$pattern" >> .gitignore
done

# CHECKLIST.md belongs to the deployment, but upstream adds items to it over time.
# Merge upstream's changes since the last sync, keeping local ticks and edits: the
# base is the checklist at the previously synced template version, "ours" is the
# local copy and "theirs" is the new upstream one.
previous=$(git rev-parse "HEAD:$UPSTREAM" 2>/dev/null || true)
if [ -n "$previous" ] && [ -f "$UPSTREAM/CHECKLIST.md" ] && [ -f CHECKLIST.md ]; then
    base=$(mktemp)
    if git -C "$UPSTREAM" show "$previous:CHECKLIST.md" > "$base" 2>/dev/null; then
        if git merge-file -L "your CHECKLIST.md" -L "checklist at last sync" -L "upstream CHECKLIST.md" \
               CHECKLIST.md "$base" "$UPSTREAM/CHECKLIST.md"; then
            echo "Merged any new checklist items from upstream into CHECKLIST.md."
        else
            echo "CHECKLIST.md has conflicts with upstream: resolve the conflict markers before committing."
        fi
    fi
    rm -f "$base"
fi

git add -p ansible
git add $(git ls-files ansible --others --exclude-standard)
git add src/datalab-ansible-terraform docs zensical.toml .gitignore
git commit -m "Sync with upstream definitions from datalab-ansible-terraform $commit"
echo "Review and commit any remaining changes to CHECKLIST.md, Makefile, README.md, requirements.* and .vault-pass.sh separately."
