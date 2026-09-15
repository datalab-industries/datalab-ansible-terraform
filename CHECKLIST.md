# Deployment checklist

This checklist belongs to your deployment.
It is not overwritten by `sync-ansible-upstream.sh`, so tick items off, remove those that do not apply and add your own.

Paths such as `docs/backups.md` refer to the template documentation.
For *datalab* settings, see the [*datalab* configuration docs](https://docs.datalab-org.io/en/stable/config/).

## Initial configuration

- [ ] Clone the repository with submodules and install Ansible (`docs/installation.md`).
- [ ] Pin `src/datalab` to the desired *datalab* release.
- [ ] Fill in `ansible/inventory.yml` with the host, `ansible_user`, `app_url` and `api_url`. If the API is under a root path (e.g., `example.org/api`), also set `ROOT_PATH` in `prod_config.json` (`docs/configuration.md`).
- [ ] Set `IDENTIFIER_PREFIX` in `ansible/vaults/datalab/prod_config.json`.
- [ ] Set `VUE_APP_API_URL` in `ansible/vaults/datalab/.env`.
- [ ] Set a long random `PYDATALAB_SECRET_KEY` in `ansible/vaults/datalab/.env_server`, e.g., from `openssl rand -hex 32`.
- [ ] Encrypt the inventory and vaults with `make encrypt-vaults`, and store the vault password safely.
- [ ] Optional: store the vault password in Bitwarden for use with `rbw` (`docs/bitwarden.md`).
- [ ] Point DNS for `app_url` (and `api_url`, if it is on a separate subdomain) at the server.

## First deployment

- [ ] Run `make` and check that it completes without errors.
- [ ] Open `app_url` in a browser and check that the app loads and can reach the API.

## Login and user accounts

Set up at least one login method.
See the [*datalab* login docs](https://docs.datalab-org.io/en/stable/config/#user-registration-authentication).

- [ ] GitHub: register an OAuth app with callback `<api_url>/login/github/authorized` and set `GITHUB_OAUTH_CLIENT_ID` and `GITHUB_OAUTH_CLIENT_SECRET` in `.env_server`. Optionally restrict sign-ups with `GITHUB_ORG_ALLOW_LIST`.
- [ ] ORCID: register for the ORCID public API and set `ORCID_OAUTH_CLIENT_ID` and `ORCID_OAUTH_CLIENT_SECRET` in `.env_server`.
- [ ] Email magic links (requires SMTP, see below).
- [ ] Run `make deploy` after changing any login settings.

### SMTP for email login

- [ ] Get SMTP credentials from your institution or a provider such as [resend](https://resend.com/), and verify the sender domain.
- [ ] Add the SMTP settings to `prod_config.json`:
  ```json
  "EMAIL_AUTH_SMTP_SETTINGS": {
      "MAIL_SERVER": "smtp.example.com",
      "MAIL_PORT": 587,
      "MAIL_USERNAME": "<username>",
      "MAIL_USE_TLS": true,
      "MAIL_DEFAULT_SENDER": "datalab@example.com"
  }
  ```
- [ ] Add `MAIL_PASSWORD=<password>` to `.env_server`.
- [ ] Optional: restrict sign-ups by domain with `EMAIL_DOMAIN_ALLOW_LIST` in `prod_config.json`.
- [ ] Run `make deploy` and test by signing in with an email address.

### First admin account

- [ ] Register the first user account through the web app.
- [ ] Make that user an admin by running the following on the server, using the display name shown in the app:
  ```shell
  cd ~/datalab
  docker compose exec api /opt/.venv/bin/python -m invoke admin.change-user-role --display-name "<display name>" --role admin
  ```
  See the [*datalab* administration docs](https://docs.datalab-org.io/en/stable/deployment/#general-server-administration) for other admin tasks.
- [ ] Log out and back in, then check that admin features are available.

## Backups

- [ ] Choose a remote Borg host, ideally separate from the *datalab* server (`docs/backups.md`).
- [ ] Create an SSH key pair, add the public key to the Borg host, and save the private key as `ansible/vaults/borg/.ssh/id_ed25519` (encrypted).
- [ ] Optional: add an encrypted `known_hosts` and `config` to `ansible/vaults/borg/.ssh`.
- [ ] Set `borg_repository`, `borg_remote_path` and `borg_encryption_passphrase` in the inventory.
- [ ] Store the Borg passphrase outside this repository, e.g., in a password manager.
- [ ] Run `make borg`.
- [ ] After the first scheduled run (overnight), check that an archive exists, e.g., with `borg list` against the repository or in the monitoring metrics.
- [ ] Test a restore to a separate location.

## Monitoring

- [ ] Set up uptime monitoring, e.g., with [Upptime](https://github.com/upptime/upptime) (`docs/monitoring.md`).
- [ ] Get access to a Prometheus/Grafana instance that accepts remote writes.
- [ ] Set `datalab_prefix`, `prometheus_remote_write_url`, `prometheus_user` and `prometheus_password` in the inventory.
- [ ] Run `make monitoring` and check that metrics appear in Grafana.
- [ ] Set up alerts for disk space, container health and failed backups.

## Optional

- [ ] Customise branding (`VUE_APP_LOGO_URL`, `VUE_APP_WEBSITE_TITLE`, `VUE_APP_HOMEPAGE_URL`) in `.env`.
- [ ] Install plugins (`docs/plugins.md`).
- [ ] Add extra services (`docs/extras.md`).
- [ ] Configure remote filesystems with `REMOTE_FILESYSTEMS` and SSH keys in `ansible/vaults/datalab/.ssh`.

## Ongoing maintenance

- [ ] Run `make maintenance` regularly to update system packages.
- [ ] Update *datalab* after reading the release notes and checking backups (`docs/deployment.md`).
- [ ] Sync with the upstream template with `./sync-ansible-upstream.sh`.
- [ ] Record changes and incidents in `deployment-notes/`.
