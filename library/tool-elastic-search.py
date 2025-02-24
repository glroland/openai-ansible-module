import os
from elasticsearch import Elasticsearch

tool_name = "count_log_entries"

tool_prompt_addendum = f"Always use the {tool_name} tool to get the number of log entries that exist for a given machine name."

def tool_function(ansible_module, args):
    machine_name = args["machine_name"]

    elastic_client = Elasticsearch(
        os.environ["ES_URL"],
        api_key=os.environ["ES_API_KEY"],
        verify_certs=False
    )

    elastic_client.info()

    result_set = elastic_client.search(index="ocp-index", q=machine_name)
    result = -1
    if result_set is not None:
        result = len(result_set)

    ansible_module.warn(f"Tool {tool_name} for arguments {args} == {result}")

    return result


tool_definition = {
    "type": "function",
    "function": {
        "name": tool_name,
        "description": "Counts the number of log entries that exist for the specified machine name.",
        "parameters": {
            "type": "object",
            "properties": {
                "machine_name": {"type": "string"}
            },
            "required": ["machine_name"],
            "additionalProperties": False
        },
        "strict": True
    }
}
