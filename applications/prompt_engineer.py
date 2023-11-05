from agents import custom_agents
from operator import itemgetter
import autogen

user_proxy, prompt_engineer, critic = itemgetter('user_proxy', 'prompt_engineer', 'critic')(custom_agents.get_agents())
agents = custom_agents.get_agents()

groupchat = autogen.GroupChat(agents=[user_proxy, prompt_engineer, critic], messages=[], max_round=10)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=custom_agents.get_llm_config(custom_agents.gpt3_config))

user_proxy.initiate_chat(
    manager,
    message="""
    I am defining the following role for a coder ai LLM:
    ```
    Expert coder responsible for debugging, code optimization, and software design.
    ```
    This is used to better set the context before i actually start giving it tasks.
    Suggest how to improve this this role definition.
    """
)