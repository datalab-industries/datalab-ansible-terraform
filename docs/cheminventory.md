---
title: ChemInventory syncing
---

# ChemInventory syncing

Items from a [ChemInventory](https://www.cheminventory.net/) inventory can be synced into *datalab* on a schedule, using the [datalab-cheminventory-plugin](https://github.com/datalab-industries/datalab-cheminventory-plugin).

## Setup

1. Create a ChemInventory API key (see the ChemInventory [API authentication docs](https://www.cheminventory.net/support/api/#apiauthentication)).
2. Find the numeric ID of the inventory to sync by running the plugin's `status` command.
   This only needs the ChemInventory API key, not a *datalab* connection:
   ```shell
   docker run --rm -e CHEMINVENTORY_API_KEY=<your_cheminventory_api_key> \
     ghcr.io/datalab-industries/datalab-cheminventory-plugin:latest \
     uv run datalab-cheminventory-sync status
   ```
   This lists the key's default inventory and any other inventories it can access, each with its ID in brackets, e.g., `Default inventory: My Lab (12345)`.
3. Create a *datalab* API key for the sync to use when writing items.
4. Add the settings to your inventory:
   ```yaml
   cheminventory_inventory_id: <your_cheminventory_inventory_id>
   cheminventory_api_key: <your_cheminventory_api_key>
   cheminventory_datalab_api_key: <a_datalab_api_key_for_the_sync>
   cheminventory_cron_frequency: "44 * * * *"  # optional; defaults to daily at 6:11am
   ```
5. Run the playbook with the `cheminventory` tag:
   ```shell
   make cheminventory
   ```

The role is skipped unless the three required settings are present.

## Details

- The sync targets the host's `api_url` by default.
  Override it with `cheminventory_datalab_api_url`.
- The plugin version is set with `cheminventory_image_version`.
- The API keys are written to an env file that only the docker user can read, rather than into the crontab.
- The output of the latest sync is written to `~/last_cheminventory_sync.txt` in the docker user's home directory.
- Failed syncs can be emailed to you (see [Emails for failed cron jobs](cron-email.md)).

A one-off import from a ChemInventory export is also possible without this role (see the [*datalab* administration docs](https://docs.datalab-org.io/en/stable/deployment/#importing-chemical-inventories)).
