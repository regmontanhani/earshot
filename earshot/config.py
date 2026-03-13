"""Configuration and settings management."""

import os
import json
from pathlib import Path

# Default settings
DEFAULTS = {
    "model_size": "large-v3",
    "output_dir": str(Path.home() / "Documents" / "Earshot"),
    "audio_device": "BlackHole 2ch",
    "auto_stop_enabled": True,
    "silence_timeout": 60,
    "chunk_duration": 30,
    "output_formats": ["json", "txt", "srt", "vtt", "tsv"],
}

CONFIG_DIR = Path.home() / ".config" / "earshot"
CONFIG_FILE = CONFIG_DIR / "settings.json"


def load_settings() -> dict:
    """Load settings from config file, using defaults for missing values."""
    settings = DEFAULTS.copy()
    
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                saved = json.load(f)
                settings.update(saved)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Ensure output directory exists
    os.makedirs(settings["output_dir"], exist_ok=True)
    
    return settings


def save_settings(settings: dict) -> None:
    """Save settings to config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def get_output_dir() -> Path:
    """Get the output directory path."""
    settings = load_settings()
    path = Path(settings["output_dir"])
    path.mkdir(parents=True, exist_ok=True)
    return path
