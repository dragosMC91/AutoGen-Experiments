from typing import List
from subprocess import check_call
from setuptools import setup, find_packages
from distutils.cmd import Command


def create_command(text: str, commands: List[List[str]]):
    class GeneratedCommand(Command):
        user_options: List[str] = []
        description = text

        # Required method for the Command interface
        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            for cmd in commands:
                check_call(cmd)

    return GeneratedCommand


setup(
    name='autogen-experiments',
    version='0.1.0',
    author='dragos',
    author_email='campean_dragos@ymail.com',
    description='An autogen playground for experimenting.',
    license='none',
    packages=find_packages(),
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
    ),
)
