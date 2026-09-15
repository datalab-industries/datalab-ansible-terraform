# Cloud provisioning (legacy)

!!! warning
    The Terraform/OpenTofu plans are no longer actively supported.
    They are kept for existing users but may not work with current provider versions.
    We recommend provisioning the server yourself and using the Ansible playbooks directly.

The `./terraform` directory contains Terraform/OpenTofu plans for provisioning cloud hardware (VMs, storage, etc.) for *datalab*.
Only Azure is implemented.

## Usage

These instructions use [OpenTofu](https://opentofu.org/), an open source fork of Terraform.
Install it by following the [OpenTofu docs](https://opentofu.org/docs/intro/install/).
OpenTofu authenticates your local machine with your cloud provider and performs operations you would otherwise do in the provider's dashboard.
Here, it provisions a Linux VM of configurable size and its storage.

You also need the [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/) installed and logged in (`az login`).

1. Initialise OpenTofu from the root of the repository:
   ```shell
   tofu -chdir=terraform/azure init
   ```
   This guides you through any extra steps, such as installing provider plugins and authenticating.
2. Adjust the variables in `./terraform/azure/variables.tf`, e.g., the VM location and the usernames of local accounts on the VM.
3. Generate a plan without provisioning any hardware:
   ```shell
   tofu -chdir=terraform/azure plan -out main.tfplan
   ```
4. Apply the plan to request the resources and start the VMs:
   ```shell
   tofu -chdir=terraform/azure apply main.tfplan
   ```

!!! danger
    Applying the plan starts billing with your cloud provider.

If the variables are set correctly, this launches a VM with SSH and networking ready for *datalab*.
You can query it with the `az` CLI using outputs from OpenTofu:

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
    This also destroys attached storage, which is rarely what you want.
