---
title: Monitoring
---

# Monitoring

## Uptime monitoring

A simple option for uptime monitoring is a free GitHub Actions based service such as [Upptime](https://github.com/upptime/upptime).
For example, the central *datalab* organisation uses it at [datalab-org/datalab-org-status](https://github.com/datalab-org/datalab-org-status).

## Server metrics

The `monitoring` role installs [Prometheus](https://prometheus.io/) and [Node Exporter](https://github.com/prometheus/node_exporter) to collect metrics from the host.
If [Borg backups](backups.md) are enabled, their status is also reported.

Per-container metrics from [cAdvisor](https://github.com/google/cadvisor) can be enabled by setting `monitoring_cadvisor: true` in the inventory.
It uses noticeably more CPU than the other exporters, so it is off by default.
When it is off, any existing cAdvisor container is removed.

If the server already runs its own exporters on the default ports, change them with `monitoring_node_exporter_port` (9100), `monitoring_prometheus_port` (9090) and `monitoring_cadvisor_port` (8080).

The local Prometheus sends metrics to a remote Prometheus server, which can be:

- a self-hosted [Grafana instance](https://grafana.com/oss/grafana) with Prometheus accepting remote writes, which can be deployed with [datalab-industries/datalab-grafana-deployment](https://github.com/datalab-industries/datalab-grafana-deployment),
- a hosted service such as [Grafana Cloud](https://grafana.com/products/cloud/),
- access to the central *datalab* Grafana instance. Ask us on Slack or by email.

The central instance is itself deployed from [datalab-industries/datalab-grafana-deployment](https://github.com/datalab-industries/datalab-grafana-deployment), which is a sibling of this repository and follows the same Ansible approach.

To enable monitoring, add the following to the inventory:

```yaml
datalab_prefix: <label for this instance>
prometheus_remote_write_url: <e.g., https://grafana.datalab.industries/prometheus/api/v1/write>
prometheus_user: <prometheus_username>
prometheus_password: <prometheus_password>
```

Then run the playbook with the `monitoring` tag:

```shell
make monitoring
```

The role is skipped unless all three `prometheus_*` settings are present.

## Deployed versions

When monitoring is configured, each successful `make deploy` also exports the deployed versions through Node Exporter's textfile collector:

| Metric | Meaning |
| --- | --- |
| `datalab_deployment_info{version, ansible_version}` | The *datalab* version, and the version of these playbooks, that were last deployed |
| `datalab_last_deploy_timestamp_seconds` | When *datalab* was last deployed successfully |

## Automatic upgrade monitoring

On Ubuntu, the `maintenance` tasks schedule unattended upgrades for around 01:00, with any required reboot at 02:00 (see [Updating system packages and Docker](updating.md#updating-system-packages-and-docker)).
When monitoring is configured, an hourly `datalab-apt-metrics.timer` also exports these metrics through Node Exporter's textfile collector:

| Metric | Meaning |
| --- | --- |
| `apt_unattended_upgrade_last_success_timestamp_seconds` | Last time `unattended-upgrade` exited successfully (it also succeeds daily when there is nothing to do) |
| `apt_update_last_success_timestamp_seconds` | Last successful periodic `apt-get update` |
| `apt_upgrades_pending{type="security"\|"other"}` | Installed packages with an available upgrade |
| `apt_upgrades_held`, `apt_unattended_upgrade_kept_back` | Packages held with `apt-mark hold`, or kept back on the last run (e.g., by a conffile prompt) |
| `apt_dpkg_broken_packages`, `apt_cache_broken_dependencies` | Packages left half-installed by dpkg, or with unmet dependencies |
| `node_reboot_required`, `node_reboot_required_since_timestamp_seconds` | Whether (and since when) `/var/run/reboot-required` exists |
| `apt_metrics_collector_success`, `apt_metrics_last_run_timestamp_seconds` | Whether the metrics script itself ran cleanly, and when it last ran |

`apt-daily-upgrade.service` reports success even when the upgrade fails, so alert on the age of the success timestamp rather than on systemd unit state.
Suggested Grafana alert rules:

```promql
# Upgrades have not succeeded for over a day (one missed nightly run)
time() - apt_unattended_upgrade_last_success_timestamp_seconds > 36 * 3600
# Package lists have not refreshed
time() - apt_update_last_success_timestamp_seconds > 36 * 3600
# dpkg was interrupted or a package is broken; needs `dpkg --configure -a` by hand
apt_dpkg_broken_packages > 0 or apt_cache_broken_dependencies > 0
# Security updates are not being applied (pair with a `for: 2d` pending period)
apt_upgrades_pending{type="security"} > 0
# The 02:00 automatic reboot did not happen
node_reboot_required == 1 and time() - node_reboot_required_since_timestamp_seconds > 12 * 3600
# The exporter has stopped writing metrics
apt_metrics_collector_success == 0 or time() - apt_metrics_last_run_timestamp_seconds > 3 * 3600
```
