# Makefile that passes the CLI args to ansible for the given playbook tags

SHELL := /bin/bash
RBW_AVAILABLE = $(shell command -v rbw 2> /dev/null)
VAULT_PASS_ARGS = $(if $(RBW_AVAILABLE),--vault-password-file ./.vault-pass.sh, --ask-vault-pass)
PLAYBOOK_CMD = uv run ansible-playbook $(VAULT_PASS_ARGS) -i ansible/inventory.yml ansible/playbook.yml
VAULT_FILES := $(shell find ansible/vaults/ -type f) ansible/inventory.yml

# Extract tags directly from YAML (faster but less accurate)
VALID_TAGS := $(shell grep -r "tags:" ansible/playbook.yml | sed 's/.*tags://g' | tr -d '[]"' | tr ',' '\n' | tr -d ' ' | sort -u | grep -v '^$$')

all: ansible/inventory.yml
	$(PLAYBOOK_CMD)

# Start a new deployment: install ansible, then create the inventory from the example
quickstart: install-ansible ansible/inventory.yml
	@echo
	@echo "Next steps:"
	@echo "  1. Edit ansible/inventory.yml: the host, ansible_user, app_url and api_url."
	@echo "  2. Edit the datalab config in ansible/vaults/datalab/."
	@echo "  3. Encrypt them with 'make encrypt-vaults'."
	@echo "  4. Deploy with 'make'."
	@echo "Full instructions: https://datalab-industries.github.io/datalab-ansible-terraform"

# Create the local inventory from the example the first time it is needed.
# Deliberately has no prerequisite: it must never overwrite an inventory that
# already exists, e.g. when a sync brings in a newer example.
ansible/inventory.yml:
	@cp ansible/inventory.example.yml $@
	@echo "Created $@ from ansible/inventory.example.yml. Edit it before deploying."

list:
	uv run ansible-playbook --list-tags ansible/playbook.yml

inventory: ansible/inventory.yml
	uv run ansible-vault edit $(VAULT_PASS_ARGS) ansible/inventory.yml

install-ansible: requirements.txt
	uv venv --python=3.13; uv pip install -r requirements.txt; uv run ansible-galaxy collection install -r ansible/requirements.yml

encrypt-vaults: ansible/inventory.yml
	@echo "Encrypting all vault files in ansible/vaults/ directory: $(VAULT_FILES)";
	uv run ansible-vault encrypt $(VAULT_FILES)

vaults: ansible/inventory.yml
	@echo "Select a vault file to edit:"; \
	select file in $$(find ansible/inventory.yml ansible/vaults/ -type f); do \
		if [ -n "$$file" ]; then \
			uv run ansible-vault edit $(VAULT_PASS_ARGS) "$$file"; \
			break; \
		fi; \
	done

# Generate the role reference pages from the roles' argument specs
docs-reference:
	uv run --quiet scripts/gen-role-docs.py

ZENSICAL = uvx zensical@0.0.62

docs: docs-reference
	$(ZENSICAL) serve

docs-build: docs-reference
	$(ZENSICAL) build --clean

# The catch-all must not take prerequisites, or make applies it to the Makefile
# itself, so the inventory is created from inside the recipe instead.
%:
	@if echo "$(VALID_TAGS)" | grep -wq "$@"; then \
		$(MAKE) --no-print-directory ansible/inventory.yml; \
		echo "Running playbook with tag: $@"; \
		$(PLAYBOOK_CMD) --tags=$@; \
	else \
		echo "Error: '$@' is not a valid tag."; \
		echo "Valid tags are: $(VALID_TAGS)"; \
		exit 1; \
	fi


.PHONY: all quickstart list inventory install-ansible encrypt-vaults vaults docs docs-reference docs-build
