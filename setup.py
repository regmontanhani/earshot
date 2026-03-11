"""Setup script for building Earshot as a macOS app."""

from setuptools import setup

APP = ["earshot/app.py"]
DATA_FILES = []

OPTIONS = {
    "argv_emulation": False,
    "iconfile": None,  # Add icon path here if you have one
    "plist": {
        "CFBundleName": "Earshot",
        "CFBundleDisplayName": "Earshot",
        "CFBundleIdentifier": "com.earshot.app",
        "CFBundleVersion": "1.0.0",
        "CFBundleShortVersionString": "1.0.0",
        "LSUIElement": True,  # Hide from Dock (menu bar app)
        "NSMicrophoneUsageDescription": "Earshot needs microphone access to record audio for transcription.",
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
    name="Earshot",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
