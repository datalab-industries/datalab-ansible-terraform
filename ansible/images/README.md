# Pinned container images

Each directory holds a Dockerfile with a single pinned `FROM` line for one of
the third-party images the roles run, so that dependabot can open PRs when a
new version is released.

The roles build these on the host with `tasks/build_local_image.yml`, tagged as
`datalab-<directory name>` (e.g., `datalab-node-exporter`), and run that local
image. To update an image by hand, change the tag in its Dockerfile and rerun
the relevant role.
