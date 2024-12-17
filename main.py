from diffusers import DiffusionPipeline

pipe = DiffusionPipeline.from_pretrained("ali-vilab/text-to-video-ms-1.7b")

prompt = "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k"
image = pipe(prompt).images[0]


