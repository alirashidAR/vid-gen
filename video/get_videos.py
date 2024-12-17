import requests

def get_videos(query:str):
    headers = {
        'Authorization': 'E2G2gl5kXzvn0iJWeFqixbm82lJMtE5NJoieVzmynk6lHSV0XVfWH30E'
    }
    response = requests.get(f'https://api.pexels.com/videos/search?query={query}&per_page=2', headers=headers)
    video_data = response.json()
    video_urls = []

    for video in video_data['videos']:
        for file in video['video_files']:
            if file['file_type'] == 'video/mp4':
                video_urls.append(file['link'])

    return video_urls

print(get_videos("home"))