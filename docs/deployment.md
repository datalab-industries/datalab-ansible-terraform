---
title: Deploying
---

# Deploying

## DNS

Point the DNS records for `app_url`, and for `api_url` if it is a separate host, at the server's IP address.
Do this before the first deployment, as SSL certificates cannot be issued until DNS resolves.

## Running the playbook

Once the configuration is complete, run the full playbook from the root of the repository:

```shell
make
```

This is equivalent to:

```shell
uv run ansible-playbook --ask-vault-pass -i ansible/inventory.yml ansible/playbook.yml
```

The playbook installs all prerequisite services, builds the Docker containers, connects them via NGINX and adds hardening services such as fail2ban.
When it completes, *datalab* is running at the configured URLs.

## Running individual parts

Each part of the playbook has one or more tags.
To list them, run:

```shell
make list
```

To run only the tasks with a given tag, pass the tag to `make`, e.g.:

```shell
make deploy       # rebuild and relaunch datalab
make maintenance  # update system packages and renew nginx/SSL
make borg         # configure Borg backups
make monitoring   # configure Prometheus monitoring
```

After the first deployment, work through the [deployment checklist](checklist.md): logins, an admin account, backups and so on.

Later updates to *datalab* and the playbooks are covered in [Updating](updating.md).
