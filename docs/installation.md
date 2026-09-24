---
title: Installation
---

# Installation

## Prerequisites

These instructions assume you have prepared the server on which you want to deploy *datalab*, and that it is:

- accessible via SSH (using your local SSH config),
- running one of the [supported distributions](#supported-distributions), e.g., Ubuntu 24.04.

They also assume that your local machine runs a Unix-like OS (Linux, WSL, macOS) with `git`, `bash`, `make` and `sed` available.

More information on the requirements for the server and control node is in the [Ansible documentation](https://docs.ansible.com/ansible/latest/getting_started/get_started_ansible.html).

## Supported distributions

The playbooks have been tested on Ubuntu (22.04, 24.04) and Red Hat Enterprise Linux 9.7.
They will likely work on any Debian-based distribution that uses `apt` and `systemd`, with minor changes.

The *datalab* deployment itself is containerised.
If Docker can be installed independently of the playbooks, the deployment should work on any distribution.
Some features will not be available if the OS is not supported by the playbooks (e.g., automatic mounting of data disks, fail2ban).
See [Rootless Docker and managed hosts](managed-hosts.md) for servers where you do not have root access, or where Docker runs as a rootless daemon.

If you need support for a specific Linux distribution, please raise an issue on [GitHub](https://github.com/datalab-industries/datalab-ansible-terraform/issues).
Windows and macOS are not supported as target servers.

## Installing Ansible

Clone this repository (or your fork or templated copy) with its submodules, then install Ansible and its dependencies.
We recommend [uv](https://astral.sh/uv) for this, as the [`Makefile`](https://github.com/datalab-industries/datalab-ansible-terraform/blob/main/Makefile) uses it to run the playbooks in a virtual environment.

```shell
git clone --recurse-submodules git@github.com:datalab-industries/datalab-ansible-terraform
cd datalab-ansible-terraform
make install-ansible
uv run ansible-galaxy collection install -r ansible/requirements.yml
```

`make install-ansible` is equivalent to:

```shell
uv venv --python 3.13
uv pip install -r requirements.txt
```

If you already cloned the repository without submodules, run:

```shell
git submodule update --init
```

Next, [configure your deployment](configuration.md).
