from agents import custom_agents
from operator import itemgetter
import autogen
from utils import prompt_utils

multiline_message = """
Who should read this paper: https://arxiv.org/abs/2308.08155
"""

user_proxy, advanced_assistant, critic = itemgetter(
    'user_proxy', 'advanced_assistant', 'critic'
)(custom_agents.get_agents())

groupchat = autogen.GroupChat(
    agents=[user_proxy, advanced_assistant, critic], messages=[], max_round=10
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=custom_agents.get_llm_config(custom_agents.gpt3_config),
)

user_proxy.initiate_chat(
    manager,
    message=prompt_utils.get_initial_prompt(multiline_message),
)
