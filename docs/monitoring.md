---
title: Monitoring
---

# Monitoring

## Uptime monitoring

A simple option for uptime monitoring is a free GitHub Actions based service such as [Upptime](https://github.com/upptime/upptime).
For example, the central *datalab* organisation uses it at [datalab-org/datalab-org-status](https://github.com/datalab-org/datalab-org-status).

## Server metrics

The playbook contains a role tagged `monitoring`.
It installs and configures [Prometheus](https://prometheus.io/), with [Node Exporter](https://github.com/prometheus/node_exporter), to collect metrics from the host system.
If [Borg backups](backups.md) are enabled, their status is also reported.

Per-container metrics from [cAdvisor](https://github.com/google/cadvisor) can be enabled by setting `monitoring_cadvisor: true` in the inventory.
It uses noticeably more CPU than the other exporters, so it is off by default.
When it is off, any existing cAdvisor container is removed.

If the server already runs its own exporters on the default ports, change them with `monitoring_node_exporter_port` (9100), `monitoring_prometheus_port` (9090) and `monitoring_cadvisor_port` (8080).

The local Prometheus sends metrics to a remote Prometheus server.
To view them, you need one of the following:

- your own [Grafana instance](https://grafana.com/oss/grafana) with Prometheus accepting remote writes, which can be deployed with [datalab-industries/datalab-grafana-deployment](https://github.com/datalab-industries/datalab-grafana-deployment),
- a hosted service such as [Grafana Cloud](https://grafana.com/products/cloud/),
- access to the central *datalab* Grafana instance. Ask us on Slack or by email.

The central instance is itself deployed from [datalab-industries/datalab-grafana-deployment](https://github.com/datalab-industries/datalab-grafana-deployment), which is a sibling of this repository and follows the same Ansible approach.

To enable monitoring, add the following to your inventory:

```yaml
datalab_prefix: <label for this instance>
prometheus_remote_write_url: <e.g., https://grafana.datalab.industries/prometheus/api/v1/write>
prometheus_user: <your_prometheus_username>
prometheus_password: <your_prometheus_password>
```

Then run the playbook with the `monitoring` tag:

```shell
make monitoring
```

The role is skipped unless all three `prometheus_*` settings are present.
