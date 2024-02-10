import os
import logging


def get_llms_config():
    config = [
        {"model": "gpt-3.5-turbo-0125", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-3.5-turbo", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-3.5-turbo-16k-1106", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-4-0125-preview", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-4-turbo-preview", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-4-vision-preview", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "dall-e-3", "api_key": os.getenv('OPENAI_API_KEY')},
        {
            "base_url": "http://localhost:30000",
            "model": "openai/mistral-medium",
            "api_key": "sk-xxxxx",
        },
        {
            "base_url": "http://localhost:30000",
            "model": "ollama/codellama",
            "api_key": "sk-xxxxx",
        },
        {"model": "DALLE 2", "api_key": os.getenv('OPENAI_API_KEY')},
    ]

    for model_info in config:
        if not model_info.get('api_key'):
            # The api_key is not set (None, null, or empty string)
            model_name = model_info.get(
                'model', 'Unknown model'
            )  # Get the model name or use a default
            warning_message = f"Warning: the api key for model {model_name} was not set. Make sure to set it if you need it in your scripts."
            logging.warning(warning_message)

    return config
