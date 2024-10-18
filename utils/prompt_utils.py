import re
import builtins
from pygments.lexers import guess_lexer
from pygments.lexers.python import PythonLexer
from pygments.lexer import Lexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit import prompt as toolkit_prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.formatted_text import HTML

from contextlib import contextmanager
from rich.console import Console
from rich.text import Text

from rich.progress import (
    Progress,
    TextColumn,
    SpinnerColumn,
)

from autogen.io.base import IOStream
from typing import Any


class CustomLexer(Lexer):
    def __init__(self, **options):
        super().__init__(**options)

    def get_tokens_unprocessed(self, text):
        lexer = guess_lexer(text)
        return lexer.get_tokens_unprocessed(text)


class OptionCompleter(Completer):
    def __init__(self, options):
        self.options = options

    def get_completions(self, document, complete_event):
        text = document.text
        for option in self.options:
            if text.lower() in option.lower():
                yield Completion(option, start_position=-len(text))


def ask_for_prompt_input(
    prompt='Please input user prompt.',
):
    """
    Prompts the user for a multiline string.
    - multiline=True has a side effect where Enter key now inserts a new line
    instead of accepting and returning the input. Accept input via (Meta|Esc)+Enter.
    - mouse_support=True has a side effect that actions like scroll, select text
    from the terminal require keeping the Fn key pressed.
    """
    prompt_suffix = 'Submit prompt via (Meta|Esc)+Enter.'
    original = 'Press enter to skip and use auto-reply'
    formatted = (
        '\nLeave prompt empty for auto-reply or to execute LLM suggested function call'
    )
    user_prompt = toolkit_prompt(
        HTML(
            f'<ansigreen>\n{prompt.replace(original, formatted)}\n{prompt_suffix}\n\n</ansigreen>'
        ),
        multiline=True,
        lexer=PygmentsLexer(PythonLexer),
    )
    print("\n", "-" * 80, flush=True, sep="")
    return user_prompt


def ask_for_initial_prompt_input():
    return ask_for_prompt_input()


def is_non_empty_prompt(prompt):
    pattern = r'^[\r\n\t\f\v ]*$'
    return not bool(re.match(pattern, prompt))


def get_initial_prompt(prompt=""):
    return prompt if is_non_empty_prompt(prompt) else ask_for_initial_prompt_input()


console = Console()


def is_code_snippet(arg):
    # Simple heuristic to determine if a string might be a code snippet
    # This can be adjusted based on the characteristics of your code snippets
    return '\n' in arg and ('    ' in arg or '\t' in arg)


class RichIOStream(IOStream):
    def __init__(self):
        self.console = Console()

    def print(self, *args: Any, **kwargs) -> None:
        # Remove 'flush' argument if present, as it's not supported by rich.console.Console.print
        kwargs.pop('flush', None)
        processed_args = []
        for arg in args:
            if isinstance(arg, str):
                if is_code_snippet(arg):
                    # Handle potential code snippets differently
                    # For example, by not converting them with Text.from_ansi
                    # This preserves formatting but does not interpret ANSI codes
                    processed_args.append(arg)
                else:
                    # Convert args with ANSI codes into rich Text objects
                    processed_args.append(Text.from_ansi(arg))
            else:
                # Non-string arguments are added without modification
                processed_args.append(arg)

        self.console.print(markup=False, *processed_args, **kwargs)

    def input(self, prompt: str = "", *, password: bool = False) -> str:
        return ask_for_prompt_input(prompt)


default_rich_io_stream = RichIOStream()


def set_custom_IO_overrides():
    IOStream.set_global_default(default_rich_io_stream)


# Custom rich print function that should handle ANSI escape sequences correctly
def rich_print(*args, **kwargs):
    # Remove 'flush' argument if present, as it's not supported by rich.console.Console.print
    kwargs.pop('flush', None)

    # TODO: add better support for colorized/ better formatted output depending on output type
    processed_args = []
    for arg in args:
        if isinstance(arg, str):
            if is_code_snippet(arg):
                # Handle potential code snippets differently
                # For example, by not converting them with Text.from_ansi
                # This preserves formatting but does not interpret ANSI codes
                processed_args.append(arg)
            else:
                # Convert args with ANSI codes into rich Text objects
                processed_args.append(Text.from_ansi(arg))
        else:
            # Non-string arguments are added without modification
            processed_args.append(arg)

    console.print(markup=False, *processed_args, **kwargs)


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


# Match agent names with the ones from custom_agents.py
AGENT_NAMES = [
    'openai_coder',
    'anthropic_coder',
    'mistral_coder',
    'github_actions_specialist',
    'docker_assistant',
    'advanced_assistant',
    'basic_assistant',
    'prompt_engineer',
    'codellama_coder',
]


def ask_for_prompt_with_completer(
    prompt='Select AI (press Tab for options): ',
    options=AGENT_NAMES,
    selection_mandatory=True,
):
    """Prompts the user to select an option with autocompletion support.

    Args:
        prompt (str): The prompt message to display.
        options (list): The list of options for autocompletion.

    Returns:
        The selected option if valid, otherwise prints an error message.
    """
    kb = KeyBindings()

    @kb.add(Keys.Backspace)
    @kb.add(Keys.Delete)
    def handle_key_events(event):
        """Handle backspace and delete keys explicitly."""
        event.app.current_buffer.delete_before_cursor() if event.key_sequence[
            0
        ].key == Keys.Backspace else event.app.current_buffer.delete()
        refresh_completions(event)

    def refresh_completions(event):
        """Force refresh completions on every key press."""
        buffer = event.app.current_buffer
        buffer.complete_state = None
        buffer.start_completion(select_first=False)

    completer = OptionCompleter(options)

    selected_option = toolkit_prompt(
        HTML(f'<ansigreen>{prompt}</ansigreen>'),
        completer=completer,
        key_bindings=kb,
        complete_while_typing=True,
    )

    # Ensure the selected option is one of the options, or users skipped
    # selecting an option, otherwise, print a warning message.
    is_input_skipped = not selection_mandatory and selected_option == ''
    if selected_option in options or is_input_skipped:
        print("\n", "-" * 80, flush=True, sep="")
        return selected_option
    else:
        print(
            f'Invalid selection "{selected_option}". Please run the script again and select a valid option from {options}.'
        )


progress_bar = Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    transient=True,
)


# 1 additional layer of inner functions is used to be able to pass a 'description' to the decorator
def with_progress_bar(description):
    def wrap_function(target_function):
        def wrapped_function(*args, **kwargs):
            with progress_bar as progress:
                task_id = progress.add_task(description=description, total=100)
                result = target_function(*args, **kwargs)
                progress.remove_task(task_id)
                return result

        return wrapped_function

    return wrap_function
