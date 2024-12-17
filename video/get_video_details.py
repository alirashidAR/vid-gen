import google.generativeai as genai

genai.configure(api_key="AIzaSyDW_yw4qBFnp3RmVOB9yj-XZSJfSOkVxrw")
model = genai.GenerativeModel("gemini-1.5-flash")

def get_content(product_name:str,tagline:str,duration:int):

    prompt = '''
    For the following {{product_name}} advertisement, write a script that is engaging and informative and should just be one paragraph no need to identify scenes. The tagline is{{tagline}} The script should be {{duration}} seconds long and return one noun and adjective pair that best describes the product. Give in the following format:
    Script:
    "The EcoVive Water Bottle is the perfect companion for your daily adventures. Stay hydrated in style and make a positive impact on the environment. Join the movement and make a difference today. Shop now!"
    Word: Adjective,Noun'''

    prompt = prompt.replace("{{product_name}}",product_name)
    prompt = prompt.replace("{{tagline}}",tagline)
    prompt = prompt.replace("{{duration}}",str(duration))

    response = model.generate_content(prompt)
    return response.text

print(get_content("Heavy Duty Bags","Too cool for school",15))
