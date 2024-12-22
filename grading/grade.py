import google.generativeai as genai
import typing_extensions as typing
import time
import json
import requests
import os
import dotenv

dotenv.load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Set up the Google Generative AI API key
genai.configure(api_key=GEMINI_API_KEY)

# Define a structured schema for the video analysis
class VideoGradingResult(typing.TypedDict):
    background_foreground_separation: int
    brand_guideline_adherence: int
    creativity_visual_appeal: int
    product_focus: int
    call_to_action: int
    audience_relevance: int

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Function to download the video file from the provided URL
def download_video(file_url, download_path):
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(download_path, 'wb') as file:
            file.write(response.content)
        print(f"Video downloaded successfully: {download_path}")
        print(download_path)
        return download_path
    else:
        raise ValueError("Failed to download video.")

# Function to upload, check, and grade the video with customizable scoring criteria
def upload_check_and_grade_video(file_url, scoring_criteria):
    # Define a temporary path to save the video
    video_filename = "downloaded_video.mp4"
    video_file_path = os.path.join(".", video_filename)  # You can specify your own temp directory
    
    # Download the video
    download_video(file_url, video_file_path)
    
    # Upload the video
    video_file = genai.upload_file(path=video_file_path)

    # Check the video processing status
    while video_file.state.name == "PROCESSING":
        time.sleep(10)
        video_file = genai.get_file(video_file.name)

    if video_file.state.name == "FAILED":
        raise ValueError(f"Video processing failed. State: {video_file.state.name}")

    # Create the grading prompt based on dynamic scoring_criteria
    prompt = f"""
    Please grade the following video based on these criteria:
    - Background and foreground separation: {scoring_criteria['background_foreground_separation']} points
    - Brand guideline adherence: {scoring_criteria['brand_guideline_adherence']} points
    - Creativity and visual appeal: {scoring_criteria['creativity_visual_appeal']} points
    - Product focus: {scoring_criteria['product_focus']} points
    - Call to action: {scoring_criteria['call_to_action']} points
    - Audience relevance: {scoring_criteria['audience_relevance']} points
    Give response in JSON format.Make sure to give a score to each criteria.
    """
    
    # Make the LLM request to generate the grade
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json", 
            response_schema=list[VideoGradingResult]
        )
    )

    # Delete the uploaded file after task is done
    video_file.delete()

    # Optionally, delete the local video file as well
    if os.path.exists(video_file_path):
        os.remove(video_file_path)

    return response.text
