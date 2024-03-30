import requests
from requests.exceptions import ConnectionError


def is_litellm_server_running():
    path = '/routes'

    try:
        response = requests.get(url=f'http://localhost:30000{path}')
    except ConnectionError:
        print(
            "\nLiteLLM server is not started. If you want to monitor costs, make sure to boot it up.\n"
        )
        return False

    if response.status_code != 200:
        print("LiteLLM server was not started correctly")
        return False

    try:
        data = response.json()
    except ValueError:
        print(
            f"The response of the {path} request is not a valid JSON. LiteLLM might not be started correctly."
        )
        return False

    if 'routes' not in data or not isinstance(data['routes'], list):
        print(
            f"Failed to validate {path} response: it does not contain a 'routes' key or it's not a list."
        )
        return False

    return True
