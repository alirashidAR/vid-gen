import os
import boto3
import json
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from audio import audio_generation, get_video_details
from video import get_image_stable, get_image_flux, get_videos_pexels
from compilation import make_clip
from dotenv import load_dotenv
import httpx  # Use httpx for asynchronous requests
from fastapi.middleware.cors import CORSMiddleware
from grading import grade

# Load secrets from .env
load_dotenv()

app = FastAPI()

# Add CORS middleware
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8000/generate_video",
    "http://localhost:8000/grade_video",
    "*"
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
    brand_palette: list[str] = []
    dimensions: dict
    duration: int
    cta_text: str
    logo_url: str
    product_video_url: str

class VideoRequest(BaseModel):
    video_details: VideoDetails

class VideoGradingRequest(BaseModel):
    file_url: str
    scoring_criteria: dict

class GeneralRequest(BaseModel):
    video_request: VideoRequest
    video_grading_request: VideoGradingRequest

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
        generate_image(f"Generate an image for {video_details.product_name} in {', '.join(video_details.brand_palette)} with {video_details.tagline}", output_path),
        get_video(video_details.product_name, output_path)
    )
    
    # After all are generated, stitch them together into a final video
    video_filename = make_clip.stitch_video(video_details.duration / 5, video_details.cta_text, 5, width=video_details.dimensions["width"], height=video_details.dimensions["height"])
    
    return video_filename

async def upload_video_to_s3(file_path: str, s3_key: str):
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
async def generate_and_upload_video(request: GeneralRequest):
    try:
        # Extract VideoRequest and VideoGradingRequest from GeneralRequest
        video_details = request.video_request.video_details
        video_filename = await generate_video(video_details)  # Generate video
        video_file_path = os.path.join(".", video_filename)  # Full file path
        print(f"Generated video: {video_file_path}")

        # Upload the generated video to S3
        s3_key = f"videos/{video_filename}"
        video_url = await upload_video_to_s3(video_file_path, s3_key)

        print(f"Video uploaded to S3: {video_url}")
        print("Grading video...")

        # Perform grading with async httpx
        async with httpx.AsyncClient() as client:
            try:
                score = await client.post("http://localhost:8000/grade_video", json={
                    "file_url": video_url,
                    "scoring_criteria": request.video_grading_request.scoring_criteria
                }, timeout=10)  # Set a timeout for the request
                
                score.raise_for_status()  # Raise an error for HTTP errors
                
                print("Grading response:", score.json())
            except httpx.RequestError as e:
                raise HTTPException(status_code=500, detail=f"Error with grading service: {str(e)}")
            except httpx.TimeoutException:
                raise HTTPException(status_code=504, detail="Grading service request timed out.")
        
        # Return the S3 URL if upload was successful
        return {
            "status": "success",
            "video_url": video_url,
            "scoring": score.json(),
            "metadata": {
                "file_size": os.path.getsize(video_file_path),
                "duration": video_details.duration,
                "dimensions": video_details.dimensions
            }
        }

    except HTTPException as e:
        raise e  # Reraise known exceptions
    except Exception as e:
        # Catch any other exceptions and return a proper response
        raise HTTPException(status_code=500, detail=f"Error generating or uploading video: {str(e)}")

@app.post("/grade_video")
async def grade_video(request: VideoGradingRequest):
    try:
        # Extract file_url and scoring_criteria from the request
        file_url = request.file_url
        scoring_criteria = request.scoring_criteria

        # Pass the file_url and scoring_criteria to the grade function
        # Assuming your function supports scoring_criteria as a parameter
        response = grade.upload_check_and_grade_video(file_url, scoring_criteria)

        return {"grading_response": json.loads(response)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error grading video: {str(e)}")
