import os
import requests
import logging

logger = logging.getLogger(__name__)

class AudioService:
    API_URL = "https://api.elevenlabs.io/v1/text-to-speech"
    DEFAULT_VOICE = "21m00Tcm4TlvDq8ikWAM"
    
    @classmethod
    def is_available(cls):
        return os.environ.get('ELEVEN_LABS_API_KEY') is not None
    
    @classmethod
    def generate_audio(cls, text: str, voice_id: str = None) -> bytes:
        api_key = os.environ.get('ELEVEN_LABS_API_KEY')
        
        if not api_key:
            logger.warning("ELEVEN_LABS_API_KEY not set")
            return None
        
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for audio generation")
            return None
        
        # Limit text to 2000 chars for Eleven Labs (it has strict limits)
        text_limited = text[:2000]
        
        voice_id = voice_id or cls.DEFAULT_VOICE
        url = f"{cls.API_URL}/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": api_key
        }
        
        data = {
            "text": text_limited,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=60)
            response.raise_for_status()
            logger.info(f"Audio generated successfully ({len(response.content)} bytes)")
            return response.content
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error generating audio: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error generating audio: {e}", exc_info=True)
            return None
    
    @classmethod
    def save_audio(cls, audio_data: bytes, filename: str) -> str:
        if not audio_data:
            return None
        
        audio_dir = "static/audio"
        os.makedirs(audio_dir, exist_ok=True)
        
        filepath = os.path.join(audio_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(audio_data)
        
        return filepath
