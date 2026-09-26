---
title: Updating
---

# Updating

## Updating *datalab*

To update *datalab*, update the git submodule in `src/datalab` and redeploy:

```shell
cd src/datalab
git fetch --tags
git checkout <tag>
cd ../..
git commit src/datalab -m "Update datalab to <tag>"
make deploy
```

The submodule can point to your own fork to include custom changes.
In that case you may also need to test and maintain your own Ansible rules and configuration.

Read the [*datalab* release notes](https://github.com/datalab-org/datalab/releases) and make sure your backups work before updating.

## Syncing with the upstream template

To pull in changes to the playbooks from this template repository, update the submodule in `src/datalab-ansible-terraform` and run the helper script:

```shell
cd src/datalab-ansible-terraform
git fetch --tags
git checkout <tag>
cd ../..
./sync-ansible-upstream.sh
```

The script copies the upstream playbooks, `Makefile`, `README.md`, `requirements.*`, `.vault-pass.sh`, `docs/` and `zensical.toml` into your repository.
It asks you to review each change to the `ansible` directory before staging it.
Review carefully if you have made custom changes to the playbooks.
It then commits the playbooks, `docs/`, `zensical.toml` and the submodule update, so you know exactly which version of the playbooks is running.
Changes to the other copied files are left uncommitted for you to review.

The script never overwrites your vaults, inventory or `deployment-notes/`.

## Keeping the checklist up to date

The [deployment checklist](checklist.md) belongs to your deployment, so the sync script does not overwrite it.
New items are still added to it upstream as the playbooks gain features.

To bring those in, the script merges upstream's changes to the checklist into your copy, three ways:

- the base is the checklist as it was at the version of the template you last synced,
- one side is your copy, with your ticks, removals and additions,
- the other side is the new upstream checklist.

New upstream items appear in your copy, and your own edits are kept.
If both sides changed the same lines, the script leaves conflict markers and tells you, so you can resolve them before committing.

Review the result with `git diff CHECKLIST.md` after each sync.
