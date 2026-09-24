# <div align="center">Deploying <i>datalab</i></div>

<div align="center">
<a href="https://github.com/the-grey-group/datalab#MIT-1-ov-file"><img src="https://badgen.net/github/license/the-grey-group/datalab?icon=license&color=purple"></a>
<a href="https://the-datalab.readthedocs.io/en/latest/?badge=latest"><img src="https://img.shields.io/readthedocs/the-datalab?logo=readthedocs"></a>
<a href="https://join.slack.com/t/datalab-world/shared_invite/zt-2h58ev3pc-VV496~5je~QoT2TgFIwn4g"><img src="https://img.shields.io/badge/Slack-chat_with_us-yellow?logo=slack"></a>
</div>

Ansible playbooks for deploying [*datalab*](https://github.com/datalab-org/datalab) instances.
Use this repository as a template for your own deployment and resync it when new versions are released.

## Quick start

```shell
git clone --recurse-submodules git@github.com:datalab-industries/datalab-ansible-terraform
cd datalab-ansible-terraform
make quickstart
# edit ansible/inventory.yml and ansible/vaults/datalab/*
make encrypt-vaults
make
```

## Documentation

- [`docs/`](docs/index.md): template documentation, published at [datalab-industries.github.io/datalab-ansible-terraform](https://datalab-industries.github.io/datalab-ansible-terraform/). Preview it locally with `make docs`.
- [`CHECKLIST.md`](CHECKLIST.md): setup and maintenance tasks for your deployment, published with the docs.
- [`deployment-notes/`](deployment-notes/index.md): Markdown notes for your deployment, kept out of the published site.

`README.md` and `docs/` are overwritten by `sync-ansible-upstream.sh`.
`deployment-notes/` is never touched, and new upstream items in `CHECKLIST.md` are merged into your copy.

The Terraform/OpenTofu plans in `./terraform` are no longer actively supported (see [docs/terraform.md](docs/terraform.md)).

The changelog is in the [release notes](https://github.com/datalab-industries/datalab-ansible-terraform/releases).
