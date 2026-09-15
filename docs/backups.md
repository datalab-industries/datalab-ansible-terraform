# Backups

## Native backups

By default, the playbook schedules *datalab*'s native snapshot backups (the `weekly-snapshots` strategy) with the retention rules set in the *datalab* config.
These backups can be synced with a remote system to avoid data loss if the *datalab* server has a hardware failure.

More information is in the [*datalab* backup documentation](https://docs.datalab-org.io/en/stable/deployment/#backups).

## Borg backups (recommended)

This repository contains playbooks that automate more robust backups with [Borg](https://www.borgbackup.org/) and [borgmatic](https://torsion.org/borgmatic/).

These backups are encrypted, de-duplicated and compressed.
They need much less space than native backups and can be synced to remote Borg servers over SSH.
Both the database and the `/data` directory are backed up.

You need a remote server running Borg, ideally separate from the *datalab* server.
We recommend [rsync.net](https://www.rsync.net/products/borg.html), which has good Borg support.

!!! note
    If you run a *datalab* instance and need a place for encrypted Borg backups, reach out to us.
    We may be able to act as a secondary backup host.

### Setup

1. Create an SSH key pair for passwordless access to your remote Borg server.
   Save the private key as `ansible/vaults/borg/.ssh/id_ed25519` and encrypt it.
2. Optionally, add other files to `ansible/vaults/borg/.ssh`, each encrypted.
   All of them are mounted into the Borg container during backups.
   For example, add a `config` for extra settings (e.g., proxies) or a `known_hosts` for strict host checking.
3. Add the Borg settings to your inventory:
   ```yaml
   borg_encryption_passphrase: <passphrase for borg encryption>
   borg_remote_path: <command to run borg on the repository, e.g., borg1>
   borg_repository: <path to the borg repository, local or remote>
   ```
4. Run the playbook with the `borg` tag:
   ```shell
   make borg
   ```

The Borg role is skipped unless the SSH key and all three inventory settings are present.

Store the Borg encryption passphrase somewhere other than this repository's vaults (e.g., a password manager).
Without it, the backups cannot be restored.

Other settings, such as the retention policy and backup schedule, have defaults in `ansible/roles/borg/defaults/main.yml`.
They can be overridden in the inventory.
