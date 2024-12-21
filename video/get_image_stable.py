import asyncio
from huggingface_hub import InferenceClient

async def generate_image(text,path):
    client = InferenceClient("stabilityai/stable-diffusion-3.5-large", token="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")
    
    # output is a PIL.Image object
    image = client.text_to_image(text)
    
    image.save(path+"/stable.png")

