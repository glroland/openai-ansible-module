install:
	pip install ansible-core
	pip install openai
	pip install langchain
	pip install langchain-openai
	pip install langchain_community
	pip install unstructured

smokechat:
	ANSIBLE_LIBRARY=./library ansible -m openai-chat -a 'endpoint_url=http://envision:11434/v1 model_name=granite3.1-dense:8b user_content=Hello' localhost

smokesummarize:
	ANSIBLE_LIBRARY=./library ansible -m openai-summarize -a 'endpoint_url=http://envision:11434/v1 model_name=granite3.1-dense:8b dir_path=tests file_regex=*.txt' localhost

test:
	for testfile in ./tests/*.yml; do ANSIBLE_LIBRARY=./library ansible-playbook $$testfile; done
