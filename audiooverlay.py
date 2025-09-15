import os
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
from moviepy.audio.fx.volumex import volumex

def overlay_dialogue_on_video(input_video_path, dialogue_path, output_video_path):
    # Load the original video
    video_clip = VideoFileClip(input_video_path)

    # Adjust the volume of the original video's audio to 30%
    original_audio = volumex(video_clip.audio, 0.3)

    # Load the dialogue audio and set it to 100% (1.0 is no volume change, but ensures clarity)
    dialogue_audio = volumex(AudioFileClip(dialogue_path), 1.0)

    # Combine the two audio tracks
    combined_audio = CompositeAudioClip([original_audio, dialogue_audio])

    # Set the combined audio back to the video
    final_clip = video_clip.set_audio(combined_audio)

    # Write the final video file
    final_clip.write_videofile(
        output_video_path,
        codec='libx264',
        audio_codec='aac',
        temp_audiofile='temp-audio.m4a',
        remove_temp=True
    )

def main(video_path, audio_path, output_video_path):
    overlay_dialogue_on_video(video_path, audio_path, output_video_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python subtitlesoverlay.py <video_path> <audio_path> <output_video_path>")
        sys.exit(1)
    video_path = sys.argv[1]
    audio_path = sys.argv[2]
    output_video_path = sys.argv[3]
    main(video_path, audio_path, output_video_path)