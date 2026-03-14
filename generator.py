import pdfplumber
import math
import os
import requests
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

# ----------------------------
# API KEYS (use environment variables)
# ----------------------------

MURF_API_KEY = os.getenv("HF_API_KEY")
HF_API_KEY = os.getenv("MURF_API_KEY")

# ----------------------------
# Murf configuration
# ----------------------------

VOICE_ID = "en-US-ronnie"

VOICE_STYLES = {
    "calm": "Calm and warm",
    "professional": "Clear and professional",
    "narrative": "Expressive and narrative",
    "academic": "Neutral and academic"
}

MURF_URL = "https://api.murf.ai/v1/speech/generate"

# ----------------------------
# HuggingFace configuration
# ----------------------------

HF_MODEL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

hf_headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# ----------------------------
# Generate audio
# ----------------------------

def generate_audio(text, index, style, audio_dir):

    payload = {
        "text": text,
        "voiceId": VOICE_ID,
        "style": style
    }

    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(MURF_URL, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Murf API error: {response.text}")

    result = response.json()

    if "audioFile" not in result:
        raise Exception(f"Audio generation failed: {result}")

    audio_url = result["audioFile"]

    audio_data = requests.get(audio_url)

    audio_path = f"{audio_dir}/section_{index}.mp3"

    with open(audio_path, "wb") as f:
        f.write(audio_data.content)

    print("Audio saved:", audio_path)

    return audio_path


# ----------------------------
# Generate image
# ----------------------------

def generate_image(prompt, index, image_dir):

    response = requests.post(
        HF_MODEL,
        headers=hf_headers,
        json={"inputs": prompt}
    )

    if response.status_code != 200:
        raise Exception(f"Image generation failed: {response.text}")

    content_type = response.headers.get("content-type", "")

    if "application/json" in content_type:
        raise Exception(f"HF returned error: {response.json()}")

    image_path = f"{image_dir}/image_{index}.png"

    with open(image_path, "wb") as f:
        f.write(response.content)

    print("Image saved:", image_path)

    return image_path


# ----------------------------
# Main pipeline
# ----------------------------

def generate_visual_audiobook(pdf_path, frames, style, job_id):

    base_dir = f"jobs/{job_id}"
    audio_dir = f"{base_dir}/audio"
    image_dir = f"{base_dir}/images"

    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(image_dir, exist_ok=True)

    pages_text = []

    with pdfplumber.open(pdf_path) as pdf:

        total_pages = len(pdf.pages)

        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages_text.append(text)

    print("Total pages:", total_pages)

    pages_per_section = math.ceil(total_pages / frames)

    sections = []

    for i in range(0, total_pages, pages_per_section):

        section_pages = pages_text[i:i + pages_per_section]
        section_text = " ".join(section_pages)

        sections.append(section_text)

    print("Total sections:", len(sections))

    audio_files = []
    image_files = []

    for i, section in enumerate(sections):

        print(f"\nProcessing section {i+1}")

        audio_path = generate_audio(
            section[:1500],
            i + 1,
            style,
            audio_dir
        )

        audio_files.append(audio_path)

        prompt = f"""
Artwork inspired by a book scene.

Scene description:
{section[:400]}

Style: cinematic illustration, dramatic lighting
"""

        image_path = generate_image(
            prompt,
            i + 1,
            image_dir
        )

        image_files.append(image_path)

    clips = []

    for i in range(len(audio_files)):

        audio_clip = AudioFileClip(audio_files[i])

        image_clip = ImageClip(image_files[i]).with_duration(audio_clip.duration)

        video_clip = image_clip.with_audio(audio_clip)

        clips.append(video_clip)

    final_video = concatenate_videoclips(clips)

    output_path = f"{base_dir}/visual_audiobook.mp4"

    final_video.write_videofile(output_path, fps=24)

    print("\nVisual audiobook created:", output_path)

    return output_path