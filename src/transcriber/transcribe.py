import os
import time
import requests
from pathlib import Path

# Import from package
from common.logging_utils import get_logger
from transcriber.configs.transcribe_config import config

# Get script directory for reliable absolute paths
SCRIPT_DIR = Path(__file__).resolve().parent

class Transcriber:
    """
    Handles transcription using OpenAI Whisper API and pastes the result at the cursor.
    """
    def __init__(self):
        # Set up logger for the transcribe module
        self.logger = get_logger("transcriber")
        self.logger.debug("Loading transcription configuration")
        
        # Load configuration from Python config module
        cfg = config
        self.model = cfg.model
        self.timeout = cfg.timeout
        self.max_retries = cfg.max_retries
        self.language = cfg.language
        self.prompt = cfg.prompt
        self.temperature = cfg.temperature
        self.response_format = cfg.response_format
        
        # Load API key from environment - FAIL FAST if missing
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            error_msg = "OPENAI_API_KEY environment variable is not set. Please set it before running the application."
            self.logger.error(error_msg)
            raise EnvironmentError(error_msg)
        
        self.logger.debug(f"Transcriber initialized with model: {self.model}")

    def transcribe(self, audio_bytes):
        """
        Send audio (WAV bytes) to OpenAI Whisper and return the transcription.
        Handles both text and json response formats.
        """
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        # Verify audio bytes
        if not audio_bytes:
            self.logger.error("No audio data received for transcription")
            return ""
            
        # Log audio data details
        buffer_size = audio_bytes.getbuffer().nbytes
        self.logger.debug(f"Audio data size: {buffer_size} bytes ({buffer_size/1024:.2f} KB)")
        
        # Reset the buffer position for the request
        audio_bytes.seek(0)
        
        # Save a copy of the audio being sent to API for debugging (only if enabled)
        if os.getenv('SAVE_DEBUG_AUDIO') or os.getenv('DEBUG_MODE'):
            try:
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                output_dir = Path(SCRIPT_DIR).parent / "tests"
                output_dir.mkdir(exist_ok=True)
                debug_file = output_dir / f"openai_request_{timestamp}.wav"
                with open(debug_file, 'wb') as f:
                    audio_bytes.seek(0)
                    f.write(audio_bytes.read())
                    audio_bytes.seek(0)
                self.logger.debug(f"Saved API request audio to {debug_file}")
            except Exception as e:
                self.logger.warning(f"Failed to save debug audio: {e}")
        
        data = {
            "model": self.model,
            "language": self.language,
            "prompt": self.prompt,
            "temperature": self.temperature,
            "response_format": self.response_format,
        }
        
        self.logger.debug(f"API request details:")
        self.logger.debug(f"URL: {url}")
        self.logger.debug(f"Headers: Authorization: Bearer ****{self.api_key[-4:] if self.api_key else ''}")
        self.logger.debug(f"Files: audio.wav (audio/wav)")
        self.logger.debug(f"Data parameters: {data}")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.debug(f"Sending audio to OpenAI (attempt {attempt})...")
                print(f"Sending audio to OpenAI (attempt {attempt}/{self.max_retries})...")
                
                # Create a fresh file object for each attempt to prevent file position issues
                audio_bytes.seek(0)
                files = {
                    "file": ("audio.wav", audio_bytes, "audio/wav"),
                }
                
                response = requests.post(url, headers=headers, files=files, data=data, timeout=self.timeout)
                
                self.logger.debug(f"Response status code: {response.status_code}")
                self.logger.debug(f"Response headers: {dict(response.headers)}")
                
                # Check for HTTP errors
                if response.status_code != 200:
                    self.logger.error(f"API error - Status code: {response.status_code}")
                    self.logger.error(f"API response: {response.text}")
                    print(f"Error from OpenAI API: {response.status_code} - {response.text}")
                    if attempt == self.max_retries:
                        return ""
                    continue
                
                # Log the full raw response for debugging
                self.logger.debug(f"Raw API response: {response.text}")
                
                if self.response_format == "json":
                    result = response.json()
                    text = result.get("text", "")
                    self.logger.debug(f"Parsed JSON response: {result}")
                    self.logger.info(f"Transcription result: {text}")
                else:
                    text = response.text
                    self.logger.info(f"Transcription result: {text}")
                
                return text.strip()
            except Exception as e:
                self.logger.error(f"Transcription attempt {attempt} failed: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
                if attempt == self.max_retries:
                    print(f"Failed to transcribe after {self.max_retries} attempts: {e}")
                    raise
        return ""
