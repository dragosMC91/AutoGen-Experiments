from agents import custom_agents
from sys import argv
from operator import itemgetter

code_to_review = """
write 2 test cases for the section of the bayut.com website in the following image:
<img /Users/dragoscampean/Desktop/bayut.jpg>
"""

user_proxy, image_analyst = itemgetter('user_proxy', 'image_analyst')(
    custom_agents.get_agents()
)

# the assistant receives a message from the user, which contains the task description
user_proxy.initiate_chat(
    image_analyst,
    message=f"""
    Analyze this image:
    ```````````````````````````
    <img {argv[1]}>
    ```````````````````````````
    """
    if len(argv) > 1
    else code_to_review,
)
