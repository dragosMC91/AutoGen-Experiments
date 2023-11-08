import autogen
from agents import custom_agents

assistant = autogen.AssistantAgent(
    name="coder",
    llm_config=custom_agents.get_llm_config(custom_agents.gpt4_config),
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="ALWAYS",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={"work_dir": "web", "use_docker": "python:3.10.13"},
    llm_config=custom_agents.get_llm_config(custom_agents.gpt3_config),
    system_message="""
    Reply TERMINATE if the task has been solved at full satisfaction.
    Otherwise, reply CONTINUE, or the reason why the task is not solved yet.
    Can also execute code written by the other agents.
    """,
)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message="""
    some query
    """,
)
