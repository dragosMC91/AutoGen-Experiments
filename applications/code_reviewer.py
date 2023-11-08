from agents import custom_agents
from sys import argv
from operator import itemgetter

user_proxy, openai_coder = itemgetter('user_proxy', 'openai_coder')(
    custom_agents.get_agents()
)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    openai_coder,
    message=f"""
    Review the following code
    ```````````````````````````
    {argv[1]}
    ```````````````````````````
    """,
)
