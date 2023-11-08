from agents import custom_agents
from operator import itemgetter
import autogen

user_proxy, nutritionist, master_chef = itemgetter(
    'user_proxy', 'nutritionist', 'master_chef'
)(custom_agents.get_agents())
agents = custom_agents.get_agents()

groupchat = autogen.GroupChat(
    agents=[user_proxy, nutritionist, master_chef], messages=[], max_round=10
)
manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=custom_agents.get_llm_config(custom_agents.gpt3_config),
)

user_proxy.initiate_chat(
    manager,
    message="""
    I want to make vegan lasagna in my tefal pressure cooker. How can i do it ?
    """,
)
