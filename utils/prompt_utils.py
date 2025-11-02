import re
from pygments.lexers.python import PythonLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit import prompt as toolkit_prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.formatted_text import HTML

from rich.console import Console

from rich.progress import (
    Progress,
    TextColumn,
    SpinnerColumn,
)

line_separator = "\n" + "-" * 80
console = Console()


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
    print(line_separator, flush=True, sep="")
    return user_prompt


def is_non_empty_prompt(prompt):
    pattern = r'^[\r\n\t\f\v ]*$'
    return not bool(re.match(pattern, prompt))


def get_initial_prompt(prompt=""):
    return prompt if is_non_empty_prompt(prompt) else ask_for_prompt_input()


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
        (
            event.app.current_buffer.delete_before_cursor()
            if event.key_sequence[0].key == Keys.Backspace
            else event.app.current_buffer.delete()
        )
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
        print(line_separator, flush=True, sep="")
        return selected_option
    else:
        raise ValueError(
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
