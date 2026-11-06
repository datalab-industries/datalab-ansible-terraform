---
title: Deployment notes
---

# Deployment notes

A repository created from this template holds two kinds of documentation.

| Location | Owner | Updated by `sync-ansible-upstream.sh` |
|---|---|---|
| `README.md`, `docs/`, `zensical.toml` | Upstream template | Yes, overwritten |
| `CHECKLIST.md` | Shared | New upstream items are merged in, local edits are kept |
| `deployment-notes/` | The deployment | No, never touched |

Do not edit files in `docs/` for a single deployment.
The sync script replaces the whole directory, so local changes are lost.

## `deployment-notes/`

Markdown notes about the deployment itself.
A sync never overwrites this folder, and it is not published on this site.

Worth recording here:

- server details, the hosting provider and who has access,
- DNS and domain records,
- where secrets such as the vault password and Borg passphrase are stored,
- a log of incidents, migrations and manual changes,
- custom changes to the playbooks.

`deployment-notes/index.md` is the starting point.
Add more files beside it and link them from there.
They render as ordinary Markdown on GitHub or in an editor.

!!! warning
    These files are committed in plain text.
    Keep secrets in the encrypted vaults or a password manager, not here.

## `CHECKLIST.md`

Setup and maintenance tasks, published on this site as the [deployment checklist](checklist.md).

Tick items off when done, remove the ones that do not apply, and add new ones.
The sync script merges new upstream items in without discarding local edits (see [Keeping the checklist up to date](updating.md#keeping-the-checklist-up-to-date)).

## Building these docs

This site is built with [zensical](https://zensical.org).
It is not part of `requirements.txt`: the `Makefile` runs a pinned version with `uvx`, so the docs cannot affect the Ansible install.

```shell
make docs         # serve with live reload
make docs-build   # build the static site into ./site
```

Both first regenerate the [variable reference](reference/index.md) from the roles' argument specs.
The generated pages are not committed.
