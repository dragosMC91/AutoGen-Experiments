import autogen

gpt3_config = autogen.config_list_from_json(
    env_or_file="llms_config",
    file_location='.',
    filter_dict={
        "model": ["gpt-3.5-turbo-16k"],
    },
)
llm_config={
    "request_timeout": 300,
    "seed": 42,
    "config_list": gpt3_config,
    "temperature": 0,
}

ollama = autogen.config_list_from_json(
    env_or_file="llms_config",
    file_location='.',
    filter_dict={
        "model": ["ollama/codellama"],
    },
)
ozama={
    "request_timeout": 300,
    "seed": 42,
    "config_list": ollama,
    "temperature": 0,
}

assistant = autogen.AssistantAgent(
    name="coder",
    llm_config=ozama,
)

user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "web", 
        "use_docker": "python:3.10.13"
    },
    llm_config=llm_config,
    system_message="""
    Reply TERMINATE if the task has been solved at full satisfaction.
    Otherwise, reply CONTINUE, or the reason why the task is not solved yet.
    Can also execute code written by the other agents.
    """
)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message="""
    What is your base AI model ? Brief answer please.
    """
)