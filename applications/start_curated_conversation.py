# a group conversation between a human -> an AI agent -> AI critic
from agents import custom_agents
from utils import prompt_utils
import autogen

message = """
"""

assistant_name = prompt_utils.ask_for_prompt_with_completer(
    options=custom_agents.get_agents_options()
)

assistant, user_proxy, critic, task_planner = custom_agents.get_agents(
    names=[assistant_name, 'user_proxy', 'critic', 'task_planner']
).values()

groupchat = autogen.GroupChat(
    agents=[user_proxy, task_planner, assistant, critic],
    messages=[],
    speaker_selection_method="round_robin",
    max_round=20,
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=custom_agents.get_llm_config(custom_agents.Configs.gpt4o_mini),
    code_execution_config=False,
    system_message="""
    Manage a chat workflow between a task planner, an assistant and a critic.
    Any task will follow this flow:
    1. Pass the initial prompt to the planner for refinement
    2. Pass the detailed plan to the assistant.
    3. Pass the output from the assistant to the critic.
    4. Ask the user for input for the next steps.
    """,
)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    manager,
    message=prompt_utils.get_initial_prompt(message),
)
