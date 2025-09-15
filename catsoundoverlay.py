import os
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
import json
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CAT_SOUNDS_DIR = os.path.join(SCRIPT_DIR, "cat_sounds")

def overlay_cat_sounds(video_path, overlay_data_path, output_video_path):
    """
    Overlays cat sounds (MP3 files) onto a video. Each JSON entry provides:
      - "sound_file": The cat-sound filename (relative to `CAT_SOUNDS_DIR`).
      - "start_time": The moment (in seconds) to begin playing the entire sound.
      - "speaker": 'ST' or 'DT' for fallback to S-Default.mp3 or D-Default.mp3 if file not found.

    IMPORTANT: We do NOT cut or subclip the sound to 'end_time'—the entire
    audio plays from start_time onward, ignoring 'end_time'.

    Example JSON (overlay_data_path):
    [
      {
        "sound_file": "S-Happy.mp3",
        "start_time": 3.0,
        "end_time": 4.5,  # Ignored
        "speaker": "ST"
      },
      {
        "sound_file": "D-Angry.mp3",
        "start_time": 10.0,
        "end_time": 12.5, # Ignored
        "speaker": "DT"
      }
    ]
    """

    # Load base video
    video_clip = VideoFileClip(video_path)
    original_fps = video_clip.fps

    # Load JSON data
    with open(overlay_data_path, 'r') as f:
        overlay_data = json.load(f)

    audio_clips = []
    # Add the original audio if present
    original_audio = video_clip.audio
    if original_audio:
        audio_clips.append(original_audio)

    # Process each cat-sound entry
    for overlay in overlay_data:
        sound_file = overlay.get("sound_file")
        speaker = overlay.get("speaker", "")
        start_time = overlay.get("start_time", 0)
        # end_time is ignored in this version

        if not sound_file:
            print(f"Skipping entry with no 'sound_file': {overlay}")
            continue

        # Build path within 'cat_sounds' folder
        requested_path = os.path.join(CAT_SOUNDS_DIR, sound_file)

        # Check if the file exists; fallback if not
        if not os.path.exists(requested_path):
            print(f"Sound file not found: {requested_path}")
            if speaker == "ST":
                fallback = os.path.join(CAT_SOUNDS_DIR, "S-Default.mp3")
                if os.path.exists(fallback):
                    print("Using fallback for Sunny: S-Default.mp3")
                    requested_path = fallback
                else:
                    print("No fallback found for ST. Skipping this sound.")
                    continue
            elif speaker == "DT":
                fallback = os.path.join(CAT_SOUNDS_DIR, "D-Default.mp3")
                if os.path.exists(fallback):
                    print("Using fallback for Dusty: D-Default.mp3")
                    requested_path = fallback
                else:
                    print("No fallback found for DT. Skipping this sound.")
                    continue
            else:
                print("No recognized speaker to pick a default. Skipping.")
                continue

        # Load entire cat-sound clip (no subclip)
        cat_sound_clip = AudioFileClip(requested_path)

        # Set the volume to 20% of its original loudness
        cat_sound_clip = cat_sound_clip.volumex(0.2)

        # Place the clip at 'start_time'
        cat_sound_clip = cat_sound_clip.set_start(start_time)
        audio_clips.append(cat_sound_clip)

    # Merge all audio sources
    composite_audio = CompositeAudioClip(audio_clips) if audio_clips else None

    # Attach new audio to the video
    final_clip = video_clip.set_audio(composite_audio)

    # Write final video
    final_clip.write_videofile(
        output_video_path,
        codec="libx264",
        audio_codec="aac",
        fps=original_fps
    )

def main(video_path, overlay_data_path, output_video_path):
    overlay_cat_sounds(video_path, overlay_data_path, output_video_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python catsoundoverlay.py <video_path> <cat_sounds_json> <output_video_path>")
        sys.exit(1)

    video_arg = sys.argv[1]
    overlay_arg = sys.argv[2]
    out_arg = sys.argv[3]
    main(video_arg, overlay_arg, out_arg)