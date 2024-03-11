import re
import builtins
from pygments.lexers import guess_lexer
from pygments.lexer import Lexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit import prompt as toolkit_prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from contextlib import contextmanager
from rich import print as rich_print


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
        lexer=PygmentsLexer(CustomLexer),
    )


def ask_for_initial_prompt_input():
    return ask_for_prompt_input()


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


# Match agent names with the ones from custom_agents.py
AGENT_NAMES = [
    'openai_coder',
    'github_actions_specialist',
    'docker_assistant',
    'advanced_assistant',
    'basic_assistant',
    'prompt_engineer',
]


def ask_for_prompt_with_completer(
    prompt='Select AI (press Tab for options): ',
    options=AGENT_NAMES,
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
        prompt, completer=completer, key_bindings=kb, complete_while_typing=True
    )

    # Ensure the selected option is one of the options, otherwise, print a message.
    if selected_option in options:
        return selected_option
    else:
        print(
            'Invalid selection. Please run the script again and select a valid option.'
        )
