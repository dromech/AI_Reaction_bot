import os
import sys
import time
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired, ClientError

def upload_single_video(video_path, caption_path, username, password):
    """
    Uploads a single video (video_path) to Instagram with a caption read from caption_path.
    """
    # Verify that the video file exists
    if not os.path.isfile(video_path):
        print(f"Error: Video file '{video_path}' not found.")
        return

    # Verify that the caption file exists and read its contents.
    if not os.path.isfile(caption_path):
        print(f"Error: Caption file '{caption_path}' not found.")
        return

    with open(caption_path, 'r', encoding='utf-8') as f:
        caption = f.read().strip()

    if not caption:
        print("Warning: Caption file is empty. Using default caption.")
        caption = "CAT POST"

    print(f"Uploading video: {video_path}")
    print(f"Using caption: {caption}\n")

    # Initialize the Instagram client
    client = Client()

    try:
        # Login to Instagram
        client.login(username, password)
        print("Login successful!")
    except (LoginRequired, ChallengeRequired) as e:
        print(f"Login error: {e}")
        return
    except ClientError as e:
        print(f"Client error: {e}")
        return

    # Pause before uploading (if needed)
    time.sleep(5)

    try:
        # Upload the video
        client.clip_upload(video_path, caption=caption)
        print("Upload successful!")
    except ClientError as e:
        print(f"Error uploading video: {e}")
    finally:
        # Logout after uploading
        client.logout()

def main(video_file_path, cap_file_path):

    # credentials.txt in the same folder as this script
    credentials = {}

    with open("credentials.txt", "r") as f:
        for line in f:
            if ":" in line:  # only process valid key:value lines
                key, value = line.strip().split(":", 1)
                credentials[key] = value

    # Load Instagram credentials
    username = credentials.get("igusername")
    password = credentials.get("igpassword")

    if not username or not password:
        print("Error: Instagram credentials not found in environment variables.")
        return

    upload_single_video(video_file_path, cap_file_path, username, password)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python uploader.py <video_file_path> <cap_file_path>")
        sys.exit(1)
    video_file_path = sys.argv[1]
    cap_file_path = sys.argv[2]
    main(video_file_path, cap_file_path)