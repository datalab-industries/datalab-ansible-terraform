---
title: Installation
---

# Installation

## Prerequisites

The server must:

- be reachable over SSH, using the local SSH config,
- run one of the [supported distributions](#supported-distributions), e.g., Ubuntu 24.04.

The local machine (the Ansible control node) needs a Unix-like OS (Linux, WSL or macOS) with `git`, `bash`, `make` and `sed`.

The [Ansible documentation](https://docs.ansible.com/ansible/latest/getting_started/get_started_ansible.html) has more on the requirements for both.

## Supported distributions

The playbooks are tested on Ubuntu 22.04 and 24.04, and on Red Hat Enterprise Linux 9.7.
Other Debian-based distributions that use `apt` and `systemd` should work with minor changes.

*datalab* itself runs in containers, so it can run on any distribution where Docker is installed separately (see [Rootless Docker and managed hosts](managed-hosts.md)).
Features that manage the OS, such as data disk mounting and fail2ban, are then unavailable.

Windows and macOS are not supported as servers.
To request support for another distribution, raise an issue on [GitHub](https://github.com/datalab-industries/datalab-ansible-terraform/issues).

## Installing Ansible

Clone the repository (or a fork or templated copy) with its submodules, then install Ansible.
The [`Makefile`](https://github.com/datalab-industries/datalab-ansible-terraform/blob/main/Makefile) uses [uv](https://astral.sh/uv) to run the playbooks in a virtual environment.

```shell
git clone --recurse-submodules git@github.com:datalab-industries/datalab-ansible-terraform
cd datalab-ansible-terraform
make quickstart
```

`make quickstart` creates the virtual environment, installs Ansible and its collections, and copies `ansible/inventory.example.yml` to `ansible/inventory.yml`.
It is equivalent to:

```shell
uv venv --python=3.13
uv pip install -r requirements.txt
uv run ansible-galaxy collection install -r ansible/requirements.yml
cp ansible/inventory.example.yml ansible/inventory.yml
```

It is safe to run again, as an existing inventory is never overwritten.
`make install-ansible` only does the install, without touching the inventory.

For a repository cloned without submodules, fetch them with:

```shell
git submodule update --init
```

Next, [configure the deployment](configuration.md).
