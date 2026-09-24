---
title: Documenting your deployment
---

# Documenting your own deployment

Repositories created from this template keep two kinds of documentation.

| Location | Owner | Updated by `sync-ansible-upstream.sh` |
|---|---|---|
| `README.md`, `docs/`, `zensical.toml` | Upstream template | Yes, overwritten |
| `CHECKLIST.md` | Shared | New upstream items are merged in, your edits are kept |
| `deployment-notes/` | Your deployment | No, never touched |

Do not edit files in `docs/` for your own deployment.
The sync script replaces the whole directory, so local changes will be lost.

## `deployment-notes/`

Write your own documentation as Markdown files in this folder.
Nothing in it is ever overwritten by a sync, and nothing in it is published to this site, so it can describe your servers as plainly as you need.

Useful things to record:

- server details, hosting provider and who has access,
- DNS and domain records,
- where secrets such as the vault password and Borg passphrase are stored,
- a log of incidents, migrations and manual changes,
- custom changes you have made to the playbooks.

`deployment-notes/index.md` is a starting point.
Add as many files as you like beside it and link them from there.
They read as ordinary Markdown on GitHub, or in any editor.

!!! warning
    These files are committed in plain text.
    Do not write secrets in them. Keep secrets in the encrypted vaults or a password manager.

## `CHECKLIST.md`

A list of setup and maintenance tasks, published on this site as the [deployment checklist](checklist.md).

Tick items off as you complete them, remove the ones that do not apply, and add your own.
The sync script merges new upstream items into your copy without discarding your edits (see [Keeping the checklist up to date](updating.md#keeping-the-checklist-up-to-date)).

## Building these docs

This documentation is built with [zensical](https://zensical.org).
It is not part of `requirements.txt`.
The `Makefile` runs a pinned version with `uvx`, so building the docs is optional and cannot affect the Ansible install.

```shell
make docs         # serve with live reload
make docs-build   # build the static site into ./site
```

Both first regenerate the [variable reference](reference/index.md) from the roles' argument specs.
The generated pages are not committed.
