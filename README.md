# Earshot

A macOS menu bar app for audio transcription. Capture live meetings locally, transcribe audio files via OpenAI.

![Menu Bar](https://img.shields.io/badge/macOS-Menu%20Bar%20App-blue)
![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-Optimized-green)

## Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Live Meeting Transcription** | Capture system audio in real-time from any app (Zoom, Teams, Meet, etc.) - runs locally |
| 📁 **File Transcription** | Transcribe audio/video files via OpenAI Whisper API (fast, handles large files) |
| 🔴 **Live Audio Monitor** | Visual feedback in menu bar showing audio levels while recording |
| 🤖 **Speaker Diarization** | Automatic speaker identification using local Ollama LLM |
| 📝 **Multiple Formats** | Outputs JSON, TXT, SRT, VTT, TSV |
| ⏹️ **Auto-Stop** | Configurable auto-stop after silence (or disable for manual control) |

## Quick Start

### One-Command Setup

```bash
git clone https://github.com/regmontanhani/earshot.git
cd earshot
./setup.sh
```

The setup script will:
- Install all dependencies (Homebrew, BlackHole, Python packages, Ollama)
- Pull the llama3.2 model for speaker identification
- Guide you through audio device configuration
- Optionally configure auto-start on login

### OpenAI API Key (for file transcription)

File transcription uses the OpenAI Whisper API. Add your key to a `.env` file:

```bash
echo "OPENAI_API_KEY=your-key-here" > .env
```

Or set it as an environment variable. Without an API key, file transcription falls back to local processing (slower, uses more memory).

### Manual Installation

<details>
<summary>Click to expand manual installation steps</summary>

#### 1. System Dependencies

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required packages
brew install blackhole-2ch portaudio ffmpeg

# Restart Core Audio to detect BlackHole
sudo killall coreaudiod
```

#### 2. Python Dependencies

```bash
pip3 install rumps mlx-whisper pyaudio soundfile numpy
```

#### 3. Audio Device Setup

For live meeting transcription, you need to route system audio through BlackHole:

1. Open **Audio MIDI Setup** (Spotlight → "Audio MIDI Setup")
2. Click **+** at bottom-left → **Create Multi-Output Device**
3. Check both:
   - ☑️ **BlackHole 2ch**
   - ☑️ **Your speakers/headphones**
4. Double-click "Multi-Output Device" to rename it → **Meeting Audio**

This creates a virtual device that sends audio to both your speakers AND BlackHole for recording.

#### 4. Ollama for Speaker Identification

```bash
brew install ollama
ollama pull llama3.2
```

</details>

## Usage

### Start the App

```bash
./run_app.sh
```

A **🎙️** icon appears in your menu bar.

### Menu Options

| Option | Description |
|--------|-------------|
| **Start Live Transcription** | Begin capturing system audio |
| **Transcribe File...** | Select an audio/video file to transcribe |
| **Open Output Folder** | View saved transcripts |
| **Settings → Model Size** | Choose Whisper model (tiny → large-v3) |
| **Settings → Audio Input** | Select audio capture device |
| **Quit** | Stop the app |

### Live Meeting Transcription

1. **Before the meeting:**
   - Set Mac audio output to **Meeting Audio** (System Settings → Sound → Output)

2. **During the meeting:**
   - Click **🎙️ → Start Live Transcription**
   - Icon changes to **🔴** with animated audio level bars
   - Continue your meeting normally - you'll hear audio through your speakers

3. **After the meeting:**
   - Click **🔴 → Stop Recording**
   - Transcription runs automatically
   - Files saved to `~/Documents/Earshot/`

### File Transcription

1. Click **🎙️ → Transcribe File...**
2. Select any audio or video file
3. Wait for transcription (uses OpenAI API - fast even for large files)
4. Output files saved next to the original file

> **Note:** Requires `OPENAI_API_KEY` in `.env` or environment. Falls back to local if not set.

## Output Formats

All transcriptions generate these files:

| Format | Extension | Description |
|--------|-----------|-------------|
| **JSON** | `.json` | Full transcript with timestamps, segments, metadata |
| **Text** | `.txt` | Plain text transcript |
| **SRT** | `.srt` | SubRip subtitles (for video players) |
| **VTT** | `.vtt` | WebVTT subtitles (for web/browsers) |
| **TSV** | `.tsv` | Tab-separated values (for spreadsheets) |

## How It Works

| Mode | Engine | Why |
|------|--------|-----|
| **Live Recording** | Local MLX-Whisper | Audio is chunked (30s), low memory usage |
| **File Transcription** | OpenAI API | Fast, handles large files without memory issues |
| **Speaker ID** | Local Ollama | Privacy - speaker names stay on your machine |

## Models

For **live recording**, select model in **Settings → Model Size**:

| Model | Download Size | RAM Usage | Speed | Quality |
|-------|--------------|-----------|-------|---------|
| `tiny` | ~75 MB | ~1 GB | ⚡⚡⚡⚡⚡ | ★☆☆☆☆ |
| `base` | ~140 MB | ~1 GB | ⚡⚡⚡⚡ | ★★☆☆☆ |
| `small` | ~460 MB | ~2 GB | ⚡⚡⚡ | ★★★☆☆ |
| `medium` | ~1.5 GB | ~5 GB | ⚡⚡ | ★★★★☆ |
| `large-v3` | ~3 GB | ~10 GB | ⚡ | ★★★★★ |

**Recommendation:** Use `large-v3` for best quality on Apple Silicon Macs.

Models download automatically on first use.

## Configuration

Settings are stored in `~/.config/earshot/settings.json`:

```json
{
  "model_size": "large-v3",
  "output_dir": "~/Documents/Earshot",
  "audio_device": "BlackHole 2ch",
  "auto_stop_enabled": true,
  "silence_timeout": 60,
  "chunk_duration": 30,
  "output_formats": ["json", "txt", "srt", "vtt", "tsv"]
}
```

OpenAI API key can be set in `.env` file or as `OPENAI_API_KEY` environment variable.

## Auto-Start on Login

```bash
# Enable
launchctl load ~/Library/LaunchAgents/com.earshot.app.plist

# Disable
launchctl unload ~/Library/LaunchAgents/com.earshot.app.plist
```

## CLI Tool

For command-line transcription:

```bash
# Basic usage
./earshot_run /path/to/audio.m4a

# Specify model
./earshot_run /path/to/video.mp4 --model small

# Manual speaker names
./earshot_run /path/to/call.wav --speakers "Alice,Bob"

# See all options
./earshot_run --help
```

**Options:**
| Option | Description |
|--------|-------------|
| `--model MODEL` | Whisper model (tiny, base, small, medium, large-v3). Default: large-v3 |
| `--speakers NAMES` | Comma-separated speaker names |
| `--help` | Show help message |

You can also set `EARSHOT_MODEL` environment variable to change the default model.

## Troubleshooting

### BlackHole not appearing as audio device

```bash
sudo killall coreaudiod
```

If still not visible, reboot your Mac.

### No audio being captured

1. Check System Settings → Sound → Output is set to "Meeting Audio"
2. Check Earshot Settings → Audio Input is set to "BlackHole 2ch"
3. Make sure the meeting app is playing audio

### Transcription quality is poor

- Switch to a larger model (Settings → Model Size → `large-v3`)
- Ensure good audio quality in the meeting
- Reduce background noise

### App not appearing in menu bar

The app may be running as a Dock app instead. Restart the app:

```bash
pkill -f "earshot.app"
./run_app.sh
```

### First transcription is slow

The first run downloads the Whisper model (~3GB for large-v3). Subsequent runs are fast.

## Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **macOS** | 12.0 (Monterey) | 13.0+ (Ventura/Sonoma) |
| **Chip** | Any Mac | Apple Silicon (M1/M2/M3/M4) |
| **RAM** | 8 GB | 16 GB+ |
| **Python** | 3.10 | 3.11+ |
| **Disk** | 5 GB free | 10 GB free |

## Dependencies

### System (via Homebrew)

- `blackhole-2ch` - Virtual audio device for capturing system audio
- `portaudio` - Audio I/O library (required by PyAudio)
- `ffmpeg` - Audio/video processing

### Python

- `rumps` - macOS menu bar framework
- `mlx-whisper` - MLX-optimized Whisper for Apple Silicon (live recording)
- `openai` - OpenAI API client (file transcription)
- `pyaudio` - Audio capture
- `soundfile` - Audio file handling
- `numpy` - Numerical processing

### Required

- `ollama` + `llama3.2` - Local LLM for speaker identification

## Project Structure

```
earshot/
├── earshot/
│   ├── __init__.py
│   ├── app.py              # Menu bar application
│   ├── transcriber.py      # MLX-Whisper wrapper
│   ├── audio_capture.py    # Live audio recording
│   ├── file_processor.py   # Audio/video file handling
│   ├── output_writer.py    # Generate output formats
│   ├── diarization.py      # Speaker identification (Ollama)
│   └── config.py           # Settings management
├── setup.sh                # One-command setup script
├── run_app.sh              # Run the menu bar app
├── earshot_run             # CLI tool
├── requirements.txt        # Python dependencies
└── README.md
```

## License

MIT
