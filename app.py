# -*- coding: utf-8 -*-
"""app

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1PJvvBKI4QgiizYgiuGEiXfbUtVq64ryi
"""

!pip install streamlit

import streamlit as st
import datetime
import os
import requests
from PIL import Image, ImageOps
from io import BytesIO

# Streamlit title and introduction
st.title("NOAA Weather Data GIF Generator")
st.write("Enter the parameters below to generate and download a weather-related GIF.")

# Input Fields
date_input = st.date_input("Select the date (YYYY-MM-DD):", datetime.date.today())
start_hour = st.number_input("Start Hour (UTC, 0-23):", min_value=0, max_value=23, value=0)
end_hour = st.number_input("End Hour (UTC, 0-23):", min_value=0, max_value=23, value=12)
parameter = st.text_input("Enter the parameter (e.g., 8fnt):", "8fnt")

# Convert date input to the required string format (YYYYMMDD)
date_str = date_input.strftime("%Y%m%d")

# Define helper functions
def fetch_image(date, hour, parameter):
    base_url = "https://www.spc.noaa.gov/exper/ma_archive/images_s4"
    url = f"{base_url}/{date}/{hour:02d}_{parameter}.gif"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            image = Image.open(BytesIO(response.content)).convert("RGBA")
            white_bg = Image.new("RGBA", image.size, "WHITE")
            combined = Image.alpha_composite(white_bg, image)
            return combined.convert("RGB")
        except Exception as e:
            print(f"Failed to identify image for time {hour:02d}:00, Error: {e}")
            return None
    else:
        print(f"Failed to fetch image for time {hour:02d}:00, Status Code: {response.status_code}")
        return None

def fetch_and_save_images(date, start_hour, end_hour, parameter):
    os.makedirs('images', exist_ok=True)
    images = []
    for hour in range(start_hour, end_hour + 1):
        image = fetch_image(date, hour, parameter)
        if image:
            image_path = f'images/{hour:02d}_{parameter}.gif'
            image.save(image_path)
            images.append(image_path)
    return images

def create_gif(image_paths, output_path):
    images = [Image.open(path) for path in image_paths]
    if images:
        images[0].save(output_path, save_all=True, append_images=images[1:], loop=0, duration=500, disposal=2)
        return output_path
    else:
        return None

# When the user clicks "Generate GIF", run the GIF creation process
if st.button("Generate GIF"):
    st.write(f"Generating GIF for {parameter} from {start_hour}:00 to {end_hour}:00 UTC on {date_str}...")

    image_paths = fetch_and_save_images(date_str, start_hour, end_hour, parameter)
    output_gif_path = f"{date_str}_{start_hour}z-{end_hour}z_{parameter}.gif"

    gif_path = create_gif(image_paths, output_gif_path)

    if gif_path:
        st.success("GIF Generated Successfully!")
        st.image(gif_path)  # Display the GIF
        with open(gif_path, "rb") as file:
            btn = st.download_button(
                label="Download GIF",
                data=file,
                file_name=os.path.basename(gif_path),
                mime="image/gif"
            )
    else:
        st.error("No GIF could be generated. Please check your inputs.")

streamlit run app.py