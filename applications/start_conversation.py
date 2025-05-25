# a simple 2 way conversation between a human and an AI agent
from agents import custom_agents
from utils import prompt_utils

message = """
"""

# fetching keys via get_type_hints not cls.__dict__.keys() so that definition order is maintained
assistant_name = prompt_utils.ask_for_prompt_with_completer(
    options=custom_agents.get_agents_options()
)

agents = custom_agents.AgentFactory()

assistant, user_proxy = agents.get_agents(names=[assistant_name, 'user_proxy']).values()

default_llm = assistant.llm_config["config_list"][0]["model"]
custom_llm_to_use = prompt_utils.ask_for_prompt_with_completer(
    prompt=f"Select LLM to use (default is {default_llm}): ",
    options=custom_agents.get_config_options(),
    selection_mandatory=False,
)

# re-fetch assistant agent with new config is one is selected
if custom_llm_to_use:
    assistant = agents.create_agent(
        name=assistant_name,
        config=getattr(custom_agents.Configs, custom_llm_to_use),
    )

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    assistant,
    message=prompt_utils.get_initial_prompt(message),
)
