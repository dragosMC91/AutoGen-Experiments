from typing import List
from subprocess import check_call
from setuptools import setup, find_packages
from distutils.cmd import Command
from pathlib import Path
import importlib
import os


class CustomCommand(Command):
    user_options: List[str] = []
    description = 'A custom command'

    # Required method for the Command interface
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


def create_command(text: str, commands: List[List[str]]):
    class GeneratedCommand(CustomCommand):
        description = text

        def run(self):
            for cmd in commands:
                check_call(cmd)

    return GeneratedCommand


class ReviewCommand(CustomCommand):
    user_options = [('file=', 'f', 'File to review')]

    def initialize_options(self):
        self.file = None

    def finalize_options(self):
        assert self.file is not None, "You must provide a file to review."

    def read_file(self, file_path):
        return Path(file_path).read_text()

    def run(self):
        # Here you can define what it means to "review" a file.
        # You can add more checks or reviews as needed.
        check_call(
            ['python', 'applications/code_reviewer.py', self.read_file(self.file)]
        )


class StartLiteLLMServerCommand(CustomCommand):
    def initialize_options(self):
        self.file = None

    def run(self):
        # dynamic import is used in this case because importing dotenv
        # directly in setup.py throws an error on pip install -e .
        module = importlib.import_module('utils.file_utils')

        # loading the secrets file is needed to gain access to the mistral api key
        # without having to expose it in the litellm config file directly
        module.load_env('.env.secrets')
        check_call(['litellm', '--config', 'litellm_config.yml', '--port', '30000'])


class StartAutogenStudioCommand(CustomCommand):
    def initialize_options(self):
        self.file = None

    def run(self):
        # dynamic import is used in this case because importing dotenv
        # directly in setup.py throws an error on pip install -e .
        module = importlib.import_module('utils.file_utils')
        root_dir = os.getcwd()
        # loading the secrets file is needed to gain access to the mistral api key
        # without having to expose it in the litellm config file directly
        module.load_env('.env.secrets')
        check_call(
            ['autogenstudio', 'ui', '--port', '8083', '--appdir', f"{root_dir}/ui"]
        )


class CleanupRepo(CustomCommand):
    def initialize_options(self):
        self.file = None

    def run(self):
        module = importlib.import_module('utils.file_utils')

        module.remove_junk_dirs(
            module.find_junk_dirs(
                '.', ['.cache', '__pycache__', 'autogen_experiments.egg-info']
            )
        )


setup(
    name='autogen-experiments',
    version='0.1.1',
    author='dragos',
    author_email='campean_dragos@ymail.com',
    description='An autogen playground for experimenting.',
    license='none',
    packages=find_packages(),
    install_requires=[
        'aiohttp>=3.12.0',
        'aiosignal>=1.3.1',
        'annotated-types>=0.6.0',
        'anyio>=4',
        'appdirs==1.4.4',
        'APScheduler>=3.10.4',
        'argon2-cffi==23.1.0',
        'argon2-cffi-bindings==21.2.0',
        'arxiv==2.1.3',
        'async-timeout==4.0.3',
        'attrs==23.1.0',
        'backoff==2.2.1',
        'black==23.11.0',
        'build==1.0.3',
        'certifi==2025.1.31',
        'cffi==1.16.0',
        'charset-normalizer==3.4.0',
        'chardet==5.2.0',
        'click==8.1.7',
        'diskcache==5.6.3',
        'distro==1.8.0',
        'dnspython==2.6.1',
        'docformatter==1.7.5',
        'docker==6.1.3',
        'email_validator==2.1.1',
        'exceptiongroup==1.1.3',
        'fastapi==0.115.5',
        'fastapi-sso==0.16.0',
        'feedparser==6.0.10',
        'filelock==3.13.1',
        'flake8==6.1.0',
        'FLAML==2.1.1',
        'frozenlist==1.4.0',
        'fsspec==2023.10.0',
        'gunicorn==23.0.0',
        'h11==0.14.0',
        'httpcore==1.0.4',
        'httpx==0.28.1',
        'huggingface-hub==0.26.0',
        'idna==3.4',
        'importlib-metadata==6.8.0',
        'Jinja2==3.1.2',
        'litellm==1.71.1',
        'markdown-it-py==3.0.0',
        'MarkupSafe==2.1.3',
        'mccabe==0.7.0',
        'mcp>=1.5.0',
        'mdurl==0.1.2',
        'multidict==6.0.4',
        'mypy-extensions==1.0.0',
        'numpy==1.26.2',
        'oauthlib==3.2.2',
        'openai==1.68.2',
        'orjson==3.9.14',
        'packaging==23.2',
        'pathspec==0.11.2',
        'Pillow==10.1.0',
        'pip-tools==7.3.0',
        'platformdirs==3.11.0',
        'prompt-toolkit==3.0.43',
        'ag2==0.8.7',
        'pycodestyle==2.11.1',
        'pycparser==2.21',
        'pydantic==2.10.6',
        'pydantic_core==2.27.2',
        'pyflakes==3.1.0',
        'Pygments==2.17.2',
        'PyJWT==2.8.0',
        'pypdf==4.3.1',
        'pyproject_hooks==1.0.0',
        'python-dotenv==1.0.1',
        'python-multipart==0.0.18',
        'pytz==2024.2',
        'PyYAML==6.0.1',
        'redis==5.0.2',
        'regex==2023.10.3',
        'requests==2.32.3',
        'rich==13.7.1',
        'rq==1.16.1',
        'sgmllib3k==1.0.0',
        'six==1.16.0',
        'sniffio==1.3.0',
        'starlette==0.40.0',
        'termcolor==2.3.0',
        'tiktoken==0.7.0',
        'tokenizers==0.21.0',
        'tomli==2.0.1',
        'tomli_w==1.0.0',
        'tqdm==4.66.1',
        'typer==0.12.3',
        'typing_extensions==4.12.2',
        'tzlocal==5.2',
        'untokenize==0.1.1',
        'urllib3==2.1.0',
        'uvicorn==0.29.0',
        'wcwidth==0.2.13',
        'websocket-client==1.6.4',
        'websockets==14.0',
        'yarl>=1.9.2',
        'zipp==3.17.0',
    ],
    extras_require={
        'proxy': [
            # https://github.com/BerriAI/litellm/blob/main/pyproject.toml
            # uv pip install 'litellm[proxy]' -U if server start fails
            'prisma==0.11.0',
            'hf-xet>=1.1.2',
            'litellm-enterprise>=0.1.5',
            'litellm-proxy-extras>=0.2.0',
            'uvloop>=0.21.0',
            'httpx-aiohttp>=0.1.4',
            'cryptography>=43.0.1',
            'opentelemetry-api==1.30.0',
            'opentelemetry-sdk==1.30.0',
        ],
        'text-compression': [
            'ag2[long-context]',
            'huggingface-hub==0.26.0',
            'accelerate==1.0.1',
        ],
        # other tool installs which are needed
        # 1. playwright install
        'deep-research': [
            'ag2[browser-use]',
        ],
        'rag': [
            'llama-index==0.11.21',
        ],
        'all': [
            'autogen-experiments[proxy]',
            'autogen-experiments[text-compression]',
            'autogen-experiments[rag]',
            'autogen-experiments[deep-research]',
        ],
    },
    cmdclass=dict(
        fix=create_command(
            'Auto fix and lint code',
            [
                ['python', 'setup.py', 'format'],
                ['python', 'setup.py', 'lint'],
                ['python', 'setup.py', 'format_docstrings'],
            ],
        ),
        format=create_command('Auto format code', [['black', '-S', '.']]),
        lint=create_command('Lint the code', [['flake8', '.']]),
        format_docstrings=create_command(
            "Auto format doc strings",
            [['docformatter', '-r', '-i', '.']],
        ),
        review=ReviewCommand,
        litellm=StartLiteLLMServerCommand,
        ui=StartAutogenStudioCommand,
        clean=CleanupRepo,
    ),
)
