---
title: Deploying datalab
hide:
  - toc
---

# Deploying *datalab*

This repository contains tools and rules for deploying *datalab* instances with Ansible.
Use it as a template for your own deployment, and resync it when new versions are released.

The playbooks can set up *datalab* on existing hardware, including shared hardware.
All mandatory services run in containers, so the full NGINX and *datalab* stack can run alongside an existing reverse proxy that manages other services, which you configure yourself.

Most of the configuration is transferable between instances.
Ideally you only provide instance-specific settings such as usernames and domain names, which lets you keep your copy in sync with this template as *datalab*'s requirements change.

<div class="grid cards" markdown>

-   __Deploying for the first time__

    Read in order: prerequisites, the inventory and vaults, then the playbook itself.

    [Installation](installation.md) ·
    [Configuration](configuration.md) ·
    [Deploying](deployment.md)

-   __Running an instance__

    Keeping *datalab* and the playbooks current, and the tasks that follow a first deployment.

    [Updating](updating.md) ·
    [Deployment checklist](checklist.md)

-   __Optional features__

    Each stands alone. Add them whenever you need them.

    [Backups](backups.md) ·
    [Monitoring](monitoring.md) ·
    [Cron emails](cron-email.md) ·
    [ChemInventory](cheminventory.md) ·
    [Plugins](plugins.md) ·
    [Extra containers](extras.md) ·
    [Rootless Docker](managed-hosts.md) ·
    [Bitwarden](bitwarden.md)

-   __Looking something up__

    Every variable the playbooks accept, and where to put your own documentation.

    [Role reference](reference/index.md) ·
    [Documenting your deployment](project-docs.md)

</div>

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

## Related repositories

- [datalab-org/datalab](https://github.com/datalab-org/datalab): *datalab* itself, included here as a submodule.
- [datalab-industries/datalab-grafana-deployment](https://github.com/datalab-industries/datalab-grafana-deployment): Ansible deployment for the Grafana and Prometheus instance that collects metrics from *datalab* servers, used with [Monitoring](monitoring.md).

## Getting help

Chat with us on [Slack](https://join.slack.com/t/datalab-world/shared_invite/zt-2h58ev3pc-VV496~5je~QoT2TgFIwn4g) or raise an issue on [GitHub](https://github.com/datalab-industries/datalab-ansible-terraform/issues).
The main *datalab* documentation is at [docs.datalab-org.io](https://docs.datalab-org.io).
