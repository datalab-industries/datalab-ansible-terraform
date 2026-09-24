# Contributing

This repository is the upstream template for *datalab* deployments.
Changes here reach every deployment that runs `sync-ansible-upstream.sh`, so keep them general.

## Playbooks

- Every role declares the variables it accepts in `ansible/roles/<role>/meta/argument_specs.yml`.
  Add new variables there in the same commit that introduces them.
  Ansible validates the inventory against these specs at the start of each run, and the [role reference](https://datalab-industries.github.io/datalab-ansible-terraform/reference/) pages are generated from them.
- Mark an option `required` only if the playbook genuinely cannot run without it.
  A new required option breaks every existing inventory that omits it.
- Give new features their own tag in `ansible/playbook.yml`, so they can be run with `make <tag>`.
- A new role also needs an entry under `Reference` in the nav in `zensical.toml`.
  `make docs` fails if the nav and the roles disagree.
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
