all:
	ansible-playbook -v -i inventory.yml --ask-vault-pass playbook.yml

deploy:
	ansible-playbook -v -i inventory.yml --ask-vault-pass playbook.yml --tags="deploy"

setup:
	ansible-playbook -v -i inventory.yml --ask-vault-pass playbook.yml --tags="setup"

maintenance:
	ansible-playbook -v -i inventory.yml --ask-vault-pass playbook.yml --tags="maintenance"

borg:
	ansible-playbook -v -i inventory.yml --ask-vault-pass playbook.yml --tags="borg"

ssl:
	ansible-playbook -v -i inventory.yml --ask-vault-pass playbook.yml --tags="ssl"
