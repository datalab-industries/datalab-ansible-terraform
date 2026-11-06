---
title: Managing multiple deployments
---

# Managing multiple deployments

[`tools/dlmeta`](https://github.com/datalab-industries/datalab-ansible-terraform/blob/main/tools/dlmeta) shows the state of several deployments, each its own fork of this repository, and runs commands across them.
It is optional: nothing in the playbooks depends on it.

`dlmeta` lives in `tools/` of the template repository, not in each deployment, so `sync-ansible-upstream.sh` does not copy it.
Run it from a checkout of the template, or from the `src/datalab-ansible-terraform` submodule of any deployment.

## Setup

`dlmeta` only needs [uv](https://astral.sh/uv).
Link it onto the `PATH` and copy the [example config](https://github.com/datalab-industries/datalab-ansible-terraform/blob/main/tools/dlmeta.example.toml):

```shell
ln -s "$PWD/tools/dlmeta" ~/.local/bin/dlmeta
cp tools/dlmeta.example.toml ~/.config/dlmeta/config.toml
```

The config sets:

- `deployments`: deployment repos, or folders containing them. Repos are identified by their folder name, so names must be unique.
- `[inactive]`: deployments hidden unless `--all` is passed, each with a reason.
- `[flagged]`: *datalab* versions to warn about, as version specifiers (e.g., `"<0.7.0"`).
- `[flagged_rules]`: the same, for versions of the playbooks.
- `state_dir`: where the run ledger, probe results and logs are kept (default `~/.local/state/dlmeta`).

## Status of every deployment

```shell
dlmeta status  # table of local, deployed and live versions, last runs and maintenance
dlmeta         # the same as an interactive TUI, which can also bump and deploy
```

Two other commands fill in the table:

- `dlmeta discover` reads each deployment's `api_url` from its encrypted inventory, using the vault password from [Bitwarden](bitwarden.md).
- `dlmeta probe` asks each deployment's public `/info` endpoint which version it is running.

## Recording playbook runs

The "Last run", "Deployed" and "Maintenance" columns come from a ledger of playbook runs.
An Ansible callback in [`tools/callback_plugins`](https://github.com/datalab-industries/datalab-ansible-terraform/blob/main/tools/callback_plugins/deployment_ledger.py) writes it to `~/.local/state/dlmeta/runs`.

`dlmeta` enables the callback for everything it runs.
To also record runs started by hand, such as `make deploy` inside a deployment, enable it in `~/.ansible.cfg`:

```ini
[defaults]
callback_plugins = /path/to/datalab-ansible-terraform/tools/callback_plugins
callbacks_enabled = deployment_ledger
```

Unrecorded runs make a deployment look older than it is, so `dlmeta deploy` may redeploy it.
If `state_dir` is set in the config, also export `DEPLOYMENT_LEDGER_DIR=<state_dir>/runs` so that the callback writes there.

## Running a command in several deployments

`dlmeta run` lists what it will do and asks for confirmation first:

```shell
dlmeta run -- make maintenance
dlmeta run --only 'demo-*' --exclude demo-old -- make deploy
```

- Up to 8 deployments run at a time, with a live summary and a tab streaming each deployment's output.
- A failure does not stop the others. To roll out a risky change gradually, select a few deployments first with `--only`.
- Deployments where the ledger shows that `make maintenance`, or a whole-playbook run, succeeded in the last day are skipped.
  `--rerun-after` changes that window (e.g., `12h`, `1w`, or `0` to always run), or applies one to other targets, e.g., `dlmeta run --rerun-after 1h -- make deploy`.
- `x` stops new deployments from starting, and pressing `q` twice interrupts those running.
  Closing the terminal may also kill them, so run long batches inside `tmux` or similar.
- Anything that needs a prompt, such as a vault password when `rbw` has no entry, fails rather than waits.
- Logs for each run are kept in `~/.local/state/dlmeta/logs`.

## Updating and deploying *datalab*

`dlmeta deploy` updates *datalab* and deploys in one step.
It first shows each deployment's upgrade and asks for confirmation:

```shell
dlmeta deploy --only 'demo-*'                # the newest release on each deployment's own release line
dlmeta deploy --to v0.7.12                   # a specific tag
dlmeta deploy --to main --only demo-staging  # upstream's branch, or a specific commit
dlmeta deploy --nightly --only demo-staging  # the latest commit on upstream's main branch
```

`--nightly` moves deployments on a release line onto `main` where it can, and the plan warns about this, so combine it with `--only` unless every deployment should run the development version.
Deployments already on the target commit are skipped, so repeating a deploy is safe.
`-n` only shows the plan.

The `src/datalab` submodule is checked out but never staged or committed, so the result needs reviewing and committing afterwards (see [Updating](updating.md)).

Deployments that cannot be updated are not deployed.
They are flagged in red before and after the run, and `dlmeta` exits with a non-zero code.
This happens, for example, if:

- the fetch fails,
- `src/datalab` has uncommitted changes,
- the target version is listed under `[flagged]` in the config,
- the update would lose commits that are not pushed anywhere,
- with the default target, the checkout has commits that the newest release lacks.

Naming a target with `--to` allows leaving behind pushed commits, with a warning, so check what those commits are first.

Unlike `dlmeta run`, a failed deploy stops further deploys from starting, though those already running finish.
There is no automatic rollback.

## Syncing the playbooks

`dlmeta sync` updates each deployment's `src/datalab-ansible-terraform` submodule, then runs upstream's copy of `sync-ansible-upstream.sh` in it (see [Syncing with the upstream template](updating.md#syncing-with-the-upstream-template)):

```shell
dlmeta sync -n               # show the plan, warning about any datalab version outside the new release's supported versions
dlmeta sync --only 'demo-*'  # the newest release
dlmeta sync --to v0.10.2     # a specific tag, branch or commit (or --nightly for the latest commit on main)
dlmeta deploy                # then deploy, which also picks up deployments whose ansible/ has changed since their last deploy
```

The sync script asks which changes to commit, so deployments are synced one at a time, in a terminal.
It commits locally; nothing is pushed or deployed.

A deployment is skipped, and flagged in red, if its repo:

- has staged changes,
- has uncommitted changes in files the script overwrites, including anything untracked under `ansible/`, which the script would add,
- is not on a branch,
- or fails any of the checks listed above for `dlmeta deploy`.

The script leaves some changes uncommitted: the other copied files, such as `Makefile` and `README.md`, and any declined hunks.
It asks about those a second time, and the upstream version then stays in the working tree, where it would be deployed.
The submodule update is committed even if every hunk is declined.
`dlmeta sync` lists what was left uncommitted, and does not sync that deployment again until it has been committed or restored with `git restore`.
