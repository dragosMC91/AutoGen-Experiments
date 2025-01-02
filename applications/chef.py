from agents import custom_agents
import autogen
from utils import prompt_utils

message = """
"""

nutritionist, user_proxy, master_chef = custom_agents.get_agents(
    names=['nutritionist', 'user_proxy', 'master_chef']
).values()

groupchat = autogen.GroupChat(
    agents=[user_proxy, master_chef, nutritionist],
    messages=[],
    speaker_selection_method="round_robin",
    max_round=10,
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=custom_agents.get_llm_config(custom_agents.Configs.deepseek_v3),
    system_message="""
    Manage a chat workflow between a chef and a nutritionist.
    Any task will follow this flow:
    1. Pass the initial prompt to the chef to provide a recipe
    2. Pass the generated recipe to the nutritionist for analysis.
    3. Ask the user for extra input for the next steps.
    """,
)

user_proxy.initiate_chat(
    manager,
    message=prompt_utils.get_initial_prompt(message),
)
