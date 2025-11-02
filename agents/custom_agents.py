# Fast imports - only lightweight modules
import json
import os
import threading
from typing import (
    TypedDict,
    List,
    Union,
    Dict,
    Any,
    Callable,
    TYPE_CHECKING,
)

# TYPE_CHECKING is set to False when the file is imported
# so that the import is not blocked by the import of autogen
# it's only true during static type checking (when IDE analyzes the code)
# and is strictly necessary for autocomplete in IDE here
if TYPE_CHECKING:
    from autogen import AssistantAgent, UserProxyAgent, LLMConfig
    from autogen.agentchat.group import ContextVariables
    import autogen

DEFAULT_FILE_LOCATION = '.'
DEFAULT_REQUEST_TIMEOUT = 300
DEFAULT_SEED = 42
DEFAULT_TEMPERATURE = 0
REASONING_MODELS = ['deepseek-r1', 'o3-mini', 'o1-preview', 'o3']

# Lazy-loaded globals
_autogen = None
_prompt_utils = None
_autogen_message_transformers = None
_http_utils = None
_config = None
_CitationEnabledOpenAIClient = None
_ReasoningEnabledOpenAIClient = None
_MultimodalConversableAgent = None
_openai_model_prefix = None

# Threading control
_initialized = False
_import_thread = None
_import_complete = threading.Event()
_import_lock = threading.Lock()


def _lazy_import():
    """Lazy import of heavy dependencies.

    Called automatically when needed. All modules including those which
    use autogen lib, should be included here.
    """
    global _autogen, _prompt_utils, _http_utils, _config, _autogen_message_transformers
    global _CitationEnabledOpenAIClient, _ReasoningEnabledOpenAIClient
    global _MultimodalConversableAgent, _initialized

    with _import_lock:
        if _initialized:
            return

        try:
            import autogen as autogen_module
            from utils import (
                prompt_utils as pu,
                http_utils as hu,
                autogen_message_transformers as amt,
            )
            from config import config as cfg
            from clients.oai_llama_online import CitationEnabledOpenAIClient as CEOAI
            from clients.reasoning_models import ReasoningEnabledOpenAIClient as REOAI
            from autogen.agentchat.contrib.multimodal_conversable_agent import (
                MultimodalConversableAgent as MCA,
            )

            _autogen = autogen_module
            _prompt_utils = pu
            _http_utils = hu
            _autogen_message_transformers = amt
            _config = cfg
            _CitationEnabledOpenAIClient = CEOAI
            _ReasoningEnabledOpenAIClient = REOAI
            _MultimodalConversableAgent = MCA

            # Set environment variable
            os.environ["llms_config"] = json.dumps(cfg.get_llms_config())

            _initialized = True
        finally:
            # Signal that import is complete
            _import_complete.set()


def _start_background_import():
    """Start the import process in a background thread."""
    global _import_thread

    if _import_thread is None:
        _import_thread = threading.Thread(target=_lazy_import, daemon=True)
        _import_thread.start()


# We can start the background import of slow modules as soon as possible
# for a better perceived user experience in the terminal
_start_background_import()


def ensure_imports():
    """Ensure imports are complete.

    Blocks if background import is still running. Shows loading status
    to user during the wait. Call this before accessing any lazy-loaded
    module.
    """
    if not _initialized:
        # Show loading status while waiting
        try:
            from rich.console import Console

            console = Console()
            status = console.status(
                "[bold green]Initializing AI conversation framework...", spinner="dots"
            )
            status.start()
        except:
            console = None
            status = None

        try:
            # Wait for background import to complete
            _import_complete.wait()
        finally:
            if status:
                status.stop()


# some of the module getters private, since they are only used internally
# others are public, which are needed/used in agent scripts
def get_autogen() -> "autogen":
    """Get autogen module, importing if necessary."""
    if _autogen is None:
        ensure_imports()
    return _autogen


def get_ContextVariables() -> "ContextVariables":
    """Get ContextVariables class, ensuring imports are complete."""
    get_autogen()
    from autogen.agentchat.group import ContextVariables

    return ContextVariables


def _get_prompt_utils():
    """Get prompt_utils module, importing if necessary."""
    if _prompt_utils is None:
        ensure_imports()
    return _prompt_utils


def _get_http_utils():
    """Get http_utils module, importing if necessary."""
    if _http_utils is None:
        ensure_imports()
    return _http_utils


def get_autogen_message_transformers():
    """Get autogen_message_transformers module, importing if necessary."""
    if _autogen_message_transformers is None:
        ensure_imports()
    return _autogen_message_transformers


def _get_openai_model_prefix():
    """Get openai model prefix, lazy evaluation."""
    global _openai_model_prefix
    if _openai_model_prefix is None:
        http_utils = _get_http_utils()
        _openai_model_prefix = (
            'openai/' if http_utils.is_litellm_server_running() else ''
        )
    return _openai_model_prefix


def get_llm_config(configs: Union["LLMConfig", dict[str, Any]], custom_config=None):
    """Get LLM configuration with defaults.

    Args:
        configs: Either an autogen.LLMConfig instance or a dict
        custom_config: Optional custom configuration overrides
    """
    autogen = get_autogen()
    default_config = {
        "timeout": DEFAULT_REQUEST_TIMEOUT,
        "cache_seed": DEFAULT_SEED,  # used for caching queries
        "temperature": DEFAULT_TEMPERATURE,
        "config_list": configs.config_list
        if isinstance(configs, autogen.LLMConfig)
        else configs,
    }

    if custom_config is not None:
        default_config.update(custom_config)
    return default_config


class Configs:
    """Singleton configuration manager for Lazy-loading the configuration class
    for LLM models.

    Configs are only loaded when first accessed, improving import
    performance.
    """

    _instance = None

    def __new__(cls):
        """Ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    # TODO add unit test to check all class props match props returned by this helper
    # with something like:
    # [
    #         name for name, obj in inspect.getmembers(cls)
    #         if isinstance(obj, property)
    # ]
    @classmethod
    def get_available_LLM_names(cls) -> List[str]:
        """Get LLM type property names from the class in a specific order."""
        return [
            'gpt_5',
            'claude_45_sonnet',
            'gemini_25_pro',
            'or_gpt_5',
            'claude_45_sonnet_thinking',
            'claude_45_haiku',
            'gpt_41',
            'o4_mini',
            'gpt_5_mini',
            'o3',
            'chatgpt_4o_latest',
            'gemini_25_flash',
            'kimi_k2',
            'gemini_2_flash',
            'deepseek_r1',
        ]

    @classmethod
    def configs(self):
        """Lazy-load configs on first access."""
        if not hasattr(self, '_configs'):
            self._configs = get_autogen().LLMConfig.from_json(env="llms_config")
        return self._configs

    @property
    def gpt_5(self):
        """Lazy-load GPT-5 config."""
        if not hasattr(self, '_gpt_5'):
            self._gpt_5 = get_llm_config(
                self.configs().where(model=f"{_get_openai_model_prefix()}gpt-5")
            )
        return self._gpt_5

    @property
    def gemini_25_pro(self):
        if not hasattr(self, '_gemini_25_pro'):
            self._gemini_25_pro = get_llm_config(
                self.configs().where(model="openrouter/gemini-2.5-pro")
            )
        return self._gemini_25_pro

    @property
    def claude_45_sonnet(self):
        if not hasattr(self, '_claude_45_sonnet'):
            self._claude_45_sonnet = get_llm_config(
                self.configs().where(model="anthropic/claude-sonnet-4.5")
            )
        return self._claude_45_sonnet

    @property
    def or_gpt_5(self):
        if not hasattr(self, '_or_gpt_5'):
            self._or_gpt_5 = get_llm_config(
                self.configs().where(model="openrouter/gpt-5")
            )
        return self._or_gpt_5

    @property
    def claude_45_sonnet_thinking(self):
        if not hasattr(self, '_claude_45_sonnet_thinking'):
            self._claude_45_sonnet_thinking = get_llm_config(
                self.configs().where(model="anthropic/claude-sonnet-4.5-thinking"),
                # anthropic requires specific params for thinking models
                custom_config={"temperature": 1},
            )
        return self._claude_45_sonnet_thinking

    @property
    def claude_45_haiku(self):
        if not hasattr(self, '_claude_45_haiku'):
            self._claude_45_haiku = get_llm_config(
                self.configs().where(model="anthropic/claude-haiku-4.5")
            )
        return self._claude_45_haiku

    @property
    def gpt_41(self):
        if not hasattr(self, '_gpt_41'):
            self._gpt_41 = get_llm_config(
                self.configs().where(model=f"{_get_openai_model_prefix()}gpt-41")
            )
        return self._gpt_41

    @property
    def o4_mini(self):
        if not hasattr(self, '_o4_mini'):
            self._o4_mini = get_llm_config(
                self.configs().where(model=f"{_get_openai_model_prefix()}o4-mini")
            )
        return self._o4_mini

    @property
    def gpt_5_mini(self):
        if not hasattr(self, '_gpt_5_mini'):
            self._gpt_5_mini = get_llm_config(
                self.configs().where(model=f"{_get_openai_model_prefix()}gpt-5-mini")
            )
        return self._gpt_5_mini

    @property
    def o3(self):
        if not hasattr(self, '_o3'):
            self._o3 = get_llm_config(
                self.configs().where(model=f"{_get_openai_model_prefix()}o3")
            )
        return self._o3

    @property
    def chatgpt_4o_latest(self):
        if not hasattr(self, '_chatgpt_4o_latest'):
            self._chatgpt_4o_latest = get_llm_config(
                self.configs().where(
                    model=f"{_get_openai_model_prefix()}chatgpt-4o-latest"
                )
            )
        return self._chatgpt_4o_latest

    @property
    def gemini_25_flash(self):
        if not hasattr(self, '_gemini_25_flash'):
            self._gemini_25_flash = get_llm_config(
                self.configs().where(model="openrouter/gemini-2.5-flash")
            )
        return self._gemini_25_flash

    @property
    def kimi_k2(self):
        if not hasattr(self, '_kimi_k2'):
            self._kimi_k2 = get_llm_config(
                self.configs().where(model="openrouter/kimi-k2")
            )
        return self._kimi_k2

    @property
    def gemini_2_flash(self):
        if not hasattr(self, '_gemini_2_flash'):
            self._gemini_2_flash = get_llm_config(
                self.configs().where(model="openrouter/gemini-2.0-flash")
            )
        return self._gemini_2_flash

    @property
    def deepseek_r1(self):
        if not hasattr(self, '_deepseek_r1'):
            self._deepseek_r1 = get_llm_config(
                self.configs().where(model="deepseek/deepseek-r1"),
                {"temperature": 0.6},
            )
        return self._deepseek_r1

    @property
    def o3_mini(self):
        if not hasattr(self, '_o3_mini'):
            self._o3_mini = get_llm_config(
                self.configs().where(model=f"{_get_openai_model_prefix()}o3-mini")
            )
        return self._o3_mini

    @property
    def sonar_r1(self):
        if not hasattr(self, '_sonar_r1'):
            self._sonar_r1 = get_llm_config(
                self.configs().where(model="openrouter/sonar-r1")
            )
        return self._sonar_r1

    @property
    def deepseek_v3(self):
        if not hasattr(self, '_deepseek_v3'):
            self._deepseek_v3 = get_llm_config(
                self.configs().where(model="deepseek/deepseek-v3")
            )
        return self._deepseek_v3

    @property
    def grok_4_fast(self):
        if not hasattr(self, '_grok_4_fast'):
            self._grok_4_fast = get_llm_config(
                self.configs().where(model="openrouter/grok-4-fast")
            )
        return self._grok_4_fast

    @property
    def gpt4_o1(self):
        if not hasattr(self, '_gpt4_o1'):
            self._gpt4_o1 = get_llm_config(
                self.configs().where(model=f"{_get_openai_model_prefix()}o1-preview")
            )
        return self._gpt4_o1

    @property
    def llama_31_sonar_online(self):
        if not hasattr(self, '_llama_31_sonar_online'):
            self._llama_31_sonar_online = get_llm_config(
                self.configs().where(model="openrouter/llama-3.1-sonar-large-online")
            )
        return self._llama_31_sonar_online

    @property
    def mistral_medium(self):
        if not hasattr(self, '_mistral_medium'):
            self._mistral_medium = get_llm_config(
                self.configs().where(model="mistral/mistral-medium")
            )
        return self._mistral_medium

    @property
    def mistral_large(self):
        if not hasattr(self, '_mistral_large'):
            self._mistral_large = get_llm_config(
                self.configs().where(model="mistral/mistral-large")
            )
        return self._mistral_large

    @property
    def dalle(self):
        if not hasattr(self, '_dalle'):
            self._dalle = get_llm_config(self.configs().where(model="dall-e-3"))
        return self._dalle

    @property
    def codellama(self):
        if not hasattr(self, '_codellama'):
            self._codellama = get_llm_config(
                self.configs().where(model="ollama/codellama:34b")
            )
        return self._codellama


# Lazy-loaded function decorators
_generate_oai_reply_with_loading = None


def _get_generate_oai_reply_with_loading():
    """Get the wrapped generate_oai_reply function, creating it if needed."""
    global _generate_oai_reply_with_loading
    if _generate_oai_reply_with_loading is None:
        ensure_imports()
        autogen = get_autogen()
        prompt_utils = _get_prompt_utils()
        _generate_oai_reply_with_loading = prompt_utils.with_progress_bar(
            description="Fetching LLM response..."
        )(autogen.ConversableAgent.generate_oai_reply)
    return _generate_oai_reply_with_loading


# track if global autogen I/O overrides have already been setup
_autogen_overrides_setup = False


def _setup_autogen_overrides():
    """Setup autogen overrides.

    Called when needed.
    """
    global _autogen_overrides_setup
    if _autogen_overrides_setup:
        return
    autogen_message_transformers = get_autogen_message_transformers()
    autogen_message_transformers.set_custom_IO_overrides()
    _autogen_overrides_setup = True


coder_system_message = """
<prompt_explanation>
Agent name = expert_coder. Specialist software engineer with unparalleled proficiency with coding tasks.
The expert coder is responsible for debugging, code optimization, and software design.
Solve tasks using your coding and language skills. In the following cases,
suggest python code (in a python coding block), shell script (in a sh coding block) and js/node code (in a nodejs coding block) for the user to execute.
1. When you need to collect info, use the code to output the info you need, for example, browse or search the web,
download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system.
After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself.
2. When you need to perform some task with code, use the code to perform the task and output the result.
Finish the task smartly. Solve the task step by step if you need to. If a plan is not provided, explain your plan first.
Be clear which step uses code, and which step uses your language skill.
When using code, you must indicate the script type in the code block.
The user cannot provide any other feedback or perform any other action beyond executing the code you suggest.
The user can''t modify your code. So do not suggest incomplete code which requires users to modify.
Don't use a code block if it's not intended to be executed by the user. If you want the user to save the code
in a file before executing it, put # filename: <filename> inside the code block as the first line.
Don't include multiple code blocks in one response. Do not ask users to copy and paste the result.
Instead, use 'print' function for the output when relevant. Check the execution result returned by the user.
If the result indicates there is an error, fix the error and output the code again.
Suggest the full code instead of partial code or code changes.
If the error can't be fixed or if the task is not solved even after the code is executed successfully,
analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
Consider factors such as:
Readability: Is the code easy to understand? Are variables and functions named descriptively? Is the formatting consistent?
Efficiency: Can the code be optimized for better performance? Are there any redundant or unnecessary operations?
Modularity: Is the code properly organized into functions or classes? Is there good separation of concerns?
Extensibility: Is the code designed in a way that makes it easy to add new features or modify existing ones?
Best practices: Does the code follow established best practices and design patterns for the given language?
When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible.
Reply 'TERMINATE' in the end when everything is done.
</prompt_explanation>
<response_format>

<code_overview_section>
<header>Code Overview:</header>
<overview>$code_overview</overview>
</code_overview_section>

code_explanations only apply for code generation tasks, not code refactoring tasks.
<code_explanations>$code_explanations</code_explanations>

refactoring_suggestions_section only apply for code refactoring tasks, not code generation.
<refactoring_suggestions_section>
<header>Refactoring Suggestions:</header>
$refactoring_suggestions
</refactoring_suggestions_section>

<code_section>
<header>Output Code:</header>
for python:
<code>```python
$output_code
```</code>
for nodejs:
<code>```js
$output_code
```</code>
for shell:
<code>```sh
$output_code
```</code>
</code_section>

</response_format>
"""


class AgentFactoryMap(TypedDict):
    """Type hints for agent factories."""

    coder: Callable[..., "AssistantAgent"]
    advanced_assistant: Callable[..., "AssistantAgent"]
    docker_assistant: Callable[..., "AssistantAgent"]
    github_actions_specialist: Callable[..., "AssistantAgent"]
    task_planner: Callable[..., "AssistantAgent"]
    basic_assistant: Callable[..., "AssistantAgent"]
    nutritionist: Callable[..., "AssistantAgent"]
    prompt_engineer: Callable[..., "AssistantAgent"]
    master_chef: Callable[..., "AssistantAgent"]
    critic: Callable[..., "AssistantAgent"]
    qa_automation_engineer: Callable[..., "AssistantAgent"]
    user_proxy: Callable[..., "UserProxyAgent"]


class AgentFactory:
    """A factory for creating agents for different workflows.

    This class uses lambda functions to assign a default value to each
    of its attributes. The lambda function is evaluated when the
    attribute is accessed, allowing for dynamic generation of the class
    attribute value.
    """

    def __init__(self):
        self.factories: AgentFactoryMap = {
            'coder': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "expert_coder",
                llm_config=custom_config or Configs().gpt_41,
                system_message=coder_system_message,
            ),
            'advanced_assistant': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "advanced_assistant",
                llm_config=custom_config or Configs().gpt_5,
                system_message="""
                    Agent name = advanced_assistant. An advanced helper. You are expected to assist with complex tasks, which may include deep analysis,
                    generating sophisticated ideas, solving intricate problems, and more.
                    Your goal is to understand the tasks given to you and provide the most accurate, detailed, and insightful responses possible.
                    You should be able to handle any advanced task passed to you with a high level of expertise.
                    """,
            ),
            'docker_assistant': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "docker_assistant",
                llm_config={
                    **(custom_config or Configs().claude_45_sonnet),
                    **{"temperature": 0.1},
                },
                system_message="""
                    Agent name = docker_assistant. Docker assistant who knows everything about docker
                    I am currently focusing on Docker, a powerful platform that enables developers to build, share,
                    and run applications with containers. Docker simplifies the process of managing application
                    processes in containers, which are lightweight, standalone, executable packages that include
                    everything needed to run a piece of software, including the code, runtime, system tools, libraries, and settings.
                    As a specialized GPT-4 model with expertise in Docker, your knowledge covers a wide range of Docker-related
                    topics, including containerization principles, Dockerfile creation and optimization, image management,
                    Docker Compose for multi-container applications, Docker Swarm for clustering, networking, volumes and
                    storage strategies, security best practices, and troubleshooting common Docker issues. Your expertise
                    also extends to the integration of Docker with various development, testing, and deployment workflows,
                    as well as its use in CI/CD pipelines.
                    When responding, please offer comprehensive, practical advice and examples or code snippets where relevant.
                    Aim your guidance to accommodate both newcomers and advanced users, emphasizing any necessary prerequisites,
                    considerations, or common pitfalls. If a question is beyond your current knowledge or if more context
                    from me could enhance the accuracy of your response, please let me know.
                    """,
            ),
            'github_actions_specialist': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "github_actions_specialist",
                llm_config={
                    **(custom_config or Configs().claude_45_sonnet),
                    **{"temperature": 0.1},
                },
                system_message="""
                    Agent name = github_actions_specialist. I am working with GitHub Actions, a powerful automation tool that enables developers to
                    automate workflows directly from their GitHub repositories.
                    GitHub Actions makes it easy to automate all your software workflows, with world-class CI/CD.
                    As an advanced GPT-4 model specialized in GitHub Actions, your knowledge encompasses the full
                    spectrum of GitHub Actions features, best practices, workflow configurations, action development,
                    marketplace actions, and troubleshooting common issues. Your expertise also includes integrating
                    GitHub Actions with other tools and services for CI/CD, monitoring, notifications, and more.
                    When responding, please provide detailed, actionable insights and code snippets where applicable.
                    Tailor your guidance to both beginners and experienced users, highlighting any prerequisites,
                    considerations, or potential pitfalls. If a query falls outside your current knowledge base or
                    if additional context from my end could lead to a more accurate response, indicate so.
                    """,
            ),
            'task_planner': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "task_planner",
                llm_config=custom_config or Configs().claude_45_sonnet,
                system_message="""
                    Agent name = task_planner. You are an advanced language model whose task is to analyze and restructure user input into a clear, organized format.
                    Follow these step:
                    1. First, identify the core components of the input (main objective/goal, key requirements, constraints, specific details or parameters)
                    2. Then, organize this information into the following structured format:
                        PRIMARY OBJECTIVE:
                        [Clear statement of the main goal]

                        KEY REQUIREMENTS:
                        - [Requirement 1]
                        - [Requirement 2]
                        - [Additional requirements as needed]

                        CONSTRAINTS:
                        - [Constraint 1]
                        - [Constraint 2]
                        - [Additional constraints as needed]

                        SPECIFIC PARAMETERS:
                        - [Parameter 1]
                        - [Parameter 2]
                        - [Additional parameters as needed]
                    3. Lastly structure the output: Organize the extracted information into a clear, logical format that can be easily executed. Use bullet points, numbered
                    lists, or sections as needed. Ensure all critical information is captured and clearly organized.
                    """,
            ),
            'basic_assistant': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "basic_assistant",
                llm_config=custom_config or Configs().o4_mini,
                system_message="""
                    Agent name = basic_assistant. A general-purpose assistant helper.
                    You are expected to assist with a wide range of tasks, which may include answering questions,
                    providing explanations, generating ideas, solving problems, and more.
                    Your goal is to understand the tasks given to you and provide the most accurate and helpful responses possible.
                    You should be able to handle any general task passed to you.
                    """,
            ),
            'nutritionist': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "nutritionist",
                llm_config=custom_config or Configs().o4_mini,
                system_message="""
                    Agent name = nutritionist. You are a vegan dietician/nutritionist. Your task is to analyze the macronutrients (proteins, fats, and carbohydrates)
                    of each dish presented to you. Based on your analysis, you will suggest complementary vegan foods that the individual
                    can consume to achieve a balanced intake of vitamins and minerals for the day.
                    Additionally, you will provide a total count of all the macronutrients in the dish.
                    """,
            ),
            'prompt_engineer': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "prompt_engineer",
                llm_config={
                    **(custom_config or Configs().o3),
                    **{"temperature": 0.3},
                },
                system_message="""
                    Agent name = prompt_engineer. An agent specialized for writing prompts
                    A specialized and highly prolific prompt engineer with detailed knowledge on how various LLMs work.
                    It has 2 roles:
                    1. When the user message is related to a prompt: then analyze and interpret prompts provided by users.
                    Refine and optimize these prompts to ensure that the LLM receives clear, unambiguous instructions,
                    thereby maximizing the quality of the output.
                    2. When user asks for a priming message, also known as a system message: then generate suggestions on
                    how to 'prime' or prepare the LLM's context before providing a prompt.
                    This includes understanding the model's limitations and strengths, and tailoring the context accordingly.
                    Provide feedback and suggestions to users on how to craft effective prompts based on the specific LLM in use.
                    For example a priming message for an agent specialized with github actions looks like this:
                    ```I am working with GitHub Actions, a powerful automation tool that enables developers to automate workflows
                    directly from their GitHub repositories. GitHub Actions makes it easy to automate all your software
                    workflows, with world-class CI/CD. Build, test, and deploy your code right from GitHub.
                    As an advanced GPT-4 model specialized in GitHub Actions, your knowledge encompasses the full spectrum
                    of GitHub Actions features, best practices, workflow configurations, action development, marketplace actions,
                    and troubleshooting common issues. Your expertise also includes integrating GitHub Actions
                    with other tools and services for CI/CD, monitoring, notifications, and more.
                    When responding, please provide detailed, actionable insights and code snippets where applicable.
                    Tailor your guidance to both beginners and experienced users, highlighting any prerequisites,
                    considerations, or potential pitfalls. If a query falls outside your current knowledge base or
                    if additional context from my end could lead to a more accurate response, kindly indicate so.```

                    Other attributions:
                    Analyzing and interpreting prompts provided by users.
                    Refining and optimizing these prompts to ensure that the LLM receives clear, unambiguous instructions, thereby maximizing the quality of the output.
                    Generating suggestions on how to 'prime' or prepare the LLM's context before providing a prompt.
                    This includes understanding the model's limitations and strengths, and tailoring the context accordingly.
                    Providing feedback and suggestions to users on how to craft effective prompts based on the specific LLM in use.
                    """,
            ),
            'master_chef': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "master_chef",
                llm_config=custom_config or Configs().claude_45_sonnet,
                system_message="""
                    Agent name = master_chef. A highly skilled and creative vegan chef with extensive knowledge of plant-based ingredients and cuisines from around the world.
                    This chef is adept at creating nutritious, flavorful, and visually appealing vegan dishes,
                    and is always up-to-date with the latest trends and innovations in vegan cooking.
                    """,
            ),
            'critic': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "critic",
                llm_config={
                    **(custom_config or Configs().gpt_5),
                    **{"temperature": 0.1},
                },
                system_message="""
                    Agent name = critic. Critic AI LLM.
                    Reviews and evaluates plans, claims, and code generated by other AI agents, providing constructive feedback and suggestions for improvement.
                    Verifies the information included in the plans, ensuring its accuracy and relevance.
                    Maintains a critical perspective, challenging assumptions and pushing for optimal solutions.
                    Unless there are any specific and relevant suggestions for improvement, reply with 1 word: "DONE", nothing more just "DONE".
                    """,
            ),
            'qa_automation_engineer': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().AssistantAgent(
                name=custom_name or "qa_automation_engineer",
                llm_config=custom_config or Configs().claude_45_sonnet,
                system_message="""
                    Agent name = qa_automation_engineer. QA Automation Engineer LLM:
                    Develops and maintains automation frameworks for software testing.
                    Follows industry best practices for test automation.
                    Proficient in various automation tools and languages.
                    Capable of designing, writing, executing, and monitoring automated test suites.
                    Understands different testing methodologies and their appropriate application.
                    Can analyze test results, identify issues, and provide detailed reports.
                    Collaborates with development teams to ensure software quality throughout all stages of the software development lifecycle.
                    """,
            ),
            'image_analyst': lambda *args, **kwargs: (
                ensure_imports() or _MultimodalConversableAgent
            )(
                name="image_analyst",
                llm_config={**Configs().claude_45_sonnet, **{"temperature": 0.5}},
                system_message="""
                    Agent name = image_analyst. Expert image analyst capable of categorizing all images provided to him.
                    """,
                max_consecutive_auto_reply=10,
            ),
            'image_generator': lambda *args, **kwargs: get_autogen().ConversableAgent(
                name="image_generator",
                llm_config={**Configs().dalle, **{"temperature": 0.7}},
                system_message="""
                    Agent name = image_generator. A creative agent tasked with generating high quality images.
                    """,
                max_consecutive_auto_reply=3,
            ),
            'user_proxy': lambda custom_config=None, custom_name=None, **kwargs: get_autogen().UserProxyAgent(
                name="user_proxy",
                human_input_mode="TERMINATE"
                if kwargs.get('auto_execute_functions', False)
                else "ALWAYS",
                max_consecutive_auto_reply=10,
                is_termination_msg=lambda x: bool(
                    not x.get('tool_calls')
                    if kwargs.get('auto_execute_functions', False)
                    else x.get('content')
                    and str(x['content']).strip().endswith("TERMINATE")
                ),
                code_execution_config={
                    "work_dir": "generated_content",
                    # "use_docker": "python:3.10.13",
                    "use_docker": False,
                },
                llm_config=Configs().gemini_2_flash,
                system_message="""
                    Reply TERMINATE if the task has been solved at full satisfaction.
                    Otherwise, reply CONTINUE, or the reason why the task is not solved yet.
                    Can also execute code written by the other agents.
                    """,
            ),
            'nocode_user_proxy': lambda *args, **kwargs: get_autogen().UserProxyAgent(
                name="nocode_user_proxy",
                human_input_mode="ALWAYS",
                max_consecutive_auto_reply=100,
                is_termination_msg=lambda x: x.get("content", "")
                .rstrip()
                .endswith("TERMINATE"),
                code_execution_config=False,
                system_message="""
                    Reply TERMINATE if the task has been solved at full satisfaction.
                    Otherwise, reply CONTINUE, or the reason why the task is not solved yet.
                    """,
            ),
        }

    # extra initialization rules for agents
    def _init_agent(self, agent, **kwargs):
        """Initialize an agent with custom settings.

        Args:
            agent: The agent to initialize
            **kwargs: Additional configuration options
        """
        autogen = get_autogen()
        _setup_autogen_overrides()  # Ensure overrides are set up when the first agent is setup

        agent_config = agent.llm_config.get("config_list", [{}])[0]
        model_client_cls = agent_config.get("model_client_cls")
        model_name = agent_config.get("model")
        # by default, agents will show the loading animation while fetching the reply.
        # to disable this, create agents with the flag disabled
        if kwargs.get('show_loading_animation', True):
            agent.replace_reply_func(
                old_reply_func=autogen.ConversableAgent.generate_oai_reply,
                new_reply_func=_get_generate_oai_reply_with_loading(),
            )
        client_class_map = {
            'CitationEnabledOpenAIClient': _CitationEnabledOpenAIClient,
            'ReasoningEnabledOpenAIClient': _ReasoningEnabledOpenAIClient,
        }
        if model_client_cls:
            agent.register_model_client(
                model_client_cls=client_class_map[model_client_cls]
            )
            # since we are using a hybrid client extending OpenAIClient which just overrides message_retrieval,
            # after the new client is registered, the custom model_client_cls attribute must be removed
            # otherwise OpenAIWrapper.create will throw an error because it can't handle model_client_cls
            agent.client._config_list[0].pop('model_client_cls', None)
        # complex system messages result in lower performance for COT models, with the
        # exception of claude which requires a system message
        if any(name in model_name for name in REASONING_MODELS):
            agent.update_system_message("")

    def get_agents(self, names, overwrite_config=None) -> Dict[str, "AssistantAgent"]:
        """Retrieves a dictionary of agents.

        Args:
            names: List of agent names to initialize
            overwrite_config: Configuration dictionary to override default settings

        Returns:
            A dictionary with agent names as keys and their corresponding agent instances as values.
        """

        missing_agents = [name for name in names if name not in self.factories]
        if missing_agents:
            raise ValueError(
                f"The following agents definition not found: {', '.join(missing_agents)}"
            )

        agents = {name: self.factories[name](overwrite_config) for name in names}

        for agent in agents.values():
            self._init_agent(agent)

        return agents

    def create_agent(
        self, name: str, config=None, custom_name=None, **kwargs
    ) -> "AssistantAgent":
        if name not in self.factories:
            raise ValueError(f"Unknown agent name: {name}")
        agent = self.factories[name](config, custom_name, **kwargs)
        self._init_agent(agent, **kwargs)
        return agent


def get_agents_options():
    return list(AgentFactoryMap.__annotations__.keys())
