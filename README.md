# WhisperX

A macOS menu bar app for local audio transcription using MLX-optimized Whisper models. Perfect for transcribing meetings when you don't have admin access to record.

![Menu Bar](https://img.shields.io/badge/macOS-Menu%20Bar%20App-blue)
![Apple Silicon](https://img.shields.io/badge/Apple%20Silicon-Optimized-green)
![Local](https://img.shields.io/badge/100%25-Local-orange)

## Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Live Meeting Transcription** | Capture system audio in real-time from any app (Zoom, Teams, Meet, etc.) |
| 📁 **File Transcription** | Transcribe audio/video files (m4a, mp3, wav, mp4, mkv, mov, etc.) |
| 🔴 **Live Audio Monitor** | Visual feedback in menu bar showing audio levels while recording |
| 🤖 **Speaker Diarization** | Automatic speaker identification using local Ollama LLM |
| 💻 **Fully Local** | No cloud APIs, no costs - runs entirely on your Mac |
| 📝 **Multiple Formats** | Outputs JSON, TXT, SRT, VTT, TSV |
| ⏹️ **Auto-Stop** | Automatically saves after 60 seconds of silence |

## Quick Start

### One-Command Setup

```bash
git clone https://github.com/regmontanhani/whisperx.git
cd whisperx
./setup.sh
```

The setup script will:
- Install all dependencies (Homebrew, BlackHole, Python packages)
- Guide you through audio device configuration
- Optionally install Ollama for speaker identification
- Optionally configure auto-start on login

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

#### 4. (Optional) Ollama for Speaker Identification

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
   - Files saved to `~/Documents/WhisperX/`

### File Transcription

1. Click **🎙️ → Transcribe File...**
2. Select any audio or video file
3. Wait for transcription (notification when complete)
4. Output files saved next to the original file

## Output Formats

All transcriptions generate these files:

| Format | Extension | Description |
|--------|-----------|-------------|
| **JSON** | `.json` | Full transcript with timestamps, segments, metadata |
| **Text** | `.txt` | Plain text transcript |
| **SRT** | `.srt` | SubRip subtitles (for video players) |
| **VTT** | `.vtt` | WebVTT subtitles (for web/browsers) |
| **TSV** | `.tsv` | Tab-separated values (for spreadsheets) |

## Models

Select model in **Settings → Model Size**:

| Model | Download Size | RAM Usage | Speed | Quality |
|-------|--------------|-----------|-------|---------|
| `tiny` | ~75 MB | ~1 GB | ⚡⚡⚡⚡⚡ | ★☆☆☆☆ |
| `base` | ~140 MB | ~1 GB | ⚡⚡⚡⚡ | ★★☆☆☆ |
| `small` | ~460 MB | ~2 GB | ⚡⚡⚡ | ★★★☆☆ |
| `medium` | ~1.5 GB | ~5 GB | ⚡⚡ | ★★★★☆ |
| `large-v3` | ~3 GB | ~10 GB | ⚡ | ★★★★★ |

**Recommendation:** Use `large-v3` for best quality. Your M4 Max handles it easily.

Models download automatically on first use.

## Configuration

Settings are stored in `~/.config/whisperx/settings.json`:

```json
{
  "model_size": "large-v3",
  "output_dir": "~/Documents/WhisperX",
  "audio_device": "BlackHole 2ch",
  "silence_timeout": 60,
  "chunk_duration": 30,
  "output_formats": ["json", "txt", "srt", "vtt", "tsv"]
}
```

## Auto-Start on Login

```bash
# Enable
launchctl load ~/Library/LaunchAgents/com.whisperx.app.plist

# Disable
launchctl unload ~/Library/LaunchAgents/com.whisperx.app.plist
```

## CLI Tool

For quick command-line transcription (uses OpenAI API):

```bash
# Set your API key
echo 'OPENAI_API_KEY=sk-...' > .env

# Transcribe a file
./whisperx_run /path/to/audio.m4a
```

## Troubleshooting

### BlackHole not appearing as audio device

```bash
sudo killall coreaudiod
```

If still not visible, reboot your Mac.

### No audio being captured

1. Check System Settings → Sound → Output is set to "Meeting Audio"
2. Check WhisperX Settings → Audio Input is set to "BlackHole 2ch"
3. Make sure the meeting app is playing audio

### Transcription quality is poor

- Switch to a larger model (Settings → Model Size → `large-v3`)
- Ensure good audio quality in the meeting
- Reduce background noise

### App not appearing in menu bar

The app may be running as a Dock app instead. This version includes a fix for this - restart the app:

```bash
pkill -f "whisperx_app.app"
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
- `mlx-whisper` - MLX-optimized Whisper for Apple Silicon
- `pyaudio` - Audio capture
- `soundfile` - Audio file handling
- `numpy` - Numerical processing

### Optional

- `ollama` + `llama3.2` - Local LLM for speaker identification

## Project Structure

```
whisperx/
├── whisperx_app/
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
├── whisperx_run            # CLI tool (OpenAI API)
├── requirements.txt        # Python dependencies
└── README.md
```

## License

MIT
