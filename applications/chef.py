from agents import custom_agents
import autogen
from utils import prompt_utils

message = """
"""

nutritionist, user_proxy, master_chef = custom_agents.get_agents(
    names=['nutritionist', 'user_proxy', 'master_chef']
)

groupchat = autogen.GroupChat(
    agents=[user_proxy, nutritionist, master_chef], messages=[], max_round=10
)
manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=custom_agents.get_llm_config(custom_agents.Configs.gpt3_config),
)

user_proxy.initiate_chat(
    manager,
    message=prompt_utils.get_initial_prompt(message),
)
