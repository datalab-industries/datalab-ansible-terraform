# <div align="center">Deploying <i>datalab</i></div>

<div align="center">
<a href="https://github.com/the-grey-group/datalab#MIT-1-ov-file"><img src="https://badgen.net/github/license/the-grey-group/datalab?icon=license&color=purple"></a>
<a href="https://the-datalab.readthedocs.io/en/latest/?badge=latest"><img src="https://img.shields.io/readthedocs/the-datalab?logo=readthedocs"></a>
</div>

<div align="center">
<a href="https://join.slack.com/t/datalab-world/shared_invite/zt-2h58ev3pc-VV496~5je~QoT2TgFIwn4g"><img src="https://img.shields.io/badge/Slack-chat_with_us-yellow?logo=slack"></a>
</div>

This repository contains tools and rules for automatically deploying datalab instances using Terraform/OpenTofu and Ansible.
It can be used as a template for deploying your own datalab instance, and optionally periodically resynced on new releases.

Use of Terraform/OpenTofu for cloud provisioning is OPTIONAL; the Ansible playbooks are sufficient to set up a datalab instance on a existing hardware.
The Ansible playbooks can even be used to deploy datalab on shared hardware; all mandatory services will be deployed within containers, so it is possible to set up the full NGINX + datalab stack alongside an existing reverse proxy managing other services, although this will need to be configured by the user.

Ideally, various aspects of the configuration will be transferrable, and thus only instance-specific configuration will need to be provided (e.g., usernames, domain names), in which case your instance version of this repository can be kept fairly in-sync with the main branch (which will continue to be updated as datalab's requirements grow and change).

Attempts will be made to tabulate the supported versions of datalab with each release of from this repository.

## Supported versions

<div align="center">

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

</div>

## Changelog

The changelog for this repository can be found in the [release notes](https://github.com/datalab-industries/datalab-ansible-terraform/releases) on GitHub.

## Overview

### Cloud provisioning with Terraform/OpenTofu

The `./terraform` directory contains Terraform/OpenTofu plans for provisioning cloud hardware (VMs, storage etc.) for use with datalab.

Implemented providers:

- Azure

Planned providers:

- OpenStack
- Hetzner

### Infrastructure automation with Ansible

The `./ansible` directory contains Ansible "playbooks" for taking a fresh VM and installing, configuring, launching, re-launching and managing datalab and NGINX containers.

Stack:

- NGINX
- Docker Compose for API, app and database containers
- Simple filesystem for filestore

### *datalab* versioning

The Ansible playbooks will deploy the datalab version that is included as a `git
submodule` to this repository.
It is highly recommended to only run the Ansible playbook from a clean
repository state (i.e., no uncommited changes) to ensure reproducibility.

## Usage

### Ansible automation

#### First-time setup

These instructions assume you have prepared the server on which you would like
to deploy *datalab*, and that it is:

- accessible via SSH (using your local SSH config),
- running one of the supported Linux distributions, e.g., Ubuntu 24.04 (see [Supported distributions](#supported-distributions)),

It also assumes that your local machine is running a Unix-like OS (Linux, WSL, macOS) with `git` and `bash`,
`make` and `sed` available.

You can find more information on the requirements of the server and control node in the [Ansible documentation](https://docs.ansible.com/ansible/latest/getting_started/get_started_ansible.html).

The first step is to clone this repository (or your fork/templated version) with submodules and then install Ansible and its dependencies.
We recommend using [uv](https://astral.sh/uv) for this, as the included [`Makefile`](Makefile) will use it to run the playbooks in a virtual
environment.

```shell
git clone git@github.com:datalab-industries/datalab-ansible-terraform
git submodule init
git submodule update
cd datalab-ansible-terraform
uv venv --python 3.12
uv pip install -r requirements.txt
uv run ansible-galaxy collection install -r ansible/requirements.yml
```

or alternatively,

```shell
git clone git@github.com:datalab-industries/datalab-ansible-terraform
git submodule init
git submodule update
cd datalab-ansible-terraform
make install-ansible
```

You can then navigate to the to the `./ansible` directory to begin configuring
your deployment.

There are two main sources of configuration:

1. The Ansible inventory, which tells Ansible which hosts to deloy to,
2. *datalab* configuration files.

To create the Ansible inventory ([full
documentation](https://docs.ansible.com/ansible/latest/inventory_guide/intro_inventory.html)), you need to edit the YML file
called `inventory.yml` in the `./ansible` directory:

```yaml
ungrouped:
  hosts:
    <hostname>:
      ansible_become_method: sudo
      ansible_user: <remote_username>
      api_url: <desired_datalab_api_url>
      app_url: <desired_datalab_app_url>
      # Additional optional settings:
      ansible_become_password: <remote_user_password> # (If needed for non-root user)
      mount_data_disk: <disk device file location, e.g., /dev/sda, /dev/sdb or otherwise or a full fstab configuration, e.g., `UUID=aaaa-bbbb-ccc>
      data_disk_type: <the fstype of the data disk, defaults to 'xfs'
      borg_encryption_passphrase: <the passphrase for the borg encryption>
      borg_remote_path: <the command to run borg on the repository (e.g., borg1 vs borg2)>
      borg_repository: <the path to the borg repository, either local or remote>
      prometheus_remote_write_url: <your_prometheus_instance_url, e.g., https://grafana.datalab.industries/prometheus/api/v1/write>
      prometheus_user: <your_prometheus_username>
      prometheus_password: <your_prometheus_password>
      manage_system: <whether to install system packages and docker, defaults to true (see "Rootless docker and externally managed hosts" below)>
      docker_rootless: <whether to use a rootless docker daemon, defaults to false>
      docker_user: <the user that runs docker commands, defaults to ansible_user>
      extras:   # (See discussion "Running additional containers" below)
        <service_name>:
          url: <service_url>
          port: <service_port>
```

where `<hostname>` and the various setting should be configured with your chosen
values.

Next, we can edit the config files in the `./vaults/datalab` directory.
See the [online documentation](https://the-datalab.readthedocs.io/en/stable/config/) for an
explanation of each of the settings.
These files contain the desired *datalab* settings:

1. `./vaults/datalab/prod_config.json`: the *datalab* Python config file.
2. `./vaults/datalab/.env_server`: the secrets required by the server as an env
   file (e.g., keys to external integration with GitHub, ORCID).
3. `./vaults/datalab/.env`: any variables required by the web app.
4. `./vaults/datalab/.ssh` (OPTIONAL): any SSH keys and config required to be mounted into the server container. These files should each be individually encrypted.
5. `./vaults/borg/.ssh` (OPTIONAL): any SSH keys or known hosts required to configure the borg backup system. These files should be individually encrypted.

It is recommended that you version control these files **with encryption** and commit it to your
fork.
To encrypt them, you can run

```shell
ansible-vault encrypt inventory.yml vaults/datalab/prod_config.json vaults/datalab/.env vaults/datalab/.env_server vaults/datalab/.ssh/* vaults/borg/.ssh/*
```

or simply

```shell
make encrypt-vaults
```

and provide a password when prompted (which will then need to be kept safe and
used every time the Ansible playbook is run).
You should never commit these files directly without encryption, even to a
private git repository.

If you are using your own domain (configured via `app_url` and `api_url` in the inventory),
then you will need to update your domain's DNS settings so that your subdomains point to the IP
of the server as given in your inventory file.

The API can either be served from its own subdomain (e.g. `app_url: example.org` with
`api_url: api.example.org`), or mounted under a root path on the
same host as the app (e.g. `api_url: example.org/api`).
In the latter case, only one certificate name is requested, and nginx serves the API as a
sublocation of the app's server block rather than as a separate server.
The root path is proxied through untouched, so the API must be told to serve its own
routes under it: set `ROOT_PATH` in `./vaults/datalab/prod_config.json` to the matching
path (e.g. `/api`), and `VUE_APP_API_URL` in `./vaults/datalab/.env` to the full URL.

Once all these configuration steps have been performed, we can try to execute
the Ansible "playbook" that will install all the pre-requisite services, build
the Docker containers as configured, connect them via Nginx and add hardening
services such as fail2ban to the server.

This is achieved by running:

```shell
ansible-playbook --ask-vault-pass -i inventory.yml playbook.yml
```

or simply

```
make
```

If completed successfully, the server should now be running a *datalab* instance at your configured URLs!

#### Supported distributions

The Ansible playbooks have been tested on Ubuntu (22.04, 24.04) and Red Hat Enterprise Linux 9.7, and will likely work on any Debian-based distribution that uses `apt` and `systemd` with minor modifications.

As the *datalab* deployment itself is containerised, as long as Docker can be installed independently of the playbooks, then the deployment playbook should work on any distribution, but some features
will not be available (e.g., automatic mounting of data disks, fail2ban, etc.) if the underlying OS is not supported by the playbooks.

If you need to support for a specific Linux distribution, please raise an
issue on GitHub at [datalab-industries/datalab-ansible-terraform](https://github.com/datalab-industries/datalab-ansible-terraform/issues).
Official support will not be provided for Windows or macOS as target servers.

#### Rootless docker and externally managed hosts

By default, the playbook manages the whole server: it bootstraps the `ansible_user` as root,
installs system packages and Docker, and configures fail2ban and sshd.
On servers managed by someone else (e.g., a university IT service), you may not have root
access, and Docker may instead be provided as a [rootless daemon](https://docs.docker.com/engine/security/rootless/)
owned by a separate user.

Both cases can be configured in the inventory:

```yaml
manage_system: false      # assume system packages and docker are already installed
manage_nginx: false       # a reverse proxy and its certificates are managed elsewhere
docker_rootless: true     # use a rootless docker daemon...
docker_user: docker       # ...owned by this user, which ansible_user must be able to become
docker_shared_group: datalab  # a group containing both users, used to share synced files
# docker_host: unix:///run/user/<uid>/docker.sock  # (optional) defaults to the docker_user's rootless socket
```

With `manage_system: false`, the playbook skips bootstrapping, disk mounting, package installation,
fail2ban, sshd hardening and upgrades, and only checks that the configured Docker daemon is reachable
before deploying the *datalab* services.

With `manage_nginx: false`, no nginx or certbot containers are created and no certificate
renewal is scheduled. The app and API containers still publish their ports (8081 and 5001),
so an externally managed reverse proxy can be pointed at them; it is then responsible for TLS
and for the `app_url`/`api_url` routing that the bundled nginx config would otherwise handle.

With `docker_rootless: true`, all Docker commands (including scheduled cron jobs) are run as
`docker_user` against its daemon.
In this case, the server must already provide:

- a rootless daemon for `docker_user` that keeps running without a login session (i.e., with lingering enabled),
- the ability for `ansible_user` to become `docker_user` (e.g., via sudo), and for `docker_user` to use cron,
- read access for `docker_user` to the `ansible_user`'s home directory (via `docker_shared_group`),
- read and write access for `docker_user` to `/data`,
- permission to bind the ports used by nginx (80 and 443), e.g., via the `net.ipv4.ip_unprivileged_port_start` sysctl.

Borg configuration and metrics are stored in `docker_user`'s home directory, so that the backup
container can read and write them.
If the server already runs its own exporters on the monitoring ports, these can be changed with
`monitoring_node_exporter_port`, `monitoring_prometheus_port` and `monitoring_cadvisor_port`.

#### Keeping things up to date

To update the *datalab* version, you simply update the git submodule in
`src/datalab` and rerun the playbook. This can be pinned to your fork and accomodate any custom changes
you desire (though you may also need to test and maintain your own set of
ansible rules and configuration for this).

Once you have chosen the *datalab* version, it can be redployed with `make
deploy` or

```shell
ansible-playbook --ask-vault-pass -i inventory.yml playbook.yml --tags deploy
```

To update the ansible playbooks themselves with any changes from the upstream
repository, you can similarly maintain the submodule in
`src/datalab-ansible-terraform` and either manually sync changes across, or use
the helper script:

```shell
chmod u+x sync-ansible-upstream.sh && ./sync-ansible-upstream.sh
```

which will copy just the changed playbooks across, and commit them. You should
be careful to review these changes before committing them to your fork,
especially if you have made any custom changes to the playbooks.
Be sure to also commit the changes to your submodule so you know precisely which versions
of the playbooks are running.

The [`Makefile`](Makefile) also contains a number of other useful commands, such as:

```shell
make vaults
```

to edit the encrypted vault files, and

```shell
make list
```

to list all of the available Ansible tags that can be run individually.

#### Installing *datalab* plugins

*datalab* supports first-party and third-party plugins (custom data blocks, etc.) which extend the API server.
Plugins can be declared in a `plugins.toml` file at the root of the *datalab* repository (alongside `pydatalab/` and `webapp/`) and installed by the `invoke dev.install` task during the API image build; see the upstream [plugins documentation](https://docs.datalab-org.io/en/latest/plugins/) for the file format and the full description of the install procedure.

To install plugins on a server deployed with this repository:

1. Edit the `plugins.toml` at `./src/plugins.toml`.
   The Ansible role copies it into place on the remote so the Dockerfile picks it up at build time.
   Example:
   ```toml
   dependencies = [
       "datalab-app-plugin-insitu",
       "my-local-plugin",
   ]

   [tool.uv.sources]
   datalab-app-plugin-insitu = { git = "https://github.com/datalab-org/datalab-app-plugin-insitu.git", rev = "v0.4.1" }
   my-local-plugin = { path = "pydatalab/plugins/my-local-plugin" }
   ```
2. Any local or private plugins can be added as git submodules under `./src/plugins/<plugin-name>/`.
   These will be synced to the remote; the `plugins.toml` path should then refer to `pydatalab/plugins/<plugin-name>`, which is the corresponding path on the server.
3. Run `make deploy`.
   The API container is rebuilt with the plugins baked in.
   Removing `./src/plugins.toml` and redeploying reverts to the base (plugin-free) lockfile.

> [!WARNING]
> Plugins run with full API server privileges; only install plugins from sources you trust.

#### Bitwarden integration

Constantly entering the vault password for every attempted deployment can be a
bit tedious, so by default, the [`Makefile`](Makefile) will attempt to retrieve the vault
password from Bitwarden using the unofficial [rbw client](https://github.com/doy/rbw),
which either only requires you to enter your Bitwarden password once per
session, or can be configured to remain logged in.

To use this feature, you will need to store your vault password in Bitwarden
using the same name as the cloned repository as reported locally by

```shell
$ git remote get-url origin
git@github.com:datalab-org/datalab-demo-deployment
                           {^^^^^^^^^^^^^^^^^^^^^}
                               repository name
```

If you intially cloned this repo and then renamed it, you can update your local
version to use the same name using:

```shell
git remote set-url origin <my-git-repo-url>
```

You can also simply edit the `.vault-pass.sh` script to return your vault
password in another way if you prefer.

You may also need to set the script to be executable with

```shell
chmod u+x .vault-pass.sh
```

#### Backups

##### Native backups

By default, *datalab* will take native snapshot backups at a certain frequency
and save them into `/data/backups` on the server with the configured retention
rules (typically keeping 7 daily copies, 6 monthly and 4 yearly).
These backups can be synced with a remote system to avoid data loss in the event
of a hardware failure on your *datalab* server.

More information on backups can be found in the
[datalab documentation](https://docs.datalab-org.io/en/stable/deployment/#backups).

##### Borg backups (recommended)

This repository contains playbooks for automating much more robust backups
using [Borg](https://www.borgbackup.org/en/stable/) and
[borgmatic](https://torsion.org/borgmatic/).

These backups are encrypted, de-duplicated and compressed, requiring significantly
less space than the native backup option, and can be synced easily with remote
Borg instances over SSH.
By default, only `/data/files` is backed up from disk, alongside a dump of the
*datalab* MongoDB database made by borgmatic's database hook.
Other paths under `/data` (native snapshots in `/data/backups`, logs, and the
data directory of a rootless Docker daemon) are deliberately left out, as they
are either reproducible or covered elsewhere; set `borg_source_directories` in
your inventory to back up more.

You will need to have an appropriate remote server (ideally separate from the *datalab* server itself)
running Borg (we recommend [rsync.net](https://www.rsync.net/products/borg.html) which has excellent borg support).

To activate the Borg playbooks, you must first provide an encrypted SSH key pair for accessing
your remote Borg server in the `./vaults/borg/.ssh` directory.
It should be named `./vaults/borg/.ssh/id_ed25519` and contain the private key for
passwordless SSH connection to the remote Borg server configured in the
inventory.
Any other encrypted files in this `.ssh` vault will be mounted in the Borg
container during the backup procedure. You may wish to include an `.ssh/config`
to set up any extra settings (e.g., proxies, host checking), or an `.ssh/known_hosts` to enable strict host checking.

> If you are running a *datalab* instance yourself and are looking for a place
> for your encrypted Borg backups, feel free to reach out to us as we may have
> enough of an overhead to be a secondary backup host for you.

#### Server monitoring

One basic option for uptime monitoring is to use a free GitHub Actions based
service like [Upptime](https://github.com/upptime/upptime).
For example, this is used for simple services in the central *datalab* organisation at [datalab-org/datalab-org-status](https://github.com/datalab-org/datalab-org-status).

For more advanced monitoring, the Ansible playbooks contain a role tagged as
`monitoring`, which will install and configure metrics harvesters using
[Prometheus](https://prometheus.io/) (with [Node Exporter](https://github.com/prometheus/node_exporter)) to monitor the host system.
Per-container metrics from [cAdvisor](https://github.com/google/cadvisor) can also be enabled by setting
`monitoring_cadvisor: true`, though note that this uses noticeably more CPU.

To make use of this monitoring, you will need your own [Grafana instance](https://grafana.com/oss/grafana) (also running Prometheus as a harvester of the remote metrics) to visualise the metrics.

Alternatively, you can use a hosted Grafana service such as [Grafana Cloud](https://grafana.com/products/cloud/), or request to use our central
*datalab* Grafana instance by reaching out to us on Slack or over email.

This integration can be enabled by adding the following variables to your inventory:

```yaml
prometheus_remote_write_url: <your_prometheus_instance_url, e.g., https://grafana.datalab.industries/prometheus/api/v1/write>
prometheus_user: <your_prometheus_username>
prometheus_password: <your_prometheus_password>
```
and then running the playbook with the `monitoring` tag:

```shell
make monitoring
```

#### ChemInventory syncing

Items from a [ChemInventory](https://www.cheminventory.net/) inventory can be
periodically synced into *datalab* using the
[datalab-cheminventory-plugin](https://github.com/datalab-industries/datalab-cheminventory-plugin).
This is enabled by adding the following variables to your inventory:

```yaml
cheminventory_inventory_id: <your_cheminventory_inventory_id>
cheminventory_api_key: <your_cheminventory_api_key>
cheminventory_datalab_api_key: <a_datalab_api_key_for_the_sync>
cheminventory_cron_frequency: "44 * * * *"  # (optional) defaults to daily at 6:11am
```

The inventory ID is the numeric ID of the ChemInventory inventory to sync.
To find it, run the plugin's `status` command with your ChemInventory API key
(see the ChemInventory [API authentication docs](https://www.cheminventory.net/support/api/#apiauthentication)
for how to create one); no *datalab* connection is needed:

```shell
docker run --rm -e CHEMINVENTORY_API_KEY=<your_cheminventory_api_key> \
  ghcr.io/datalab-industries/datalab-cheminventory-plugin:latest \
  uv run datalab-cheminventory-sync status
```

This lists the key's default inventory and any other inventories it can
access, each with its ID in brackets, e.g., `Default inventory: My Lab (12345)`.

The sync targets the host's `api_url` by default (override with
`cheminventory_datalab_api_url`), and the plugin version can be set with
`cheminventory_image_version`.
The API keys are written to an env file readable only by the docker user,
rather than into the crontab, and the output of the latest sync is written to
`~/last_cheminventory_sync.txt`.
Then run the playbook with the `cheminventory` tag:

```shell
make cheminventory
```

#### Emails for failed cron jobs

The playbook schedules several cron jobs as the docker user (certificate
renewal, weekly snapshots, borg backups and ChemInventory syncing).
Each writes its output to `~/last_<job>.txt`, and only prints it if the job
fails, in which case cron emails it to the `MAILTO` address.
This can be enabled by adding the following variables to your inventory, e.g.,
for [Resend](https://resend.com/docs/send-with-smtp):

```yaml
cron_mailto: <the address to email failed cron jobs to>
cron_mail_from: <the sender address, on a domain verified with the SMTP provider>
cron_smtp_host: smtp.resend.com
cron_smtp_user: resend
cron_smtp_password: <your Resend API key>
cron_smtp_port: 587  # (optional) the default; STARTTLS, or implicit TLS for port 465
```

All of these (except `cron_smtp_port`) must be set together; setting only some
of them fails the playbook run.
Then run the playbook with the `cron_email` tag:

```shell
make cron_email
```

This installs [msmtp](https://marlam.de/msmtp/) as the system `sendmail` on Debian/Ubuntu,
configures it for the docker user, and sets `MAILTO` in their crontab.
A test email is sent whenever the SMTP settings or addresses change.
If the host already runs a mail server (e.g., postfix), or the system is not
managed by the playbook (`manage_system: false`), msmtp is not installed, and
the existing `sendmail` is used instead.

##### Alerting with PagerDuty (or similar)

Failures can also raise incidents in an alerting service that accepts inbound
email, such as [PagerDuty](https://support.pagerduty.com/main/docs/email-integration-guide).
Add an **Email** integration to a PagerDuty service, and add its address to
`cron_mailto` (multiple addresses can be comma-separated), e.g.,

```yaml
cron_mailto: "team@example.com,datalab-cron@yourorg.pagerduty.com"
```

The cron email subject names the host and job, so configure the integration to
open a new incident only if one is not already open for the same subject, to
avoid a new incident for each repeated failure.
Note that incidents are not resolved automatically when a job next succeeds,
and that the test email sent when the settings change will also raise an
incident.

#### Running additional containers

It is often the case that users wish to run additional services alongside *datalab* on the same server.
This can be achieved by populating the `./src/extras` directory with directories (ideally git submodules) containing containerised applications with their own `Dockerfile` (e.g., `./src/extras/service_A/Dockerfile`) and then a top-level `./src/extras/docker-compose.yml` file that configures all extras, e.g.,

```yaml
name: extras
services:
  service_A:
    build:
      context: service_A
    restart: unless-stopped
    ports:
      - "5002:5001"

networks:
  backend:
    driver: bridge
```

Currently it is recommended that the services expose a port rather than using Docker networking directly, but this constraint may be lifted in future.

The ansible role `./ansible/roles/extras` will build and launch these containers alongside the main *datalab* stack when the playbook is run with the `extras` tag.
Finally, the service needs to be listed in `./ansible/inventory.yml` in the `extras` section, so that NGINX can generate the correct reverse proxy rules, e.g.,

```yaml
  extras:
    service_A:
      url: service_A.example.com
      port: 5002
```

which will be mapped to the (abridged) NGINX config snippet:

```config
server {
  listen 443 ssl;

  # set the correct host(s) for your site
  server_name service_A.example.com;

  location / {
    proxy_pass http://localhost:5002;
  }

```


### Cloud provisioning

These instructions will use OpenTofu, an open source fork of Terraform.
You should install OpenTofu for your local machine by following the instructions in the [OpenTofu docs](https://opentofu.org/docs/intro/install/).
OpenTofu will let you authenticate your local machine with your cloud provider (with provider-specific instructions) and perform the kind of operations you would normally have to do in your cloud providers' dashboard.
Here, we use it to simply provision a Linux VM (of configurable size) and associated storage.

After installing OpenTofu, the first step is to run, from the base of this repository:

```shell
tofu -chdir=terraform init
```

This will initialise your local machine and guide you through any additional
steps (such as installing cloud provider APIs, authenticating against them, etc.).

The next step is to adjust any of the variables in `./terraform/azure/variables.tf` for your deployment, for example, the desired location of VMs, the usernames for any local accounts to be created on the VM.

As of writing, only Azure is supported as a cloud provider, but in the future we will aim to abstract these variables somewhat to enable other providers.
As such, you will need to have the [https://learn.microsoft.com/en-us/cli/azure/](Azure CLI) installed locally (and logged in, via `az login`).

The next step is to generate plan of your infrastructure, without actually
provisioninig the hardware.
This can be achieved with

```shell
tofu -chdir=terraform/azure plan -out main.tfplan
```

To now request the resources from the provider and initialise any VMs, we apply
the plan with:

```shell
tofu -chdir=terraform/azure apply main.tfplan
```

> [!WARNING]
> 🚨 This will start the billing process with your cloud provider! 🚨

Providing that the variables for the given cloud provider have been set correctly, this should launch a VM that has the correct SSH and networking config ready for datalab.
For example, using the Azure provider, you should now be able to locally query your instance with the `az` CLI, using info provided by OpenTofu.

```shell
resource_group_name=$(tofu -chdir=terraform/azure output -raw resource_group_name)
az vm list --resource-group $resource_group_name --query "[].{\"VM Name\":name}" -o table
```

You can destroy running resources by first, naturally, plotting their destruction:

```shell
tofu -chdir=terraform/azure plan -destroy -out main.destroy.tfplan
```

then applying it

```shell
tofu -chdir=terraform/azure apply main.destroy.tfplan
```

This will also destroy attached storage (rarely desirable), so care must be taken when executing this plan.
