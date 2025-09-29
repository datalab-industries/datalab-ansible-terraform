# Makefile that passes the CLI args to ansible for the given playbook tags
BW_AVAILABLE = $(shell command -v bw 2> /dev/null)
VAULT_PASS_ARGS = $(if $(BW_AVAILABLE),--vault-password-file ./.vault-pass.sh, --ask-vault-pass)
PLAYBOOK_CMD = uv run ansible-playbook $(VAULT_PASS_ARGS) -i ansible/inventory.yml ansible/playbook.yml
VAULT_FILES := $(shell find ansible/vaults/ -type f);

# Extract tags directly from YAML (faster but less accurate)
VALID_TAGS := $(shell grep -r "tags:" ansible/playbook.yml | sed 's/.*tags://g' | tr -d '[]"' | tr ',' '\n' | tr -d ' ' | sort -u | grep -v '^$$')

all:
	$(PLAYBOOK_CMD)

list:
	uv run ansible-playbook --list-tags ansible/playbook.yml

inventory:
	uv run ansible-vault edit $(VAULT_PASS_ARGS) ansible/inventory.yml

install-ansible: requirements.txt
	uv venv --python=3.13; uv pip install -r requirements.txt

encrypt-vaults:
	@echo "Encrypting all vault files in ansible/vaults/ directory: $(VAULT_FILES)";
	uv run ansible-vault encrypt $(VAULT_FILES)

vaults:
	@echo "Select a vault file to edit:"; \
	select file in $$(find ansible/inventory.yml ansible/vaults/ -type f); do \
		if [ -n "$$file" ]; then \
			uv run ansible-vault edit $(VAULT_PASS_ARGS) "$$file"; \
			break; \
		fi; \
	done

%:
	@if echo "$(VALID_TAGS)" | grep -wq "$@"; then \
		echo "Running playbook with tag: $@"; \
		$(PLAYBOOK_CMD) --tags=$@; \
	else \
		echo "Error: '$@' is not a valid tag."; \
		echo "Valid tags are: $(VALID_TAGS)"; \
		exit 1; \
	fi


.PHONY: list
