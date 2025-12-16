import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ELEVEN_LABS_API_URL = "https://api.elevenlabs.io/v1/text-to-speech"

def generate_audio(text: str, voice_id: str = None) -> bytes:
    api_key = os.environ.get('ELEVEN_LABS_API_KEY')
    
    if not api_key:
        logger.warning("ELEVEN_LABS_API_KEY not set")
        return None
    
    if not voice_id:
        voice_id = "21m00Tcm4TlvDq8ikWAM"
    
    url = f"{ELEVEN_LABS_API_URL}/{voice_id}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        return response.content
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        return None

def save_audio_file(audio_data: bytes, filename: str) -> str:
    if not audio_data:
        return None
    
    audio_dir = "static/audio"
    os.makedirs(audio_dir, exist_ok=True)
    
    filepath = os.path.join(audio_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(audio_data)
    
    return filepath
