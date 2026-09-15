# Deploying *datalab*

This repository contains tools and rules for automatically deploying *datalab* instances with Ansible.
It can be used as a template for deploying your own *datalab* instance, and can be resynced periodically when new versions are released.

The Ansible playbooks can set up a *datalab* instance on existing hardware.
They can also deploy *datalab* on shared hardware.
All mandatory services run in containers, so the full NGINX and *datalab* stack can run alongside an existing reverse proxy that manages other services.
You will need to configure this yourself.

Most of the configuration is transferable between instances.
Ideally, you only need to provide instance-specific configuration (e.g., usernames, domain names).
This lets you keep your copy of this repository in sync with the upstream `main` branch, which will continue to change as *datalab*'s requirements change.

## Contents

- [Installation](installation.md): prerequisites and installing Ansible.
- [Configuration](configuration.md): the Ansible inventory and *datalab* config vaults.
- [Deploying and updating](deployment.md): running the playbook and keeping your deployment up to date.
- [Backups](backups.md), [Monitoring](monitoring.md), [Emails for failed cron jobs](cron-email.md), [ChemInventory syncing](cheminventory.md), [Plugins](plugins.md), [Additional containers](extras.md), [Rootless Docker and managed hosts](managed-hosts.md) and [Bitwarden](bitwarden.md): optional features.
- [About deployment docs](project-docs.md): where to write documentation for your own deployment.
- [Cloud provisioning (legacy)](terraform.md): Terraform/OpenTofu plans for Azure. These are no longer actively supported.

## What gets deployed

The `./ansible` directory contains Ansible playbooks that take a fresh VM and install, configure, launch, relaunch and manage the *datalab* and NGINX containers.

Stack:

- NGINX, with SSL certificates from certbot
- Docker Compose for the API, app and database containers
- A simple filesystem for the filestore
- Hardening services such as fail2ban and SSH configuration
- Optional: Borg backups, Prometheus monitoring, plugins and extra containers

## *datalab* versioning

The playbooks deploy the *datalab* version that is included as a git submodule at `src/datalab`.
Only run the playbook from a clean repository state (i.e., no uncommitted changes) so that deployments are reproducible.

## Supported versions

| This repository version | *datalab* version |
|---|---|
| v0.1.x | v0.4.x  |
| v0.2.x | v0.4.x  |
| v0.3.x | v0.5.0-rc.x |
| v0.4.x | v0.5.x |
| v0.5.x | v0.6.x |
| v0.6.x | v0.6.x |
| v0.7.x | v0.7.x-rc.x |
| v0.8.x | v0.7.x |

## Changelog

The changelog for this repository is in the [release notes](https://github.com/datalab-industries/datalab-ansible-terraform/releases) on GitHub.

## Getting help

Chat with us on [Slack](https://join.slack.com/t/datalab-world/shared_invite/zt-2h58ev3pc-VV496~5je~QoT2TgFIwn4g) or raise an issue on [GitHub](https://github.com/datalab-industries/datalab-ansible-terraform/issues).
The main *datalab* documentation is at [docs.datalab-org.io](https://docs.datalab-org.io).
