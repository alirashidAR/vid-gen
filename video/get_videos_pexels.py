import os
import requests
import asyncio


async def fetch_and_download_media(query,path):
    # Define URLs and headers for Pexels API
    video_url = "https://api.pexels.com/videos/search"
    image_url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": "E2G2gl5kXzvn0iJWeFqixbm82lJMtE5NJoieVzmynk6lHSV0XVfWH30E"
    }

    # Fetch videos
    video_params = {
        "query": query,
        "per_page": 2
    }
    video_response = requests.get(video_url, headers=headers, params=video_params)
    if video_response.status_code == 200:
        videos = video_response.json()
    else:
        print(f"Failed to fetch videos. Status code: {video_response.status_code}")
        videos = None

    # Fetch images
    image_params = {
        "query": query,
        "per_page": 2,
        "colour": "yellow"
    }
    image_response = requests.get(image_url, headers=headers, params=image_params)
    if image_response.status_code == 200:
        images = image_response.json()
    else:
        print(f"Failed to fetch images. Status code: {image_response.status_code}")
        images = None

    # Create a 'media' folder if it doesn't exist
    media_folder = path
    os.makedirs(media_folder, exist_ok=True)

    # Download videos
    video_count = 1
    if videos and "videos" in videos:
        for video in videos["videos"]:
            video_files = video["video_files"]
            highest_quality = max(video_files, key=lambda x: x["width"])
            video_url = highest_quality["link"]
            file_name = f"{media_folder}/video_{video_count}.mp4"
            print(f"Downloading {file_name} from {video_url}...")
            response = requests.get(video_url, stream=True)
            if response.status_code == 200:
                with open(file_name, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                print(f"Downloaded: {file_name}")
                video_count += 1
            else:
                print(f"Failed to download video {video_count}.")

    # Download images
    image_count = 1
    if images and "photos" in images:
        for image in images["photos"]:
            image_url = image["src"]["original"]
            file_name = f"{media_folder}/image_{image_count}.jpg"
            print(f"Downloading {file_name} from {image_url}...")
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                with open(file_name, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                print(f"Downloaded: {file_name}")
                image_count += 1
            else:
                print(f"Failed to download image {image_count}.")


