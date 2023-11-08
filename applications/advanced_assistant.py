from agents import custom_agents
from operator import itemgetter
import autogen

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
    message="""
    Who should read this paper: https://arxiv.org/abs/2308.08155
    """,
)
