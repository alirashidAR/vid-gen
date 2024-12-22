import asyncio
from huggingface_hub import InferenceClient
import os
import dotenv

dotenv.load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

async def generate_image(text,path):
    client = InferenceClient("stabilityai/stable-diffusion-3.5-large", token=HUGGINGFACE_TOKEN)
    
    # output is a PIL.Image object
    image = client.text_to_image(text)
    
    image.save(path+"/stable.png")

