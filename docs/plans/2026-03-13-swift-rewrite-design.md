# Earshot Swift Rewrite - Design Document

## Problem

The current Python + PySide6 implementation has persistent issues on macOS:
- Window management (always-on-top) doesn't work reliably
- Menu bar shows "Python" instead of app name (requires hacks)
- Audio capture requires manual setup of BlackHole + Aggregate Devices
- No path to iOS without a complete rewrite
- Heavy dependency chain (PyAudio, faster-whisper, PySide6, pyobjc)

## Proposed Approach

Rewrite Earshot as a native Swift app using Apple frameworks. Single Xcode project with a shared framework (EarshotKit) for maximum code reuse between macOS and iOS.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Swift | Native macOS/iOS, no bridging hacks |
| UI | SwiftUI + AppKit bridging | Cross-platform with NSPanel for floating window |
| Audio (macOS) | ScreenCaptureKit + AVAudioEngine | System audio + mic, no virtual devices needed |
| Audio (iOS) | Broadcast Extension + RPScreenRecorder | System audio + mic on iPhone |
| Audio scope | User choice: all system or specific app | Any app that produces audio, including browsers |
| Transcription | WhisperKit (local only) | Apple Neural Engine optimized, works on both platforms |
| Diarization | CoreML model (pyannote-based, ~50MB) | On-device, works offline on both platforms |
| Export formats | JSON, TXT, SRT | Same as current |
| Settings | UserDefaults + Codable | Native persistence |

## Architecture

```
Earshot/
  EarshotKit/              # Shared Swift Package
    Sources/
      Audio/
        AudioMixer.swift           # Combines system + mic streams
        AudioChunk.swift           # Shared audio buffer model
      Transcription/
        TranscriptionEngine.swift  # WhisperKit wrapper
        TranscriptionResult.swift  # Timestamped segments
      Diarization/
        SpeakerIdentifier.swift    # CoreML diarization model
      Export/
        JSONExporter.swift
        TextExporter.swift
        SRTExporter.swift
      Models/
        Session.swift              # Recording session
        Transcript.swift           # Segments + speakers
        Settings.swift             # App configuration (Codable)
      History/
        SessionManager.swift       # Browse past sessions

  Earshot-macOS/             # macOS App Target
    App/
      EarshotApp.swift             # @main, MenuBarExtra
      FloatingPanel.swift          # NSPanel subclass (always-on-top)
    Audio/
      ScreenCaptureManager.swift   # ScreenCaptureKit integration
      AppAudioPicker.swift         # Enumerate running apps
    Views/
      MainView.swift               # Waveform, timer, controls
      SettingsView.swift           # Preferences sheet
      TranscriptView.swift         # Live transcript display
      HistoryView.swift            # Past sessions browser

  Earshot-iOS/               # iOS App Target
    App/
      EarshotApp.swift             # @main
    Audio/
      BroadcastManager.swift       # RPScreenRecorder integration
    BroadcastExt/
      SampleHandler.swift          # Broadcast Upload Extension
    Views/
      RecordingView.swift          # Full-screen recording
      HistoryView.swift            # Past sessions
      SettingsView.swift           # Preferences
```

## Audio Capture

### macOS - ScreenCaptureKit + AVAudioEngine

1. `SCShareableContent.current()` enumerates all running apps
2. User picks "All System Audio" or a specific app (Chrome, Zoom, Teams, etc.)
3. `SCStream` captures system/app audio as `CMSampleBuffer`
4. `AVAudioEngine` captures microphone simultaneously
5. `AudioMixer` combines both into 16kHz mono PCM for WhisperKit
6. One-time macOS permission prompt (Screen Recording) - no manual device setup

### iOS - Broadcast Extension

1. `RPScreenRecorder.shared()` with `isMicrophoneEnabled = true`
2. Captures system audio + mic in a single stream
3. Extension passes audio via App Group shared container
4. Main app reads audio chunks from shared container
5. Same `AudioChunk` model feeds into EarshotKit pipeline

### Zero Setup

No BlackHole. No Aggregate Device. No setup.sh. Just a permission prompt.

## Transcription Pipeline

```
AudioChunk (16kHz mono)
    -> WhisperKit.transcribe()
    -> [Segment {text, start, end}]
    -> SpeakerIdentifier.identify()
    -> [Segment {text, start, end, speaker}]
    -> ExportManager.write(formats: [.json, .txt, .srt])
```

- WhisperKit models: tiny, base, small, large-v3
- Models cached in ~/Library/Application Support/Earshot/Models/
- 30-second chunks with overlap for continuity
- CoreML diarization adds speaker labels post-transcription

## UI Design

### macOS

- **Floating window** via `NSPanel` (native always-on-top, no hacks)
- **Menu bar** via `MenuBarExtra` (SwiftUI native, macOS 13+)
- **App picker** dropdown showing running apps with icons
- **Settings** as `.sheet` modifier (always on top of parent window)
- **Dark/Light** via `@Environment(\.colorScheme)` with custom accent tokens

### iOS

- Full-screen recording view with waveform
- Tab bar: Record, History, Settings
- Share sheet for transcript export
- Background audio session support

### Shared Views

- WaveformView (real-time audio visualization)
- TranscriptView (scrolling transcript with speaker labels)
- SessionHistoryList (browse past recordings)

## Settings

Stored via UserDefaults with Codable struct:

```swift
struct EarshotSettings: Codable {
    var modelSize: WhisperModel = .small
    var outputFormats: Set<ExportFormat> = [.json, .txt, .srt]
    var outputDirectory: URL = defaultOutputDir
    var theme: Theme = .system
    var alwaysOnTop: Bool = true
    var audioSource: AudioSource = .systemAudio
    var selectedAppBundleID: String? = nil
    var silenceTimeout: TimeInterval = 60
    var chunkDuration: TimeInterval = 30
}
```

## Minimum Requirements

- macOS 14+ Sonoma (ScreenCaptureKit improvements)
- iOS 17+ (Broadcast Extension improvements)
- Apple Silicon recommended (Neural Engine for WhisperKit)
- Intel Macs supported (WhisperKit falls back to CPU/GPU)

## What Gets Eliminated

- BlackHole virtual audio device
- Aggregate Device manual setup
- setup.sh audio configuration
- PyAudio, portaudio (Homebrew)
- PySide6/Qt (replaced by SwiftUI)
- pyobjc hacks for menu bar name, window level
- faster-whisper / Python ML stack
- Ollama dependency for diarization
