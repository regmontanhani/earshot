"""Setup script for building WhisperX as a macOS app."""

from setuptools import setup

APP = ["whisperx_app/app.py"]
DATA_FILES = []

OPTIONS = {
    "argv_emulation": False,
    "iconfile": None,  # Add icon path here if you have one
    "plist": {
        "CFBundleName": "WhisperX",
        "CFBundleDisplayName": "WhisperX",
        "CFBundleIdentifier": "com.whisperx.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "LSUIElement": True,  # Hide from Dock (menu bar app)
        "NSMicrophoneUsageDescription": "WhisperX needs microphone access to record audio for transcription.",
    },
    "packages": [
        "rumps",
        "mlx_whisper",
        "mlx",
        "numpy",
        "soundfile",
    ],
}

setup(
    name="WhisperX",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
