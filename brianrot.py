import os
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
import sys
import subprocess
import cv2
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from tqdm import tqdm
import shutil
from datetime import datetime
import time
import tiktoken
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, AudioFileClip
import torch
from openai import OpenAI
import brianrottts
import audiooverlay
import emotionoverlay
import subtitlesoverlay
import catsoundoverlay
import instascraper
import uploader
import cleanup

base_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(base_dir, "credentials.txt")

credentials = {}
with open(cred_path, "r") as f:
    for line in f:
        if ":" in line:
            key, value = line.strip().split(":", 1)
            credentials[key] = value

key = credentials.get("api_key")

# Set your OpenAI API key
client = OpenAI(
    api_key = key
)

# Settings
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMES_PER_SECOND = 5        # Number of frames per second to analyze
VIDEOS_NUM = 1               # The ammount of videos scraped into the scrape folder
DESCRIBE_SCENES = True       # Toggle scene description on/off
PERSONALITY_DUSTY = "Stupid Kid"   # Dusty's personality
PERSONALITY_SUNNY = "Silly Old Lady"     # Sunny's personality
MODEL = "gpt-4o"             # Choose the AI model (e.g., "gpt-3.5-turbo", "gpt-4", "gpt-4-32k")
OUTPUT_FILE = "script.txt"   # Output file name
OUTPUT_CAPTION = "caption.txt" # Output file name for the caption
NUM_BEAMS = 7                # Quality of AI descriptions (beam width)
MAX_LENGTH = 50              # Max length of the descriptions
DUSTY_EMOTIONS = [
    "[D-Happy]", # Added
    "[D-Sad]", # Added
    "[D-Surprised]", # Added
    "[D-Scared]", # Added
    "[D-Unimpressed]", # Added
    "[D-Playful]", # Added
    "[D-Angry]", # Added
    "[D-Content]", # Added
    "[D-Loving]", # Added
    "[D-Curious]", # Added
    "[D-Indifferent]", # Added
    "[D-Hungry]", # Added
    "[D-Relaxed]", # Added
    "[D-Confused]", # Added
    "[D-Annoyed]", # Added
    "[D-Excited]", # Added
    "[D-Terrified]", # Added
    "[D-Mischievous]", # Added
    "[D-Pensive]", # Added
    "[D-Jealous]", # Added
    "[D-Nervous]", # Added
    "[D-Affectionate]",
    "[D-Bored]", # Added
    "[D-Proud]", # Added
    "[D-Sleepy]" # Added
    "[D-Resigned]" # Added
    "[D-Disgusted]" # Added
]
SUNNY_EMOTIONS = [
    "[S-Happy]", # Added
    "[S-Sad]", # Added
    "[S-Surprised]", # Added
    "[S-Scared]", # Added
    "[S-Unimpressed]", # Added
    "[S-Playful]", # Added
    "[S-Angry]", # Added
    "[S-Content]", # Added
    "[S-Loving]", # Added
    "[S-Curious]", # Added
    "[S-Indifferent]", # Added
    "[S-Hungry]", # Added
    "[S-Relaxed]", # Added
    "[S-Confused]", # Added
    "[S-Annoyed]", # Added
    "[S-Excited]", # Added
    "[S-Terrified]", # Added
    "[S-Mischievous]", # Added
    "[S-Pensive]", # Added
    "[S-Jealous]", # Added
    "[S-Nervous]", # Added
    "[S-Affectionate]", # Added
    "[S-Bored]", # Added
    "[S-Proud]", # Added
    "[S-Sleepy]" # Added
    "[S-Resigned]" # Added
    "[S-Disgusted]" # Added
]

# Add a catch for displaying an image that does not exist just use the default

# Model-specific token limits
MODEL_TOKEN_LIMITS = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-4": 32768,
    "gpt-4o": 32768,
    "gpt-4-32k": 32768,
}

# Load the image captioning model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")
caption_model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning").to(device)
caption_processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
caption_tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

def extract_frames(video_path, frames_per_second=1): # This is nice and fast. Progress bar is not necessary but could be nice
    """
    Extracts frames from the video based on the specified number of frames per second.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = max(int(fps // frames_per_second), 1)
    frames = []
    frame_count = 0
    print_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % interval == 0:
            frames.append(frame)
            print(f"Extracted frame: {print_count}")
            print_count += 1
        frame_count += 1
    cap.release()
    return frames

def get_video_duration(video_path):
    """
    Returns the duration of the video in seconds.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Unable to open video file: {video_path}")
        return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        print("FPS value is zero, defaulting to 30 FPS.")
        fps = 30  # Default to 30 FPS if not available
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps
    cap.release()
    return duration

def analyze_frames_with_comments(frames): # Upgraded to now get visual description and read the on screen text. Still slow with a cpu
    """
    Analyze frames and generate descriptive comments for each frame using an image captioning model.
    Also reads on-screen text using OCR (pytesseract) and appends it to the description.
    Displays a progress bar using tqdm.
    """
    descriptions = []
    
    # Loop over frames with a progress bar
    for idx, frame in enumerate(tqdm(frames, desc="Analyzing frames", unit="frame")):
        # Convert the frame to RGB as the model expects RGB images
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Preprocess the image for captioning
        pixel_values = caption_processor(images=rgb_frame, return_tensors="pt").pixel_values.to(device)

        # Generate caption from the image
        output_ids = caption_model.generate(pixel_values, max_length=MAX_LENGTH, num_beams=NUM_BEAMS)
        caption = caption_tokenizer.decode(output_ids[0], skip_special_tokens=True)

        # Use pytesseract to extract any on-screen text from the RGB frame
        ocr_text = pytesseract.image_to_string(rgb_frame).strip()

        # Append OCR text to the caption if any text is found
        if ocr_text:
            full_caption = f"{caption} (The text that is on the screen says: {ocr_text})"
        else:
            full_caption = caption

        # Create and store the description for the frame
        description = f"Frame {idx + 1}: {full_caption}"
        descriptions.append(description)

    return descriptions

def count_tokens(text, model=MODEL):
    """
    Counts the number of tokens in a text input for a specified model.
    """
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))

def convert_mov_to_mp4(video_path): # Could maybe be improved
    """
    If the input video is a .mov, convert it to MP4 and return the new path.
    The conversion uses FFmpeg's scale filter to preserve the original video resolution and aspect ratio.
    """
    base, ext = os.path.splitext(video_path)
    if ext.lower() == ".mov":
        new_path = base + ".mp4"
        print(f"Converting {video_path} to {new_path} ...")
        
        # This version stretches the video
        # clip = VideoFileClip(video_path)
        # # Save the clip as an .MP4 file
        # clip.write_videofile(new_path, codec="libx264", audio_codec="aac",ffmpeg_params=['-preset', 'fast', '-crf', '23', '-threads', '4'])
        # clip.close()

        # This version takes longer but it does not stretch the video
        command = ['ffmpeg', '-i', video_path, new_path]
        subprocess.run(command)

        return new_path
    return video_path

def generate_script_with_personality(frame_descriptions, personality_dusty=PERSONALITY_DUSTY, personality_sunny=PERSONALITY_SUNNY,semo=SUNNY_EMOTIONS,demo=DUSTY_EMOTIONS, model=MODEL, video_duration = None):
    """
    Uses OpenAI GPT model to generate a script with personality, based on frame descriptions.
    """
    # Combine the extracted visual details
    combined_input = (
        "Visual Descriptions:\n" + "\n".join(frame_descriptions) +
        f"\n\nPlease write a script that is ~{int(2.5*video_duration)} words where 2 cats (Sunny and Dusty) describe what is happening in the video while reviewing it and talking to eachother about the video. "
        f"The comments and observations for Dusty should be in a {personality_dusty} tone and the comment observations for Sunny should be in a {personality_sunny} tone. "
        f"When Sunny is talking mark her lines at the start with [ST] and when Dusty is talking mark his lines at the start with [DT]\n\n"
        f"When switching speakers add a new line character"
        f"Dusty's Emotions markers: {', '.join(demo)}\nSunny's Emotions markers: {', '.join(semo)}\n"
        f"Whenever in the script you want one of the cats emotions to switch use thier appropriate emotion marker at the start of sentence to match the emotion of the current sentence."
        f"Make it so the script is just a paragraph and don't mention the frames or scences in the script and imagine the Visual Descriptions are a cohesive video."
        f'Have it also so the last line of the script is always one of the cats saying "Follow for more!"'
    )

    # Count tokens to avoid exceeding limits
    token_count = count_tokens(combined_input, model=model)
    print(f"Token count for input: {token_count}")

    # Get the token limit for the selected model
    token_limit = MODEL_TOKEN_LIMITS.get(model, 4096)

    if token_count > token_limit:
        raise ValueError(f"Input text exceeds token limit for {model} (limit: {token_limit} tokens). Please reduce the input size.")

    # Use OpenAI's GPT model
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a 2 cats named Sunny and Dusty who are creative scriptwriters and video reviewers."},
            {"role": "user", "content": combined_input}
        ],
        max_tokens=min(1000, token_limit - token_count),  # Ensure the response stays within the token limit
        temperature=0.7,
        n=1,
    )

    # Extract the script from the response
    script = response.choices[0].message.content
    return script

def generate_caption_with_personality(frame_descriptions, personality_dusty=PERSONALITY_DUSTY, personality_sunny=PERSONALITY_SUNNY,semo=SUNNY_EMOTIONS,demo=DUSTY_EMOTIONS, model=MODEL, video_duration = None):
    """
    Uses OpenAI GPT model to generate a script with personality, based on frame descriptions.
    """
    # Combine the extracted visual details
    combined_input = (
        "Visual Descriptions:\n" + "\n".join(frame_descriptions) +
        f"\n\nPlease write a short and simple caption for a instagram post where the cats are reacting to a video which is represented by the Visual Descriptions. Use lots of emojis please."
        f"Do not mention anything about the frames just write a short couple sentence caption."
    )

    # Count tokens to avoid exceeding limits
    token_count = count_tokens(combined_input, model=model)
    print(f"Token count for input: {token_count}")

    # Get the token limit for the selected model
    token_limit = MODEL_TOKEN_LIMITS.get(model, 4096)

    if token_count > token_limit:
        raise ValueError(f"Input text exceeds token limit for {model} (limit: {token_limit} tokens). Please reduce the input size.")

    # Use OpenAI's GPT model
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a 2 cats named Sunny and Dusty who are creative scriptwriters and video reviewers."},
            {"role": "user", "content": combined_input}
        ],
        max_tokens=min(1000, token_limit - token_count),  # Ensure the response stays within the token limit
        temperature=0.7,
        n=1,
    )

    # Extract the caption from the response
    caption = response.choices[0].message.content
    return caption

# Main Program
def create_reacted(video_path):

    # Convert the file type just in case:
    video_path = convert_mov_to_mp4(video_path)

    # Get video duration
    video_duration = get_video_duration(video_path)
    if video_duration is None:
        print("Could not determine video duration.")
        exit(1)
    print(f"Video duration: {video_duration:.2f} Seconds")
    print(f"Expected Script Length: {int(2.5*video_duration)} Words")
    print(f"FPS: {FRAMES_PER_SECOND}")

    frames = extract_frames(video_path, frames_per_second=FRAMES_PER_SECOND)
    if not frames:
        print("No frames were extracted from the video. Please check the video file and settings.")
        exit(1)
    frame_descriptions = analyze_frames_with_comments(frames) if DESCRIBE_SCENES else []

    print(frame_descriptions)

    # Generate script with OpenAI
    personality_script = generate_script_with_personality(
        frame_descriptions, personality_dusty=PERSONALITY_DUSTY, personality_sunny=PERSONALITY_SUNNY,semo=SUNNY_EMOTIONS,demo=DUSTY_EMOTIONS, model=MODEL, video_duration=video_duration
    )

    print("Final Script with Personality:\n", personality_script)

    # Write the script to a file
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(SCRIPT_DIR, OUTPUT_FILE)
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(personality_script)
    print(f"Final script has been written to {script_path}")

    # Generate caption with personality
    personality_caption = generate_caption_with_personality(
        frame_descriptions, personality_dusty=PERSONALITY_DUSTY, personality_sunny=PERSONALITY_SUNNY,semo=SUNNY_EMOTIONS,demo=DUSTY_EMOTIONS, model=MODEL, video_duration=video_duration
    )

    print("Current caption with Personality:\n", personality_caption)

    # Write the caption to a file
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    caption_path = os.path.join(SCRIPT_DIR, OUTPUT_CAPTION)
    with open(caption_path, 'w', encoding='utf-8') as f:
        f.write(personality_caption)
    print(f"Final script has been written to {caption_path}")


    # Call the TTS
    # Fix to be a dynamic helper function later
    brianrottts.main()

    # Overlay the reaction audio
    audiooverlay.main(video_path, "dialogue.mp3", "reacted.mp4")

    # Oerlay the subtitles
    subtitlesoverlay.main("reacted.mp4", "dialogue_overlay_data.json", "reacted2.mp4")

    # Overlay the reaction images
    emotionoverlay.main("reacted2.mp4", "dialogue_overlay_data.json", "reacted3.mp4")

    # Overlay the cat sounds
    catsoundoverlay.main("reacted3.mp4", "dialogue_overlay_data.json", "reacted4.mp4")

    print("DONE")

    if sys.argv[1].lower() == "scrape":
        # Copy the final reacted video to a "scrape_reacts" folder.
        reacts_folder = os.path.join(SCRIPT_DIR, "scrape_reacts")
        if not os.path.exists(reacts_folder):
            os.makedirs(reacts_folder)
        base_name = os.path.basename(video_path)
        name_without_ext, _ = os.path.splitext(base_name)
        dest_file = os.path.join(reacts_folder, f"{name_without_ext}_reacted.mp4")
        shutil.copy2("reacted4.mp4", dest_file)
        print(f"Final reacted video copied to: {dest_file}\n")
        # Update the caption for uploading:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        caption_path = os.path.join(SCRIPT_DIR, "caption.txt")
        video_filename = os.path.basename(dest_file)          
        base_name, _ = os.path.splitext(video_filename)
        credits_path = os.path.join(SCRIPT_DIR, "credits", f"{base_name}.txt")
        if os.path.exists(credits_path):
            # Read credits content
            with open(credits_path, "r", encoding="utf-8") as f:
                credits_content = f.read().strip()

            # Read the existing caption
            with open(caption_path, "r", encoding="utf-8") as f:
                caption_content = f.read().rstrip()

            # Combine them with a newline (or two) in between
            new_caption_content = caption_content + "\n\n" + credits_content

            # Write updated text back to caption.txt
            with open(caption_path, "w", encoding="utf-8") as f:
                f.write(new_caption_content)

            print(f"Appended credits from '{base_name}.txt' to 'caption.txt'")
            
            # Now copy to the captions folder
            caption_folder = os.path.join(SCRIPT_DIR, "captions")
            if not os.path.exists(caption_folder):
                os.makedirs(caption_folder)
            dest_file_cap = os.path.join(caption_folder, f"{name_without_ext}_reacted.txt")
            shutil.copy2(caption_path, dest_file_cap)
            print(f"Final caption copied to: {dest_file_cap}\n")
            # Now upload
            time.sleep(60)
            # This is working now!!!!
            uploader.main(dest_file, dest_file_cap)
            
        else:
            print(f"No matching credits file found for: {base_name}.txt")
            # Now upload
            time.sleep(60)
            # This is working now!!!!
            uploader.main(dest_file, caption_path)


    else:
        # Copy the final reacted video to a "reacts" folder.
        reacts_folder = os.path.join(SCRIPT_DIR, "reacts")
        if not os.path.exists(reacts_folder):
            os.makedirs(reacts_folder)
        base_name = os.path.basename(video_path)
        name_without_ext, _ = os.path.splitext(base_name)
        dest_file = os.path.join(reacts_folder, f"{name_without_ext}_reacted.mp4")
        shutil.copy2("reacted4.mp4", dest_file)
        print(f"Final reacted video copied to: {dest_file}\n")

        # Create custom original caption
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
        caption_path = os.path.join(SCRIPT_DIR, "caption.txt")

        with open(caption_path, "r", encoding="utf-8") as f:
                caption_content = f.read().rstrip()
        
        # The credit for the video
        credit_text = (
            f"Content provided by: Our Owners\n"
            f'Leave a comment saying: "react to: @username" to have their content featured next!'
        )
        new_caption_content = caption_content + "\n\n" + credit_text

        with open(caption_path, "w", encoding="utf-8") as f:
                f.write(new_caption_content)


def main():
    if len(sys.argv) < 2:
        print("Usage: python briantrot.py <video1> [<video2> ...] or python briantrot.py scrape")
        sys.exit(1)
    
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # If the first argument is "scrape", then process every video in the "scrape" folder.
    if sys.argv[1].lower() == "scrape":
        target_folder = os.path.join(SCRIPT_DIR, "scrape")
        if not os.path.exists(target_folder):
            print(f"Scrape folder not found: {target_folder}")
            sys.exit(1)
        # Scrape the videos:
        # Check for command line video ammount pass. If none use default
        if len(sys.argv) > 2:
            try:
                videos_num = int(sys.argv[2])
                print(f"Scraping {videos_num} videos")
            except ValueError:
                videos_num = VIDEOS_NUM
                print(f"ValueError\nScraping {videos_num} videos")
        else:
            videos_num = VIDEOS_NUM
            print(f"No video amount given\nUsing default\nScraping {videos_num} videos")
        if len(sys.argv) > 3:
           check_last = str(sys.argv[3])
           if check_last == "check":
               check = True
               print("Checking previous post for comment")
           else:
               check = False
        else:
            check = False  
        for i in range(videos_num):
            instascraper.main(check)
            time.sleep(5) 
        # Define allowed video extensions (adjust as needed)
        allowed_extensions = (".mp4", ".mov", ".avi", ".mkv")
        # List all video files in the target folder
        video_files = [f for f in os.listdir(target_folder)
                       if f.lower().endswith(allowed_extensions)]
        if not video_files:
            print(f"No video files found in {target_folder}.")
            sys.exit(1)
        for video in video_files:
            video_path = os.path.join(target_folder, video)
            try:
                create_reacted(video_path)
            except Exception as e:
                print(f"Error processing {video_path}: {e}")
        # Now have clean up
        # cleanup.main()

    else:
        # Otherwise, treat the provided command-line arguments as file names in the "originals" folder.
        originals_folder = os.path.join(SCRIPT_DIR, "originals")
        if not os.path.exists(originals_folder):
            print(f"Originals folder not found: {originals_folder}")
            sys.exit(1)
        video_files = sys.argv[1:]
        for video in video_files:
            video_path = os.path.join(originals_folder, video)
            if not os.path.exists(video_path):
                print(f"Error: {video} not found in the originals folder ({originals_folder}).")
                continue
            try:
                create_reacted(video_path)
            except Exception as e:
                print(f"Error processing {video_path}: {e}")

if __name__ == "__main__":
    main()