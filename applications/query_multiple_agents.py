import concurrent.futures

from agents import custom_agents
from utils import prompt_utils
from typing import Annotated
from autogen.agentchat.group import ContextVariables
from autogen import register_function, ConversableAgent
from rich import print
from rich.table import Table
from rich.console import Group
from typing import Dict, Tuple
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text

# relevant resources:
# https://docs.ag2.ai/docs/user-guide/advanced-concepts/pattern-cookbook/redundant
# https://docs.ag2.ai/latest/docs/use-cases/notebooks/notebooks/run_and_event_processing/#sequential-run

# --- Agents creation section ---
assistant_name = prompt_utils.ask_for_prompt_with_completer(
    options=custom_agents.get_agents_options()
)

factory = custom_agents.AgentFactory()

user_proxy = factory.create_agent(
    name="user_proxy",
    config=custom_agents.Configs.gemini_25_flash,
    auto_execute_functions=True,
)
taskmaster_agent = factory.create_agent(
    name="advanced_assistant",
    custom_name='taskmaster_agent',
    config=custom_agents.Configs.gpt_5,
)

taskmaster_agent.update_system_message(
    """You are the Task Manager responsible for managing a conversation with a user.

    Your role is to:
    1. Understand the user's request and frame it as a clear task
    2. Initiate the task to be processed by multiple independent agents
    3. Return to the user with the final selected result

    For each request:
    1. Use the ask_agents tool to start the process for all user queries
    2. Write a clear task which reflects the user's query
    3. Each new task must be self contained, meaning the task must make sense in isolation so details from previous replies must be included.
    You might include code snippets from previous queries so agents understand the context.
    4. After all agents have submitted their results and evaluation is complete, present the final result to the user
    without editing it in any way!

    Important: never reply yourself ! always try to pass the query to the user query + appropriate context to the independent agents!
    """
)
# temporarily disabled and rely on human eval
evaluator_agent = factory.create_agent(
    name="advanced_assistant",
    custom_name='evaluator_agent',
    config=custom_agents.Configs.gemini_25_pro,
)
evaluator_agent.update_system_message(
    """You are the Evaluator Agent responsible for assessing multiple approaches to the same task and selecting or synthesizing the best result.
    Your role is to:
    1. Carefully review each approach and result
    2. Evaluate each solution based on criteria appropriate to the task type
    3. Assign scores to each approach on a scale of 1-10
    4. Either select the best approach or synthesize a superior solution by combining strengths

    When appropriate, rather than just selecting a single approach, synthesize a superior solution by combining the strengths of multiple approaches.

    Use the evaluate_and_select tool to submit your final evaluation, including detailed scoring and rationale.""",
)
assistant_1 = factory.create_agent(
    name=assistant_name,
    custom_name='assistant_1',
    config=custom_agents.Configs.gpt_5,
    show_loading_animation=False,
)
assistant_2 = factory.create_agent(
    name=assistant_name,
    custom_name='assistant_2',
    config=custom_agents.Configs.gemini_25_pro,
    show_loading_animation=False,
)
assistant_3 = factory.create_agent(
    name=assistant_name,
    custom_name='assistant_3',
    config=custom_agents.Configs.claude_4_sonnet,
    show_loading_animation=False,
)

# Silence outputs for more granular control of terminal output
assistant_1.silent = True
assistant_2.silent = True
assistant_3.silent = True

# Shared context for tracking important conversation attributes and redundant agent
# results (shared_context not included in the context window but agents can access it)
shared_context = ContextVariables(
    data={
        # Process state
        "task_initiated": False,
        "task_completed": False,
        "evaluation_complete": False,
        # Task tracking
        "current_task": "",
        "approach_count": 0,
        # Results from different agents
        "assistant_1_result": None,
        "assistant_2_result": None,
        "assistant_3_result": None,
        "aggregated_responses": None,
        # Evaluation metrics
        "evaluation_scores": {},
        "final_result": None,
        "selected_approach": None,
    }
)


# --- UI Generation Functions ---
def make_layout() -> Layout:
    """Defines the layout of the terminal UI."""
    layout = Layout(name="root")
    layout.split_row(
        Layout(name="left"),
        Layout(name="middle"),
        Layout(name="right"),
    )
    return layout


def generate_loading_panel(assistant_name: str) -> Panel:
    """Returns a Panel with a loading spinner."""
    return Panel(
        Spinner("dots", text="Fetching response..."),
        title=f"[bold yellow]:hourglass: {assistant_name}",
        border_style="yellow",
        title_align="left",
    )


def generate_result_panel(assistant_name: str, status: str, content: str) -> Panel:
    """Generates a final, styled panel with the full content."""
    if status == "success":
        if isinstance(content, list):
            # If we have a list, group the renderables together.
            renderable_content = Group(*content)
        else:
            # Fallback for simple text content
            renderable_content = Text(content, overflow="fold")
        return Panel(
            renderable_content,
            title=f"[bold green]:heavy_check_mark: {assistant_name}",
            border_style="green",
            title_align="left",
        )
    else:
        return Panel(
            Text(f"An error occurred:\n{content}", style="red"),
            title=f"[bold red]:x: {assistant_name}",
            border_style="red",
            title_align="left",
        )


# Isolates each agent's message history so they only see the task and no other agents' responses
redundant_agents = [assistant_1, assistant_2, assistant_3]
assistant_names = list(map(lambda x: x.name, redundant_agents))


def ask_agent(agent: ConversableAgent, task: str):
    agent_response = agent.run(
        message=task,
        max_turns=1,
    )
    agent_response.process()

    message = agent_response.messages[1]["content"]
    blocks = prompt_utils.parse_content_blocks(message)
    return prompt_utils.create_renderable_blocks(blocks)


def ask_agents(
    task: Annotated[
        str,
        "The task to be processed by multiple agents - needs to be self contained, each task must make sense by itself",
    ],
) -> str:
    """
    Initiate processing of a task across multiple redundant agents with different approaches
    """
    console = Console()
    layout = make_layout()
    layout_names = ["left", "middle", "right"]

    results: Dict[str, Tuple[str, str]] = {}

    # --- Phase 1: Live Updates ---
    # `transient=True` will make the live display disappear when all agents have replied.
    with Live(
        layout, console=console, transient=True, screen=True, refresh_per_second=5
    ) as live:
        live.console.rule("[bold yellow]Fetching responses from assistants")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_assistant = {
                executor.submit(ask_agent, agent, task): agent.name
                for agent in redundant_agents
            }

            for i, agent in enumerate(redundant_agents):
                layout[layout_names[i]].update(generate_loading_panel(agent.name))

            for future in concurrent.futures.as_completed(future_to_assistant):
                assistant_name = future_to_assistant[future]
                layout_name = layout_names[assistant_names.index(assistant_name)]

                try:
                    result_text = future.result()
                    results[assistant_name] = ("success", result_text)
                    layout[layout_name].update(
                        generate_result_panel(
                            assistant_name,
                            "success",
                            result_text,
                        )
                    )
                except Exception as e:
                    error_msg = str(e)
                    results[assistant_name] = ("error", error_msg)
                    # Use the final panel generator here for consistency
                    layout[layout_name].update(
                        generate_result_panel(assistant_name, "error", error_msg)
                    )

    # --- Phase 2: Final Review and Prompt ---
    # The (non scrollable) Live display is now gone. We print the full results.
    final_panels = []
    table = Table.grid(expand=True)
    for name in assistant_names:
        table.add_column(ratio=1)  # Equal width columns
        panel = generate_result_panel(
            name,
            results.get(name, ("error", "Result not found."))[0],
            results.get(name, ("error", "Result not found."))[1],
        )
        final_panels.append(panel)
    table.add_row(*final_panels)
    console.print(table)

    selection = prompt_utils.ask_for_prompt_with_completer(
        prompt="Select the best agent answer (press Tab for options): ",
        options=[*assistant_names, "custom"],
    )

    if selection == 'custom':
        return prompt_utils.ask_for_prompt_input(prompt="Input custom reply:")

    return results[selection]


# Function for evaluator provide their evaluation and select the best result
def evaluate_and_select(
    evaluation_notes: Annotated[str, "Detailed evaluation of each agent's result"],
    score_a: Annotated[int, "Score for Agent A's approach (1-10 scale)"],
    score_b: Annotated[int, "Score for Agent B's approach (1-10 scale)"],
    score_c: Annotated[int, "Score for Agent C's approach (1-10 scale)"],
    selected_result: Annotated[str, "The selected or synthesized final result"],
    selection_rationale: Annotated[
        str, "Explanation for why this result was selected or how it was synthesized"
    ],
    context_variables: ContextVariables,
) -> None:
    """
    Evaluate the different approaches and select or synthesize the best result
    """
    # Create scores dictionary from individual parameters
    scores = {"assistant_1": score_a, "assistant_2": score_b, "assistant_3": score_c}

    context_variables["evaluation_notes"] = evaluation_notes
    context_variables["evaluation_scores"] = scores
    context_variables["final_result"] = selected_result
    context_variables["evaluation_complete"] = True

    # Determine which approach was selected (highest score)
    max_score = 0
    selected_approach = None
    for agent, score in scores.items():
        if score > max_score:
            max_score = score
            selected_approach = agent
    context_variables["selected_approach"] = selected_approach

    print(f"Evaluation complete. Selected result: {selection_rationale[:100]}...")


register_function(
    caller=taskmaster_agent,
    executor=user_proxy,
    f=ask_agents,
    name="ask_agents",
    description="Initiate processing of a task across multiple redundant agents with different approaches - each task is self contained, and must make sense by itself.",
)
register_function(
    caller=evaluator_agent,
    executor=user_proxy,
    f=evaluate_and_select,
    name="evaluate_and_select",
    description="Evaluate the different approaches and select or synthesize the best result",
)

taskmaster_agent.context_variables = shared_context
user_proxy.initiate_chat(
    recipient=taskmaster_agent,
    message=prompt_utils.get_initial_prompt(),
    max_rounds=33,
)
