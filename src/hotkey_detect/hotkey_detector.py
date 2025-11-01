#!/usr/bin/env python3
"""
Hotkey Detector for JAssist

This module provides functionality to detect hotkey combinations,
record audio while keys are held, and automatically transcribe and paste
the results when keys are released.
"""

import time
import threading
import keyboard
from pathlib import Path
from io import BytesIO

# Import jassist modules
from common.logging_utils import get_logger
from recorder.record import Record
from transcriber.transcribe import Transcriber
from common.utils.paste_from_clipboard import paste_clipboard
from hotkey_detect.configs.hotkey_config import config
import pyperclip

# Get script directory for reliable absolute paths
SCRIPT_DIR = Path(__file__).resolve().parent

class HotkeyDetector:
    """
    Detects configured hotkey combinations, records audio while keys are held,
    and automatically transcribes and pastes the results when keys are released.
    """
    
    def __init__(self):
        """Initialize the hotkey detector with configuration settings."""
        # Set up logger
        self.logger = get_logger("hotkey_detector")
        self.logger.debug("Loading hotkey configuration")
        
        # Load configuration from Python config module
        cfg = config
        
        # Extract hotkey configuration
        self.hotkey_combinations = cfg.hotkey_combinations
        self.active_hotkeys = []
        
        for combo in self.hotkey_combinations:
            if combo.enabled:
                self.active_hotkeys.append({
                    "name": combo.name,
                    "keys": combo.keys,
                    "description": combo.description
                })
        
        if not self.active_hotkeys:
            self.logger.warning("No enabled hotkeys found, using default")
            self.active_hotkeys.append({
                "name": "default",
                "keys": ["ctrl", "alt"],
                "description": "Default hotkey combination"
            })
        
        # Set minimum recording duration (discard recordings shorter than this)
        self.min_duration = 1.25  # seconds
        
        # Initialize state variables
        self.pressed_keys = set()
        self.is_recording = False
        self.recorder = None
        self.transcriber = None
        
        # Initialize components
        self.init_components()
        
        self.logger.info("HotkeyDetector initialized")
    
    def init_components(self):
        """Initialize recorder and transcriber components."""
        try:
            self.recorder = Record()
            self.transcriber = Transcriber()
            self.logger.debug("Components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize components: {e}")
            raise
    
    def on_key_event(self, event):
        """Handle keyboard events."""
        try:
            # Update pressed keys set
            if event.event_type == 'down':
                self.pressed_keys.add(event.name)
            elif event.event_type == 'up':
                self.pressed_keys.discard(event.name)
            
            # Check for active hotkey combinations
            for hotkey in self.active_hotkeys:
                hotkey_set = set(hotkey["keys"])
                
                # Start recording when hotkey is pressed
                if hotkey_set.issubset(self.pressed_keys) and not self.is_recording:
                    self.start_recording()
                
                # Stop recording when hotkey is released
                elif self.is_recording and not hotkey_set.issubset(self.pressed_keys):
                    self.stop_recording_and_process()
        except Exception as e:
            self.logger.error(f"Error in key event handler: {e}")
    
    def start_recording(self):
        """Start audio recording."""
        try:
            self.logger.debug("Starting recording")
            if self.recorder.start():
                self.is_recording = True
                self.logger.debug("Recording started")
            else:
                self.logger.error("Failed to start recording")
        except Exception as e:
            self.logger.error(f"Error starting recording: {e}")
    
    def stop_recording_and_process(self):
        """Stop recording, transcribe if duration is sufficient, and paste result."""
        try:
            self.logger.debug("Stopping recording")
            if not self.recorder.stop():
                self.logger.error("Failed to stop recording")
                self.is_recording = False
                return
            
            duration = self.recorder.get_duration()
            self.logger.debug(f"Recording stopped. Duration: {duration:.2f} seconds")
            self.is_recording = False
            
            # Discard recordings shorter than minimum duration
            if duration < self.min_duration:
                self.logger.info(f"Recording too short ({duration:.2f}s < {self.min_duration}s), discarding")
                self.recorder.discard()
                return
            
            # Get audio bytes directly from memory instead of saving to file
            audio_bytes = self.recorder._get_audio_bytes()
            if not audio_bytes:
                self.logger.error("No audio data available")
                self.recorder.discard()
                return
            
            # Transcribe the audio with retry logic
            self.transcribe_and_paste(audio_bytes)
            
            # Clean up
            self.recorder.discard()
        except Exception as e:
            self.logger.error(f"Error in stop_recording_and_process: {e}")
            # Ensure recording is stopped and memory is cleared
            if self.is_recording:
                self.recorder.stop()
                self.recorder.discard()
                self.is_recording = False
    
    def transcribe_and_paste(self, audio_bytes):
        """Transcribe audio and paste the result with retry logic."""
        max_retries = 3
        
        for attempt in range(1, max_retries + 1):
            try:
                self.logger.debug(f"Transcription attempt {attempt}/{max_retries}")
                
                # Transcribe the audio
                transcription = self.transcriber.transcribe(audio_bytes)
                
                if not transcription:
                    self.logger.warning(f"Empty transcription on attempt {attempt}")
                    if attempt < max_retries:
                        continue
                    else:
                        self.logger.error("All transcription attempts failed")
                        return
                
                # Copy transcription to clipboard
                self.logger.debug(f"Transcription result: {transcription}")
                pyperclip.copy(transcription)
                
                # Paste the transcription
                if paste_clipboard():
                    self.logger.info("Transcription pasted successfully")
                else:
                    self.logger.warning("Failed to paste transcription")
                
                # Success, no need for more retries
                break
            except Exception as e:
                self.logger.error(f"Transcription attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    self.logger.error("All transcription attempts failed")
    
    def start(self):
        """Start the hotkey detector."""
        try:
            self.logger.info("Starting hotkey detector")
            for hotkey in self.active_hotkeys:
                self.logger.info(f"Listening for hotkey combination: {hotkey['name']} - {hotkey['keys']}")
            
            # Register key event handler
            keyboard.hook(self.on_key_event)
            
            # Prevent the program from exiting
            self.logger.info("Hotkey detector running. Press and hold hotkey to record.")
            
            # Run indefinitely
            while True:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    # Ignore Ctrl+C
                    self.logger.debug("KeyboardInterrupt ignored")
                    continue
        except Exception as e:
            self.logger.error(f"Error in hotkey detector: {e}")
            raise
        finally:
            # This should never execute unless there's a critical error
            keyboard.unhook_all()
            self.logger.info("Hotkey detector stopped")


def main():
    """Main entry point for the hotkey detector."""
    try:
        detector = HotkeyDetector()
        detector.start()
    except Exception as e:
        # Set up basic logging if logger isn't available
        import logging
        logging.basicConfig(level=logging.ERROR)
        logging.error(f"Critical error in hotkey detector: {e}")
        import traceback
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    main()



