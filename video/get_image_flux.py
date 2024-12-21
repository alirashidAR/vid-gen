import asyncio
from huggingface_hub import InferenceClient
from PIL import Image
from io import BytesIO

async def generate_image(text,path):
    client = InferenceClient("black-forest-labs/FLUX.1-dev", token="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")
    
    # output is a PIL.Image object
    image = client.text_to_image(text)
    
    # save the image
    image.save(path+"/flux.png")

