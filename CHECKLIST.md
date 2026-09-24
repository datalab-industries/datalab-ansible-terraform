# Deployment checklist

This checklist belongs to your deployment.
Tick items off as you complete them, remove the ones that do not apply, and add your own.

`sync-ansible-upstream.sh` never overwrites it. It merges in any items added upstream, keeping your edits, and tells you if it could not merge them cleanly.

Sections without a label are required for a working instance.
Sections marked **(optional)** can be skipped, and items marked **Optional:** can be skipped within a required section.

Paths such as `docs/backups.md` refer to the template documentation.
For *datalab* settings, see the [*datalab* configuration docs](https://docs.datalab-org.io/en/stable/config/).

## Initial configuration

- [ ] Clone the repository with submodules and install Ansible (`docs/installation.md`).
- [ ] Pin `src/datalab` to the desired *datalab* release.
- [ ] Copy `ansible/inventory.example.yml` to `ansible/inventory.yml` and fill in the host, `ansible_user`, `app_url` and `api_url` (`docs/configuration.md`).
- [ ] **Optional:** if the API is under a root path on the app's host (e.g., `example.org/api`), set `ROOT_PATH` in `prod_config.json`.
- [ ] **Optional:** if you do not have root access or use rootless Docker, set the `manage_*` and `docker_*` settings (`docs/managed-hosts.md`).
- [ ] Set `IDENTIFIER_PREFIX` in `ansible/vaults/datalab/prod_config.json`.
- [ ] Set `VUE_APP_API_URL` in `ansible/vaults/datalab/.env`.
- [ ] Set a long random `PYDATALAB_SECRET_KEY` in `ansible/vaults/datalab/.env_server`, e.g., from `openssl rand -hex 32`.
- [ ] Encrypt the inventory and vaults with `make encrypt-vaults`, and store the vault password safely.
- [ ] **Optional:** store the vault password in Bitwarden for use with `rbw` (`docs/bitwarden.md`).
- [ ] Point DNS for `app_url` (and `api_url`, if it is on a separate subdomain) at the server.

## First deployment

- [ ] Run `make` and check that it completes without errors.
- [ ] Open `app_url` in a browser and check that the app loads and can reach the API.

## Login and user accounts

Set up **at least one** login method.
See the [*datalab* login docs](https://docs.datalab-org.io/en/stable/config/#user-registration-authentication).

- [ ] GitHub: register an OAuth app with callback `<api_url>/login/github/authorized` and set `GITHUB_OAUTH_CLIENT_ID` and `GITHUB_OAUTH_CLIENT_SECRET` in `.env_server`.
- [ ] **Optional:** restrict GitHub sign-ups with `GITHUB_ORG_ALLOW_LIST`.
- [ ] ORCID: register for the ORCID public API and set `ORCID_OAUTH_CLIENT_ID` and `ORCID_OAUTH_CLIENT_SECRET` in `.env_server`.
- [ ] Email magic links: set up SMTP (see below).
- [ ] Run `make deploy` after changing any login settings.

### SMTP for email login (optional)

Only needed for email login.

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
- [ ] **Optional:** restrict sign-ups by domain with `EMAIL_DOMAIN_ALLOW_LIST` in `prod_config.json`.
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

## Borg backups (optional, strongly recommended)

Without Borg, only *datalab*'s native snapshots are taken, and they are stored on the same server (`docs/backups.md`).

- [ ] Choose a remote Borg host, ideally separate from the *datalab* server.
- [ ] Create an SSH key pair, add the public key to the Borg host, and save the private key as `ansible/vaults/borg/.ssh/id_ed25519` (encrypted).
- [ ] **Optional:** add an encrypted `known_hosts` and `config` to `ansible/vaults/borg/.ssh`.
- [ ] Set `borg_repository`, `borg_remote_path` and `borg_encryption_passphrase` in the inventory.
- [ ] **Optional:** set `borg_source_directories` to back up more than `/data/files` and the database.
- [ ] Store the Borg passphrase outside this repository, e.g., in a password manager.
- [ ] Run `make borg`.
- [ ] After the first scheduled run (overnight), check that an archive exists, e.g., with `borg list` against the repository or in the monitoring metrics.
- [ ] Test a restore to a separate location.

## Monitoring (optional)

- [ ] Set up uptime monitoring, e.g., with [Upptime](https://github.com/upptime/upptime) (`docs/monitoring.md`).
- [ ] Get access to a Prometheus/Grafana instance that accepts remote writes, e.g. the central *datalab* one, or your own from [datalab-grafana-deployment](https://github.com/datalab-industries/datalab-grafana-deployment).
- [ ] Set `datalab_prefix`, `prometheus_remote_write_url`, `prometheus_user` and `prometheus_password` in the inventory.
- [ ] **Optional:** set `monitoring_cadvisor: true` for per-container metrics.
- [ ] Run `make monitoring` and check that metrics appear in Grafana.
- [ ] Set up alerts for disk space, container health and failed backups.

## Emails for failed cron jobs (optional)

- [ ] Get SMTP credentials and verify the sender domain. These can be the same as for email login (`docs/cron-email.md`).
- [ ] Set all of the `cron_*` settings in the inventory.
- [ ] **Optional:** add a PagerDuty (or similar) email address to `cron_mailto`.
- [ ] Run `make cron_email` and check that the test email arrives.

## Other features (optional)

- [ ] Customise branding (`VUE_APP_LOGO_URL`, `VUE_APP_WEBSITE_TITLE`, `VUE_APP_HOMEPAGE_URL`) in `.env`.
- [ ] Install plugins (`docs/plugins.md`).
- [ ] Add extra services (`docs/extras.md`).
- [ ] Sync a ChemInventory inventory into *datalab* with `make cheminventory` (`docs/cheminventory.md`).
- [ ] Configure remote filesystems with `REMOTE_FILESYSTEMS` and SSH keys in `ansible/vaults/datalab/.ssh`.

## Ongoing maintenance

- [ ] Run `make maintenance` regularly to update system packages.
- [ ] Update *datalab* after reading the release notes and checking backups (`docs/updating.md`).
- [ ] Sync with the upstream template with `./sync-ansible-upstream.sh`.
- [ ] Record changes and incidents in `deployment-notes/`.

## Your own items

Add anything specific to this deployment below, rather than in the sections above.
Upstream only adds items to its own sections, so keeping yours here means a sync can merge new items without a conflict.
