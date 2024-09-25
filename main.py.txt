import os
import random
import textwrap
import time
from PIL import Image, ImageFont, ImageDraw
from instagrapi import Client
import google.generativeai as genai

# Configure your Google AI API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model
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
    {
      "role": "model",
      "parts": [
        "##  $The Price of Perfection$ \n\n(Imagine a world where every day was meticulously planned, where every emotion was controlled, and where every decision was flawless. Sounds great, right? But what if that perfection came at the cost of your individuality, your spontaneity, your ability to make mistakes? Would you trade your human flaws for a perfect life? )\n\n[A hand reaches out towards a vibrant butterfly, but just before touching it, the butterfly vanishes, leaving only a shimmering trail of light.]\n\n{#perfection, #flaws, #humanity, #choice, #individuality, #reflection, #thoughtprovoking, #poetry, #philosophy, #life, #theverseweaver} \n",
      ],
    },
  ]
)

response = chat_session.send_message("INSERT_INPUT_HERE")

print(response.text)

# Function to create an image with the generated content
def create_image_with_content(heading, main_content, caption, hashtags):
    color_picker = (255, 255, 255)  # White background
    img = Image.new('RGB', (800, 800), color=color_picker)
    draw = ImageDraw.Draw(img)

    font_path = "fonts/Neuton-Regular.ttf"
    font = ImageFont.truetype(font_path, size=30)

    # Text positions
    heading_position = (50, 50)
    content_position = (50, 150)
    #caption_position = (50, 650)

    # Adding text to the image
    draw.text(heading_position, f"{heading}", font=font, fill=(0, 0, 0))  # Black text
    wrapped_content = textwrap.fill(main_content, width=40)
    draw.text(content_position, wrapped_content, font=font, fill=(0, 0, 0))
    #draw.text(caption_position, caption + " " + hashtags, font=font, fill=(0, 0, 0))

    # Save the image
    img.save("post_image.png")

# Automate posts on Instagram
def post_to_instagram():
    user_name = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    # Prepare image for posting
    jpg_image_path = 'post_image.jpg'
    img = Image.open("post_image.png")
    img.convert("RGB").save(jpg_image_path, "JPEG")

    # Login and post
    client = Client()
    client.login(user_name, password)
    caption = f"{caption} {hashtags}"  # Combine caption and hashtags
    client.photo_upload(jpg_image_path, caption)

# Main loop to generate content and post every 2 hours
while True:
    # Generate content
    
    response = chat_session.send_message("content")
    content = response.text

    # Split the content into heading, main content, caption, and hashtags
    heading = "Your Heading Here"  # Customize as needed
    main_content = content  # Use the generated response as main content
    caption = "Check out this content!"  # Customize as needed
    hashtags = "{#example, #hashtags, #related}"  # Customize as needed

    create_image_with_content(heading, main_content, caption, hashtags)
    post_to_instagram()

    time.sleep(7200)  # Wait for 2 hours



"""

# Main loop to run every 2 hours
while True:
    content = get_random_content()
    caption = create_image_with_content(content)
    post_to_instagram(caption)
    print(f"Posted to Instagram at {datetime.now()}")
    time.sleep(2 * 60 * 60)  # Sleep for 2 hours
"""
