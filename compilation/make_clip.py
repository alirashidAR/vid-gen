from moviepy.editor import ImageClip, VideoFileClip, AudioFileClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont

def create_text_image(text, output_path, size=(1920, 1080), font_size=70):
    """
    Create an image with text at the center and save it to a file.

    :param text: Text to display.
    :param output_path: Path to save the generated image.
    :param size: Size of the image (default is 1920x1080).
    :param font_size: Size of the text (default is 70).
    """
    img = Image.new("RGB", size, color="black")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("GOTHICBI.TTF", font_size)  # Use a valid font file path
    
    # Use textbbox to calculate the bounding box of the text
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Calculate position to center the text
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, fill="white", font=font)
    img.save(output_path)


def stitch_video(duration, end_text, end_text_duration, width=1920, height=1080):
    """
    Create a video with images, video clips, and audio, and display a text at the end.
    
    :param duration: Duration for each image and video clip.
    :param end_text: The text to display at the end.
    :param end_text_duration: Duration of the end text clip.
    :param width: Width of the final video (default is 1920).
    :param height: Height of the final video (default is 1080).
    """
    resolution = (width, height)
    images = ["media/product_logo.png", "media/flux.png", "media/stable.png","media/image_1.jpg","media/image_2.jpg"]
    videos = ["media/video_1.mp4", "media/video_2.mp4","media/product_video.mp4"]
    audio_file = "media/audio.mp3"
    output_file = "media/output_video.mp4"
    
    # Create a list of ImageClips for the images and resize them
    image_clips = [ImageClip(img).set_duration(duration).resize(resolution) for img in images]
    
    # Create a list of VideoFileClips for the video clips and resize them
    video_clips = [VideoFileClip(video).subclip(0, duration).resize(resolution) for video in videos]
    
    # Concatenate all image and video clips
    all_clips = []
    
    # One image then one video
    for img, video in zip(image_clips, video_clips):
        all_clips.extend([img, video])
    
    # Add the last images two images to the list
    all_clips.extend([image_clips[-1], image_clips[-2]])

    final_video = concatenate_videoclips(all_clips, method="compose")
    
    # Add audio to the final video
    audio = AudioFileClip(audio_file)
    final_video = final_video.set_audio(audio)
    
    # Set the duration of the video to match the audio duration if necessary
    final_video = final_video.set_duration(audio.duration)
    
    # Generate the text image
    create_text_image(end_text, "end_text.jpg", size=resolution, font_size=100)
    
    # Create a TextClip from the generated image and resize it
    text_clip = ImageClip("end_text.jpg").set_duration(end_text_duration).resize(resolution)
    
    # Concatenate the final video with the text clip at the end
    final_video = concatenate_videoclips([final_video, text_clip])
    
    # Write the final video file
    final_video.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)

    return output_file

# # Example usage
# if __name__ == "__main__":
#     width = int(input("Enter the width of the video: "))
#     height = int(input("Enter the height of the video: "))
#     stitch_video(duration=5, end_text="Thank you for watching!", end_text_duration=5, width=width, height=height)
#     print("Video created: output_video.mp4")
