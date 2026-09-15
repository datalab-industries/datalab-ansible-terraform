# Rootless Docker and externally managed hosts

By default, the playbook manages the whole server.
It bootstraps the `ansible_user` as root, installs system packages and Docker, and configures fail2ban and sshd.

On servers managed by someone else, such as a university IT service, you may not have root access.
Docker may also be provided as a [rootless daemon](https://docs.docker.com/engine/security/rootless/) owned by a separate user.
Both cases are configured in the inventory:

```yaml
manage_system: false          # assume system packages and docker are already installed
manage_nginx: false           # a reverse proxy and its certificates are managed elsewhere
docker_rootless: true         # use a rootless docker daemon...
docker_user: docker           # ...owned by this user, which ansible_user must be able to become
docker_shared_group: datalab  # a group containing both users, used to share synced files
# docker_host: unix:///run/user/<uid>/docker.sock  # optional; defaults to the docker_user's rootless socket
```

These settings are independent, so you can use any combination of them.

## `manage_system: false`

The playbook skips bootstrapping, disk mounting, package installation, fail2ban, sshd hardening and package upgrades.
It only checks that the configured Docker daemon is reachable, then deploys the *datalab* services.

Docker and the Python Docker SDK must already be installed on the server.

## `manage_nginx: false`

No NGINX or certbot containers are created, and no certificate renewal is scheduled.

The app and API containers still publish their ports (8081 and 5001), so an externally managed reverse proxy can be pointed at them.
That proxy is then responsible for TLS and for the `app_url` and `api_url` routing that the bundled NGINX config would otherwise handle.

## `docker_rootless: true`

All Docker commands, including scheduled cron jobs, run as `docker_user` against its daemon.
The server must already provide:

- a rootless daemon for `docker_user` that keeps running without a login session, i.e., with lingering enabled,
- the ability for `ansible_user` to become `docker_user`, e.g., via sudo, and for `docker_user` to use cron,
- read access for `docker_user` to the `ansible_user`'s home directory, via `docker_shared_group`,
- read and write access for `docker_user` to `/data`,
- permission to bind the ports used by NGINX (80 and 443), e.g., via the `net.ipv4.ip_unprivileged_port_start` sysctl.

Borg configuration and metrics are stored in the `docker_user`'s home directory, so that the backup container can read and write them.

## Other useful overrides

- `ansible_user_home_dir`: where the *datalab* repository, NGINX files and other deployment files are kept.
  It defaults to the `ansible_user`'s home directory.
  Override it for accounts whose home is elsewhere, such as a service account.
- `monitoring_node_exporter_port`, `monitoring_prometheus_port` and `monitoring_cadvisor_port`: change these if the server already runs its own exporters on those ports (see [Monitoring](monitoring.md)).
