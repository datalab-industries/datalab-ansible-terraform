---
title: Cloud provisioning (legacy)
---

# Cloud provisioning (legacy)

!!! warning
    The Terraform/OpenTofu plans are no longer actively supported, and may not work with current provider versions.
    Provisioning the server by other means and running the Ansible playbooks against it is recommended.

The `./terraform` directory contains Terraform/OpenTofu plans that provision a Linux VM and its storage for *datalab*.
Only Azure is implemented.

## Usage

These steps use [OpenTofu](https://opentofu.org/), an open source fork of Terraform ([install instructions](https://opentofu.org/docs/intro/install/)), and the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/), logged in with `az login`.

1. Initialise OpenTofu from the root of the repository:
   ```shell
   tofu -chdir=terraform/azure init
   ```
   This prompts for any extra steps, such as installing provider plugins and authenticating.
2. Adjust the variables in `./terraform/azure/variables.tf`, e.g., the VM location and the usernames of local accounts on the VM.
3. Generate a plan without provisioning anything:
   ```shell
   tofu -chdir=terraform/azure plan -out main.tfplan
   ```
4. Apply the plan to create the resources and start the VM:
   ```shell
   tofu -chdir=terraform/azure apply main.tfplan
   ```

!!! danger
    Applying the plan starts billing with the cloud provider.

The result is a VM with SSH and networking ready for *datalab*.
To list it with the `az` CLI, using outputs from OpenTofu:

```shell
resource_group_name=$(tofu -chdir=terraform/azure output -raw resource_group_name)
az vm list --resource-group $resource_group_name --query "[].{\"VM Name\":name}" -o table
```

## Destroying resources

Plan the destruction:

```shell
tofu -chdir=terraform/azure plan -destroy -out main.destroy.tfplan
```

Then apply it:

```shell
tofu -chdir=terraform/azure apply main.destroy.tfplan
```

!!! danger
    This also destroys attached storage.
