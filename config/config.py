import os
import logging

base_url = "http://localhost:30000"


def get_llms_config():
    config = [
        {"model": "gpt-3.5-turbo-0125", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-3.5-turbo", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "o1-preview", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-4-turbo-2024-04-09", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-4o", "api_key": os.getenv('OPENAI_API_KEY')},
        # {"model": "gpt-4o-2024-08-06", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-4-vision-preview", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "dall-e-3", "api_key": os.getenv('OPENAI_API_KEY')},
        {
            "base_url": base_url,
            "model": "mistral/mistral-medium",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "openai/o1-preview",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "openai/gpt-4-turbo-2024-04-09",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            # "model": "openai/gpt-4o-2024-08-06",
            "model": "openai/gpt-4o",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "openai/gpt-3.5-turbo-0125",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "openai/gpt-3.5-turbo",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "openai/dall-e-3",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "mistral/mistral-large",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "anthropic/claude-3-opus",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "anthropic/claude-3-sonnet",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "anthropic/claude-3.5-sonnet",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "anthropic/claude-3-haiku",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "ollama/codellama:34b",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
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
