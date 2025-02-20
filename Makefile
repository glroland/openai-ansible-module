# Configuration
openai_endpoint ?= http://envision:11434/v1
openai_token ?= no-token-needed
openai_model ?= granite3.1-dense:8b

install:
	pip install -r requirements.txt

smoketest.chat:
	ANSIBLE_LIBRARY=./library ansible -m openai-chat -a 'endpoint_url=$(openai_endpoint) api_key=$(openai_token) model_name=$(openai_model) user_content=Hello' localhost

smoketest.summarize:
	ANSIBLE_LIBRARY=./library ansible -m openai-summarize -a 'endpoint_url=$(openai_endpoint) api_key=$(openai_token)  model_name=$(openai_model) dir_path=tests file_regex=*.txt' localhost

smoketest: smoketest.chat smoketest.summarize

test:
	for testfile in ./tests/*.yml; do ANSIBLE_LIBRARY=./library ansible-playbook -e 'config_openai_endpoint=$(openai_endpoint) config_openai_token=$(openai_token) config_openai_model=$(openai_model)' $$testfile; done
