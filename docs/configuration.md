---
title: Configuration
---

# Configuration

There are two main sources of configuration:

1. The Ansible inventory, which tells Ansible which hosts to deploy to and how.
2. The *datalab* configuration files, stored in `ansible/vaults`.

Both should be encrypted before committing (see [Encrypting the configuration](#encrypting-the-configuration)).

## Ansible inventory

Edit `ansible/inventory.yml`, which `make quickstart` copied from the example (see the [full inventory documentation](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)).
Any `make` target that runs the playbook creates it from the example if it is missing.

The example lists every setting most deployments need:

```yaml title="ansible/inventory.example.yml"
--8<-- "ansible/inventory.example.yml"
```

Replace `<hostname>` and each setting with your own values, and delete the ones you do not need. Only `ansible_user`, `api_url` and `app_url` are required.

The API can be served in one of two ways:

- **On its own subdomain**, e.g., `app_url: example.org` and `api_url: api.example.org`.
- **Under a root path on the app's host**, e.g., `api_url: example.org/api`.
  Only one certificate is requested, and NGINX serves the API as a location inside the app's server block.
  The root path is passed through unchanged, so the API must be told to serve its routes under it.
  Set `ROOT_PATH` in `vaults/datalab/prod_config.json` to the path (e.g., `/api`), and set `VUE_APP_API_URL` in `vaults/datalab/.env` to the full URL.

If `mount_data_disk` is set, the disk is mounted at `/data`, which is where *datalab* stores its files and database.

The Borg, Prometheus, `cron_*`, `cheminventory_*` and `extras` settings are described in [Backups](backups.md), [Monitoring](monitoring.md), [Emails for failed cron jobs](cron-email.md), [ChemInventory syncing](cheminventory.md) and [Additional containers](extras.md).
The `manage_*` and `docker_*` settings are described in [Rootless Docker and managed hosts](managed-hosts.md).

Every variable the playbooks accept is listed under [Variables](reference/index.md), including the ones most deployments never change.

Each role declares its variables in `meta/argument_specs.yml`, and Ansible validates your inventory against those specs at the start of every run, before any task changes the server.
This happens even under `--check` and when running a single tag, so a missing required setting or a value of the wrong type stops the run immediately, naming the role and the variable.
Note that a variable whose name is misspelled is not recognised at all, so it is ignored rather than reported.

## *datalab* configuration

The files in `ansible/vaults/datalab` contain the *datalab* settings.
See the [*datalab* configuration docs](https://docs.datalab-org.io/en/stable/config/) for an explanation of each setting.

1. `vaults/datalab/prod_config.json`: the *datalab* Python config file.
2. `vaults/datalab/.env_server`: secrets required by the server as an env file (e.g., keys for GitHub or ORCID login, SMTP passwords).
3. `vaults/datalab/.env`: variables required by the web app (e.g., `VUE_APP_API_URL`).
4. `vaults/datalab/.ssh` (optional): SSH keys and config to mount into the server container, e.g., for remote filesystems.
5. `vaults/borg/.ssh` (optional): SSH keys and known hosts for the Borg backup system.

## Encrypting the configuration

Version control these files **with encryption** in your fork.
Never commit them without encryption, even to a private repository.

To encrypt them, run the following from the root of the repository:

```shell
make encrypt-vaults
```

This is equivalent to:

```shell
uv run ansible-vault encrypt ansible/inventory.yml ansible/vaults/datalab/prod_config.json ansible/vaults/datalab/.env ansible/vaults/datalab/.env_server
```

Files in the `.ssh` directories must each be encrypted individually.
`make encrypt-vaults` encrypts every file under `ansible/vaults`.

Provide a password when prompted.
Keep this password safe, as it is needed every time the playbook is run.
To avoid typing it each time, see [Vault password with Bitwarden](bitwarden.md).

To edit an encrypted file later, run:

```shell
make vaults      # choose any vault file to edit
make inventory   # edit the inventory directly
```

Next, [deploy](deployment.md).
