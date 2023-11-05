from agents import custom_agents
from operator import itemgetter
import autogen
debug = True

gpt3_config = autogen.config_list_from_json(
    env_or_file="llms_config",
    file_location='.',
    filter_dict={
        "model": ["gpt-3.5-turbo-16k"],
    },
)

user_proxy, critic, openai_coder, codellama_coder = itemgetter('user_proxy', 'critic', 'openai_coder', 'codellama_coder')(custom_agents.get_agents())
agents = custom_agents.get_agents()

groupchat = autogen.GroupChat(agents=[user_proxy, critic, openai_coder, codellama_coder], messages=[], max_round=10)
manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=custom_agents.get_llm_config(custom_agents.gpt3_config))

user_proxy.initiate_chat(
    manager,
    message="""
    Give me feedback and suggestions for the following code:
    `````````````````````````````````````
    import autogen
    from typing import Dict

    gpt3_config = autogen.config_list_from_json(
        env_or_file="llms_config",
        file_location='.',
        filter_dict={
            "model": ["gpt-3.5-turbo-16k", "gpt-3.5-turbo", "gpt-3.5-turbo-16k-0613"],
        },
    )

    gpt4_config = autogen.config_list_from_json(
        env_or_file="llms_config",
        file_location='.',
        filter_dict={
            "model": ["gpt-4"],
        },
        
    )

    codellama_config = autogen.config_list_from_json(
        env_or_file="llms_config",
        file_location='.',
        filter_dict={
            "model": ["ollama/codellama"],
        },
        
    )

    def get_llm_config(specific_config, custom_config=None):
        default_config = {
            "request_timeout": 300,
            "seed": 42, # used for caching
            "config_list": specific_config,
            "temperature": 0,
        }

        if custom_config is not None:
            for key in custom_config:
                default_config[key] = custom_config[key]
        
        return default_config

    def get_agents() -> Dict:
        # Define your agent retrieval logic here
        return {
            "basic_assistant": autogen.AssistantAgent(
                name="basic_assistant",
                llm_config=get_llm_config(gpt3_config),  # configuration for autogen's enhanced inference API which is compatible with OpenAI API
                system_message=\"\"\"
                A general-purpose assistant helper. 
                You are expected to assist with a wide range of tasks, which may include answering questions, 
                providing explanations, generating ideas, solving problems, and more. 
                Your goal is to understand the tasks given to you and provide the most accurate and helpful responses possible. 
                You should be able to handle any general task passed to you.
                \"\"\" # for defining the role
            ),
            ...many other agents in the format of `basic_assistant`
        }

    `````````````````````````````````````
    """
)