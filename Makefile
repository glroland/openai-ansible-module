init:
	pip install ansible-core
	pip install openai

test:
	ANSIBLE_LIBRARY=./library ansible -m openai -a 'name=hello new=true' localhost
