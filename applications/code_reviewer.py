from agents import custom_agents
from operator import itemgetter
import autogen

debug = True

user_proxy, critic, openai_coder, codellama_coder = itemgetter(
    'user_proxy', 'critic', 'openai_coder', 'codellama_coder'
)(custom_agents.get_agents())
agents = custom_agents.get_agents()

groupchat = autogen.GroupChat(
    agents=[user_proxy, critic, openai_coder, codellama_coder],
    messages=[],
    max_round=10,
)
manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=custom_agents.get_llm_config(custom_agents.gpt3_config),
)

user_proxy.initiate_chat(
    manager,
    message="""
    First pass the code to openai_coder then the reviewed code goes to codellama_coder and the critic will evaluate the final result
    Give me feedback and suggestions for the following code:
    `````````````````````````````````````
    `````````````````````````````````````
    """,
)
