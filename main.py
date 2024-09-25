import os
import google.generativeai as genai
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import requests
import random
import textwrap
from instagrapi import Client
import time
from instagrapi.types import Media as OriginalMedia
from typing import Union

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model (adjust settings as needed)
generation_config = {
  "temperature": 1.7,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)


class Media(OriginalMedia):
    pk: Union[str, int]

"""
def create_image_with_content(content_data):
    image_path = random.choice(os.listdir("aryan"))  # Choose random image from "aryan" folder
    image_path = os.path.join("aryan", image_path)
    img = Image.open(image_path)  # Open the image

    # Crop to square for Instagram
    width, height = img.size
    min_dimension = min(width, height)
    left = (width - min_dimension) // 2
    top = (height - min_dimension) // 2
    right = left + min_dimension
    bottom = top + min_dimension
    img = img.crop((left, top, right, bottom))
    img = img.resize((1080, 1080))  # Resize to 1080x1080

    draw = ImageDraw.Draw(img)

    # Extract content parts
    heading = content_data.get('heading', '')
    main_content = content_data.get('main_content', '')

    font_path = "fonts/Neuton-Regular.ttf"
    font_heading = ImageFont.truetype(font_path, size=30)  
    font_content = ImageFont.truetype(font_path, size=22)  

    # Positions in the image (adjust as needed)
    heading_position = (50, 50)
    content_position = (50, 100)

    # Multiple lines for content
    max_line_length = 50
    content_lines = textwrap.wrap(main_content, width=max_line_length)

    # Draw transparent square block (adjust size and position)
    block_width = 700
    block_height = 400
    block_left = (img.width - block_width) // 2
    block_top = (img.height - block_height) // 2
    draw.rectangle(
        [(block_left, block_top), (block_left + block_width, block_top + block_height)],
        fill=(255, 255, 255, 90),  # White with 150 opacity (semi-transparent)
    )

    # Adding text to the image
    draw.text(heading_position, heading, font=font_heading, fill='black')
    for i, line in enumerate(content_lines):
        if i == 0:
            draw.text((content_position[0], content_position[1] + i*35), line, font=font_content, fill='black')
        else:
            draw.text((content_position[0], content_position[1] + i*35), line, font=font_content, fill='black')

    img.save("random_content.png")
"""
def create_image_with_content(content_data):
    image_path = random.choice(os.listdir("aryan"))  # Choose random image from "aryan" folder
    image_path = os.path.join("aryan", image_path)
    img = Image.open(image_path)  # Open the image

    # Crop to square for Instagram
    width, height = img.size
    min_dimension = min(width, height)
    left = (width - min_dimension) // 2
    top = (height - min_dimension) // 2
    right = left + min_dimension
    bottom = top + min_dimension
    img = img.crop((left, top, right, bottom))
    img = img.resize((1080, 1080))  # Resize to 1080x1080

    draw = ImageDraw.Draw(img)

    # Extract content parts
    heading = content_data.get('heading', '')
    main_content = content_data.get('main_content', '')

    font_path = "fonts/Neuton-Regular.ttf"
    font_heading = ImageFont.truetype(font_path, size=30)  
    font_content = ImageFont.truetype(font_path, size=22)  

    # Calculate text dimensions
    heading_width, heading_height = draw.textsize(heading, font=font_heading)
    total_content_height = sum([draw.textsize(line, font=font_content)[1] for line in content_lines])
    total_content_height += (len(content_lines) - 1) * 35  # Account for line spacing

    # Calculate center positions for heading and content
    heading_center_x = img.width // 2 - heading_width // 2
    heading_center_y = img.height // 2 - heading_height // 2 - total_content_height // 2
    content_center_x = img.width // 2
    content_center_y = img.height // 2 + total_content_height // 2

    # Draw transparent square block (adjust size and position)
    block_width = 700
    block_height = 400
    block_left = (img.width - block_width) // 2
    block_top = (img.height - block_height) // 2
    draw.rectangle(
        [(block_left, block_top), (block_left + block_width, block_top + block_height)],
        fill=(255, 255, 255, 50),  # White with 100 opacity (more transparent)
    )

    # Adding text to the image
    draw.text((heading_center_x, heading_center_y), heading, font=font_heading, fill='black', anchor='mm')  # Center align heading
    for i, line in enumerate(content_lines):
        line_width, line_height = draw.textsize(line, font=font_content)
        line_center_x = content_center_x - line_width // 2
        line_center_y = content_center_y + i * (line_height + 35) - total_content_height // 2
        draw.text((line_center_x, line_center_y), line, font=font_content, fill='black', anchor='mm')  # Center align content lines

    img.save("random_content.png")


# Automate posts on Instagram
def post_to_instagram(content_data):  # Pass content_data to this function
    user_name = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    png_image_path = 'random_content.png'
    jpg_image_path = 'random_content.jpg'

    # PNG to JPEG
    img = Image.open(png_image_path)
    img.convert("RGB").save(jpg_image_path, "JPEG")

    client = Client()
    client.login(user_name, password)
    client.photo_upload(jpg_image_path, caption=f"{content_data['image_caption']}\n{content_data['hashtags']}")  # Use caption and hashtags from content_data

# Generate content using Gemini API
def get_content():
    # Initialize the chat session
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "From now on you're a autopost bot for my Instagram account username @the.verse.weaver and I'm its owner, refer me as ARM\n\nIts a literature based account that promotes literary and informative ideas by posting plagiarism free short poetry, poems, jokes, shocking facts, relatable day to day life things, relatable quotes, depressed quotes, 2 line-horror stories, very short stories, heart breaking facts, human psychology and other fun and eye catching entertainment content.\n\nand from now on whenever I'll write the word \"content\" to you \nYou will will send me any random relevant content to post on my page (keep the language simple and understandable to the people and it must pique curiosity)\n\nthe format is as follows\n\n$Heading$ short heading in between $$\n\n(Main Content)\n\n[Image Caption] Must relate to main content and be within []\n\n{#Hashtags} upto 29 single word hashtags including '#' relating to content or heading within {}",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "Okay, I'm ready to be your autopost bot for @the.verse.weaver! Just tell me when you want some \"content\" and I'll generate a random post for you following the format you provided. Let's weave some captivating stories together! \n\nARM, please let me know whenever you need a new post and I'll be happy to create something engaging. \n",
                ],
            },
        ]
    )

    # Get the response from the model
    response = chat_session.send_message("content")

    # Extract the content parts from the response
    content_data = {}
    lines = response.text.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("##"):
            content_data['heading'] = line.strip("## ")
        elif line.startswith("("):
            content_data['main_content'] = line.strip("()").strip()
        elif line.startswith("["):
            content_data['image_caption'] = line.strip("[]").strip()
        elif line.startswith("{"):
            content_data['hashtags'] = line.strip("{}").strip()

    return content_data

# Main loop for posting content every 2 hours
while True:
    content_data = get_content()
    create_image_with_content(content_data)
    time.sleep(10)
    post_to_instagram(content_data)
    time.sleep(7200) # Sleep for 2 hours (7200 seconds)
