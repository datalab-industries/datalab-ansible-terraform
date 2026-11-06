---
title: Deploying datalab
hide:
  - toc
---

<div align="center" class="home-logo" markdown>
![datalab logo](assets/logo.svg#only-light){ width="160" }
![datalab logo](assets/logo-dark.svg#only-dark){ width="160" }
</div>

# Deploying *datalab* { .home-title }

Ansible playbooks for deploying *datalab* instances.
Each deployment is a copy of this template repository, resynced when new versions are released.

The playbooks set up *datalab* on existing hardware, including shared servers.
All services run in containers, so the NGINX and *datalab* stack can run alongside an existing reverse proxy for other services.

Most of the configuration is shared between instances.
A deployment only sets instance-specific values such as usernames and domain names, so it can stay in sync with the template as *datalab*'s requirements change.

<div class="grid cards home-cards" markdown>

-   :material-rocket-launch-outline:{ .lg .middle } __Deploying for the first time__

    ---

    Read in order: prerequisites, the inventory and vaults, then the playbook itself.

    [:material-arrow-right: &nbsp; getting-started](installation.md)

-   :material-server-outline:{ .lg .middle } __Running an instance__

    ---

    Updating *datalab*, the playbooks and the server, the tasks after a first deployment, and managing several deployments at once.

    [:material-arrow-right: &nbsp; updating](updating.md)

-   :material-puzzle-outline:{ .lg .middle } __Optional features__

    ---

    Backups, monitoring, cron emails, ChemInventory, plugins, extra containers, rootless Docker and Bitwarden.

    [:material-arrow-right: &nbsp; features](features.md)

-   :material-book-open-variant:{ .lg .middle } __Looking something up__

    ---

    Every variable the playbooks accept, and notes for a single deployment.

    [:material-arrow-right: &nbsp; reference](reference/index.md)

</div>

## What gets deployed

The playbooks in `./ansible` take a fresh VM and install, configure, launch and manage the *datalab* and NGINX containers:

- NGINX, with SSL certificates from certbot
- Docker Compose for the API, app and database containers
- A simple filesystem for the filestore
- Hardening services such as fail2ban and SSH configuration
- Optional: Borg backups, Prometheus monitoring, plugins and extra containers

## *datalab* versioning

The playbooks deploy the *datalab* version that is included as a git submodule at `src/datalab`.
Run the playbook only from a clean repository, with no uncommitted changes, so that deployments are reproducible.

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
| v0.9.x | v0.7.x |
| v0.10.x | v0.8.x-alpha.x |

## Changelog

See the [release notes](https://github.com/datalab-industries/datalab-ansible-terraform/releases) on GitHub.

## Related repositories

- [datalab-org/datalab](https://github.com/datalab-org/datalab): *datalab* itself, included here as a submodule.
- [datalab-industries/datalab-grafana-deployment](https://github.com/datalab-industries/datalab-grafana-deployment): Ansible deployment for the Grafana and Prometheus instance that collects metrics from *datalab* servers, used with [Monitoring](monitoring.md).

## Getting help

Ask on [Slack](https://join.slack.com/t/datalab-world/shared_invite/zt-2h58ev3pc-VV496~5je~QoT2TgFIwn4g) or raise an issue on [GitHub](https://github.com/datalab-industries/datalab-ansible-terraform/issues).
The main *datalab* documentation is at [docs.datalab-org.io](https://docs.datalab-org.io).
