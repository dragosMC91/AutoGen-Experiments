from agents import custom_agents
from utils import prompt_utils
from autogen.agentchat.contrib.capabilities import generate_images
import os
import time

message = """
"""

image_generator = custom_agents.get_agents(names=['image_generator'])["image_generator"]

resolution = prompt_utils.ask_for_prompt_with_completer(
    prompt='Select Resolution (press Tab for options): ',
    options=['1024x1024', '1024x1792', '1792x1024'],
)
quality = prompt_utils.ask_for_prompt_with_completer(
    prompt='Select Image Quality (press Tab for options): ', options=['standard', 'hd']
)
image_path = f"{os.getcwd()}/dalle_art/{time.time()}.png"
image_description = prompt_utils.get_initial_prompt()

generator = generate_images.DalleImageGenerator(
    image_generator.llm_config, resolution=resolution, quality=quality, num_images=1
)


@prompt_utils.with_progress_bar(description='Generating image...')
def generate_image():
    return generator.generate_image(image_description)


image = generate_image()
image.save(image_path)
print(f"Generated image saved to {image_path}")

# https://github.com/microsoft/autogen/blob/main/notebook/agentchat_image_generation_capability.ipynb
