---
title: Local patches
---

# Local patches to *datalab*

Small, deployment-specific changes to *datalab* that don't warrant a fork or a [plugin](plugins.md) can be kept as patch files in `./src/patches/datalab/`.

When deploying, any `*.patch` files there are applied, in filename order, to a temporary local copy of `./src/datalab`.
That copy is then synced to the server in its place, so the `./src/datalab` submodule itself is never modified.
If any patch does not apply cleanly (e.g., after updating the *datalab* submodule), the deployment fails before anything is synced, and the patch must be regenerated.
Running the playbook with `--check` also validates that the patches apply.

Without a `./src/patches/datalab/` directory, no patching is done and `./src/datalab` is synced as it is.
In both cases the *datalab* folder on the server is made to match what is synced, removing any other files (see [Updating *datalab*](updating.md#updating-datalab)).

## Creating a patch

Make your changes in `./src/datalab` and export them, including any new or binary files, with e.g.,

```shell
cd src/datalab
git add -N <any new files>
git diff --binary > ../patches/datalab/0001-my-change.patch
```

Commit the patch file to the deployment repository, and reset `./src/datalab` to leave the submodule clean.

## Applying patches locally

The helper script `apply-patches.sh` applies all patches to your local `./src/datalab`, e.g., to test or develop them.
Patches that are already applied are skipped, and `--revert` un-applies them in reverse order:

```shell
./apply-patches.sh            # apply
./apply-patches.sh --revert   # un-apply
```

Keep patches independent of each other, and squash any that modify the same lines.
Such a series applies to a clean checkout, but `apply-patches.sh` cannot detect it as already applied, so re-running it on a patched `./src/datalab` will fail.

The *datalab* folder on the server is synced to match the patched copy exactly, so files that a patch adds are removed from the server when the patch is removed, and files that a patch deletes are removed from the server too.
