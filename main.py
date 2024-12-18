import asyncio
import os
import google.generativeai as genai
from PIL import Image, ImageFont, ImageDraw
import requests
import random
import textwrap
from instagrapi import Client
import time
from instagrapi.types import Media as OriginalMedia
from typing import Union
from tools import create_image_video, create_text_video
from moviepy.editor import CompositeVideoClip, AudioFileClip
from pathlib import Path
import edge_tts
import uuid  # Import uuid to generate unique filenames

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create the model (adjust settings as needed)
generation_config = {
    "temperature": 2,
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

images_folder = 'images'
audio_folder = 'music'
output_video = 'output_video.mp4'
time_per_image = 0.15
num_images = 30
video_size = (1080, 1920)

# Text styling variables
font_path_quote = "fonts/SitkaB.ttc"
font_path_author = "fonts/BRITANIC.TTF"
font_path_watermark = "fonts/arial.ttf"
text_color = (255, 255, 255)
border_color = (0, 0, 0)
border_width = 6
line_spacing = 20
fontsize_quote = 70
fontsize_author = 50
fontsize_watermark = 50
margin_between_quote_and_author = 40
username = "the.verse.weaver"

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
    img = img.crop((left, top, right, bottom)).resize((1080, 1080)).convert("RGBA")

    draw = ImageDraw.Draw(img)

    # Extract content parts
    heading = content_data.get('heading', '')
    main_content = content_data.get('main_content', '')

    font_path = "fonts/Neuton-Regular.ttf"
    font2 = "fonts/Roboto-Regular.ttf"
    font_heading = ImageFont.truetype(font_path, size=45)  # 1.5x bigger
    font_content = ImageFont.truetype(font2, size=33)  # 1.5x bigger
    watermark_font = ImageFont.truetype(font_path, size=20)  # Watermark font size

    # Calculate text dimensions
    heading_width, heading_height = draw.textsize(heading, font=font_heading)
    content_lines = textwrap.wrap(main_content, width=50)
    total_content_height = sum(draw.textsize(line, font=font_content)[1] for line in content_lines) + (len(content_lines) - 1) * 35

    # Determine block dimensions
    block_width = max(heading_width, max(draw.textsize(line, font=font_content)[0] for line in content_lines)) + 50
    block_height = heading_height + total_content_height + 50

    # Calculate block position to center it
    block_left = (img.width - block_width) // 2
    block_top = (img.height - block_height) // 2

    # Draw curved rectangle block
    radius = 30
    draw.rectangle([(block_left + radius, block_top), (block_left + block_width - radius, block_top + block_height)], fill=(255, 255, 255, 5))
    draw.rectangle([(block_left, block_top + radius), (block_left + block_width, block_top + block_height - radius)], fill=(255, 255, 255, 5))

    # Add watermark text
    watermark_text = "ARM"
    watermark_width, watermark_height = draw.textsize(watermark_text, font=watermark_font)
    draw.text((block_left + (block_width - watermark_width) // 2, block_top + block_height - watermark_height - 10), watermark_text, font=watermark_font, fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

    # Adding text to the image
    draw.text(((block_left + block_width // 2) - heading_width // 2, block_top + heading_height // 2), heading, font=font_heading, fill='black', anchor='mm')
    for i, line in enumerate(content_lines):
        line_width, line_height = draw.textsize(line, font=font_content)
        draw.text(((block_left + block_width // 2) - line_width // 2, block_top + heading_height + 25 + i * (line_height + 35)), line, font=font_content, fill='black', anchor='mm')

    img.save("random_content.png")  

def post_to_instagram(client, content_data):  
    png_image_path = 'random_content.png'
    jpg_image_path = 'random_content.jpg'

    # PNG to JPEG
    img = Image.open(png_image_path).convert("RGB")
    img.save(jpg_image_path, "JPEG")

    max_retries = 3
    for retries in range(max_retries):
        try:
            client.photo_upload(jpg_image_path, caption=f"{content_data['image_caption']}\n{content_data['hashtags']}")
            print("Post successful!")
            break
        except Exception as e:
            print(f"Error posting to Instagram: {e}. Retrying ({retries + 1}/{max_retries})...")
            time.sleep(60)  # Wait for 60 seconds before retrying

def get_content():
    max_retries = 3
    for retries in range(max_retries):
        try:
            chat_session = model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": [
                            "From now on you're a autopost bot for my Instagram account username @the.verse.weaver and I'm its owner, refer me as ARM\n\nIts a literature based account that promotes literary and informative ideas by posting plagiarism free content based on one of following topics from the list\n1. short poetry\n2. poems\n3. jokes\n4. shocking facts\n5. relatable day to day life things\n6. relatable quotes\n7. depressed quotes\n8. 2 line-horror stories\n9. very short stories\n10. heart breaking facts\n11. human psychology\n12. human psychology facts\n\n\nand from now on whenever I'll write the word \"content\" to you \nYou will will send me any random relevant content to post on my page (keep the language simple and understandable to the people and it must pique curiosity)\nYou can even choose other fun and eye catching entertainment content suiting to the users needs. Make sure to add a lot of hashtags to ensure that it reaches a lot of people and use atleast 25 bare minimum relatable hashtags for every post.\n\nthe format is as follows\n\n$Heading$ short heading in between $$\n\n(Main Content)\n\n[Caption] Must relate to main content and be within []\n\n{#Hashtags} upto 25 single word hashtags are must including '#' relating to content or heading within {} with space as the only separator in it",
                        ],
                    },
                    {
                        "role": "model",
                        "parts": [
                            "Okay, I understand! I'm ready to be your autopost bot for @the.verse.weaver. Just say \"content\" whenever you need a post, and I'll provide a suggestion in the requested format. \n\nLet's weave some literary magic! ✨ \n",
                        ],
                    },
                ]
            )

            response = chat_session.send_message("content")
            content_data = {}
            lines = response.text.splitlines()
            for line in lines:
                if line.startswith("$"):
                    content_data['heading'] = line.strip("$$")
                elif line.startswith("("):
                    content_data['main_content'] = line.strip("()").strip()
                elif line.startswith("["):
                    content_data['image_caption'] = line.strip("[]").strip()
                elif line.startswith("{"):
                    content_data['hashtags'] = line.strip("{}").strip()

            return content_data

        except Exception as e:
            print(f"Error getting content from Gemini: {e}. Retrying ({retries + 1}/{max_retries})...")
            time.sleep(60) 

chat_session2 = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        "youre a reel poster bot for @the.verse.weaver and u generates quotes like the following and in same format but one at a time whenever i say my magic word that is \"bazinga\"\n\nquotes = [\n{\"content\": \"The best time to plant a tree was 20 years ago. The second best time is now.\", \"author\": \"Chinese Proverb\"},\n{\"content\": \"An unexamined life is not worth living.\", \"author\": \"Socrates\"},\n{\"content\": \"Eighty percent of success is showing up.\", \"author\": \"Woody Allen\"},\n{\"content\": \"Your time is limited, so don’t waste it living someone else’s life.\", \"author\": \"Steve Jobs\"},\n{\"content\": \"The only way to do great work is to love what you do.\", \"author\": \"Steve Jobs\"},\n]\n\nif the quote has no author and is widely known write the author as unknown and if the quote is plagiarism free then author should be the.verse.weaver",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, I'm ready to weave some quote magic!  Just say \"**bazinga**\" and I'll create a reel-ready quote poster for @the.verse.weaver. ✨ \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "bazinga\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "## \"The best time to plant a tree was 20 years ago. The second best time is now.\" \n\n- *Chinese Proverb*\n\n@the.verse.weaver \n\n(Image:  Choose an image related to nature, growth, or opportunity) \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "bazinga\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "##  \"An unexamined life is not worth living.\"\n\n- *Socrates*\n\n@the.verse.weaver\n\n(Image: A thought-provoking image like a person deep in thought, a labyrinth, or a mirror) \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "dont use my quotes but generate by yourself\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Understood!  From now on, I'll be crafting original quotes for @the.verse.weaver.  \n\nHit me with that \"**bazinga**\" whenever you're ready for a fresh dose of inspiration. ✨ \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "bazinga\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "##  \"The universe whispers in possibilities, it's up to you to shout back with action.\"\n\n- @the.verse.weaver\n\n(Image:  A striking image of a person shouting towards a vast starry sky, a hand reaching out to touch a galaxy, or something similarly inspiring) \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "remove that image suggestion or whatever\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, I'll leave the image suggestions out. Just the quote from now on!\n\nLet me know when you're ready for another quote with \"bazinga\".  💫 \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "bazinga\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "## \"Let your stumbles be stepping stones, your doubts be fuel for courage, and your scars be reminders of battles won.\"\n\n- @the.verse.weaver \n",
      ],
    },
    {
      "role": "user",
      "parts": [
        "Whenever I'll write \"**cabinza**\" your task is to give 15 to 20 most relatable quote and reel hashtags related to content which may be motivation, poetry, success logic or any related general content and if its content is not clear add general reel and most trending hashtags and only hashtags without any comment text and text formatting.\n",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, I'm ready to generate the quote related hashtags! Just say \"**cabinza**\" and I'll add all most trending quote hashtags for @the.verse.weaver. ✨ \n",
      ],
    },
  ]
)


async def generate_tts_audio(text):
    """Generate TTS audio using Edge-TTS with a unique filename."""
    unique_filename = f"quote_audio_{uuid.uuid4()}.wav"  # Create a unique filename
    communicate = edge_tts.Communicate(text, voice='en-US-BrianNeural', output_format='audio-16khz-32bit-mono-pcm')
    with open(unique_filename, 'wb') as audio_file:
        await communicate.save(audio_file)
    return unique_filename  # Return the unique filename

def generate_hashtags():
    response = chat_session2.send_message("cabinza")
    hashtags_text = response.text.strip()
    return hashtags_text
    
def generate_quote():
    response = chat_session2.send_message("bazinga")
    quote_text = response.text.strip()
    quote = {}
    lines = quote_text.splitlines()
    quote['content'] = lines[0].strip("## ").strip()
    quote['author'] = lines[2].strip("- ").strip()
    return quote

async def create_and_post_reel(client):
    image_video = create_image_video(images_folder, num_images, time_per_image, video_size)

    # Generate a quote using Gemini
    quote = generate_quote()

    # Create the text video
    text_clip = create_text_video(video_size, quote, font_path_quote, font_path_author, font_path_watermark,
                                   text_color, border_color, border_width, line_spacing,
                                   fontsize_quote, fontsize_author, fontsize_watermark, 
                                   margin_between_quote_and_author, username)

    '''text_clip = text_clip.set_position(("center", "center"), relative=True).set_duration(image_video.duration)

    # Combine the image video with the text video
    final_video = CompositeVideoClip([image_video, text_clip])

    # Get a random audio file from the audio folder
    audio_files = os.listdir(audio_folder)
    random_audio_file = random.choice(audio_files)
    audio_path = os.path.join(audio_folder, random_audio_file)

    # Load the audio file
    audio_clip = AudioFileClip(audio_path).subclip(0, final_video.duration)

    # Set the audio for the final video
    final_video = final_video.set_audio(audio_clip)

    # Write the final video to a file
    final_video.write_videofile(output_video, fps=24)'''
    text_clip = text_clip.set_position(("center", "center"), relative=True).set_duration(image_video.duration)
    tts_audio_file = await generate_tts_audio(quote['content'])
    audio_clip = AudioFileClip(tts_audio_file)
    final_video = CompositeVideoClip([image_video, text_clip]).set_audio(audio_clip)
    final_video.write_videofile(output_video, fps=24)
    caption = f"✨✨ @the.verse.weaver\n{generate_hashtags()}"
    client.clip_upload(Path(output_video), caption)

if __name__ == "__main__":
    user_name = os.getenv('INSTAGRAM_USERNAME')
    password = os.getenv('INSTAGRAM_PASSWORD')

    client = Client()  # Create the client object
    client.login(user_name, password)  # Log in only once

    while True:
        content_data = get_content()
        create_image_with_content(content_data)
        post_to_instagram(client, content_data)
        asyncio.run(create_and_post_reel(client))  # Use asyncio.run to call the async function
        time.sleep(7200)  # Sleep for 2 hours (7200 seconds)
