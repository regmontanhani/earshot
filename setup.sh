#!/usr/bin/env bash
# Earshot Setup Script
# Installs all dependencies and configures audio for live meeting transcription

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Earshot Setup                            ║"
echo "║         Local Audio Transcription for macOS                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check for Apple Silicon
check_apple_silicon() {
    if [[ $(uname -m) == "arm64" ]]; then
        echo "✅ Apple Silicon detected - optimal performance"
    else
        echo "ℹ️  Intel Mac detected - transcription will use CPU mode"
    fi
    echo ""
}

# Check for Homebrew
check_homebrew() {
    if ! command -v brew &>/dev/null; then
        echo "📦 Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add to PATH for Apple Silicon
        if [[ -f /opt/homebrew/bin/brew ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        echo "✅ Homebrew is installed"
    fi
}

# Install system dependencies
install_system_deps() {
    echo ""
    echo "📦 Installing system dependencies..."
    
    # BlackHole for virtual audio device
    if ! brew list blackhole-2ch &>/dev/null; then
        echo "   Installing BlackHole 2ch (virtual audio device)..."
        brew install blackhole-2ch
        echo "   ⚠️  You may need to restart coreaudiod or reboot for BlackHole to appear."
    else
        echo "   ✅ BlackHole 2ch is installed"
    fi
    
    # PortAudio for PyAudio
    if ! brew list portaudio &>/dev/null; then
        echo "   Installing PortAudio..."
        brew install portaudio
    else
        echo "   ✅ PortAudio is installed"
    fi
    
    # ffmpeg for video processing
    if ! command -v ffmpeg &>/dev/null; then
        echo "   Installing ffmpeg..."
        brew install ffmpeg
    else
        echo "   ✅ ffmpeg is installed"
    fi
}

# Install Python dependencies
install_python_deps() {
    echo ""
    echo "🐍 Installing Python dependencies..."
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "   Python version: $PYTHON_VERSION"
    
    # Create venv if it doesn't exist
    if [ ! -d "$SCRIPT_DIR/.venv" ]; then
        echo "   Creating virtual environment..."
        python3 -m venv "$SCRIPT_DIR/.venv"
    fi
    
    # Activate and install
    source "$SCRIPT_DIR/.venv/bin/activate"
    pip install -q --upgrade pip
    pip install -q PySide6 rumps faster-whisper pyaudio soundfile numpy watchdog openai
    
    echo "   ✅ Python dependencies installed"
}

# Install Ollama for speaker diarization
install_ollama() {
    echo ""
    echo "🤖 Installing Ollama for speaker identification..."
    
    if ! command -v ollama &>/dev/null; then
        echo "   Installing Ollama..."
        brew install ollama
    else
        echo "   ✅ Ollama is installed"
    fi
    
    # Start Ollama service if not running
    if ! pgrep -x "ollama" &>/dev/null; then
        echo "   Starting Ollama service..."
        ollama serve &>/dev/null &
        sleep 2
    fi
    
    # Pull the model
    echo "   Pulling llama3.2 model (this may take a few minutes)..."
    ollama pull llama3.2
    echo "   ✅ Ollama ready with llama3.2"
}

# Setup Audio Devices (Multi-Output + Aggregate)
setup_audio_device() {
    echo ""
    echo "🔊 Setting up Audio Devices for Meeting Capture..."
    echo ""
    
    # Check if BlackHole is visible
    if ! system_profiler SPAudioDataType 2>/dev/null | grep -q "BlackHole"; then
        echo "   ⚠️  BlackHole not detected in audio devices."
        echo "   Restarting Core Audio service..."
        sudo killall coreaudiod 2>/dev/null || true
        sleep 2
    fi
    
    # Check again
    if system_profiler SPAudioDataType 2>/dev/null | grep -q "BlackHole"; then
        echo "   ✅ BlackHole detected"
    else
        echo "   ⚠️  BlackHole still not visible. You may need to reboot."
    fi
    
    # Guide user through audio device setup
    echo ""
    echo "   To capture meeting audio (others + yourself), you need TWO devices:"
    echo ""
    echo "   1. MULTI-OUTPUT DEVICE (for system sound output)"
    echo "      Sends audio to speakers AND BlackHole"
    echo ""
    echo "   2. AGGREGATE DEVICE (for Earshot input)"
    echo "      Captures BlackHole + your microphone"
    echo ""
    
    read -p "   Open Audio MIDI Setup to create these now? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "   ┌─────────────────────────────────────────────────────────┐"
        echo "   │  STEP 1: CREATE MULTI-OUTPUT DEVICE                    │"
        echo "   │                                                         │"
        echo "   │  1. Click '+' at bottom-left → 'Create Multi-Output    │"
        echo "   │     Device'                                            │"
        echo "   │                                                         │"
        echo "   │  2. Check the boxes for:                               │"
        echo "   │     ☑ BlackHole 2ch                                    │"
        echo "   │     ☑ Your speakers/headphones                         │"
        echo "   │                                                         │"
        echo "   │  3. Double-click to rename it 'Meeting Output'         │"
        echo "   └─────────────────────────────────────────────────────────┘"
        echo ""
        
        open -a "Audio MIDI Setup"
        
        read -p "   Press Enter when you've created the Multi-Output Device..."
        
        echo ""
        echo "   ┌─────────────────────────────────────────────────────────┐"
        echo "   │  STEP 2: CREATE AGGREGATE DEVICE                       │"
        echo "   │                                                         │"
        echo "   │  1. Click '+' at bottom-left → 'Create Aggregate       │"
        echo "   │     Device'                                            │"
        echo "   │                                                         │"
        echo "   │  2. Check the boxes for:                               │"
        echo "   │     ☑ BlackHole 2ch (captures others' audio)           │"
        echo "   │     ☑ MacBook Pro Microphone (captures your voice)     │"
        echo "   │                                                         │"
        echo "   │  3. Double-click to rename it 'Meeting Input'          │"
        echo "   │                                                         │"
        echo "   │  4. Close Audio MIDI Setup when done                   │"
        echo "   └─────────────────────────────────────────────────────────┘"
        echo ""
        
        read -p "   Press Enter when you've created both devices..."
        echo ""
        echo "   ✅ Audio devices setup complete!"
        echo ""
        echo "   📝 IMPORTANT: Before joining a meeting:"
        echo "      • Set Mac audio OUTPUT to 'Meeting Output'"
        echo "      • In Earshot settings, select 'Meeting Input' as input device"
    else
        echo "   You can set this up later by opening Audio MIDI Setup."
    fi
}

# Setup auto-start
setup_autostart() {
    echo ""
    read -p "🚀 Start Earshot automatically on login? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        PLIST_PATH="$HOME/Library/LaunchAgents/com.earshot.app.plist"
        
        cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.earshot.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/python3</string>
        <string>-m</string>
        <string>earshot.app</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>/tmp/earshot.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/earshot.error.log</string>
</dict>
</plist>
EOF
        
        launchctl load "$PLIST_PATH" 2>/dev/null || true
        echo "   ✅ Earshot will start on login"
    else
        echo "   Skipping auto-start setup"
    fi
}

# Make scripts executable
setup_scripts() {
    chmod +x "$SCRIPT_DIR/run_app.sh" 2>/dev/null || true
    chmod +x "$SCRIPT_DIR/earshot_run" 2>/dev/null || true
    chmod +x "$SCRIPT_DIR/build_app.sh" 2>/dev/null || true
}

# Print summary
print_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    Setup Complete! 🎉                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "To start Earshot:"
    echo "  earshot"
    echo ""
    echo "For live meeting transcription:"
    echo "  1. Set Mac audio OUTPUT to 'Meeting Output'"
    echo "  2. In Earshot settings (⌘,), select 'Meeting Input' as input"
    echo "  3. Join your meeting"
    echo "  4. Click the record button ⏺"
    echo ""
    echo "This captures BOTH meeting audio AND your microphone!"
    echo ""
    echo "Transcripts are saved to: ~/Documents/Earshot/"
    echo ""
}

# Run setup
main() {
    check_apple_silicon
    check_homebrew
    install_system_deps
    install_python_deps
    install_ollama
    setup_audio_device
    setup_scripts
    setup_autostart
    print_summary
}

main "$@"
