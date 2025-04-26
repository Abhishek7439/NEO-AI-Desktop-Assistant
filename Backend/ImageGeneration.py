import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
import os
from time import sleep

# Folder where images will be saved
IMAGE_FOLDER = r"Data"

# Hugging Face API details
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
HEADERS = {"Authorization": f"Bearer {get_key('.env', 'HuggingFaceAPIKey')}"}

# Function to open generated images
def open_images(prompt):
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 4)]
    
    for jpg_file in Files:
        image_path = os.path.join(IMAGE_FOLDER, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  
        except IOError:
            print(f"Unable to open {image_path}")

# Async function to send API requests
async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=HEADERS, json=payload)
        return response.content
    except Exception as e:
        print(f"API Error: {e}")
        return None  # Return None if API call fails

# Optimized async image generation
async def generate_images(prompt: str, num_images=5):
    prompt_text = f"{prompt}, quality=4K, high resolution, ultra sharp, seed={randint(0, 1000000)}"
    
    # Create multiple requests in parallel
    tasks = [query({"inputs": prompt_text}) for _ in range(num_images)]
    image_bytes_list = await asyncio.gather(*tasks)

    # Save images quickly
    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:  
            with open(os.path.join(IMAGE_FOLDER, f"{prompt.replace(' ', '_')}{i + 1}.jpg"), "wb") as f:
                f.write(image_bytes)

# Function to trigger image generation
def GenerateImages(prompt: str):
    asyncio.run(generate_images(prompt))  
    open_images(prompt)  

# Monitor loop for image requests
while True:
    try:
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data = f.read().strip()

        if Data:
            Prompt, Status = Data.split(",")
            if Status.strip().lower() == "true":
                print("Generating Images Fast 🚀 ...")
                GenerateImages(prompt=Prompt)

                # Reset status in file
                with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write("False,False")
                break
            else:
                sleep(1)  
    except Exception as e:
        print(f"Error: {e}")
