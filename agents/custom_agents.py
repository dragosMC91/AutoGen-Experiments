from autogen.agentchat.contrib.multimodal_conversable_agent import (
    MultimodalConversableAgent,
)
import autogen
import json
import os
from typing import TypedDict, get_type_hints, List, Dict, Any
from utils import prompt_utils, http_utils
from config import config
from clients.oai_llama_online import CitationEnabledOpenAIClient
from clients.reasoning_models import ReasoningEnabledOpenAIClient

DEFAULT_FILE_LOCATION = '.'
DEFAULT_REQUEST_TIMEOUT = 300
DEFAULT_SEED = 42
DEFAULT_TEMPERATURE = 0
REASONING_MODELS = ['deepseek-r1', 'o3-mini', 'o1-preview']

os.environ["llms_config"] = json.dumps(config.get_llms_config())


def get_config(models: list[str]):
    return autogen.config_list_from_json(
        env_or_file='llms_config',
        filter_dict={
            "model": models,
        },
    )


# if LiteLLM server is started, route all traffic through that proxy server
openai_model_prefix = 'openai/' if http_utils.is_litellm_server_running() else ''


class Configs:
    claude_35_sonnet: List[Dict[str, Any]] = get_config(["anthropic/claude-3.5-sonnet"])
    claude_37_sonnet: List[Dict[str, Any]] = get_config(["anthropic/claude-3.7-sonnet"])
    gemini_2_flash: List[Dict[str, Any]] = get_config(
        [
            "openrouter/gemini-2.0-flash",
        ]
    )
    claude_37_thinking: List[Dict[str, Any]] = get_config(
        ["openrouter/claude-3.7-thinking"]
    )
    deepseek_r1: List[Dict[str, Any]] = get_config(
        [
            "deepseek/deepseek-r1",
        ]
    )
    o3_mini: List[Dict[str, Any]] = get_config(
        [
            f"{openai_model_prefix}o3-mini",
        ]
    )
    sonar_r1: List[Dict[str, Any]] = get_config(
        [
            "openrouter/sonar-r1",
        ]
    )
    deepseek_v3: List[Dict[str, Any]] = get_config(
        [
            "deepseek/deepseek-v3",
        ]
    )
    gpt4_o: List[Dict[str, Any]] = get_config(
        [
            # f"{openai_model_prefix}gpt-4o",
            f"{openai_model_prefix}gpt-4o-2024-11-20",
        ]
    )
    gpt4_o1: List[Dict[str, Any]] = get_config(
        [
            f"{openai_model_prefix}o1-preview",
        ]
    )
    llama_31_sonar_online: List[Dict[str, Any]] = get_config(
        [
            "openrouter/llama-3.1-sonar-large-online",
        ]
    )
    gpt4_turbo: List[Dict[str, Any]] = get_config(
        [
            f"{openai_model_prefix}gpt-4-turbo-2024-04-09",
        ]
    )
    claude_35_haiku: List[Dict[str, Any]] = get_config(["anthropic/claude-3.5-haiku"])
    claude_3_opus: List[Dict[str, Any]] = get_config(["anthropic/claude-3-opus"])
    gpt4o_mini: List[Dict[str, Any]] = get_config([f"{openai_model_prefix}gpt-4o-mini"])
    gpt3: List[Dict[str, Any]] = get_config(
        [
            f"{openai_model_prefix}gpt-3.5-turbo-0125",
            f"{openai_model_prefix}gpt-3.5-turbo",
        ]
    )
    mistral_medium: List[Dict[str, Any]] = get_config(["mistral/mistral-medium"])
    mistral_large: List[Dict[str, Any]] = get_config(["mistral/mistral-large"])
    dalle: List[Dict[str, Any]] = get_config(["dall-e-3"])
    codellama: List[Dict[str, Any]] = get_config(["ollama/codellama:34b"])


def get_config_options():
    return list(get_type_hints(Configs).keys())


def get_llm_config(specific_config, custom_config=None):
    default_config = {
        "timeout": DEFAULT_REQUEST_TIMEOUT,
        "cache_seed": DEFAULT_SEED,  # used for caching
        "config_list": specific_config,
        # the temperature attribute from specific_config, if set, has precedence over the the temperature from default_config
        "temperature": DEFAULT_TEMPERATURE,
    }

    if custom_config is not None:
        default_config.update(custom_config)
    return default_config


# setup autogen overrides
autogen.ConversableAgent.generate_oai_reply = prompt_utils.with_progress_bar(
    description="Fetching LLM response..."
)(autogen.ConversableAgent.generate_oai_reply)
prompt_utils.set_custom_IO_overrides()

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


configs = Configs


class Agents(TypedDict):
    """A TypedDict for defining agent configurations with default values.

    This class uses lambda functions to assign a default value to each
    of its attributes. The lambda function is evaluated when the
    attribute is accessed, allowing for dynamic generation of the class
    attribute value.
    """

    coder: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="expert_coder",
        llm_config=get_llm_config(custom_config or configs.claude_37_sonnet),
        system_message=coder_system_message,
    )

    advanced_assistant: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="advanced_assistant",
        llm_config=get_llm_config(custom_config or configs.claude_37_sonnet),
        system_message="""
            Agent name = advanced_assistant. An advanced helper. You are expected to assist with complex tasks, which may include deep analysis,
            generating sophisticated ideas, solving intricate problems, and more.
            Your goal is to understand the tasks given to you and provide the most accurate, detailed, and insightful responses possible.
            You should be able to handle any advanced task passed to you with a high level of expertise.
            """,
    )

    docker_assistant: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="docker_assistant",
        llm_config=get_llm_config(
            custom_config or configs.claude_37_sonnet, {"temperature": 0.1}
        ),
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
    )

    github_actions_specialist: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="github_actions_specialist",
        llm_config=get_llm_config(
            custom_config or configs.claude_37_sonnet, {"temperature": 0.1}
        ),
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
    )

    task_planner: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="task_planner",
        llm_config=get_llm_config(custom_config or configs.claude_37_thinking),
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
    )

    basic_assistant: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="basic_assistant",
        llm_config=get_llm_config(custom_config or configs.claude_37_sonnet),
        system_message="""
            Agent name = basic_assistant. A general-purpose assistant helper.
            You are expected to assist with a wide range of tasks, which may include answering questions,
            providing explanations, generating ideas, solving problems, and more.
            Your goal is to understand the tasks given to you and provide the most accurate and helpful responses possible.
            You should be able to handle any general task passed to you.
            """,
    )

    nutritionist: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="nutritionist",
        llm_config=get_llm_config(custom_config or configs.gpt4_o),
        system_message="""
            Agent name = nutritionist. You are a vegan dietician/nutritionist. Your task is to analyze the macronutrients (proteins, fats, and carbohydrates)
            of each dish presented to you. Based on your analysis, you will suggest complementary vegan foods that the individual
            can consume to achieve a balanced intake of vitamins and minerals for the day.
            Additionally, you will provide a total count of all the macronutrients in the dish.
            """,
    )

    prompt_engineer: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="prompt_engineer",
        llm_config=get_llm_config(
            custom_config or configs.gpt4_o, {"temperature": 0.3}
        ),
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
    )

    master_chef: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="master_chef",
        llm_config=get_llm_config(custom_config or configs.claude_37_sonnet),
        system_message="""
            Agent name = master_chef. A highly skilled and creative vegan chef with extensive knowledge of plant-based ingredients and cuisines from around the world.
            This chef is adept at creating nutritious, flavorful, and visually appealing vegan dishes,
            and is always up-to-date with the latest trends and innovations in vegan cooking.
            """,
    )

    critic: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="critic",
        llm_config=get_llm_config(
            custom_config or configs.gemini_2_flash, {"temperature": 0.1}
        ),
        system_message="""
            Agent name = critic. Critic AI LLM.
            Reviews and evaluates plans, claims, and code generated by other AI agents, providing constructive feedback and suggestions for improvement.
            Verifies the information included in the plans, ensuring its accuracy and relevance.
            Maintains a critical perspective, challenging assumptions and pushing for optimal solutions.
            Unless there are any specific and relevant suggestions for improvement, reply with 1 word: "DONE", nothing more just "DONE".
            """,
    )

    qa_automation_engineer: autogen.AssistantAgent = lambda custom_config=None: autogen.AssistantAgent(
        name="qa_automation_engineer",
        llm_config=get_llm_config(custom_config or configs.claude_37_sonnet),
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
    )

    image_analyst: MultimodalConversableAgent = lambda *args: MultimodalConversableAgent(
        name="image_analyst",
        llm_config=get_llm_config(configs.claude_37_sonnet, {"temperature": 0.5}),
        system_message="""
            Agent name = image_analyst. Expert image analyst capable of categorizing all images provided to him.
            """,
        max_consecutive_auto_reply=10,
    )

    image_generator: autogen.ConversableAgent = lambda *args: autogen.ConversableAgent(
        name="image_generator",
        llm_config=get_llm_config(configs.dalle, {"temperature": 0.7}),
        system_message="""
            Agent name = image_generator. A creative agent tasked with generating high quality images.
            """,
        max_consecutive_auto_reply=3,
    )

    user_proxy: autogen.UserProxyAgent = lambda *args: autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: bool(
            x.get('content') and str(x['content']).strip().endswith("TERMINATE")
        ),
        code_execution_config={
            "work_dir": "generated_content",
            # "use_docker": "python:3.10.13",
            "use_docker": False,
        },
        llm_config=get_llm_config(configs.deepseek_v3),
        system_message="""
            Reply TERMINATE if the task has been solved at full satisfaction.
            Otherwise, reply CONTINUE, or the reason why the task is not solved yet.
            Can also execute code written by the other agents.
            """,
    )

    nocode_user_proxy: autogen.UserProxyAgent = lambda *args: autogen.UserProxyAgent(
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
    )


def get_agents_options():
    return list(get_type_hints(Agents).keys())


@prompt_utils.with_progress_bar(description='Initializing agents...')
def get_agents(names, overwrite_config=None) -> Agents:
    """Retrieves a dictionary of agent configurations.

    Args:
        names: List of agent names to initialize
        overwrite_config: Configuration dictionary to override default settings

    Returns:
        A dictionary with agent names as keys and their corresponding configurations as values.
    """

    valid_agent_names = list(get_type_hints(Agents).keys())
    missing_agents = {name for name in names if name not in valid_agent_names}
    if missing_agents:
        raise ValueError(
            f"The following agents definition not found: {', '.join(missing_agents)}"
        )

    agents = {name: getattr(Agents, name)(overwrite_config) for name in names}

    # extra initialization rules for agents
    for agent in agents.values():
        agent_config = agent.llm_config.get("config_list", [{}])[0]
        model_client_cls = agent_config.get("model_client_cls")
        model_name = agent_config.get("model")
        client_class_map = {
            'CitationEnabledOpenAIClient': CitationEnabledOpenAIClient,
            'ReasoningEnabledOpenAIClient': ReasoningEnabledOpenAIClient,
        }
        if model_client_cls:
            agent.register_model_client(
                model_client_cls=client_class_map[model_client_cls]
            )
            # since we are using a hybrid client extending OpenAIClient which just overrides message_retrieval,
            # after the new client is registered, the custom model_client_cls attribute must be removed
            # otherwise OpenAIWrapper.create will throw an error because it can't handle model_client_cls
            agent.client._config_list[0].pop('model_client_cls', None)
        # complex system messages result in lower performance for COT models
        if any(name in model_name for name in REASONING_MODELS):
            agent.update_system_message("")

    return agents
