import os
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
from moviepy.editor import VideoFileClip, CompositeVideoClip, ImageClip
import json

# Define the directory containing the images
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(SCRIPT_DIR, "images")

def overlay_emotion_images(video_path, overlay_data_path, output_video_path):
    """
    Overlays Sunny and Dusty's emotion images on a video. For Dusty's (D-...) images,
    the overlay is positioned so that the image's bottom-left corner aligns with the video's
    bottom left. For Sunny's (S-...) images, the overlay is positioned so that the image's
    bottom-right corner aligns with the video's bottom right.
    
    The overlay images are resized uniformly to be twice as big as one-sixth of the video's dimensions.
    
    Parameters:
        video_path (str): Path to the input video.
        overlay_data_path (str): Path to the JSON file containing overlay data.
        output_video_path (str): Path to save the output video with overlays.
    """
    # Load the base video
    video_clip = VideoFileClip(video_path)
    original_fps = video_clip.fps

    # Load overlay data from JSON
    with open(overlay_data_path, 'r') as overlay_file:
        overlay_data = json.load(overlay_file)

    overlays = []
    
    for overlay in overlay_data:
        image_path = overlay["image_path"]
        speaker = overlay.get("speaker", "")
        
        # Check for image file existence and apply fallback if necessary
        if speaker == "ST":  # Sunny
            if not os.path.exists(image_path):
                print(f"Sunny's image not found: {image_path}. Using default.")
                image_path = os.path.join(IMAGES_DIR, "S-Default.png")
            else:
                print(f"Sunny's image found: {image_path}.")
        elif speaker == "DT":  # Dusty
            if not os.path.exists(image_path):
                print(f"Dusty's image not found: {image_path}. Using default.")
                image_path = os.path.join(IMAGES_DIR, "D-Default.png")
            else:
                print(f"Dusty's image found: {image_path}.")

        # Create the image clip
        image_clip = ImageClip(image_path)
        
        # Compute the target overlay size:
        # Originally, the overlay would be 1/6 of the video dimensions.
        # Here we multiply by 2 to make them larger (i.e. 2/6 = 1/3 of the width and height).
        target_width = (video_clip.w // 6) * 2
        target_height = (video_clip.h // 6) * 2
        
        # Resize the image clip to the target size.
        image_clip = image_clip.resize(newsize=(target_width, target_height))
        
        # Now that the image has been resized, retrieve its size.
        clip_width, clip_height = image_clip.size
        
        # Compute the position based on speaker type.
        if speaker == "ST":
            # Position so that the image's bottom-right corner aligns with the video's bottom right.
            pos = (video_clip.w - clip_width, video_clip.h - clip_height)
        elif speaker == "DT":
            # Position so that the image's bottom-left corner aligns with the video's bottom left.
            pos = (0, video_clip.h - clip_height)
        else:
            # If no recognized speaker, fall back to the provided position in the JSON (or center).
            pos = overlay.get("position", "center")
        
        # Set the start time, duration, and the computed position for the overlay.
        image_clip = (
            image_clip.set_start(overlay["start_time"])
                      .set_duration(overlay["end_time"] - overlay["start_time"])
                      .set_position(pos)
        )
        
        overlays.append(image_clip)

    # Combine the base video with all overlays.
    final_video = CompositeVideoClip([video_clip] + overlays)

    # Write the final video to file.
    final_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac', fps=original_fps)

def main(video_path, subtitles_data_path, output_video_path):
    overlay_emotion_images(video_path, subtitles_data_path, output_video_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python subtitlesoverlay.py <video_path> <subtitles_json_path> <output_video_path>")
        sys.exit(1)
    video_path = sys.argv[1]
    subtitles_data_path = sys.argv[2]
    output_video_path = sys.argv[3]
    main(video_path, subtitles_data_path, output_video_path)