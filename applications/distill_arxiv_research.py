# start a conversation with an agent who has access to arxiv API tools. Use case example:
# fetch all articles on AI for 28 oct 2024, go over each title and group them
# into relevant categories based on likeness, for easy consumption format the output
# in such a way that the reader can easily parse it and extract titles of interest
# to follow up on, make sure no title from the initial list is excluded
# then you can ask the agent to follow up on a particular paper you want to go more in depth for
from agents import custom_agents
from utils import prompt_utils, llm_functions
from autogen import register_function
from autogen.agentchat.contrib.capabilities import transform_messages
from autogen.agentchat.contrib.capabilities.text_compressors import LLMLingua
from autogen.agentchat.contrib.capabilities.transforms import TextMessageCompressor
import os

# since arxiv workflow parses large prompts, LLMLingua is used for compression
# don't forget to install the required extra tools via pip install -e '.[text-compression]'
os.environ['TOKENIZERS_PARALLELISM'] = 'true'
llm_lingua = LLMLingua()
text_compressor = TextMessageCompressor(text_compressor=llm_lingua, min_tokens=500)
context_handling = transform_messages.TransformMessages(transforms=[text_compressor])

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

context_handling.add_to_agent(assistant)

result = user_proxy.initiate_chat(
    assistant,
    message=prompt_utils.get_initial_prompt(message),
)
