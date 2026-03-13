<picture>
  <source media="(prefers-color-scheme: dark)" srcset="resources/banner-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="resources/banner-light.png">
  <img alt="Earshot - Local Audio Transcription for macOS" src="resources/banner-dark.png" width="100%">
</picture>

<p align="center">
  <strong>Record meetings. Get transcripts. All on your Mac.</strong>
</p>

<p align="center">
  <a href="#-features"><img src="https://img.shields.io/badge/Platform-macOS-blue?style=flat-square" alt="macOS"></a>
  <a href="#-requirements"><img src="https://img.shields.io/badge/Apple%20Silicon-Optimized-green?style=flat-square" alt="Apple Silicon"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="MIT License"></a>
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Setup-One%20Command-orange?style=flat-square" alt="One Command Setup"></a>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Live Meeting Capture** | Record system audio from Zoom, Teams, Meet - transcribe locally |
| 📁 **File Transcription** | Drag-and-drop audio/video files for instant transcription |
| 🗣️ **Speaker Diarization** | Automatic speaker identification using local AI |
| 🌊 **Live Waveform** | Visual feedback showing audio levels while recording |
| 🎨 **Dark & Light Themes** | Modern floating window with customizable appearance |
| 📜 **Session History** | Browse and search past transcriptions |
| 🔒 **100% Local** | Audio never leaves your Mac - privacy first |

## 🚀 Quick Start

```bash
git clone https://github.com/regmontanhani/earshot.git
cd earshot
./setup.sh
```

That's it. The setup script:
- Installs dependencies (BlackHole, Ollama, Python packages)
- Guides you through audio device configuration
- Pulls the local AI model for speaker identification

Then launch:

```bash
./run_window.sh
```

## 📖 How It Works

<table>
<tr>
<td width="80" align="center">

**1️⃣**

</td>
<td>

**Configure Audio**

Create a Multi-Output Device in Audio MIDI Setup that routes sound to both your speakers AND BlackHole for capture.

</td>
</tr>
<tr>
<td align="center">

**2️⃣**

</td>
<td>

**Record**

Click Record in the floating window. The waveform shows live audio levels. Your meeting continues normally.

</td>
</tr>
<tr>
<td align="center">

**3️⃣**

</td>
<td>

**Transcribe**

Click Stop. Earshot transcribes using MLX-Whisper (optimized for Apple Silicon), then identifies speakers with local Ollama.

</td>
</tr>
<tr>
<td align="center">

**4️⃣**

</td>
<td>

**Review**

The transcript appears with speaker labels. Browse past sessions with the ◀ ▶ buttons. Open files in any format you need.

</td>
</tr>
</table>

## ⚙️ Settings

Open settings with the ⚙️ button or <kbd>Cmd</kbd>+<kbd>,</kbd>

| Setting | Options |
|---------|---------|
| **Output Directory** | Where transcripts are saved (default: `~/Documents/Earshot`) |
| **Output Formats** | JSON, TXT, SRT, VTT, TSV |
| **Model Size** | tiny → turbo (larger = more accurate, slower) |
| **Theme** | Dark or Light |
| **Opacity** | 50% - 100% window transparency |
| **Always on Top** | Keep window above other apps |
| **OpenAI API Key** | Optional - for cloud transcription |

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| <kbd>Space</kbd> | Start/Stop recording |
| <kbd>←</kbd> / <kbd>→</kbd> | Navigate session history |
| <kbd>Cmd</kbd>+<kbd>,</kbd> | Open settings |
| <kbd>Cmd</kbd>+<kbd>Q</kbd> | Quit |

## 📝 Output Formats

| Format | Use Case |
|--------|----------|
| **JSON** | Full data with timestamps, segments, speakers |
| **TXT** | Plain text for reading or sharing |
| **SRT** | Subtitles for video editors |
| **VTT** | Web subtitles for browsers |
| **TSV** | Import into spreadsheets |

## 🔧 Requirements

| | Minimum | Recommended |
|---|---------|-------------|
| **macOS** | 12.0 Monterey | 14.0+ Sonoma |
| **Chip** | Intel or Apple Silicon | Apple Silicon (M1+) |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 5 GB | 10 GB |

## 🏗️ Architecture

```
earshot/
├── window.py           # PySide6 floating window
├── widgets/            # UI components
│   ├── waveform.py     # Live audio visualization
│   ├── transcript.py   # Transcript viewer
│   └── settings.py     # Settings dialog
├── history.py          # Session history manager
├── themes.py           # Dark/Light stylesheets
├── audio_capture.py    # PyAudio + BlackHole
├── transcriber.py      # MLX-Whisper + OpenAI
├── diarization.py      # Ollama speaker ID
├── output_writer.py    # File output
└── config.py           # Settings
```

## 🔒 Privacy

- **Audio stays local** - Transcription runs on your Mac using MLX-Whisper
- **Speaker ID is local** - Ollama runs entirely offline
- **No telemetry** - No data collection, no analytics
- **Optional cloud** - OpenAI API only if you configure it

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT - see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ❤️ for people who take too many meeting notes
</p>
