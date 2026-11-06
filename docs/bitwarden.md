---
title: Vault password with Bitwarden
---

# Vault password with Bitwarden

If the unofficial Bitwarden client [rbw](https://github.com/doy/rbw) is installed, the `Makefile` uses it to fetch the vault password instead of prompting for it.
rbw asks for the Bitwarden password once per session, or can be configured to stay logged in.

Store the vault password in Bitwarden under the repository name, as reported by:

```shell
$ git remote get-url origin
git@github.com:datalab-org/datalab-demo-deployment
                           {^^^^^^^^^^^^^^^^^^^^^}
                               repository name
```

If the repository was renamed after cloning, update the remote to match:

```shell
git remote set-url origin <my-git-repo-url>
```

`.vault-pass.sh` can also be edited to fetch the password another way, but `sync-ansible-upstream.sh` overwrites it.

The script must be executable:

```shell
chmod u+x .vault-pass.sh
```
