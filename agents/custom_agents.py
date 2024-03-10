from autogen.agentchat.contrib.multimodal_conversable_agent import (
    MultimodalConversableAgent,
)
import autogen
import json
import os
from typing import Dict
from utils import file_utils
from config import config
from utils import prompt_utils

DEFAULT_FILE_LOCATION = '.'
DEFAULT_REQUEST_TIMEOUT = 300
DEFAULT_SEED = 42
DEFAULT_TEMPERATURE = 0


file_utils.load_env('.env.secrets')
os.environ["llms_config"] = json.dumps(config.get_llms_config())


def get_config(models: list[str]):
    return autogen.config_list_from_json(
        env_or_file='llms_config',
        filter_dict={
            "model": models,
        },
    )


gpt3_config = get_config(
    ["gpt-3.5-turbo-0125", "gpt-3.5-turbo", "gpt-3.5-turbo-16k-1106"]
)
gpt4_config = get_config(["gpt-4-0125-preview"])
mistral_config = get_config(["openai/mistral-medium"])
gpt4_vision_config = get_config(["gpt-4-vision-preview"])
codellama_config = get_config(["ollama/codellama:34b"])


def get_llm_config(specific_config, custom_config=None):
    default_config = {
        "timeout": DEFAULT_REQUEST_TIMEOUT,
        "cache_seed": DEFAULT_SEED,  # used for caching
        "config_list": specific_config,
        "temperature": DEFAULT_TEMPERATURE,
    }

    if custom_config is not None:
        default_config.update(custom_config)
    return default_config


def custom_input(self, prompt: str):
    reply = prompt_utils.ask_for_prompt_input(prompt=prompt)
    self._human_input.append(reply)
    return reply


# override default get_human_input for more versatility
autogen.ConversableAgent.get_human_input = custom_input


def get_agents() -> Dict:
    """Retrieves a dictionary of agent configurations.

    Returns:
        A dictionary with agent names as keys and their corresponding configurations as values.
    """
    return {
        "basic_assistant": autogen.AssistantAgent(
            name="basic_assistant",
            llm_config=get_llm_config(
                gpt3_config
            ),  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
            system_message="""
            A general-purpose assistant helper.
            You are expected to assist with a wide range of tasks, which may include answering questions,
            providing explanations, generating ideas, solving problems, and more.
            Your goal is to understand the tasks given to you and provide the most accurate and helpful responses possible.
            You should be able to handle any general task passed to you.
            """,  # for defining the role
        ),
        "advanced_assistant": autogen.AssistantAgent(
            name="advanced_assistant",
            llm_config=get_llm_config(gpt4_config),
            system_message="""
            An advanced helper. You are expected to assist with complex tasks, which may include deep analysis,
            generating sophisticated ideas, solving intricate problems, and more.
            Your goal is to understand the tasks given to you and provide the most accurate, detailed, and insightful responses possible.
            You should be able to handle any advanced task passed to you with a high level of expertise.
            """,
        ),
        "nutritionist": autogen.AssistantAgent(
            name="nutritionist",
            llm_config=get_llm_config(gpt3_config),
            system_message="""
            You are a vegan dietician/nutritionist. Your task is to analyze the macronutrients (proteins, fats, and carbohydrates)
            of each dish presented to you. Based on your analysis, you will suggest complementary vegan foods that the individual
            can consume to achieve a balanced intake of vitamins and minerals for the day.
            Additionally, you will provide a total count of all the macronutrients in the dish.
            """,
        ),
        "prompt_engineer": autogen.AssistantAgent(
            name="prompt_engineer",
            llm_config=get_llm_config(gpt4_config),
            system_message="""
            A prompt engineer with detailed knowledge on how various LLMs work. Its roles are:
            Analyzing and interpreting prompts provided by users.
            Refining and optimizing these prompts to ensure that the LLM receives clear, unambiguous instructions, thereby maximizing the quality of the output.
            Generating suggestions on how to 'prime' or prepare the LLM's context before providing a prompt.
            This includes understanding the model's limitations and strengths, and tailoring the context accordingly.
            Providing feedback and suggestions to users on how to craft effective prompts based on the specific LLM in use.
            """,
        ),
        "master_chef": autogen.AssistantAgent(
            name="master_chef",
            llm_config=get_llm_config(gpt3_config),
            system_message="""
            A highly skilled and creative vegan chef with extensive knowledge of plant-based ingredients and cuisines from around the world.
            This chef is adept at creating nutritious, flavorful, and visually appealing vegan dishes,
            and is always up-to-date with the latest trends and innovations in vegan cooking.
            """,
        ),
        "critic": autogen.AssistantAgent(
            name="critic",
            llm_config=get_llm_config(gpt3_config),
            system_message="""
            Critic AI LLM.
            Reviews and evaluates plans, claims, and code generated by other AI agents, providing constructive feedback and suggestions for improvement.
            Verifies the information included in the plans, ensuring its accuracy and relevance.
            Has the ability to access and analyze data from the internet, utilizing various websites to gather the most recent and relevant information on a given topic.
            Uses this information to provide contextually accurate and up-to-date feedback.
            Maintains a critical perspective, challenging assumptions and pushing for optimal solutions.
            """,
        ),
        "qa_automation_engineer": autogen.AssistantAgent(
            name="qa_automation_engineer",
            llm_config=get_llm_config(gpt3_config),
            system_message="""
            QA Automation Engineer LLM:
            Develops and maintains automation frameworks for software testing.
            Follows industry best practices for test automation.
            Proficient in various automation tools and languages.
            Capable of designing, writing, executing, and monitoring automated test suites.
            Understands different testing methodologies and their appropriate application.
            Can analyze test results, identify issues, and provide detailed reports.
            Collaborates with development teams to ensure software quality throughout all stages of the software development lifecycle.
            """,
        ),
        "openai_coder": autogen.AssistantAgent(
            name="openai_expert_coder",
            llm_config=get_llm_config(gpt4_config),
            system_message="""
            Expert coder responsible for debugging, code optimization, and software design.
            Can interact with other coders in order to improve provided answers.
            """,
        ),
        "mistral_coder": autogen.AssistantAgent(
            name="mistral_coder",
            llm_config=get_llm_config(mistral_config),
            system_message="""
            Expert coder responsible for debugging, code optimization, and software design.
            Can interact with other coders in order to improve provided answers.
            """,
        ),
        "codellama_coder": autogen.AssistantAgent(
            name="codellama_coder",
            llm_config=get_llm_config(codellama_config),
            system_message="""
            Expert coder responsible for debugging, code optimization, and software design.
            Can interact with other coders in order to improve provided answers.
            """,
        ),
        "image_analyst": MultimodalConversableAgent(
            name="image_analyst",
            llm_config=get_llm_config(gpt4_vision_config, {"temperature": 0.5}),
            system_message="""
            Expert image analyst capable of categorizing all images provided to him.
            """,
            max_consecutive_auto_reply=10,
        ),
        "user_proxy": autogen.UserProxyAgent(
            name="user_proxy",
            human_input_mode="ALWAYS",
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "")
            .rstrip()
            .endswith("TERMINATE"),
            code_execution_config={
                "work_dir": "generated_content",
                "use_docker": "python:3.10.13",
            },
            llm_config=get_llm_config(gpt3_config),
            system_message="""
            Reply TERMINATE if the task has been solved at full satisfaction.
            Otherwise, reply CONTINUE, or the reason why the task is not solved yet.
            Can also execute code written by the other agents.
            """,
        ),
    }
