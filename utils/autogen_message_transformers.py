import re

from rich.console import Console
from rich.text import Text
from rich.syntax import Syntax
from rich.panel import Panel

from utils import prompt_utils

from autogen.io.base import IOStream
from autogen.events.agent_events import TextEvent
from typing import List, Tuple, Any
from enum import Enum

line_separator = "\n" + "-" * 80
console = Console()
LANGUAGE_MAPPING = {
    'javascript': 'javascript',
    'js': 'javascript',
    'typescript': 'typescript',
    'ts': 'typescript',
    'python': 'python',
    'bash': 'bash',
    'sh': 'bash',
    'shell': 'bash',
    'py': 'python',
}
CODE_PATTERN = re.compile(
    f'```({"|".join(LANGUAGE_MAPPING.keys())})\n?(.*?)\n?```', re.DOTALL
)
REASONING_BLOCK_PATTERN = re.compile(
    '~~~Reasoning:\n*(.*?)\n*~~~Finished reasoning', re.DOTALL
)


class BlockType(Enum):
    TEXT = "text"
    CODE = "code"
    REASONING = "reasoning"
    MD = "markdown"


def has_overlap(
    intervals: List[Tuple[int, int]], new_interval: Tuple[int, int]
) -> bool:
    new_start, new_end = new_interval
    for start, end in intervals:
        if max(new_start, start) <= min(new_end, end):
            return True
    return False


def parse_content_blocks(text: str):
    """Split a response text into well defined individual blocks based on the
    type of each sub-section.

    Args:
        text (str): Input text containing distinguishable sub-sections like
        markdown code blocks delimited by triple backticks and optional language specifiers.

    Returns:
        List[Dict[str, str]]: List of dictionaries representing distinguishable sub-sections.
        Each dictionary has the following structure:
        - For text blocks: {'type': 'text', 'content': str}
        - For reasoning blocks: {'type': 'reasoning', 'content': str}
        - For code blocks: {'type': 'code', 'language': str, 'content': str}
    """

    blocks = []
    complete_blocks = []

    def _get_matched_intervals():
        return [block['range'] for block in blocks]

    # find and process reasoning blocks
    for match in REASONING_BLOCK_PATTERN.finditer(text):
        start, end = match.span()

        # if not has_overlap(matched_intervals, (start, end)):
        if not has_overlap(_get_matched_intervals(), (start, end)):
            blocks.append(
                {
                    'type': BlockType.REASONING,
                    'range': (start, end),
                    'content': match.group(1).strip(),
                }
            )

    # find and process code blocks
    for match in CODE_PATTERN.finditer(text):
        start, end = match.span()
        language = match.group(1).lower()
        normalized_lang = LANGUAGE_MAPPING[language]

        if not has_overlap(_get_matched_intervals(), (start, end)):
            blocks.append(
                {
                    'type': BlockType.CODE,
                    'range': (start, end),
                    'language': normalized_lang,
                    'content': match.group(2).strip(),
                }
            )

    # process normal texts between special special blocks
    blocks = sorted(blocks, key=lambda x: x['range'][0])
    current_position = 0
    for block in blocks:
        start, end = block['range']
        if current_position < start:
            complete_blocks.append(
                {
                    'type': BlockType.TEXT,
                    'range': (current_position, start - 1),
                    'content': text[current_position : start - 1],
                }
            )
        complete_blocks.append(block)
        current_position = end + 1

    # add remaining text if any
    complete_blocks.append(
        {
            'type': BlockType.TEXT,
            'content': text[current_position:],
            'range': (current_position, len(text)),
        }
    )

    return complete_blocks


def create_renderable_blocks(unformatted_blocks):
    """Handle different block types like code snippets differently For example,
    by not converting them with Text.from_ansi This preserves formatting but
    does not interpret ANSI codes."""
    renderable_blocks = []
    for block in unformatted_blocks:
        if block['type'] == BlockType.CODE:
            language = block['language']
            renderable_blocks.append(f'```{language}')
            renderable_blocks.append(get_code_syntax(block['content'], language))
            renderable_blocks.append('```')
        elif block['type'] == BlockType.REASONING:
            renderable_blocks.append(get_reasoning_block(block['content']))
        else:
            renderable_blocks.append(block['content'])
    return renderable_blocks


def get_code_syntax(code, programming_language):
    return Syntax(
        code,
        programming_language,
        theme="monokai",
        word_wrap=True,
        background_color="default",
    )


def get_reasoning_block(content: str) -> Panel:
    """Create a formatted reasoning block with a box."""
    return Panel(
        Text(content, style="italic", no_wrap=False),
        title="[b]🧠 Reasoning[/b]",
        title_align="left",
        border_style="bright_blue",
        padding=(1, 4),
        style="bright_white on default",
        expand=True,
    )


def format_agent_conversation_header(sender, receiver, sender_color='#D9E805'):
    return Text.assemble(
        "\n", (sender, f'bold {sender_color}'), " to (", (receiver, 'bold'), "):\n\n"
    )


class RichIOStream(IOStream):
    def __init__(self):
        self.console = Console()

    def send(self, original_message: Any) -> None:
        # for most messages we want to display the preset message models except for conversable_agent._print_received_message
        # where we want to beautify the terminal output
        if isinstance(original_message, TextEvent) and original_message.type == 'text':
            message_content = original_message.content
            message = getattr(message_content, 'content')
            sender_name = getattr(message_content, 'sender')
            recipient_name = getattr(message_content, 'recipient')
            processed_args = []
            blocks = parse_content_blocks(message)

            if len(blocks) == 1 and blocks[0]['type'] == BlockType.TEXT:
                processed_args.append(
                    format_agent_conversation_header(sender_name, recipient_name)
                )
                processed_args.append(message)
                processed_args.append(line_separator)
            else:
                processed_args.append(
                    format_agent_conversation_header(sender_name, recipient_name)
                )
                processed_args += create_renderable_blocks(blocks)
            self.console.print(markup=False, *processed_args)
        else:
            original_message.print()

    def input(self, prompt: str = "", *, password: bool = False) -> str:
        return prompt_utils.ask_for_prompt_input(prompt)


default_rich_io_stream = RichIOStream()


def set_custom_IO_overrides():
    IOStream.set_global_default(default_rich_io_stream)
