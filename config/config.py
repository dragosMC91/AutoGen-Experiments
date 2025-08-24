import os
import logging
from utils import file_utils

file_utils.load_env('.env.secrets')
base_url = "http://localhost:30000"


def get_llms_config():
    config = [
        # OpenAI models
        {"model": "gpt-3.5-turbo-0125", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-3.5-turbo", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-4-turbo-2024-04-09", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-4o", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-4o-mini", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "gpt-4.1", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "chatgpt-4o-latest", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "o3", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "o3-mini", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "o4-mini", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "o1-preview", "api_key": os.getenv('OPENAI_API_KEY')},
        {"model": "dall-e-3", "api_key": os.getenv('OPENAI_API_KEY')},
        {
            "base_url": base_url,
            "model": "openai/o3",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.002, 0.008],
        },
        {
            "base_url": base_url,
            "model": "openai/gpt-5",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00125, 0.01],
        },
        {
            "base_url": base_url,
            "model": "openai/gpt-5-mini",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00025, 0.002],
        },
        {
            "base_url": base_url,
            "model": "openai/o4-mini",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00015, 0.0016],
        },
        {
            "base_url": base_url,
            "model": "openai/gpt-41",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.002, 0.008],
        },
        {
            "base_url": base_url,
            "model": "openai/o1-preview",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.015, 0.06],
        },
        {
            "base_url": base_url,
            "model": "openai/gpt-4-turbo-2024-04-09",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "openai/chatgpt-4o-latest",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.005, 0.015],
        },
        {
            "base_url": base_url,
            "model": "openai/gpt-4o",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.0025, 0.010],
        },
        {
            "base_url": base_url,
            "model": "openai/o3-mini",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.0011, 0.0044],
        },
        {
            "base_url": base_url,
            "model": "openai/gpt-4o-mini",
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
        # MistralAI models
        {
            "base_url": base_url,
            "model": "mistral/mistral-medium",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        {
            "base_url": base_url,
            "model": "mistral/mistral-large",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
        },
        # AnthropicAI models
        {
            "base_url": base_url,
            "model": "anthropic/claude-3-opus",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.015, 0.075],
        },
        {
            "base_url": base_url,
            "model": "anthropic/claude-3.5-sonnet",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.003, 0.015],
        },
        {
            "base_url": base_url,
            "model": "anthropic/claude-3.7-sonnet",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.003, 0.015],
        },
        {
            "base_url": base_url,
            "model": "anthropic/claude-sonnet-4",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.003, 0.015],
        },
        {
            "base_url": base_url,
            "model": "anthropic/claude-sonnet-4-thinking",
            "model_client_cls": "ReasoningEnabledOpenAIClient",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.003, 0.015],
        },
        {
            "base_url": base_url,
            "model": "anthropic/claude-opus-4",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.015, 0.075],
        },
        {
            "base_url": base_url,
            "model": "anthropic/claude-3.5-haiku",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.001, 0.005],
        },
        # Google models
        {
            "base_url": base_url,
            "model": "google/gemini-2.0-flash",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.0001, 0.0004],
        },
        {
            "base_url": base_url,
            "model": "google/gemini-2.5-pro",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.0000, 0.0000],
        },
        # OpenRouter models
        {
            "base_url": base_url,
            "model": "openrouter/gpt-5",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00125, 0.01],
        },
        {
            "base_url": base_url,
            "model": "openrouter/gemini-2.0-flash",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.0001, 0.0004],
        },
        {
            "base_url": base_url,
            "model": "openrouter/kimi-k2",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00014, 0.00249],
        },
        {
            "base_url": base_url,
            "model": "openrouter/gemini-2.5-flash",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00015, 0.0006],
        },
        {
            "base_url": base_url,
            "model": "openrouter/gemini-2.5-pro",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00125, 0.01],
        },
        {
            "base_url": base_url,
            "model": "openrouter/claude-3.7-thinking",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "model_client_cls": "ReasoningEnabledOpenAIClient",
            "price": [0.0003, 0.0015],
        },
        {
            "base_url": base_url,
            "model": "openrouter/llama-3.1-sonar-large-online",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.001, 0.001],
            "model_client_cls": "CitationEnabledOpenAIClient",
        },
        {
            "base_url": base_url,
            "model": "openrouter/sonar-r1",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.001, 0.005],
            "model_client_cls": "CitationEnabledOpenAIClient",
        },
        {
            "base_url": base_url,
            "model": "openrouter/deepseek-v3",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00014, 0.00028],
        },
        {
            "base_url": base_url,
            "model": "openrouter/deepseek-r1",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00055, 0.00219],
        },
        # DeepseekAI models
        {
            "base_url": base_url,
            "model": "deepseek/deepseek-v3",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00014, 0.00028],
        },
        {
            "base_url": base_url,
            "model": "deepseek/deepseek-r1",
            "api_key": os.getenv('LITELLM_MASTER_KEY'),
            "price": [0.00055, 0.00219],
            "model_client_cls": "ReasoningEnabledOpenAIClient",
        },
        # Local ollama models
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
