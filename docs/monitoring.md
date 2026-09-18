# Monitoring

## Uptime monitoring

A simple option for uptime monitoring is a free GitHub Actions based service such as [Upptime](https://github.com/upptime/upptime).
For example, the central *datalab* organisation uses it at [datalab-org/datalab-org-status](https://github.com/datalab-org/datalab-org-status).

## Server metrics

The playbook contains a role tagged `monitoring`.
It installs and configures [Prometheus](https://prometheus.io/), with [Node Exporter](https://github.com/prometheus/node_exporter) and [cAdvisor](https://github.com/google/cadvisor), to collect metrics from the host system and containers.
If [Borg backups](backups.md) are enabled, their status is also reported.

The local Prometheus sends metrics to a remote Prometheus server.
To view them, you need one of the following:

- your own [Grafana instance](https://grafana.com/oss/grafana) with Prometheus accepting remote writes,
- a hosted service such as [Grafana Cloud](https://grafana.com/products/cloud/),
- access to the central *datalab* Grafana instance. Ask us on Slack or by email.

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
