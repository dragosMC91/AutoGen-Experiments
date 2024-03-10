from agents import custom_agents
from operator import itemgetter
from utils import prompt_utils

multiline_message = """
"""

user_proxy, basic_assistant = itemgetter('user_proxy', 'basic_assistant')(
    custom_agents.get_agents()
)

# the assistant receives a message from the user, which contains the task description
# the more explicit the description the better.
user_proxy.initiate_chat(
    basic_assistant,
    message=prompt_utils.get_initial_prompt(multiline_message),
)
