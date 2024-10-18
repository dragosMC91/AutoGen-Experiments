# a group conversation between a human -> an AI agent -> AI critic
from agents import custom_agents
from utils import prompt_utils
import autogen

message = """
"""

assistant_name = prompt_utils.ask_for_prompt_with_completer(
    options=custom_agents.get_agents_options()
)

assistant, user_proxy, critic = custom_agents.get_agents(
    names=[assistant_name, 'user_proxy', 'critic']
).values()

groupchat = autogen.GroupChat(
    agents=[user_proxy, assistant, critic],
    messages=[],
    speaker_selection_method="round_robin",
    max_round=20,
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=custom_agents.get_llm_config(custom_agents.Configs.gpt4o_mini),
    code_execution_config=False,
    system_message="""
    Manage the chat between the the coder and the critic.
    Any coding task will follow this flow:
    1. Pass task to the coder.
    2. Pass the output from the coder to the critic.
    3. Ask the user for input for the next steps.
    """,
)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    manager,
    message=prompt_utils.get_initial_prompt(message),
)
