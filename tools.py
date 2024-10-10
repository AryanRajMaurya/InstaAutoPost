import os
import random
from moviepy.editor import ImageClip, concatenate_videoclips, ColorClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import numpy as np




# Utility functions and tools

def crop_to_cover(image, target_size):
    img_ratio = image.width / image.height
    target_ratio = target_size[0] / target_size[1]

    if img_ratio > target_ratio:
        new_width = int(target_ratio * image.height)
        offset = (image.width - new_width) // 2
        image = image.crop((offset, 0, offset + new_width, image.height))
    else:
        new_height = int(image.width / target_ratio)
        offset = (image.height - new_height) // 2
        image = image.crop((0, offset, image.width, offset + new_height))

    return image

def wrap_text(text, max_chars=24):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars:
            if current_line:
                current_line += " " + word
            else:
                current_line = word
        else:
            lines.append(current_line)
            current_line = word
    
    if current_line:  # Add the last line if it's not empty
        lines.append(current_line)

    return "\n".join(lines)


def create_image_video(images_folder, num_images, time_per_image, video_size):
    image_files = random.sample(os.listdir(images_folder), num_images)
    clips = []

    for image_file in image_files:
        image_path = os.path.join(images_folder, image_file)
        
        with Image.open(image_path) as img:
            img = crop_to_cover(img, video_size)
            temp_image_path = "temp_image.png"
            img.save(temp_image_path)
        
        image_clip = ImageClip(temp_image_path).set_duration(time_per_image).resize(video_size)
        black_overlay = ColorClip(size=video_size, color=(0, 0, 0)).set_opacity(0.65).set_duration(time_per_image)
        final_clip = CompositeVideoClip([image_clip, black_overlay])
        clips.append(final_clip)

    return concatenate_videoclips(clips, method="compose")


def create_text_video(video_size, quote, font_path_quote, font_path_author, font_path_watermark, 
                       text_color, border_color, border_width, line_spacing, fontsize_quote, fontsize_author, 
                       fontsize_watermark, margin_between_quote_and_author, username):
    def wrap_text(text, max_chars=24):
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:  # Add the last line if it's not empty
            lines.append(current_line)

        return "\n".join(lines)

    
    quote_text = wrap_text(quote["content"])
    author_text= wrap_text(quote["author"])
    
    def create_text_image(quote, author, font_path_quote, font_path_author, fontsize_quote, fontsize_author,
                           font_path_watermark, fontsize_watermark,username, text_color, border_color,
                           border_width, size, line_spacing, margin_between_quote_and_author,opacity=0.5):
        
        font_quote = ImageFont.truetype(font_path_quote, fontsize_quote)
        font_author = ImageFont.truetype(font_path_author, fontsize_author)
        font_watermark = ImageFont.truetype(font_path_watermark, fontsize_watermark)
        wrapped_quote = wrap_text(quote)
        
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        quote_lines = wrapped_quote.split("\n")
        max_line_width = 0
        total_text_height = 0
        for line in quote_lines:
            text_width, text_height = draw.textsize(line, font=font_quote)
            max_line_width = max(max_line_width, text_width)
            total_text_height += text_height + line_spacing

        text_position_y = (size[1] - (total_text_height + fontsize_author + margin_between_quote_and_author)) // 2 - 300
        
        enclosed_quote = f'"{quote}"'
        quote_lines = wrap_text(enclosed_quote).split("\n")
        
        # quote text writing 
        for line in quote_lines:
            text_width, text_height = draw.textsize(line, font=font_quote)
            position_x = (size[0] - text_width) // 2
            position_y = text_position_y
            
            for adj in range(-border_width, border_width + 1):
                draw.text((position_x + adj, position_y), line, font=font_quote, fill=border_color)
                draw.text((position_x, position_y + adj), line, font=font_quote, fill=border_color)
                draw.text((position_x + adj, position_y + adj), line, font=font_quote, fill=border_color)
            
            draw.text((position_x, position_y), line, font=font_quote, fill=text_color)
            text_position_y += text_height + line_spacing
        
        # quote author writing 
        author_position_y = text_position_y + margin_between_quote_and_author
        for line in author.split("\n"):
            text_width, text_height = draw.textsize(line, font=font_author)
            position_x = (size[0] - text_width) // 2
            draw.text((position_x, author_position_y), f"____ {line}", font=font_author, fill=text_color)
            author_position_y += text_height
            
            
            
        watermark_text = f"@{username}"
        watermark_text_width, watermark_text_height = draw.textsize(watermark_text, font=font_watermark)
        watermark_position_x = (size[0] - watermark_text_width) // 2
        watermark_position_y = int(1200)
        draw.text((watermark_position_x, watermark_position_y), watermark_text, font=font_watermark, fill=(255, 255, 255, int(255 * opacity)))

        return np.array(image)

    text_image = create_text_image(quote_text, author_text,
                                   font_path_quote,
                                   font_path_author,
                                   fontsize_quote,
                                   fontsize_author,
                                   font_path_watermark,
                                   fontsize_watermark,
                                   username,
                                   text_color,
                                   border_color,
                                   border_width,
                                   video_size,
                                   line_spacing,
                                   margin_between_quote_and_author,
                                   opacity=0.5
                                )

    text_clip = ImageClip(text_image, duration=5)
    return text_clip


