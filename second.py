import google.generativeai as genai
import httpx
import os
import base64


genai.configure(api_key="AIzaSyDW_yw4qBFnp3RmVOB9yj-XZSJfSOkVxrw")
model = genai.GenerativeModel(model_name = "gemini-1.5-pro")


image_path = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Palace_of_Westminster_from_the_dome_on_Methodist_Central_Hall.jpg/2560px-Palace_of_Westminster_from_the_dome_on_Methodist_Central_Hall.jpg"

image = httpx.get(image_path)

image_details = {
    "product_name": "EcoVive Water Bottle",
    "tagline": "Sustainability Meets Style.",
    "brand_palette": ["#009688", "#FF5722", "#FFFFFF"],
    "dimensions": {
        "width": 1920,
        "height": 1080
    },
    "duration": 15,
    "cta_text": "Join the Movement. Shop Now!"
}

# Prompt for scoring the image with details
prompt = f'''
Analyze and score the image based on the following details and criteria:
Details:
Product Name: {image_details["product_name"]}
Tagline: {image_details["tagline"]}
Brand Palette: {", ".join(image_details["brand_palette"])}
Dimensions: {image_details["dimensions"]["width"]}x{image_details["dimensions"]["height"]}
Duration: {image_details["duration"]} seconds
Call-to-Action: {image_details["cta_text"]}

Scoring Criteria:
- Background and foreground separation: 20 points
- Brand guideline adherence: 20 points
- Creativity and visual appeal: 20 points
- Product focus: 15 points
- Call-to-action effectiveness: 15 points
- Audience relevance: 10 points
'''

prompt = "Caption this image."
response = model.generate_content([{'mime_type':'image/jpeg', 'data': base64.b64encode(image.content).decode('utf-8')}, prompt])

print(response.text)
