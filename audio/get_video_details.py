import google.generativeai as genai
import typing_extensions as typing
import json
import os
import dotenv

dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ScriptOutput(typing.TypedDict):
    script: str
    adjective: str
    noun: str

# Configure the Generative AI API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

def get_content(product_name: str, tagline: str, duration: int):
    prompt = f"Create a strictly {duration}-second or less advertisement script for {product_name} the script should just be a monologue not scenes, just give text as there is only one narrator, just give text no onomatopeia and all, one paragraph only, no quotes. The tagline is '{tagline}'. Return one key adjective and noun from the script."
    
    result = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json",
            response_schema=ScriptOutput
        )
    )
    data = json.loads(result.text)
    adjective = data["adjective"]
    noun = data["noun"]
    script = data["script"]

    return adjective, noun, script

