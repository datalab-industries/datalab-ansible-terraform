# About deployment docs

Repositories created from this template keep two kinds of documentation:

| Location | Owner | Updated by `sync-ansible-upstream.sh` |
|---|---|---|
| `README.md`, `docs/`, `zensical.toml` | Upstream template | Yes, overwritten |
| `CHECKLIST.md`, `deployment-notes/` | Your deployment | No, never touched |

Do not edit files in `docs/` for your own deployment.
The sync script replaces the whole directory, so local changes will be lost.

## `CHECKLIST.md`

A list of common setup and maintenance tasks.
The template provides a starting version.
Tick items off as you complete them, remove items that do not apply, and add your own.

## `deployment-notes/`

Free-form notes for your deployment, for example:

- server details, hosting provider and who has access,
- DNS and domain records,
- where secrets such as the vault password and Borg passphrase are stored,
- a log of incidents, migrations and manual changes,
- custom changes to the playbooks.

Add Markdown files to this folder and link them from `deployment-notes/index.md`.
They appear under "This deployment" in the rendered site.

!!! warning
    These files are committed in plain text.
    Do not write secrets in them; keep secrets in the encrypted vaults or a password manager.
