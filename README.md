## Getting Started

This section provides instructions on how to set up your development environment for working on this project.

## Prerequisites

Before you begin, ensure you have either `pyenv` or `conda` installed on your system to manage Python versions and environments.

## Python Version

This project is tested with Python `3.10.13`. It is recommended to use this specific version to avoid any compatibility issues.

## Environment Setup

### Using pyenv

If you are using `pyenv`, you can install Python `3.10.13` and set it as the local version for the project using the following commands:

```sh
pyenv install 3.10.13
pyenv local 3.10.13
pyenv virtualenv myenv
```

### Using conda

If you prefer `conda`, create a new environment with Python `3.10.13` using the following command:

```sh
conda create --name myenv python=3.10.13
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
Copy the `llms_config.example` file to create your own `llms_config` file and fill in your specific API keys and settings.

```sh
cp llms_config.example llms_config
```

Edit the `llms_config` file with your preferred text editor and update the configuration as needed.

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
## Running the Applications

After setting up the environment and configuration, you can run the applications within the `src/applications/` directory.


## Applications
Make sure to tweak the requirement message inside each application before running the code.

### chef.py
```
python chef.py
```

The `chef.py` application demonstrates how to use agents to facilitate a conversation about cooking. It shows the setup of a group chat with multiple agents and the initiation of a chat with a user query.

---

## Setup local LLMs

1. Install the [ollama tool](https://github.com/jmorganca/ollama)
2. Download any model you want for example for codellama run
```
ollama run codellama
```
3. Start the model you downloaded locally via `litellm` on the desired port
```
litellm --model ollama/codellama --port 30000
```
4. update your `llms_config` file with the appropriate localhost url for example
```
    {
        "api_base": "http://localhost:30000",
        "model": "ollama/codellama",
        "api_key":"sk-dummy-key-because-tool-requires-it"
    },
```

Other popular models: https://huggingface.co/WizardLM