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
from typing import Union

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

class Media(OriginalMedia):
    pk: Union[str, int]

# Function to create an image with the content
def create_image_with_content(content_data):
    color_picker = (1, 31, 102)
    img = Image.new('RGB', (800, 800), color=color_picker)
    draw = ImageDraw.Draw(img)

    # Extract content parts
    heading = content_data.get('heading', '')
    main_content = content_data.get('main_content', '')
    image_caption = content_data.get('image_caption', '')
    hashtags = content_data.get('hashtags', '')

    font_path = "fonts/Neuton-Regular.ttf"
    font_heading = ImageFont.truetype(font_path, size=30)  
    font_content = ImageFont.truetype(font_path, size=22)  

    # Positions in the image
    heading_position = (50, 50)
    content_position = (50, 100)
    caption_position = (50, 550)

    # Multiple lines for content
    max_line_length = 50
    content_lines = textwrap.wrap(main_content, width=max_line_length)
    
    # Adding it to an image
    draw.text(heading_position, heading, font=font_heading, fill='white')
    for i, line in enumerate(content_lines):
        if i == 0:
            draw.text((content_position[0], content_position[1] + i*35), line, font=font_content, fill='white')
        else:
            draw.text((content_position[0], content_position[1] + i*35), line, font=font_content, fill='white')

    draw.text(caption_position, image_caption + " " + hashtags, font=font_content, fill='white')

    img.save("random_content.png")

# Automate posts on Instagram
def post_to_instagram():
    user_name = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    png_image_path = 'random_content.png'
    jpg_image_path = 'random_content.jpg'

    # PNG to JPEG
    img = Image.open(png_image_path)
    img.convert("RGB").save(jpg_image_path, "JPEG")

    client = Client()
    client.login(user_name, password)
    client.photo_upload(jpg_image_path, caption=" ")

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
            {
                "role": "user",
                "parts": [
                    "content\n",
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
    post_to_instagram()
    time.sleep(7200) # Sleep for 2 hours (7200 seconds)

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

# Example of using the model (can be removed)
# response = model.generate_text(prompt="Write a short poem about the ocean.")
# print(response.text)
