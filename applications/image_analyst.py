from agents import custom_agents
from utils import prompt_utils

message = """
write 2 test cases for the section of the bayut.com website in the following image:
<img /Users/dragoscampean/Desktop/bayut.jpg>
"""

user_proxy, image_analyst = custom_agents.get_agents(
    names=['user_proxy', 'image_analyst']
).values()

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    image_analyst,
    message=f"""
    Analyze this image:
    ```````````````````````````
    <img {prompt_utils.get_initial_prompt(message)}>
    ```````````````````````````
    """,
)
