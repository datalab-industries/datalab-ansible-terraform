---
title: Plugins
---

# Plugins

*datalab* supports first-party and third-party plugins (e.g., custom data blocks) that extend the API server.
Plugins are declared in a `plugins.toml` file at the root of the *datalab* repository (alongside `pydatalab/` and `webapp/`).
They are installed by the `invoke dev.install` task when the API image is built.
See the [*datalab* plugins documentation](https://docs.datalab-org.io/en/latest/plugins/) for the file format and install procedure.

!!! warning
    Plugins run with full API server privileges.
    Only install plugins from sources you trust.

To install plugins on a server deployed with this repository:

1. Edit `./src/plugins.toml`.
   The Ansible role copies it to the server so the Dockerfile uses it at build time.
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
2. Add any local or private plugins as git submodules under `./src/plugins/<plugin-name>/`.
   These are synced to the server.
   In `plugins.toml`, refer to them as `pydatalab/plugins/<plugin-name>`, which is their path on the server.
3. Run `make deploy`.
   The API container is rebuilt with the plugins installed.

To remove all plugins, delete `./src/plugins.toml` and redeploy.
This reverts to the base lockfile without plugins.
