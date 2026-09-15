# Configuration

There are two main sources of configuration:

1. The Ansible inventory, which tells Ansible which hosts to deploy to and how.
2. The *datalab* configuration files, stored in `ansible/vaults`.

Both should be encrypted before committing (see [Encrypting the configuration](#encrypting-the-configuration)).

## Ansible inventory

Edit `ansible/inventory.yml` (see the [full inventory documentation](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)):

```yaml
ungrouped:
  hosts:
    <hostname>:
      ansible_become_method: sudo
      ansible_user: <remote_username>
      api_url: <desired_datalab_api_url>
      app_url: <desired_datalab_app_url>
      # Optional settings:
      ansible_become_password: <remote_user_password>  # if needed for a non-root user
      datalab_prefix: <prefix used for monitoring labels>
      mount_data_disk: <disk device file, e.g., /dev/sdb, or a full fstab source, e.g., UUID=aaaa-bbbb-cccc>
      data_disk_type: <fstype of the data disk, defaults to xfs>
      borg_encryption_passphrase: <passphrase for borg encryption>
      borg_remote_path: <command to run borg on the repository, e.g., borg1>
      borg_repository: <path to the borg repository, local or remote>
      prometheus_remote_write_url: <e.g., https://grafana.datalab.industries/prometheus/api/v1/write>
      prometheus_user: <your_prometheus_username>
      prometheus_password: <your_prometheus_password>
      extras:  # see "Additional containers"
        <service_name>:
          url: <service_url>
          port: <service_port>
```

Replace `<hostname>` and each setting with your own values.

The API can be served in one of two ways:

- **On its own subdomain**, e.g., `app_url: example.org` and `api_url: api.example.org`.
- **Under a root path on the app's host**, e.g., `api_url: example.org/api`.
  Only one certificate is requested, and NGINX serves the API as a location inside the app's server block.
  The root path is passed through unchanged, so the API must be told to serve its routes under it.
  Set `ROOT_PATH` in `vaults/datalab/prod_config.json` to the path (e.g., `/api`), and set `VUE_APP_API_URL` in `vaults/datalab/.env` to the full URL.

If `mount_data_disk` is set, the disk is mounted at `/data`, which is where *datalab* stores its files and database.

The Borg, Prometheus and `extras` settings are described in [Backups](backups.md), [Monitoring](monitoring.md) and [Additional containers](extras.md).

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
