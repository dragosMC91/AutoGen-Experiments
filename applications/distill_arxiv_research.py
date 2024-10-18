# start a conversation with an agent who has access to arxiv API tools. Use case example:
# fetch all articles on AI for 16 oct 2024, go over each title and
# group them into relevant categories based on likeness, for easy consumption
# make sure no title from the initial message is excluded
# then you can ask the agent to follow up on a particular paper you want to go more in depth for
from agents import custom_agents
from utils import prompt_utils, llm_functions
from autogen import register_function

message = """
"""

# claude was chosen because i found openai models exclude certain results from the response
default_llm = custom_agents.Configs.claude_35_sonnet
assistant, user_proxy = custom_agents.get_agents(
    names=['advanced_assistant', 'user_proxy'], overwrite_config=default_llm
).values()

custom_llm_to_use = prompt_utils.ask_for_prompt_with_completer(
    prompt=f"Select LLM to use (default is {default_llm[0]['model']}): ",
    options=custom_agents.get_config_options(),
    selection_mandatory=False,
)

# re-fetch assistant agent with new config is one is selected
if custom_llm_to_use:
    assistant = custom_agents.get_agents(
        names=['advanced_assistant'],
        overwrite_config=getattr(custom_agents.Configs, custom_llm_to_use),
    )['advanced_assistant']

register_function(
    **llm_functions.Functions.get_latest_arxiv_papers,
    caller=assistant,
    executor=user_proxy,
)
register_function(
    **llm_functions.Functions.get_arxiv_article_content,
    caller=assistant,
    executor=user_proxy,
)

user_proxy.initiate_chat(
    assistant,
    message=prompt_utils.get_initial_prompt(message),
)
