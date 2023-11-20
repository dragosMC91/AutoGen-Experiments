from agents import custom_agents
from operator import itemgetter
from sys import argv

# for complex tasks the user can edit this message and execute the script via `python applications/generalist.py`
# for simple queries the user can just execute `python applications/generalist.py "my question"`.
multiline_message = """
I want to create a sensor display for my pc which shows the cpu, gpu and RAM usage and temperature
and also the power consumption for the cpu and gpu. can you create an aida64 skin with this information?
the display resolution is 1024x600
"""

user_proxy, advanced_assistant = itemgetter('user_proxy', 'advanced_assistant')(
    custom_agents.get_agents()
)

# the assistant receives a message from the user, which contains the task description
# the more explicit the description the better.
user_proxy.initiate_chat(
    advanced_assistant,
    # the input passed to the python command takes precedence over the multiline_message defined here
    message=argv[1] if len(argv) > 1 else multiline_message,
)
