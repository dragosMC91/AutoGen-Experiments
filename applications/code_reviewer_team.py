from agents import custom_agents
from operator import itemgetter
import autogen
from utils import prompt_utils

debug = True

code_to_review = """
review my code:
=============================
console.log();
=============================
"""

user_proxy, critic, openai_coder, codellama_coder = itemgetter(
    'user_proxy', 'critic', 'openai_coder', 'codellama_coder'
)(custom_agents.get_agents())

groupchat = autogen.GroupChat(
    agents=[user_proxy, critic, openai_coder],
    messages=[],
    max_round=10,
)
manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=custom_agents.get_llm_config(custom_agents.gpt3_config),
    system_message="""
    Manage the chat between the the coder and the critic.
    Any coding task will follow this flow:
    1. Pass task to the coder.
    2. Pass the output from the coder to the critic.
    3. Ask the user for input for the next steps.
    """,
)

user_proxy.initiate_chat(
    manager,
    message=f"""
    Review the following code
    ```````````````````````````
    {prompt_utils.get_initial_prompt(code_to_review)}
    ```````````````````````````
    """,
)
