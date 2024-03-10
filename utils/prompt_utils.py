import re
from pygments.lexers import guess_lexer
from pygments.lexer import Lexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit import prompt as toolkit_prompt
from contextlib import contextmanager
from rich import print as rich_print
import builtins


class CustomLexer(Lexer):
    def __init__(self, **options):
        super().__init__(**options)

    def get_tokens_unprocessed(self, text):
        lexer = guess_lexer(text)
        return lexer.get_tokens_unprocessed(text)


def ask_for_prompt_input(
    prompt='Input user prompt. Submit prompt via (Meta|Esc)+Enter.',
):
    """
    Prompts the user for a multiline string.
    - multiline=True has a side effect where Enter key now inserts a new line
    instead of accepting and returning the input. Accept input via (Meta|Esc)+Enter.
    - mouse_support=True has a side effect that actions like scroll, select text
    from the terminal require keeping the Fn key pressed.
    """
    return toolkit_prompt(
        prompt + "\n\n",
        multiline=True,
        mouse_support=True,
        lexer=PygmentsLexer(CustomLexer),
    )


def ask_for_initial_prompt_input():
    prompt = ask_for_prompt_input()
    return prompt + '\n' + '-' * 80


def is_non_empty_prompt(prompt):
    pattern = r'^[\r\n\t\f\v ]*$'
    return not bool(re.match(pattern, prompt))


def get_initial_prompt(prompt):
    return prompt if is_non_empty_prompt(prompt) else ask_for_initial_prompt_input()


@contextmanager
def override_print():
    original_print = builtins.print
    builtins.print = rich_print
    try:
        yield
    finally:
        builtins.print = original_print


# Function which overrides the print statements inside any function
def custom_print_received_message(original_method):
    def wrapper(self, *args, **kwargs):
        with override_print():
            original_method(self, *args, **kwargs)

    return wrapper
