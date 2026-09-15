# Vault password with Bitwarden

Entering the vault password for every deployment is tedious.
If the unofficial Bitwarden client [rbw](https://github.com/doy/rbw) is installed, the `Makefile` will use it to fetch the vault password.
rbw only needs your Bitwarden password once per session, or can be configured to stay logged in.
If rbw is not installed, the `Makefile` asks for the vault password instead.

Store the vault password in Bitwarden with the same name as your repository, as reported by:

```shell
$ git remote get-url origin
git@github.com:datalab-org/datalab-demo-deployment
                           {^^^^^^^^^^^^^^^^^^^^^}
                               repository name
```

If you cloned the repository and then renamed it, update your local remote to match:

```shell
git remote set-url origin <my-git-repo-url>
```

You can also edit `.vault-pass.sh` to return the vault password in another way.
Note that `.vault-pass.sh` is overwritten by `sync-ansible-upstream.sh`.

The script must be executable:

```shell
chmod u+x .vault-pass.sh
```
