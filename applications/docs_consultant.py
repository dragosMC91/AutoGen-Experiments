# an agentic workflow with 3 agents acting a search engine where responses
# are curated by 2 agents: 1 autogen agent and 1 llamaindex agent
# the proxy user (manually controlled by the human) forwards questions to
# the autogen agent who decides if calling llamaindex is required
# don't forget to install the required extra tools via pip install -e '.[rag]'
from agents import custom_agents
from utils import prompt_utils, file_utils
from autogen import register_function
from utils import llamaindex

files = [
    {
        "language": "english",
        "description": """a wikipedia pdf format page containing
        detailed information about the federal budget in canada""",
        "path": f"{file_utils.get_project_root()}/external_knowledge_docs/2023_canada_federal_budget.pdf",
    },
]
priming_message = """The AI assistant has access to a query engine which stores
data from a few specific sources. Query engine should be used in the following situations:
1. the question is strictly related to information stored in the query engine
2. the assistant is not 100% certain of its answer and a double check is needed
The query passed to the engine needs to be specific and focus on keywords related
to the information which is requested.
"""


@prompt_utils.with_progress_bar(description='Initializing query engine...')
def get_query_engine():
    return llamaindex.DocumentQueryEngine.get_instance(
        llamaindex.QueryEngineConfig(
            input_files=[file["path"] for file in files],
        )
    )


query_engine = get_query_engine()

# claude main assistant + openai llamaindex assistant yield good results
default_llm = custom_agents.Configs.claude_35_sonnet
assistant, user_proxy = custom_agents.get_agents(
    names=['advanced_assistant', 'user_proxy'], overwrite_config=default_llm
).values()

custom_llm_to_use = prompt_utils.ask_for_prompt_with_completer(
    prompt=f"Select LLM to use (default is {default_llm['config_list'][0]['model']}): ",
    options=custom_agents.get_config_options(),
    selection_mandatory=False,
)

# re-fetch assistant agent with new config is one is selected
if custom_llm_to_use:
    assistant = custom_agents.get_agents(
        names=['advanced_assistant'],
        overwrite_config=getattr(custom_agents.Configs, custom_llm_to_use),
    )['advanced_assistant']


# wrapper function was created because passing an instance method
# like query_engine.query to register_function will result in an error
def query(question: str) -> str:
    return query_engine.query(question)


register_function(
    name="query",
    f=query,
    description=f"Queries the following documents: {files}. use the same language as document language for the query!",
    caller=assistant,
    executor=user_proxy,
)

result = user_proxy.initiate_chat(
    assistant,
    message=f"{priming_message}\n{prompt_utils.get_initial_prompt()}",
)
