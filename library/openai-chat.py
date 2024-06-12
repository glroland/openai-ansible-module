#!/usr/bin/python

# Copyright: (c) 2024, Lee Roland <glroland@hotmail.com>
# Apache License Version 2.0, January 2004 (http://www.apache.org/licenses/)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: openai

short_description: Ansible module to interface with OpenAI compliant APIs

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: This is an Ansible module used to interface with OpenAI compliant APIs from Ansible playbooks.

options:
    name:
        description: This is the message to send to the test module.
        required: true
        type: str
    new:
        description:
            - Control to demo if the result of this module is changed or not.
            - Parameter description can be a list as well.
        required: false
        type: bool
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
# extends_documentation_fragment:
#     - my_namespace.my_collection.my_doc_fragment_name

author:
    - Lee Roland (@glroland)
'''

EXAMPLES = r'''
# Pass in a message
- name: Test with a message
  my_namespace.my_collection.my_test:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_namespace.my_collection.my_test:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_namespace.my_collection.my_test:
    name: fail me
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule
import openai
from openai import OpenAI
import httpx

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        endpoint_url=dict(type='str', required=True),
        model_name=dict(type='str', required=True),
        user_content=dict(type='str', required=True),
        system_content=dict(type='str', required=False, default=None),
        tls_insecure=dict(type='bool', required=False, default=False),
        api_key=dict(type='str', required=False, default='api_key'),
        timeout=dict(type='int', required=False, default=30),
        tls_client_cert=dict(type='str', required=False, default=None),
        tls_client_key=dict(type='str', required=False, default=None),
        tls_client_passwd=dict(type='str', required=False, default=None, no_log=True),
        temperature=dict(type='float', required=False, default=0.1),
        max_tokens=dict(type='int', required=False, default=100),
        top_p=dict(type='int', required=False, default=1),
        frequency_penalty=dict(type='int', required=False, default=0),
        presence_penalty=dict(type='int', required=False, default=0)
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

    # Create OpenAI chat message input
    contentMessages = []
    userContentMessage = {"role": "user", "content": module.params['user_content']}
    if module.params['system_content'] == None:
        contentMessages = [ userContentMessage ]
    else:
        contentMessages = [ {"role": "system", "content": module.params['system_content']}, userContentMessage ]
    
    # store requested chat messages
    result['original_messages'] = contentMessages

    # Apply TLS security to API Call based on input parameters
    cert = None
    if module.params['tls_client_cert'] != None or module.params['tls_client_key'] != None or module.params['tls_client_passwd'] != None:
        cert = (module.params['tls_client_cert'], module.params['tls_client_key'], module.params['tls_client_passwd'])
    tls_verify = not module.params['tls_insecure']

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
            presence_penalty=module.params['presence_penalty']
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
