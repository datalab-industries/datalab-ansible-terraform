---
title: Deploying
---

# Deploying

## DNS

If you use your own domain (set by `app_url` and `api_url` in the inventory), update your domain's DNS settings so that the app host, and the API host if it is separate, point to the IP of the server.
Do this before the first deployment, as the SSL certificates cannot be issued until DNS resolves correctly.

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
If it completes successfully, the server will be running *datalab* at your configured URLs.

See the [checklist](checklist.md) for common tasks after the first deployment, such as creating an admin account.

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

Once the instance is running, work through the [deployment checklist](checklist.md) for the tasks that follow a first deployment, such as setting up logins, an admin account and backups.

To update *datalab* or the playbooks later, see [Updating](updating.md).
