# Contributing

This repository is the upstream template for *datalab* deployments.
Changes here reach every deployment that runs `sync-ansible-upstream.sh`, so keep them general.

## Playbooks

- Every setting lives in the `common` role, not in the role that uses it:
  - its default in `ansible/roles/common/defaults/main.yml`, the only place defaults are set,
  - its type and description in `ansible/roles/common/meta/argument_specs.yml`, under the matching `# Section` comment.

  Add both in the same commit that introduces the setting.
  `common` runs first in every play, so the defaults are visible to all roles, and Ansible validates the inventory against the spec before anything changes the host.
  The [variable reference](https://datalab-industries.github.io/datalab-ansible-terraform/reference/) is generated from the spec and grouped by its section comments; a new section must also be added to `SECTIONS` in `scripts/gen-role-docs.py`.
- Other roles have no `defaults/` or `meta/argument_specs.yml` of their own.
- Mark an option `required` only if the playbook genuinely cannot run without it.
  A new required option breaks every existing inventory that omits it.
- Give new features their own tag in `ansible/playbook.yml`, so they can be run with `make <tag>`.
- Files deleted from `ansible/` are also removed from deployments by `sync-ansible-upstream.sh`, unless a deployment has changed them.
- `pre-commit run --all-files` runs ansible-lint and the other checks that CI runs.

## Documentation

The site in `docs/` is built with [zensical](https://zensical.org).
Preview it with `make docs` and build it with `make docs-build`.
The navigation is defined in `zensical.toml`; a new page is not visible until it is added there.

Writing conventions, shared with the [*datalab* user guide](https://github.com/datalab-org/datalab-user-guide):

- **Plain language.** Short sentences and simple structures. Do not use em dashes.
- **Task titles, not feature names.** "Emails for failed cron jobs", not "The cron_email role".
- **Check claims against the code.** Variable names, defaults and behaviour should match the playbooks as they are now, not as they were.
- **Say when something is optional,** and what happens if it is skipped.
- **Link rather than copy.** *datalab*'s own settings are documented at [docs.datalab-org.io](https://docs.datalab-org.io); link there instead of restating them.

## What belongs to a deployment

Some files are owned by each deployment rather than by this template, and the sync script treats them accordingly:

- `CHECKLIST.md` is merged, not overwritten, so deployments keep their ticks while receiving new items.
  Add new items to an existing section rather than to the end of the file, so that merge stays clean.
- `deployment-notes/` is never touched, and is not published to the site.
- `ansible/inventory.yml` and `ansible/vaults/` are never synced.

`ansible/inventory.example.yml` is the only copy of the example inventory: the configuration page includes it as a snippet, so a new setting is documented by adding it there.
A deployment's own `ansible/inventory.yml` is gitignored here and is never overwritten downstream.
