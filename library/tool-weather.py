import requests

tool_name = "get_weather"

def tool_function(ansible_module, args):
    latitude = args["latitude"]
    longitude = args["longitude"]

    ansible_module.warn(f"Tool Inputs: {latitude}, {longitude}")

    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m&hourly=temperature_2m&temperature_unit=fahrenheit&wind_speed_unit=mph&precipitation_unit=inch&forecast_days=1")
    data = response.json()
    result = data['current']['temperature_2m']

    ansible_module.warn(f"Tool Result: {result}")

    return result


tool_definition = {
    "type": "function",
    "function": {
        "name": tool_name,
        "description": "Get current temperature for provided coordinates in fahrenheit.",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"}
            },
            "required": ["latitude", "longitude"],
            "additionalProperties": False
        },
        "strict": True
    }
}
