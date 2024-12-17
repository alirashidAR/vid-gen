import edge_tts

async def generate_audio(text,outputFilename):
    communicate = edge_tts.Communicate(text,"en-AU-WilliamNeural")
    await communicate.save(outputFilename)

import asyncio

def main():
    asyncio.run(generate_audio("Forget flimsy bags! Heavy Duty Bags are here, too cool for school.  Built tough for anything you throw at them, from groceries to gear.  Durable, dependable, and stylish – get yours today!", "output.mp3"))

main()