# Deploying datalab

This repository contains tools and rules for automatically deploying datalab instances using Terraform/OpenTofu and Ansible.
It should be forked and used as a template for deploying your own datalab instance.
Use of Terraform for cloud provisioning is OPTIONAL; the Ansible playbooks are sufficient to set up a datalab instance on a existing hardware.
The Ansible playbooks can even be used to deploy datalab on shared hardware; all mandatory services will be deployed within containers, so it is possible to set up the full NGINX + datalab stack alongside an existing reverse proxy managing other services, although this will need to be configured by the user.

Ideally, various aspects of the configuration will be transferrable, and thus only instance-specific configuration will need to be provided (e.g., usernames, domain names), in which case your instance version of this repository can be kept fairly in-sync with the main branch (which will continue to be updated as datalab's requirements grow and change). 

Attempts will be made to tabulate the supported versions of datalab with each release of from this repository.

## Overview

### Cloud provisioning with Terraform/OpenTofu

The `./terraform` directory contains Terraform/OpenTofu plans for provisioning cloud hardware (VMs, storage etc.) for use with datalab.

Implemented providers:

- Azure

Planned providers:

- OpenStack

### Infrastructure automation with Ansible

The `./ansible` directory contains Ansible "playbooks" for taking a fresh VM and installing, configuring, launching, re-launching and managing datalab and NGINX containers.

Stack:

- NGINX
- Docker Compose for API, app and database containers
- Simple filesystem for filestore

### Datalab versioning

The Ansible playbooks will deploy the datalab version that is included as a `git
submodule` to this repository.
It is highly recommended to only run the Ansible playbook from a clean
repository state (i.e., no uncommited changes) to ensure reproducibility.

## Usage

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

The next step is to adjust any of the variables in `./terraform/variables.tf` for your deployment, for example, the desired location of VMs, the usernames for any local accounts to be created on the VM.

As of writing, only Azure is supported as a cloud provider, but in the future we will aim to abstract these variables somewhat to enable other providers.

The next step is to generate plan of your infrastructure, without actually
provisioninig the hardware.
This can be achieved with 

```shell
tofu -chdir=terraform plan -out main.tfplan
```

To now request the resources from the provider and initialise any VMs, we apply
the plan with:

```shell
tofu -chdir=terraform apply
```

> [!WARNING]
> 🚨 This will start the billing process with your cloud provider! 🚨

Providing that the variables for the given cloud provider have been set correctly, this should launch a VM that has the correct SSH and networking config ready for datalab.
For example, using the Azure provider, you should now be able to locally query your instance with the `az` CLI, using info provided by OpenTofu.

```shell
resource_group_name=$(tofu -chdir=terraform output -raw resource_group_name)
az vm list --resource-group $resource_group_name --query "[].{\"VM Name\":name}" -o table
```

You can destroy running resources by first, naturally, plotting their destruction:

```shell
tofu -chdir=terraform plan -destroy -out main.destroy.tfplan
```

then applying it

```shell
tofu -chdir=terraform apply main.destroy.tfplan
```

This will also destroy attached storage (rarely desirable), so care must be taken when executing this plan.
