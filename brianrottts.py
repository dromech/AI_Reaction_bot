import boto3
import io
from pydub import AudioSegment
import re
import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
cred_path = os.path.join(base_dir, "credentials.txt")

credentials = {}
with open(cred_path, "r") as f:
    for line in f:
        if ":" in line:
            key, value = line.strip().split(":", 1)
            credentials[key] = value


# Your credentials and region
access_key_id = credentials.get("access_key_id")
secret_access_key = credentials.get("secret_access_key")
region = credentials.get("region")

polly = boto3.client(
    'polly',
    region_name=region,
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key
)

# Speaker to voice mapping
voice_map = {
    'ST': 'Amy',   # Sunny - female voice
    'DT': 'Justin' # Dusty - male voice
}

# Voice Engine can be standard or neural
ENGINE = 'standard'

# Define emotion to prosody mapping (pitch, rate)
# emotion_prosody = {
#     "S-Happy":       {'pitch': '+15%', 'rate': 'fast'},
#     "S-Sad":         {'pitch': '-10%', 'rate': 'slow'},
#     "S-Surprised":   {'pitch': '+20%', 'rate': 'fast'},
#     "S-Scared":      {'pitch': '-5%',  'rate': 'x-slow'},
#     "S-Unimpressed": {'pitch': '0%',   'rate': 'medium'},
#     "S-Playful":     {'pitch': '+10%', 'rate': 'fast'},
#     "S-Angry":       {'pitch': '-5%',  'rate': 'fast'},
#     "S-Content":     {'pitch': '0%',   'rate': 'medium'},
#     "S-Loving":      {'pitch': '+10%', 'rate': 'medium'},
#     "S-Curious":     {'pitch': '+5%',  'rate': 'medium'},
#     "S-Indifferent": {'pitch': '0%',   'rate': 'medium'},
#     "S-Hungry":      {'pitch': '-5%',  'rate': 'medium'},
#     "S-Relaxed":     {'pitch': '-10%', 'rate': 'slow'},
#     "S-Confused":    {'pitch': '-5%',  'rate': 'slow'},
#     "S-Annoyed":     {'pitch': '-5%',  'rate': 'fast'},
#     "S-Excited":     {'pitch': '+15%', 'rate': 'fast'},
#     "S-Terrified":   {'pitch': '-20%', 'rate': 'x-slow'},
#     "S-Mischievous": {'pitch': '+5%',  'rate': 'fast'},
#     "S-Pensive":     {'pitch': '-5%',  'rate': 'slow'},
#     "S-Jealous":     {'pitch': '-5%',  'rate': 'slow'},
#     "S-Nervous":     {'pitch': '-5%',  'rate': 'fast'},
#     "S-Affectionate":{'pitch': '+10%', 'rate': 'medium'},
#     "S-Bored":       {'pitch': '0%',   'rate': 'slow'},
#     "S-Proud":       {'pitch': '+5%',  'rate': 'medium'},
#     "S-Sleepy":      {'pitch': '-10%', 'rate': 'x-slow'},
#     "S-Resigned":      {'pitch': '-10%', 'rate': 'medium'},

#     "D-Happy":       {'pitch': '+10%', 'rate': 'fast'},
#     "D-Sad":         {'pitch': '-10%', 'rate': 'slow'},
#     "D-Surprised":   {'pitch': '+20%', 'rate': 'fast'},
#     "D-Scared":      {'pitch': '-5%',  'rate': 'x-slow'},
#     "D-Unimpressed": {'pitch': '0%',   'rate': 'medium'},
#     "D-Playful":     {'pitch': '+10%', 'rate': 'fast'},
#     "D-Angry":       {'pitch': '-5%',  'rate': 'fast'},
#     "D-Content":     {'pitch': '0%',   'rate': 'medium'},
#     "D-Loving":      {'pitch': '+10%', 'rate': 'medium'},
#     "D-Curious":     {'pitch': '+5%',  'rate': 'medium'},
#     "D-Indifferent": {'pitch': '0%',   'rate': 'medium'},
#     "D-Hungry":      {'pitch': '-5%',  'rate': 'medium'},
#     "D-Relaxed":     {'pitch': '-10%', 'rate': 'slow'},
#     "D-Confused":    {'pitch': '-5%',  'rate': 'slow'},
#     "D-Annoyed":     {'pitch': '-5%',  'rate': 'fast'},
#     "D-Excited":     {'pitch': '+15%', 'rate': 'fast'},
#     "D-Terrified":   {'pitch': '-20%', 'rate': 'x-slow'},
#     "D-Mischievous": {'pitch': '+5%',  'rate': 'fast'},
#     "D-Pensive":     {'pitch': '-5%',  'rate': 'slow'},
#     "D-Jealous":     {'pitch': '-5%',  'rate': 'slow'},
#     "D-Nervous":     {'pitch': '-5%',  'rate': 'fast'},
#     "D-Affectionate":{'pitch': '+10%', 'rate': 'medium'},
#     "D-Bored":       {'pitch': '0%',   'rate': 'slow'},
#     "D-Proud":       {'pitch': '+5%',  'rate': 'medium'},
#     "D-Sleepy":      {'pitch': '-10%', 'rate': 'x-slow'},
#     "D-Resigned":      {'pitch': '-10%', 'rate': 'medium'}
# }

emotion_prosody = {
    "S-Happy":       {'pitch': '+15%', 'rate': 'fast'},
    "S-Sad":         {'pitch': '-10%', 'rate': 'fast'},
    "S-Surprised":   {'pitch': '+20%', 'rate': 'fast'},
    "S-Scared":      {'pitch': '-5%',  'rate': 'fast'},
    "S-Unimpressed": {'pitch': '0%',   'rate': 'fast'},
    "S-Playful":     {'pitch': '+10%', 'rate': 'fast'},
    "S-Angry":       {'pitch': '-5%',  'rate': 'fast'},
    "S-Content":     {'pitch': '0%',   'rate': 'fast'},
    "S-Loving":      {'pitch': '+10%', 'rate': 'fast'},
    "S-Curious":     {'pitch': '+5%',  'rate': 'fast'},
    "S-Indifferent": {'pitch': '0%',   'rate': 'fast'},
    "S-Hungry":      {'pitch': '-5%',  'rate': 'fast'},
    "S-Relaxed":     {'pitch': '-10%', 'rate': 'fast'},
    "S-Confused":    {'pitch': '-5%',  'rate': 'fast'},
    "S-Annoyed":     {'pitch': '-5%',  'rate': 'fast'},
    "S-Excited":     {'pitch': '+15%', 'rate': 'fast'},
    "S-Terrified":   {'pitch': '-20%', 'rate': 'fast'},
    "S-Mischievous": {'pitch': '+5%',  'rate': 'fast'},
    "S-Pensive":     {'pitch': '-5%',  'rate': 'fast'},
    "S-Jealous":     {'pitch': '-5%',  'rate': 'fast'},
    "S-Nervous":     {'pitch': '-5%',  'rate': 'fast'},
    "S-Affectionate":{'pitch': '+10%', 'rate': 'fast'},
    "S-Bored":       {'pitch': '0%',   'rate': 'fast'},
    "S-Proud":       {'pitch': '+5%',  'rate': 'fast'},
    "S-Sleepy":      {'pitch': '-10%', 'rate': 'fast'},
    "S-Resigned":    {'pitch': '-10%', 'rate': 'fast'},

    "D-Happy":       {'pitch': '+10%', 'rate': 'fast'},
    "D-Sad":         {'pitch': '-10%', 'rate': 'fast'},
    "D-Surprised":   {'pitch': '+20%', 'rate': 'fast'},
    "D-Scared":      {'pitch': '-5%',  'rate': 'fast'},
    "D-Unimpressed": {'pitch': '0%',   'rate': 'fast'},
    "D-Playful":     {'pitch': '+10%', 'rate': 'fast'},
    "D-Angry":       {'pitch': '-5%',  'rate': 'fast'},
    "D-Content":     {'pitch': '0%',   'rate': 'fast'},
    "D-Loving":      {'pitch': '+10%', 'rate': 'fast'},
    "D-Curious":     {'pitch': '+5%',  'rate': 'fast'},
    "D-Indifferent": {'pitch': '0%',   'rate': 'fast'},
    "D-Hungry":      {'pitch': '-5%',  'rate': 'fast'},
    "D-Relaxed":     {'pitch': '-10%', 'rate': 'fast'},
    "D-Confused":    {'pitch': '-5%',  'rate': 'fast'},
    "D-Annoyed":     {'pitch': '-5%',  'rate': 'fast'},
    "D-Excited":     {'pitch': '+15%', 'rate': 'fast'},
    "D-Terrified":   {'pitch': '-20%', 'rate': 'fast'},
    "D-Mischievous": {'pitch': '+5%',  'rate': 'fast'},
    "D-Pensive":     {'pitch': '-5%',  'rate': 'fast'},
    "D-Jealous":     {'pitch': '-5%',  'rate': 'fast'},
    "D-Nervous":     {'pitch': '-5%',  'rate': 'fast'},
    "D-Affectionate":{'pitch': '+10%', 'rate': 'fast'},
    "D-Bored":       {'pitch': '0%',   'rate': 'fast'},
    "D-Proud":       {'pitch': '+5%',  'rate': 'fast'},
    "D-Sleepy":      {'pitch': '-10%', 'rate': 'fast'},
    "D-Resigned":    {'pitch': '-10%', 'rate': 'fast'}
}

def synthesize_ssml(text, voice_id):
    response = polly.synthesize_speech(
        Text=text,
        VoiceId=voice_id,
        OutputFormat='mp3',
        TextType='ssml',
        Engine=ENGINE
    )
    audio_bytes = response['AudioStream'].read()
    segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
    return segment

def process_script(script_path, output_path):
    pattern = r'(\[ST\]|\[DT\])(.*?)(?=\[ST\]|\[DT\]|$)'
    emotion_pattern = r'\[(S|D)-([A-Za-z]+)\]'

    with open(script_path, 'r', encoding='utf-8') as f:
        full_text = f.read().strip()

    if not full_text.startswith('[ST]') and not full_text.startswith('[DT]'):
        full_text = '[ST]' + full_text

    segments_raw = re.findall(pattern, full_text, flags=re.DOTALL)

    overlay_data = []
    current_time = 0.0
    segments = []

    for seg in segments_raw:
        speaker_marker = seg[0]  # [ST] or [DT]
        text = seg[1].strip()
        speaker = speaker_marker.strip('[]')  # ST or DT
        voice_id = voice_map.get(speaker, 'Amy')

        emotions_found = re.findall(emotion_pattern, text)
        chosen_pitch = '0%'
        chosen_rate = 'fast'
        emotion_image = None
        emotion_sound = None

        if emotions_found:
            first_emo = emotions_found[0]
            emotion_marker = f"{first_emo[0]}-{first_emo[1]}"
            if emotion_marker in emotion_prosody:
                chosen_pitch = emotion_prosody[emotion_marker]['pitch']
                chosen_rate = emotion_prosody[emotion_marker]['rate']
            emotion_image = os.path.join("images", f"{emotion_marker}.png")
            emotion_sound = os.path.join("cat_sounds", f"{emotion_marker}.mp3")

        # Remove emotion markers for the spoken text and subtitles.
        cleaned_text = re.sub(emotion_pattern, '', text).strip()
        if not cleaned_text:
            continue

        ssml_text = f'<speak><prosody pitch="{chosen_pitch}" rate="{chosen_rate}">{cleaned_text}</prosody></speak>'
        segment_audio = synthesize_ssml(ssml_text, voice_id)

        duration = len(segment_audio) / 1000.0  # Duration in seconds

        # Create a dictionary for the current segment that always includes text.
        data_obj = {
            "start_time": current_time,
            "end_time": current_time + duration,
            "speaker": speaker,
            "text": cleaned_text,
            "sound_file": emotion_sound
        }
        # If an emotion image was found, add the additional keys.
        if emotion_image:
            data_obj["image_path"] = emotion_image
            data_obj["position"] = [100, 100] if speaker == "ST" else [500, 300]

        overlay_data.append(data_obj)
        segments.append(segment_audio)
        current_time += duration

    if segments:
        final_audio = segments[0]
        for segment in segments[1:]:
            final_audio += segment
        final_audio.export(output_path, format="mp3")
        print(f"Final MP3 file: {output_path}")

        overlay_data_path = output_path.replace(".mp3", "_overlay_data.json")
        with open(overlay_data_path, 'w') as overlay_file:
            json.dump(overlay_data, overlay_file, indent=4)
        print(f"Overlay data saved to: {overlay_data_path}")
    else:
        print("No segments processed. Check your script file.")

def main():
    script_file = "script.txt"
    output_mp3 = "dialogue.mp3"
    process_script(script_file, output_mp3)

if __name__ == "__main__":
    main()