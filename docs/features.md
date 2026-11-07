---
title: Optional features
---

# Optional features

Each feature is optional and independent of the others.
Most are enabled by setting a few variables in the inventory and running the matching tag, at any point after the first deployment.

| Feature | What it does | Run with |
| --- | --- | --- |
| [Backups](backups.md) | Native *datalab* snapshots, plus encrypted off-site Borg backups | `make borg` |
| [Monitoring](monitoring.md) | Prometheus metrics for the server, backups, upgrades and deployed versions | `make monitoring` |
| [Emails for failed cron jobs](cron-email.md) | Mails the output of any scheduled job that fails | `make cron_email` |
| [ChemInventory syncing](cheminventory.md) | Syncs a ChemInventory inventory into *datalab* on a schedule | `make cheminventory` |
| [Plugins](plugins.md) | Extends the API server with custom data blocks | `make deploy` |
| [Local patches to *datalab*](patches.md) | Applies small patch files to *datalab* when deploying, without a fork | `make deploy` |
| [Additional containers](extras.md) | Runs extra services behind the same NGINX and certificates | `make extras` |
| [Rootless Docker and managed hosts](managed-hosts.md) | Deploys to servers where the system or Docker is managed by someone else | `make` |
| [Vault password with Bitwarden](bitwarden.md) | Fetches the vault password from Bitwarden instead of asking for it | (local only) |

Every variable these features accept is listed in the [variable reference](reference/index.md).
