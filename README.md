This project is a small wrapper over [AutoGen](https://github.com/microsoft/autogen). It integrates the [LiteLLM](https://github.com/BerriAI/litellm) proxy server to give you easy access to any LLM (proprietary or open source), without having to leave the comfort of your terminal.

It uses the [Rich](https://github.com/Textualize/rich) library to colorize output which makes reading large responses in a plain terminal a bit more digestible:
![Example Terminal Output](docs/llm_terminal_response.jpg)

## Getting Started

This section provides instructions on how to set up your development environment for working on this project.

## Prerequisites

Before you begin, ensure you have either `pyenv` or `conda` installed on your system to manage Python versions and environments.

## Python Version

This project is tested with Python `3.11.8`. It is recommended to use this specific version to avoid any compatibility issues.

## Environment Setup

### Using pyenv

If you are using `pyenv`, you can install Python `3.11.8` and set it as the local version for the project using the following commands:

```sh
pyenv install 3.11.8
pyenv local 3.11.8
pyenv virtualenv myenv
```

### Using conda

If you prefer `conda`, create a new environment with Python `3.11.8` using the following command:

```sh
conda create --name myenv python=3.11.8
conda activate myenv
```

Replace `myenv` with a name of your choice for the environment.

### Install project dependencies

Once you have the correct version of Python set up, install the project dependencies by running:

```sh
pip install -r requirements.txt
```

## Configuration

### 1. Define the LLMs config
Copy the `.env.secrets.example` file to create your own `.env.secrets` file and fill in your specific API keys for services you plan you use like OpenAI or MistralAI.

```sh
cp .env.secrets.example .env.secrets
```

Edit the `.env.secrets` file with your preferred text editor and update the API keys as needed.

### 2. Run setuptools
Run the following command in the project root to facilitate packages imports throughout the repo.
```
pip install -e .
```

This will allow you to import and use the project's modules from anywhere on your system.

With these steps, you should be ready to work on the project and run the applications.

## Useful tools
### 1. Lint code
Run the following command
```
python setup.py fix
```
### 2. Review code from file using gpt4
```
python setup.py review --file path/to/file
```
### 3. Start the LiteLLM proxy server
One of [LiteLLM](https://litellm.vercel.app/docs/)'s strong points is that it offers a unified interface for calling various LLMs among other cool features.
In this context we use to extend AutoGen's capabilities to use other AI models (which is currently not supported out of the box, but is a WIP).
```
python setup.py litellm
```

### 4. Start Autogen Studio GUI
Autogen also offers a [neat UI](https://github.com/microsoft/autogen/tree/main/samples/apps/autogen-studio).

The following command starts the AGS app and makes the ui available at http://localhost:8083.
The AGS sqlite DB together with other related artifacts are stored in `src/ui`.

```
python setup.py ui
```
## Running the Applications

After setting up the environment and configuration, you can run the applications within the `src/applications/` directory.


## Applications
Executing an application creates a new conversation session based on the flow defined in that app.

There are 2 generic apps:
1. `start_conversation.py` starts a simple conversation a selected agent from a list of predefined specialized agents.
2. `start_curated_conversation.py` adds a critic AI to the conversation which reviews the main agent's claims

New custom agents can be added in the agent definition file `agents/custom_agents.py`.


You can either tweak the `message` inside each application, or execute the script and input your prompt in the command line (recommended).
Prompts have multiline support so `Enter` just inserts a new line. In order to submit the prompt press `(Meta|Esc)+Enter`.

### chef.py
```
python chef.py
```

The `chef.py` application demonstrates how to use agents to facilitate a conversation about cooking. It shows the setup of a group chat with multiple agents and the initiation of a chat with a user query.

---

## Setup local and third party LLMs

1. Install the [ollama tool](https://github.com/jmorganca/ollama)
2. Download any model you want for example for codellama run
```
ollama run codellama
```
3. Update the `litellm_config.yml` file to contain the new local model references or references to any other API services like [Mistral AI](https://mistral.ai/).
4. Start the LiteLLM proxy server 
See the [3. Start the LiteLLM proxy server](#3-start-the-litellm-proxy-server) section for more information.

Other popular models: https://huggingface.co/WizardLM