from typing import List
from subprocess import check_call
from setuptools import setup, find_packages
from distutils.cmd import Command
from pathlib import Path
import importlib


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


setup(
    name='autogen-experiments',
    version='0.1.0',
    author='dragos',
    author_email='campean_dragos@ymail.com',
    description='An autogen playground for experimenting.',
    license='none',
    packages=find_packages(),
    install_requires=(open('requirements.txt').read().splitlines()),
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
    ),
)
