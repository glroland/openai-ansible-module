init:
	pip install ansible-core
	pip install openai
	pip install langchain
	pip install langchain-openai
	pip install langchain_community
	pip install unstructured

smokechat:
	ANSIBLE_LIBRARY=./library ansible -m openai-chat -a 'endpoint_url=http://127.0.0.1:8000/v1 model_name=models/merlinite-7b-lab-Q4_K_M.gguf user_content=Hello' localhost

smokesummarize:
	ANSIBLE_LIBRARY=./library ansible -m openai-summarize -a 'endpoint_url=http://127.0.0.1:8000/v1 model_name=models/merlinite-7b-lab-Q4_K_M.gguf dir_path=tests file_regex=*.txt' localhost

test:
	for testfile in ./tests/*.yml; do ANSIBLE_LIBRARY=./library ansible-playbook $$testfile; done
