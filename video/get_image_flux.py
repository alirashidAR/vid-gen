from huggingface_hub import InferenceClient
import dotenv   
import os

dotenv.load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

async def generate_image(text,path):
    client = InferenceClient("black-forest-labs/FLUX.1-dev", token=HUGGINGFACE_TOKEN)
    
    # output is a PIL.Image object
    image = client.text_to_image(text)
    
    # save the image
    image.save(path+"/flux.png")

