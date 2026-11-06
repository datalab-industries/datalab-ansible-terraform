---
title: Updating
---

# Updating

## Updating *datalab*

The deployed *datalab* version is the commit checked out in the `src/datalab` submodule.
To update it, check out the new tag, commit the submodule and redeploy:

```shell
cd src/datalab
git fetch --tags
git checkout <tag>
cd ../..
git commit src/datalab -m "Update datalab to <tag>"
make deploy
```

Read the [*datalab* release notes](https://github.com/datalab-org/datalab/releases) and check that backups work before updating.

The submodule can point to a fork of *datalab* with custom changes.
Any Ansible rules or configuration those changes need must then be maintained alongside the fork.

Each deploy also pulls the latest versions of the base images that the containers are built from (e.g., `mongo:8-noble`), so a redeploy picks up their security updates.

[`dlmeta deploy`](dlmeta.md#updating-and-deploying-datalab) updates and deploys several deployments at once.

## Updating system packages and Docker

System packages, including Docker, are only upgraded by the `maintenance` tag:

```shell
make maintenance
```

Run it regularly, and before deploying a new *datalab* version, as the builds need a recent Docker Compose (see [Keeping Docker up to date](managed-hosts.md#keeping-docker-up-to-date)).
Upgrading Docker restarts the Docker daemon, and with it all containers.
The Docker package repository is configured by the `docker` tag.

On Ubuntu, unattended upgrades also run every night: package lists refresh around midnight, upgrades install around 01:00, and any required reboot follows at 02:00.
With [monitoring](monitoring.md#automatic-upgrade-monitoring) configured, failed upgrades and missed reboots can be alerted on.

On RHEL-family hosts, `make maintenance` stops before upgrading if the enabled dnf repositories offer no kernel at least as new as the newest installed one.
This means the OS repositories are gone or have stopped updating, e.g., because the server's subscription-manager registration has lapsed and only the install-media repositories remain.
dnf would otherwise upgrade only third-party packages such as Docker, and leave the OS and kernel unpatched.
The error says whether the server is registered; if it is not, the server administrator needs to re-register it.

## Syncing with the upstream template

The playbooks come from this template repository, included as the `src/datalab-ansible-terraform` submodule.
To update them, check out the new version of the submodule and run the sync script:

```shell
cd src/datalab-ansible-terraform
git fetch --tags
git checkout <tag>
cd ../..
./sync-ansible-upstream.sh
```

The script copies the upstream playbooks, `Makefile`, `README.md`, `requirements.*`, `.vault-pass.sh`, `docs/` and `zensical.toml` into the deployment repository.
It asks for each change to the `ansible` directory to be reviewed before staging it, which matters most when the playbooks have local changes.
It then commits the playbooks, `docs/`, `zensical.toml` and the submodule update, so the history records exactly which version of the playbooks is running.
Changes to the other copied files are left uncommitted for review.
Files that upstream has deleted from `ansible/` are removed too, unless they have local changes, in which case the script keeps them and says so.

The script never touches the vaults, the inventory or `deployment-notes/`, and does not copy `tools/` (see [Managing multiple deployments](dlmeta.md)).

## Keeping the checklist up to date

The [deployment checklist](checklist.md) belongs to the deployment, so the sync script does not overwrite it.
Instead, it merges upstream's changes into the local copy, three ways:

- the base is the checklist at the version of the template last synced,
- one side is the local copy, with its ticks, removals and additions,
- the other side is the new upstream checklist.

New upstream items are added and local edits are kept.
If both sides changed the same lines, the script leaves conflict markers and says so, and they need resolving before committing.

Check the result with `git diff CHECKLIST.md` after each sync.
