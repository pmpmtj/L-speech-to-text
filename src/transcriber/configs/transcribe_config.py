"""
Transcription Configuration

This module defines the configuration for the OpenAI Whisper API transcription service.
All configuration values use dataclasses for better IDE support and type safety.

Note: OPENAI_API_KEY must be set as an environment variable and will be 
validated when the Transcriber class is initialized.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class TranscribeConfig:
    """
    Configuration for OpenAI Whisper API transcription.
    
    Attributes:
        model: OpenAI Whisper model to use
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        language: Language code for transcription (e.g., 'en', 'fr', 'es')
        prompt: Optional prompt to guide the transcription
        temperature: Sampling temperature (0.0 to 1.0)
        response_format: Format of the response ('text' or 'json')
    """
    model: str = "whisper-1"
    timeout: int = 30
    max_retries: int = 3
    language: str = "pt"
    prompt: str = ""
    temperature: float = 0.0
    response_format: Literal["text", "json"] = "text"


# Default configuration instance
config = TranscribeConfig()

