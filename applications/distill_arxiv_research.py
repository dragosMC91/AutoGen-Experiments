# start a conversation with an agent who has access to arxiv API tools. Use case example:
# fetch all articles on AI for 28 oct 2024, go over each title and group them
# into relevant categories based on likeness, for easy consumption format the output
# in such a way that the reader can easily parse it and extract titles of interest
# to follow up on, make sure no title from the initial list is excluded
# then you can ask the agent to follow up on a particular paper you want to go more in depth for
from agents import custom_agents
from utils import prompt_utils, llm_functions
import os

agents = custom_agents.AgentFactory()
configs = custom_agents.Configs()

# openai models and sometimes gemini exclude certain results from the response
# claude is the most reliable here but the most expensive
custom_llm_to_use = prompt_utils.ask_for_prompt_with_completer(
    prompt="Select LLM to use for the summary assistant: ",
    options=configs.get_available_LLM_names(),
    selection_mandatory=False,
)

assistant = agents.create_agent(
    name='advanced_assistant',
    config=getattr(configs, custom_llm_to_use),
)
user_proxy = agents.create_agent(name='user_proxy')

# alternative hack to "flake8: noqa: E402" each import in this block
# which is needed to avoid flake8 errors when importing here instead of
# top level of the file (to maintain lazy loading)
if True:
    from autogen.agentchat.contrib.capabilities import transform_messages
    from autogen.agentchat.contrib.capabilities.text_compressors import LLMLingua
    from autogen.agentchat.contrib.capabilities.transforms import TextMessageCompressor

# since arxiv workflow parses large prompts, LLMLingua is used for compression
# don't forget to install the required extra tools via pip install -e '.[text-compression]'
os.environ['TOKENIZERS_PARALLELISM'] = 'true'
llm_lingua = LLMLingua()
text_compressor = TextMessageCompressor(text_compressor=llm_lingua, min_tokens=500)
context_handling = transform_messages.TransformMessages(transforms=[text_compressor])

custom_agents.get_autogen().register_function(
    **llm_functions.Functions.get_latest_arxiv_papers,
    caller=assistant,
    executor=user_proxy,
)
custom_agents.get_autogen().register_function(
    **llm_functions.Functions.get_arxiv_article_content,
    caller=assistant,
    executor=user_proxy,
)

context_handling.add_to_agent(assistant)

result = user_proxy.initiate_chat(
    assistant,
    message=prompt_utils.get_initial_prompt(),
)
