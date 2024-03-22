# a simple 2 way conversation between a human and an AI agent
from agents import custom_agents
from operator import itemgetter
from utils import prompt_utils

message = """
"""

assistant_name = prompt_utils.ask_for_prompt_with_completer()

user_proxy, assistant = itemgetter('user_proxy', assistant_name)(
    custom_agents.get_agents()
)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message=prompt_utils.get_initial_prompt(message),
)
