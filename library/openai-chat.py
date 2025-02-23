#!/usr/bin/python

# Copyright: (c) 2024, Lee Roland <glroland@hotmail.com>
# Apache License Version 2.0, January 2004 (http://www.apache.org/licenses/)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: openai-chat

short_description: Ansible module to interface with OpenAI compliant APIs for Chat Completion

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This is an Ansible module used to interface with OpenAI compliant APIs from Ansible playbooks for Chat Completion.

options:
    endpoint_url:
        description: OpenAI Endpoint URL (i.e. http://127.0.0.1:8000/v1)
        required: true
        type: str
    model_name:
        description: OpenAI Model Name (must match server expectations)
        required: true
        type: str
    user_content:
        description: User Content Message (i.e. Your prompt)
        required: true
        type: str
    system_content:
        description: System Content Message (i.e. Server context to consider when generating response to prompt)
        required: false
        type: str
    api_key:
        description: OpenAI API Key
        required: false
        type: str
    timeout:
        description: Override connection timeout
        required: false
        type: int
    tls_insecure:
        description: Flag indicating whether to require TLS verification
        required: false
        type: str
    tls_client_cert:
        description: TLS Client Certificate file path
        required: false
        type: str
    tls_client_key:
        description: TLS Client Certificate Key
        required: false
        type: str
    tls_client_passwd:
        description: TLS Client Certificate Password
        required: false
        type: str
    temperature:
        description: Temperature
        required: false
        type: float
    max_tokens:
        description: Maximum Number of Tokens
        required: false
        type: int
    top_p:
        description: Top P
        required: false
        type: int
    frequency_penalty:
        description: Frequency Penalty
        required: false
        type: int
    presence_penalty:
        description: Presence Penalty
        required: false
        type: int
    tool_modules:
        description: Comma separated list of Python modules containing tools to load
        required: false
        type: str
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Lee Roland (@glroland)
'''

EXAMPLES = r'''
# Pass in a message
  - name: Run OpenAI Chat Module
    openai-chat:
      endpoint_url: 'http://127.0.0.1:8000/v1'
      model_name: 'models/merlinite-7b-lab-Q4_K_M.gguf'
      user_content: 'Hello AI Platform!  How are you today?'

'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
'''

from ansible.module_utils.basic import AnsibleModule
import openai
from openai import OpenAI
import httpx
import importlib.util
import sys
import json

def dynamically_load_python_module(file_path, module_name=None):
    if module_name is None:
        module_name = "my_module"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        endpoint_url=dict(type='str', required=True),
        model_name=dict(type='str', required=True),
        user_content=dict(type='str', required=True),
        system_content=dict(type='str', required=False, default=None),
        api_key=dict(type='str', required=False, default='api_key'),
        timeout=dict(type='int', required=False, default=30),
        tls_insecure=dict(type='bool', required=False, default=False),
        tls_client_cert=dict(type='str', required=False, default=None),
        tls_client_key=dict(type='str', required=False, default=None),
        tls_client_passwd=dict(type='str', required=False, default=None, no_log=True),
        temperature=dict(type='float', required=False, default=0.1),
        max_tokens=dict(type='int', required=False, default=100),
        top_p=dict(type='int', required=False, default=1),
        frequency_penalty=dict(type='int', required=False, default=0),
        presence_penalty=dict(type='int', required=False, default=0),
        tool_modules=dict(type='str', required=False, default=None)
    )
    
    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # Apply TLS security to API Call based on input parameters
    cert = None
    if module.params['tls_client_cert'] != None or module.params['tls_client_key'] != None or module.params['tls_client_passwd'] != None:
        cert = (module.params['tls_client_cert'], module.params['tls_client_key'], module.params['tls_client_passwd'])
    tls_verify = not module.params['tls_insecure']

    # build the system prompt
    system_prompt = module.params['system_content']
    if system_prompt == None:
        system_prompt = ""

    # Process tools modules list provided as input
    tools_list_for_openai = openai.NOT_GIVEN
    if module.params['tool_modules'] != None:
        tool_modules_filenames = module.params['tool_modules'].split(',')

        tool_modules_list = []
        tools_list_for_openai = []
        module.warn(f"Including Tool Calls in LLM Invocation: {module.params['tool_modules']}")

        for tool_module_filename in tool_modules_filenames:
            file_path = f"/Users/lroland/Projects/github.com/openai-ansible-module/library/{tool_module_filename}"
            dynamic_tool_module = dynamically_load_python_module(file_path)

            tool_modules_list.append(dynamic_tool_module)
            tools_list_for_openai.append(dynamic_tool_module.tool_definition)
            system_prompt += " " + dynamic_tool_module.tool_prompt_addendum
    system_prompt = system_prompt.strip()

    # Create OpenAI chat message input
    contentMessages = []
    userContentMessage = {"role": "user", "content": module.params['user_content']}
    if system_prompt == None or len(system_prompt) == 0:
        contentMessages = [ userContentMessage ]
    else:
        contentMessages = [ {"role": "system", "content": system_prompt}, userContentMessage ]
    
    # store requested chat messages
    result['original_messages'] = contentMessages

    try:
        openai_client = OpenAI(
            base_url = module.params['endpoint_url'],
            api_key = module.params['api_key'],
            timeout = httpx.Timeout(timeout=module.params['timeout']),
            http_client=httpx.Client(cert=cert, verify=tls_verify)
        )

        completion = openai_client.chat.completions.create(
            model=module.params['model_name'],
            messages=contentMessages,
            temperature=module.params['temperature'],
            max_tokens=module.params['max_tokens'],
            top_p=module.params['top_p'],
            frequency_penalty=module.params['frequency_penalty'],
            presence_penalty=module.params['presence_penalty'],
            tools=tools_list_for_openai
        )

        if completion.choices[0].message.tool_calls != None:
            num_tool_calls = len(completion.choices[0].message.tool_calls)
            tool_counter = 0

            for tool_call in completion.choices[0].message.tool_calls:
                tool_counter += 1
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                module.warn(f"Tool Invocation ({tool_counter} of {num_tool_calls}) Requested by LLM: {tool_name} with args: {args}")

                # Invoke the appropriate tool
                invoked_flag = False
                tool_invocation_result = None
                for tool_module in tool_modules_list:
                    if tool_module.tool_name == tool_name:
                        invoked_flag = True
                        tool_invocation_result = tool_module.tool_function(module, args)
                        break
                if not invoked_flag:
                    module.fail_json(msg=f"Unable to find tool module corresponding to tool request: {tool_name}", **result)

                #contentMessages.append(completion.choices[0].message)

                contentMessages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_invocation_result) + " degrees farhenheit"
                })

            completion = openai_client.chat.completions.create(
                model=module.params['model_name'],
                messages=contentMessages,
                temperature=module.params['temperature'],
                max_tokens=module.params['max_tokens'],
                top_p=module.params['top_p'],
                frequency_penalty=module.params['frequency_penalty'],
                presence_penalty=module.params['presence_penalty'],
                tools=tools_list_for_openai
            )

        result['response'] = completion.choices[0].message.content

    except openai.APIConnectionError as e:
        module.fail_json(msg=f"Unable to connect to endpoint: {module.params['endpoint_url']}", **result)
        
    # Assuming that successful API invocation = a change
    result['changed'] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
