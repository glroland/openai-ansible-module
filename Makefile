init:
	pip install ansible-core
	pip install openai

unittest:
	ANSIBLE_LIBRARY=./library ansible -m openai -a 'endpoint_url=http://127.0.0.1:8000/v1 model_name=models/merlinite-7b-lab-Q4_K_M.gguf' localhost

test:
	for testfile in ./tests/*.yml; do ANSIBLE_LIBRARY=./library ansible-playbook $$testfile; done
