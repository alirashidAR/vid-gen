import os
import boto3
import io
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from audio import audio_generation, get_video_details
from video import get_image_stable, get_image_flux, get_videos_pexels
from compilation import make_clip
from dotenv import load_dotenv
import requests
from fastapi.middleware.cors import CORSMiddleware

# Load secrets from .env
load_dotenv()

app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost",
    "http://localhost:8000",
    # Add other origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS S3 Configuration (loaded from environment variables)
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
print(f"Using S3 bucket: {AWS_BUCKET_NAME}")

# Initialize S3 client
s3_client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY,
                         aws_secret_access_key=AWS_SECRET_KEY, region_name=AWS_REGION)

# Pydantic models for input validation
class VideoDetails(BaseModel):
    product_name: str
    tagline: str
    brand_palette: list[str]
    dimensions: dict
    duration: int
    cta_text: str
    logo_url: str
    product_video_url: str

class VideoRequest(BaseModel):
    video_details: VideoDetails

# Helper function to download files from URLs
def download_file(url: str, filename: str):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(filename, 'wb') as file:
            file.write(response.content)
        return filename
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error downloading file: {e}")

# Helper functions to generate audio, image, and video
async def generate_audio(product_name, tagline, duration, outputFilename):
    _, _, script = get_video_details.get_content(product_name, tagline, duration)
    await audio_generation.generate_audio(script, outputFilename)

async def generate_image(text, path):
    await asyncio.gather(
        get_image_stable.generate_image(text, path),
        get_image_flux.generate_image(text, path)
    )

async def get_video(query, path):
    await get_videos_pexels.fetch_and_download_media(query, path)

async def generate_video(video_details: VideoDetails):
    output_path = "media"
    
    # Ensure the media directory exists
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Download product video and logo
    download_file(video_details.product_video_url, f"{output_path}/product_video.mp4")
    download_file(video_details.logo_url, f"{output_path}/product_logo.png")
    
    # Run all tasks concurrently to generate audio, images, and video
    await asyncio.gather(
        generate_audio(video_details.product_name, video_details.tagline, video_details.duration, f"{output_path}/audio.mp3"),
        generate_image(f"Generate an image for {video_details.product_name} in {video_details.brand_palette} with {video_details.tagline}", output_path),
        get_video(video_details.product_name, output_path)
    )
    
    # After all are generated, stitch them together into a final video
    video_filename = make_clip.stitch_video(video_details.duration / 5, video_details.cta_text, 5, width=video_details.dimensions["width"], height=video_details.dimensions["height"])
    
    return video_filename


def upload_video_to_s3(file_path: str, s3_key: str):
    print(f"Uploading {file_path} to S3 bucket {AWS_BUCKET_NAME} with key {s3_key}")
    try:
        # Open the video file as a binary stream
        with open(file_path, 'rb') as video_file:
            # Upload the video using upload_fileobj
            s3_client.upload_fileobj(
                video_file,  # Directly passing the file object
                AWS_BUCKET_NAME,
                s3_key,
                ExtraArgs={'ContentType': 'video/mp4'}  # Adjust the content type based on your video format
            )
        
        print(f"Successfully uploaded {file_path} to S3 bucket {AWS_BUCKET_NAME} with key {s3_key}")
        return f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading video to S3: {e}")



# FastAPI endpoint to generate video and upload to S3
@app.post("/generate_video")
async def generate_and_upload_video(request: VideoRequest):
    try:
        # Generate the video
        video_filename = await generate_video(request.video_details)
        video_file_path = os.path.join("media", video_filename)  # Full file path
        print(f"Generated video: {video_file_path}")

        # Upload the generated video to S3
        s3_key = f"videos/{video_filename}"
        video_url = upload_video_to_s3(video_file_path, s3_key)

        # Return the S3 URL if upload was successful
        return {"video_url": video_url}
    
    except HTTPException as e:
        raise e  # Reraise known exceptions
    except Exception as e:
        # Catch any other exceptions and return a proper response
        raise HTTPException(status_code=500, detail=f"Error generating or uploading video: {str(e)}")
