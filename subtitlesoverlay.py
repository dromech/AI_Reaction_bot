import os
os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
import json
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

def overlay_subtitles_on_video(video_path, subtitles_data_path, output_video_path):
    """
    Reads subtitle data (which must include 'start_time', 'end_time', 'text', and 'speaker')
    from a JSON file and overlays them onto a video. For each subtitle segment:
      - The text is split into words.
      - Each word is displayed for an equal fraction of the segment's duration.
      - Only one word is visible at a time; when a new word's time starts, it replaces the previous word.
    
    - For Dusty (speaker "DT"): the text appears in light blue, right-aligned (its right edge 10 pixels from the right).
    - For Sunny (speaker "ST"): the text appears in light green, left-aligned (its left edge 10 pixels from the left).
    
    Both styles use a 240-point Arial font with a white outline (stroke width 2) and are positioned
    30 pixels from the bottom.
    """
    # Load the base video
    video_clip = VideoFileClip(video_path)
    
    # Dynamically compute font size relative to video width.
    dynamic_font_size = int(video_clip.w / 10)  # Change the divisor as needed; here using 1/8 of video width.
    
    # Load subtitles data from the JSON file
    with open(subtitles_data_path, 'r') as f:
        subtitles = json.load(f)
    
    subtitle_clips = []
    
    # Process each subtitle segment
    for segment in subtitles:
        # Check for the "text" key; if it's missing, skip this segment.
        if "text" not in segment:
            print("Skipping a segment because it has no 'text' key:", segment)
            continue
        
        text = segment["text"]
        start_time = segment["start_time"]
        end_time = segment["end_time"]
        total_duration = end_time - start_time
        speaker = segment.get("speaker", "ST")
        
        words = text.split()
        if not words:
            continue
        num_words = len(words)
        word_duration = total_duration / num_words
        
        # Choose color based on speaker:
        # Dusty ("DT") → light blue; Sunny ("ST") → light green.
        if speaker == "DT":
            color = "lightblue"
        else:
            color = "lightgreen"
        
        # Create a TextClip for each word.
        for i, word in enumerate(words):
            word_start = start_time + i * word_duration
            txt_clip = TextClip(
                word,
                fontsize=dynamic_font_size,
                color=color,
                font='Arial',
                stroke_width=2,
                stroke_color="black"
            ).set_duration(word_duration).set_start(word_start)
            
            # Position the clip based on speaker:
            if speaker == "DT":
                # For Dusty: right-aligned. x = video width - clip width - 15.
                pos_x = video_clip.w - txt_clip.w - 15
            else:
                # For Sunny: left-aligned. x = 15.
                pos_x = 15
            pos_y = video_clip.h - txt_clip.h - 80  # 80 pixels from bottom.
            txt_clip = txt_clip.set_position((pos_x, pos_y))
            subtitle_clips.append(txt_clip)
    
    # Composite all subtitle clips over the base video
    final_video = CompositeVideoClip([video_clip] + subtitle_clips)
    final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac", fps=video_clip.fps)

def main(video_path, subtitles_data_path, output_video_path):
    overlay_subtitles_on_video(video_path, subtitles_data_path, output_video_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("Usage: python subtitlesoverlay.py <video_path> <subtitles_json_path> <output_video_path>")
        sys.exit(1)
    video_path = sys.argv[1]
    subtitles_data_path = sys.argv[2]
    output_video_path = sys.argv[3]
    main(video_path, subtitles_data_path, output_video_path)