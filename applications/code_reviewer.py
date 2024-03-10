from agents import custom_agents
from operator import itemgetter
from utils import prompt_utils

message = """
"""

user_proxy, openai_coder = itemgetter('user_proxy', 'openai_coder')(
    custom_agents.get_agents()
)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    openai_coder,
    message=prompt_utils.get_initial_prompt(message),
)
