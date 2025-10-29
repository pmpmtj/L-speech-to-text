"""
Hotkey Detection Configuration

This module defines the configuration for hotkey detection and recording.
All configuration values use dataclasses for better IDE support and type safety.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class HotkeyCombination:
    """Configuration for a single hotkey combination."""
    name: str
    keys: List[str]
    description: str = ""
    enabled: bool = True
    
    def __post_init__(self):
        """Validate hotkey combination."""
        if not self.keys:
            raise ValueError("Hotkey keys list cannot be empty")
        if not self.name:
            raise ValueError("Hotkey name cannot be empty")


@dataclass
class HotkeyConfig:
    """Complete hotkey configuration."""
    hotkey_combinations: List[HotkeyCombination] = None
    
    def __post_init__(self):
        """Initialize hotkey combinations if not provided."""
        if self.hotkey_combinations is None:
            self.hotkey_combinations = [
                HotkeyCombination(
                    name="record_speech",
                    keys=["ctrl", "alt"],
                    description="Press and hold to record speech, release to stop and transcribe",
                    enabled=True
                )
            ]


# Default configuration instance
config = HotkeyConfig()

