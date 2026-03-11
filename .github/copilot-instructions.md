# Copilot Instructions for Earshot

## Overview

Earshot is a macOS menu bar app for local audio transcription. It captures system audio for live meeting transcription and transcribes audio/video files - all running locally on Apple Silicon using MLX-Whisper.

## Build and Run

```bash
# Install all dependencies (Homebrew, BlackHole, Python packages, Ollama)
./setup.sh

# Run the menu bar app
./run_app.sh

# CLI transcription
./earshot_run /path/to/audio.m4a
./earshot_run video.mp4 --model small
./earshot_run call.wav --speakers "Alice,Bob"
```

No test suite exists - verify changes by running the app manually.

## Architecture

### Core Components

The `earshot/` package contains all Python modules:

- **app.py** - rumps-based menu bar application. Uses `NSApplicationActivationPolicyAccessory` to hide from Dock. Threading for background transcription.
- **transcriber.py** - MLX-Whisper wrapper. Models are HuggingFace repos (`mlx-community/whisper-*-mlx`). Handles chunk merging with time offset adjustment.
- **audio_capture.py** - PyAudio-based live recording via BlackHole virtual audio device.
- **diarization.py** - Speaker identification via local Ollama (`llama3.2`). Extracts JSON from LLM response.
- **output_writer.py** - Generates JSON, TXT, SRT, VTT, TSV formats.
- **config.py** - Settings in `~/.config/earshot/settings.json`. Defaults defined in `DEFAULTS` dict.

### Data Flow

1. **Live transcription**: Menu bar → AudioCapture (BlackHole) → WAV chunks → Transcriber → Diarization → OutputWriter → `~/Documents/Earshot/`
2. **File transcription**: File picker → ffmpeg extraction (if video) → Transcriber → OutputWriter → same directory as input

### Entry Points

- `run_app.sh` - Launches `python3 -m earshot.app`
- `earshot_run` - Bash script that embeds Python for CLI usage
- `setup.sh` - Full dependency installation with interactive audio device setup

## Key Conventions

### Transcript Format

All modules work with a transcript dict:
```python
{
    "text": "Full transcript text...",
    "segments": [
        {"start": 0.0, "end": 2.5, "text": "Hello", "speaker": "SPEAKER_00"},
        ...
    ]
}
```

### Threading Pattern

Background tasks use daemon threads with `rumps.notification()` for completion feedback:
```python
thread = threading.Thread(target=self._transcribe_file, args=(path,))
thread.daemon = True
thread.start()
```

### Settings Access

Always use `load_settings()` / `save_settings()` - never access `CONFIG_FILE` directly.

## Dependencies

- **System** (Homebrew): `blackhole-2ch`, `portaudio`, `ffmpeg`, `ollama`
- **Python**: `rumps`, `mlx-whisper`, `pyaudio`, `soundfile`, `numpy`
- **Models**: `ollama pull llama3.2` for speaker identification
