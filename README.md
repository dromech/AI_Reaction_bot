# Sunny & Dusty Reaction Bot

This project was an ambitious hobby experiment that blended together **Instagram scraping**, **AI-driven video commentary**, and **creative overlays**.  
The core idea was to grab funny or trending clips from meme accounts automatically, then process them through a pipeline that gave the illusion of two cats, **Sunny** and **Dusty**, reacting to the videos in their own quirky personalities.

---

## Features

### 🎥 Video Scraping & Upload
- Uses **Instaloader** and **Instagrapi** to log into an Instagram account (via `credentials.txt`).  
- Scrapes the latest videos from target meme pages.  
- Uploads finished reaction videos back with generated captions.  
- Relevant files: `instascraper.py`, `uploader.py`.

### 🤖 AI-Powered Scripts
- Extracts frames and analyzes them with a **Hugging Face image captioning model** + OCR (Tesseract).  
- Generates witty scripts and captions in the voices of Sunny and Dusty using **OpenAI GPT models**.  
- Relevant file: `brianrot.py`.

### 🗣️ Voice & Sound Overlays
- Dialogue voiced through **Amazon Polly** (with separate mappings for each cat).  
- Extra cat sound effects layered at specific timestamps.  
- Relevant files: `brianrottts.py`, `catsoundoverlay.py`.

### 🐾 Visual Overlays
- Cartoon cat avatars and dynamic subtitles placed in video corners.  
- Synchronization with script lines and emotional tags.  
- Relevant files: `emotionoverlay.py`, `subtitlesoverlay.py`.

### 🎬 Compositing
- Tools like **ImageMagick**, **Tesseract**, and **MoviePy** stitched everything into a polished “reaction” clip.

---

## Status

At its peak, the pipeline could **fully automate a reaction-style video**:  
from scraping a clip → generating dialogue → producing a finished, captioned, voiced, and watermarked output ready for upload.  

Now, however, the project is in a **broken, archival state**.  
Several dependencies have changed or drifted out of sync (OpenAI model calls, AWS Polly authentication, Instagram API behavior).  
Hard-coded paths, outdated packages, and fragile chaining mean the workflow no longer runs end-to-end.  

---

## Reflection

What remains is a fascinating snapshot of a **creative coding experiment** — equal parts machine learning demo, video editing hack, and playful internet automation — that served as a passion project rather than a production tool.

