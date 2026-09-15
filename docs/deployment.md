# Deploying and updating

## DNS

If you use your own domain (set by `app_url` and `api_url` in the inventory), update your domain's DNS settings so that the app host, and the API host if it is separate, point to the IP of the server.
Do this before the first deployment, as the SSL certificates cannot be issued until DNS resolves correctly.

## Running the playbook

Once the configuration is complete, run the full playbook from the root of the repository:

```shell
make
```

This is equivalent to:

```shell
uv run ansible-playbook --ask-vault-pass -i ansible/inventory.yml ansible/playbook.yml
```

The playbook installs all prerequisite services, builds the Docker containers, connects them via NGINX and adds hardening services such as fail2ban.
If it completes successfully, the server will be running *datalab* at your configured URLs.

See the [checklist](checklist.md) for common tasks after the first deployment, such as creating an admin account.

## Running individual parts

Each part of the playbook has one or more tags.
To list them, run:

```shell
make list
```

To run only the tasks with a given tag, pass the tag to `make`, e.g.:

```shell
make deploy       # rebuild and relaunch datalab
make maintenance  # update system packages and renew nginx/SSL
make borg         # configure Borg backups
make monitoring   # configure Prometheus monitoring
```

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

The script does not touch your vaults, inventory, `CHECKLIST.md` or `deployment-notes/`.
See [About deployment docs](project-docs.md).

## Building these docs

This documentation is built with [zensical](https://zensical.org).
It is not part of `requirements.txt`; the `Makefile` runs a pinned version with `uvx`, so building the docs is optional and cannot affect the Ansible install.
To preview it locally, run:

```shell
make docs         # serve with live reload
make docs-build   # build the static site into ./site
```
