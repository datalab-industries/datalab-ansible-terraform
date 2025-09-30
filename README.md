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
- running Ubuntu 22.04 or a similar distro with `apt` available.

It also assumes that your local machine is running a Unix-like OS (Linux, WSL, macOS) with `git` and `bash`,
`make` and `sed` available.

You can find more information on the requirements of the server and control node in the [Ansible documentation](https://docs.ansible.com/ansible/latest/getting_started/get_started_ansible.html).

The first step is to clone this repository (or your fork/templated version) with submodules and then install Ansible and its dependencies.
We recommend using [uv](https://astral.sh/uv) for this, as the included [Makefile] will use it to run the playbooks in a virtual
environment.

```shell
git clone --recurse-submodules git@github.com:datalab-org/datalab-ansible-terraform
cd datalab-ansible-terraform
uv venv --python 3.12
uv pip install -r requirements.txt
```

or alternatively,

```shell
git clone --recurse-submodules git@github.com:datalab-org/datalab-ansible-terraform
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
      mount_data_disk: <disk device file location, e.g., /dev/sda, /dev/sdb or otherwise or a full fstab configuration, e.g., `UUID=aaaa-bbbb-ccc>
      data_disk_type: <the fstype of the data disk, defaults to 'xfs'
      borg_encryption_passphrase: <the passphrase for the borg encryption>
      borg_remote_path: <the command to run borg on the repository (e.g., borg1 vs borg2)>
      borg_repository: <the path to the borg repository, either local or remote>
      prometheus_remote_write_url: <your_prometheus_instance_url, e.g., https://grafana.datalab.industries/prometheus/api/v1/write>
      prometheus_user: <your_prometheus_username>
      prometheus_password: <your_prometheus_password>
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

The [`Makefile`] also contains a number of other useful commands, such as:

```shell
make vaults
```

to edit the encrypted vault files, and

```shell
make list
```

to list all of the available Ansible tags that can be run individually.

#### Bitwarden integration

Constantly entering the vault password for every attempted deployment can be a
bit tedious, so by default, the `Makefile` will attempt to retrieve the vault
password from a local [Bitwarden CLI](https://bitwarden.com/help/cli/) installation,
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
[Prometheus](https://prometheus.io/) (with [Node Exporter](https://github.com/prometheus/node_exporter) and
[cAdvisor](https://github.com/google/cadvisor)) to monitor the host system and
containers.

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
