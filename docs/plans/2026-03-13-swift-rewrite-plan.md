# Earshot Swift Rewrite - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Rewrite Earshot as a native Swift app with shared framework for macOS and iOS, eliminating all Python dependencies and manual audio device setup.

**Architecture:** Single Xcode project with EarshotKit (shared Swift Package for transcription, diarization, export, models), Earshot-macOS (ScreenCaptureKit + NSPanel + MenuBarExtra), and Earshot-iOS (Broadcast Extension + SwiftUI). Audio captured via ScreenCaptureKit (mac) or RPScreenRecorder (iOS), transcribed by WhisperKit, speaker-labeled by CoreML diarization model.

**Tech Stack:** Swift 5.9+, SwiftUI, AppKit (NSPanel bridging), ScreenCaptureKit, AVFoundation, WhisperKit, CoreML, XCTest

**Design Doc:** `docs/plans/2026-03-13-swift-rewrite-design.md`

---

## Phase 1: Project Scaffolding & Shared Models

Milestone: Xcode project builds, all targets compile, shared models exist with tests.

### Task 1.1: Create Xcode Project Structure

**Files:**
- Create: `Earshot.xcodeproj` (via Xcode CLI / manual)
- Create: `EarshotKit/Package.swift`
- Create: `EarshotKit/Sources/EarshotKit/EarshotKit.swift` (namespace)
- Create: `Earshot-macOS/EarshotApp.swift`
- Create: `Earshot-iOS/EarshotApp.swift`

**Step 1: Create the project directory**

```bash
cd "/Users/regmontanhani/GitHub work/earshot"
mkdir -p Earshot-Swift
cd Earshot-Swift
```

**Step 2: Create the shared Swift Package**

```bash
mkdir -p EarshotKit/Sources/EarshotKit
mkdir -p EarshotKit/Tests/EarshotKitTests
```

Create `EarshotKit/Package.swift`:
```swift
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "EarshotKit",
    platforms: [
        .macOS(.v14),
        .iOS(.v17)
    ],
    products: [
        .library(name: "EarshotKit", targets: ["EarshotKit"])
    ],
    dependencies: [
        .package(url: "https://github.com/argmaxinc/WhisperKit.git", from: "0.9.0"),
    ],
    targets: [
        .target(
            name: "EarshotKit",
            dependencies: ["WhisperKit"],
            path: "Sources/EarshotKit"
        ),
        .testTarget(
            name: "EarshotKitTests",
            dependencies: ["EarshotKit"],
            path: "Tests/EarshotKitTests"
        ),
    ]
)
```

**Step 3: Create the Xcode workspace**

Use `xcodegen` or create manually. The workspace includes:
- EarshotKit (local Swift Package)
- Earshot-macOS (macOS app target, depends on EarshotKit)
- Earshot-iOS (iOS app target, depends on EarshotKit)

```bash
# If using xcodegen, create project.yml
# Otherwise, create via Xcode: File > New > Project > Multiplatform App
```

**Step 4: Verify everything builds**

```bash
cd EarshotKit && swift build && swift test
```

Expected: Build succeeds, 0 tests run.

**Step 5: Commit**

```bash
git checkout -b feature/swift-rewrite
git add Earshot-Swift/
git commit -m "chore: scaffold Swift project with EarshotKit package"
```

---

### Task 1.2: Shared Models - Transcript & Segment

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Models/Segment.swift`
- Create: `EarshotKit/Sources/EarshotKit/Models/Transcript.swift`
- Test: `EarshotKit/Tests/EarshotKitTests/Models/TranscriptTests.swift`

**Step 1: Write the failing test**

```swift
// TranscriptTests.swift
import XCTest
@testable import EarshotKit

final class TranscriptTests: XCTestCase {
    func testSegmentCreation() {
        let segment = Segment(text: "Hello world", start: 0.0, end: 2.5)
        XCTAssertEqual(segment.text, "Hello world")
        XCTAssertEqual(segment.start, 0.0)
        XCTAssertEqual(segment.end, 2.5)
        XCTAssertNil(segment.speaker)
    }

    func testSegmentWithSpeaker() {
        let segment = Segment(text: "Hi", start: 1.0, end: 1.5, speaker: "Alice")
        XCTAssertEqual(segment.speaker, "Alice")
    }

    func testTranscriptFullText() {
        let segments = [
            Segment(text: "Hello", start: 0.0, end: 1.0),
            Segment(text: "World", start: 1.0, end: 2.0),
        ]
        let transcript = Transcript(segments: segments)
        XCTAssertEqual(transcript.fullText, "Hello World")
    }

    func testTranscriptDuration() {
        let segments = [
            Segment(text: "A", start: 0.0, end: 1.0),
            Segment(text: "B", start: 5.0, end: 8.5),
        ]
        let transcript = Transcript(segments: segments)
        XCTAssertEqual(transcript.duration, 8.5)
    }

    func testTranscriptCodable() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Test", start: 0.0, end: 1.0, speaker: "Bob")
        ])
        let data = try JSONEncoder().encode(transcript)
        let decoded = try JSONDecoder().decode(Transcript.self, from: data)
        XCTAssertEqual(decoded.segments.count, 1)
        XCTAssertEqual(decoded.segments[0].speaker, "Bob")
    }
}
```

**Step 2: Run test to verify it fails**

```bash
cd EarshotKit && swift test --filter TranscriptTests
```

Expected: FAIL - types not defined.

**Step 3: Write minimal implementation**

```swift
// Segment.swift
import Foundation

public struct Segment: Codable, Identifiable, Sendable {
    public let id: UUID
    public var text: String
    public var start: TimeInterval
    public var end: TimeInterval
    public var speaker: String?

    public init(text: String, start: TimeInterval, end: TimeInterval, speaker: String? = nil) {
        self.id = UUID()
        self.text = text
        self.start = start
        self.end = end
        self.speaker = speaker
    }

    public var duration: TimeInterval { end - start }
}
```

```swift
// Transcript.swift
import Foundation

public struct Transcript: Codable, Sendable {
    public var segments: [Segment]
    public var createdAt: Date

    public init(segments: [Segment], createdAt: Date = .now) {
        self.segments = segments
        self.createdAt = createdAt
    }

    public var fullText: String {
        segments.map(\.text).joined(separator: " ")
    }

    public var duration: TimeInterval {
        segments.map(\.end).max() ?? 0
    }
}
```

**Step 4: Run test to verify it passes**

```bash
cd EarshotKit && swift test --filter TranscriptTests
```

Expected: All 5 tests PASS.

**Step 5: Commit**

```bash
git add -A && git commit -m "feat: add Transcript and Segment models with tests"
```

---

### Task 1.3: Shared Models - Settings

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Models/Settings.swift`
- Test: `EarshotKit/Tests/EarshotKitTests/Models/SettingsTests.swift`

**Step 1: Write the failing test**

```swift
// SettingsTests.swift
import XCTest
@testable import EarshotKit

final class SettingsTests: XCTestCase {
    func testDefaultSettings() {
        let settings = EarshotSettings()
        XCTAssertEqual(settings.modelSize, .small)
        XCTAssertTrue(settings.outputFormats.contains(.json))
        XCTAssertTrue(settings.outputFormats.contains(.txt))
        XCTAssertTrue(settings.outputFormats.contains(.srt))
        XCTAssertTrue(settings.alwaysOnTop)
        XCTAssertEqual(settings.audioSource, .systemAudio)
        XCTAssertEqual(settings.chunkDuration, 30)
        XCTAssertEqual(settings.silenceTimeout, 60)
    }

    func testSettingsCodable() throws {
        var settings = EarshotSettings()
        settings.modelSize = .largeV3
        settings.alwaysOnTop = false

        let data = try JSONEncoder().encode(settings)
        let decoded = try JSONDecoder().decode(EarshotSettings.self, from: data)
        XCTAssertEqual(decoded.modelSize, .largeV3)
        XCTAssertFalse(decoded.alwaysOnTop)
    }

    func testWhisperModelRawValues() {
        XCTAssertEqual(WhisperModel.tiny.rawValue, "tiny")
        XCTAssertEqual(WhisperModel.largeV3.rawValue, "large-v3")
    }
}
```

**Step 2: Run test to verify it fails**

```bash
cd EarshotKit && swift test --filter SettingsTests
```

**Step 3: Write minimal implementation**

```swift
// Settings.swift
import Foundation

public enum WhisperModel: String, Codable, CaseIterable, Sendable {
    case tiny, base, small, medium
    case largeV3 = "large-v3"
    case turbo
}

public enum ExportFormat: String, Codable, CaseIterable, Sendable {
    case json, txt, srt
}

public enum AudioSource: String, Codable, Sendable {
    case systemAudio = "system"
    case specificApp = "app"
}

public struct EarshotSettings: Codable, Sendable {
    public var modelSize: WhisperModel
    public var outputFormats: Set<ExportFormat>
    public var outputDirectory: String
    public var alwaysOnTop: Bool
    public var audioSource: AudioSource
    public var selectedAppBundleID: String?
    public var silenceTimeout: TimeInterval
    public var chunkDuration: TimeInterval

    public init(
        modelSize: WhisperModel = .small,
        outputFormats: Set<ExportFormat> = [.json, .txt, .srt],
        outputDirectory: String = "~/Documents/Earshot",
        alwaysOnTop: Bool = true,
        audioSource: AudioSource = .systemAudio,
        selectedAppBundleID: String? = nil,
        silenceTimeout: TimeInterval = 60,
        chunkDuration: TimeInterval = 30
    ) {
        self.modelSize = modelSize
        self.outputFormats = outputFormats
        self.outputDirectory = outputDirectory
        self.alwaysOnTop = alwaysOnTop
        self.audioSource = audioSource
        self.selectedAppBundleID = selectedAppBundleID
        self.silenceTimeout = silenceTimeout
        self.chunkDuration = chunkDuration
    }
}
```

**Step 4: Run test to verify it passes**

```bash
cd EarshotKit && swift test --filter SettingsTests
```

Expected: All 3 tests PASS.

**Step 5: Commit**

```bash
git add -A && git commit -m "feat: add EarshotSettings model with enums and tests"
```

---

### Task 1.4: Shared Models - Session & History

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Models/Session.swift`
- Create: `EarshotKit/Sources/EarshotKit/History/SessionManager.swift`
- Test: `EarshotKit/Tests/EarshotKitTests/Models/SessionTests.swift`

**Step 1: Write the failing test**

```swift
// SessionTests.swift
import XCTest
@testable import EarshotKit

final class SessionTests: XCTestCase {
    func testSessionCreation() {
        let session = RecordingSession(
            name: "Meeting 2026-03-13",
            transcript: Transcript(segments: [
                Segment(text: "Hello", start: 0, end: 1)
            ])
        )
        XCTAssertEqual(session.name, "Meeting 2026-03-13")
        XCTAssertEqual(session.transcript.segments.count, 1)
        XCTAssertNotNil(session.createdAt)
    }

    func testSessionManagerScanEmpty() throws {
        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let manager = SessionManager(directory: tempDir)
        let sessions = manager.scan()
        XCTAssertTrue(sessions.isEmpty)
    }
}
```

**Step 2: Run test to verify it fails**

```bash
cd EarshotKit && swift test --filter SessionTests
```

**Step 3: Write minimal implementation**

```swift
// Session.swift
import Foundation

public struct RecordingSession: Codable, Identifiable, Sendable {
    public let id: UUID
    public var name: String
    public var transcript: Transcript
    public var createdAt: Date
    public var outputFiles: [String]

    public init(
        name: String,
        transcript: Transcript,
        createdAt: Date = .now,
        outputFiles: [String] = []
    ) {
        self.id = UUID()
        self.name = name
        self.transcript = transcript
        self.createdAt = createdAt
        self.outputFiles = outputFiles
    }
}
```

```swift
// SessionManager.swift
import Foundation

public final class SessionManager: Sendable {
    private let directory: URL

    public init(directory: URL) {
        self.directory = directory
    }

    public func scan() -> [RecordingSession] {
        guard let contents = try? FileManager.default.contentsOfDirectory(
            at: directory,
            includingPropertiesForKeys: [.contentModificationDateKey],
            options: [.skipsHiddenFiles]
        ) else { return [] }

        return contents
            .filter { $0.pathExtension == "json" }
            .compactMap { url -> RecordingSession? in
                guard let data = try? Data(contentsOf: url),
                      let session = try? JSONDecoder().decode(RecordingSession.self, from: data)
                else { return nil }
                return session
            }
            .sorted { $0.createdAt > $1.createdAt }
    }
}
```

**Step 4: Run test to verify it passes**

```bash
cd EarshotKit && swift test --filter SessionTests
```

**Step 5: Commit**

```bash
git add -A && git commit -m "feat: add RecordingSession model and SessionManager"
```

---

## Phase 2: Export Formats

Milestone: JSON, TXT, SRT exporters work with tests.

### Task 2.1: JSON Exporter

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Export/JSONExporter.swift`
- Test: `EarshotKit/Tests/EarshotKitTests/Export/JSONExporterTests.swift`

**Step 1: Write the failing test**

```swift
// JSONExporterTests.swift
import XCTest
@testable import EarshotKit

final class JSONExporterTests: XCTestCase {
    func testExportProducesValidJSON() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Hello world", start: 0.0, end: 2.5, speaker: "Alice"),
            Segment(text: "How are you", start: 3.0, end: 5.0, speaker: "Bob"),
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let url = try JSONExporter.export(transcript, to: tempDir, name: "test")
        XCTAssertTrue(url.pathExtension == "json")

        let data = try Data(contentsOf: url)
        let decoded = try JSONDecoder().decode(Transcript.self, from: data)
        XCTAssertEqual(decoded.segments.count, 2)
        XCTAssertEqual(decoded.segments[0].speaker, "Alice")
    }
}
```

**Step 2: Run test, verify fail. Step 3: Implement:**

```swift
// JSONExporter.swift
import Foundation

public enum JSONExporter {
    public static func export(_ transcript: Transcript, to directory: URL, name: String) throws -> URL {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        let data = try encoder.encode(transcript)
        let url = directory.appendingPathComponent("\(name).json")
        try data.write(to: url)
        return url
    }
}
```

**Step 4: Run test, verify pass. Step 5: Commit.**

---

### Task 2.2: Text Exporter

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Export/TextExporter.swift`
- Test: `EarshotKit/Tests/EarshotKitTests/Export/TextExporterTests.swift`

**Step 1: Write the failing test**

```swift
// TextExporterTests.swift
import XCTest
@testable import EarshotKit

final class TextExporterTests: XCTestCase {
    func testExportPlainText() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Hello world", start: 0.0, end: 2.5),
            Segment(text: "How are you", start: 3.0, end: 5.0),
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let url = try TextExporter.export(transcript, to: tempDir, name: "test")
        let content = try String(contentsOf: url, encoding: .utf8)
        XCTAssertTrue(content.contains("Hello world"))
        XCTAssertTrue(content.contains("How are you"))
    }

    func testExportWithSpeakers() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Hi", start: 0.0, end: 1.0, speaker: "Alice"),
            Segment(text: "Hey", start: 1.0, end: 2.0, speaker: "Bob"),
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let url = try TextExporter.export(transcript, to: tempDir, name: "test")
        let content = try String(contentsOf: url, encoding: .utf8)
        XCTAssertTrue(content.contains("[Alice]"))
        XCTAssertTrue(content.contains("[Bob]"))
    }
}
```

**Step 2: Run test, verify fail. Step 3: Implement:**

```swift
// TextExporter.swift
import Foundation

public enum TextExporter {
    public static func export(_ transcript: Transcript, to directory: URL, name: String) throws -> URL {
        var lines: [String] = []
        var currentSpeaker: String?

        for segment in transcript.segments {
            if let speaker = segment.speaker, speaker != currentSpeaker {
                if !lines.isEmpty { lines.append("") }
                lines.append("[\(speaker)]")
                currentSpeaker = speaker
            }
            lines.append(segment.text)
        }

        let url = directory.appendingPathComponent("\(name).txt")
        try lines.joined(separator: "\n").write(to: url, atomically: true, encoding: .utf8)
        return url
    }
}
```

**Step 4: Run test, verify pass. Step 5: Commit.**

---

### Task 2.3: SRT Exporter

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Export/SRTExporter.swift`
- Test: `EarshotKit/Tests/EarshotKitTests/Export/SRTExporterTests.swift`

**Step 1: Write the failing test**

```swift
// SRTExporterTests.swift
import XCTest
@testable import EarshotKit

final class SRTExporterTests: XCTestCase {
    func testSRTFormat() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Hello world", start: 0.0, end: 2.5),
            Segment(text: "How are you", start: 3.0, end: 5.123),
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let url = try SRTExporter.export(transcript, to: tempDir, name: "test")
        let content = try String(contentsOf: url, encoding: .utf8)

        // SRT format: index, timestamp, text, blank line
        XCTAssertTrue(content.contains("1\n00:00:00,000 --> 00:00:02,500\nHello world"))
        XCTAssertTrue(content.contains("2\n00:00:03,000 --> 00:00:05,123\nHow are you"))
    }

    func testSRTTimestampFormat() {
        // 3723.456 seconds = 01:02:03,456
        let formatted = SRTExporter.formatTimestamp(3723.456)
        XCTAssertEqual(formatted, "01:02:03,456")
    }
}
```

**Step 2: Run test, verify fail. Step 3: Implement:**

```swift
// SRTExporter.swift
import Foundation

public enum SRTExporter {
    public static func export(_ transcript: Transcript, to directory: URL, name: String) throws -> URL {
        var srt = ""
        for (index, segment) in transcript.segments.enumerated() {
            let start = formatTimestamp(segment.start)
            let end = formatTimestamp(segment.end)
            srt += "\(index + 1)\n\(start) --> \(end)\n\(segment.text)\n\n"
        }

        let url = directory.appendingPathComponent("\(name).srt")
        try srt.write(to: url, atomically: true, encoding: .utf8)
        return url
    }

    public static func formatTimestamp(_ seconds: TimeInterval) -> String {
        let hours = Int(seconds) / 3600
        let minutes = (Int(seconds) % 3600) / 60
        let secs = Int(seconds) % 60
        let millis = Int((seconds.truncatingRemainder(dividingBy: 1)) * 1000)
        return String(format: "%02d:%02d:%02d,%03d", hours, minutes, secs, millis)
    }
}
```

**Step 4: Run test, verify pass. Step 5: Commit.**

---

### Task 2.4: Export Manager (facade)

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Export/ExportManager.swift`
- Test: `EarshotKit/Tests/EarshotKitTests/Export/ExportManagerTests.swift`

**Step 1: Write the failing test**

```swift
// ExportManagerTests.swift
import XCTest
@testable import EarshotKit

final class ExportManagerTests: XCTestCase {
    func testExportAllFormats() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Test", start: 0.0, end: 1.0)
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let urls = try ExportManager.export(
            transcript,
            to: tempDir,
            name: "meeting",
            formats: [.json, .txt, .srt]
        )
        XCTAssertEqual(urls.count, 3)
        XCTAssertTrue(urls.contains { $0.pathExtension == "json" })
        XCTAssertTrue(urls.contains { $0.pathExtension == "txt" })
        XCTAssertTrue(urls.contains { $0.pathExtension == "srt" })
    }
}
```

**Step 2-3: Implement:**

```swift
// ExportManager.swift
import Foundation

public enum ExportManager {
    public static func export(
        _ transcript: Transcript,
        to directory: URL,
        name: String,
        formats: Set<ExportFormat>
    ) throws -> [URL] {
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        var urls: [URL] = []
        for format in formats {
            let url: URL = switch format {
            case .json: try JSONExporter.export(transcript, to: directory, name: name)
            case .txt:  try TextExporter.export(transcript, to: directory, name: name)
            case .srt:  try SRTExporter.export(transcript, to: directory, name: name)
            }
            urls.append(url)
        }
        return urls
    }
}
```

**Step 4: Run test, verify pass. Step 5: Commit.**

---

## Phase 3: Audio Infrastructure

Milestone: ScreenCaptureKit captures system audio, AVAudioEngine captures mic, AudioMixer combines them.

### Task 3.1: AudioChunk Model & AudioMixer Protocol

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Audio/AudioChunk.swift`
- Create: `EarshotKit/Sources/EarshotKit/Audio/AudioMixerProtocol.swift`
- Test: `EarshotKit/Tests/EarshotKitTests/Audio/AudioChunkTests.swift`

**Step 1: Write the failing test**

```swift
// AudioChunkTests.swift
import XCTest
import AVFoundation
@testable import EarshotKit

final class AudioChunkTests: XCTestCase {
    func testAudioChunkCreation() {
        let format = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: 16000)!
        buffer.frameLength = 16000

        let chunk = AudioChunk(buffer: buffer, timestamp: 0.0)
        XCTAssertEqual(chunk.sampleRate, 16000)
        XCTAssertEqual(chunk.duration, 1.0, accuracy: 0.01)
    }
}
```

**Step 2: Run test, verify fail. Step 3: Implement:**

```swift
// AudioChunk.swift
import AVFoundation

public struct AudioChunk: Sendable {
    public let buffer: AVAudioPCMBuffer
    public let timestamp: TimeInterval

    public init(buffer: AVAudioPCMBuffer, timestamp: TimeInterval) {
        self.buffer = buffer
        self.timestamp = timestamp
    }

    public var sampleRate: Double { buffer.format.sampleRate }
    public var duration: TimeInterval {
        Double(buffer.frameLength) / sampleRate
    }
}
```

```swift
// AudioMixerProtocol.swift
import AVFoundation

public protocol AudioCaptureDelegate: AnyObject, Sendable {
    func didCaptureAudio(_ chunk: AudioChunk)
    func didUpdateLevel(_ level: Float)
    func didEncounterError(_ error: Error)
}
```

**Step 4: Run test, verify pass. Step 5: Commit.**

---

### Task 3.2: macOS ScreenCaptureKit Manager

**Files:**
- Create: `Earshot-macOS/Audio/ScreenCaptureManager.swift`
- Create: `Earshot-macOS/Audio/AppAudioPicker.swift`

> Note: ScreenCaptureKit requires entitlements and cannot be unit tested easily.
> Test manually by running the macOS app.

**Step 1: Implement ScreenCaptureManager**

```swift
// ScreenCaptureManager.swift
import ScreenCaptureKit
import AVFoundation
import EarshotKit

@MainActor
final class ScreenCaptureManager: NSObject, ObservableObject {
    @Published var availableApps: [SCRunningApplication] = []
    @Published var isCapturing = false

    private var stream: SCStream?
    private var audioEngine: AVAudioEngine?
    weak var delegate: AudioCaptureDelegate?

    // Settings
    var captureAllAudio = true
    var selectedApp: SCRunningApplication?

    func refreshApps() async throws {
        let content = try await SCShareableContent.excludingDesktopWindows(
            false, onScreenWindowsOnly: false
        )
        availableApps = content.applications
            .filter { $0.bundleIdentifier != Bundle.main.bundleIdentifier }
            .sorted { ($0.applicationName) < ($1.applicationName) }
    }

    func startCapture() async throws {
        let content = try await SCShareableContent.excludingDesktopWindows(
            false, onScreenWindowsOnly: false
        )

        let filter: SCContentFilter
        if captureAllAudio {
            // Capture all system audio except our own app
            let excluded = content.applications.filter {
                $0.bundleIdentifier == Bundle.main.bundleIdentifier
            }
            filter = SCContentFilter(
                display: content.displays.first!,
                excludingApplications: excluded,
                exceptingWindows: []
            )
        } else if let app = selectedApp {
            // Capture audio from a specific app only
            let windows = content.windows.filter {
                $0.owningApplication?.bundleIdentifier == app.bundleIdentifier
            }
            filter = SCContentFilter(
                display: content.displays.first!,
                includingApplications: [app],
                exceptingWindows: []
            )
        } else {
            throw CaptureError.noAppSelected
        }

        let config = SCStreamConfiguration()
        config.capturesAudio = true
        config.sampleRate = 16000
        config.channelCount = 1
        config.excludesCurrentProcessAudio = true
        // Don't capture video - audio only
        config.width = 1
        config.height = 1

        let stream = SCStream(filter: filter, configuration: config, delegate: nil)
        try stream.addStreamOutput(self, type: .audio, sampleHandlerQueue: .global())
        try await stream.startCapture()
        self.stream = stream
        isCapturing = true

        // Start microphone capture simultaneously
        try startMicrophoneCapture()
    }

    func stopCapture() async throws {
        try await stream?.stopCapture()
        stream = nil
        audioEngine?.stop()
        audioEngine = nil
        isCapturing = false
    }

    private func startMicrophoneCapture() throws {
        let engine = AVAudioEngine()
        let inputNode = engine.inputNode
        let format = inputNode.outputFormat(forBus: 0)

        inputNode.installTap(onBus: 0, bufferSize: 4096, format: format) { [weak self] buffer, time in
            // Mix with system audio in delegate
            let chunk = AudioChunk(buffer: buffer, timestamp: time.sampleTime.toSeconds(sampleRate: format.sampleRate))
            self?.delegate?.didCaptureAudio(chunk)
        }

        engine.prepare()
        try engine.start()
        self.audioEngine = engine
    }
}

extension ScreenCaptureManager: SCStreamOutput {
    nonisolated func stream(_ stream: SCStream, didOutputSampleBuffer sampleBuffer: CMSampleBuffer, of type: SCStreamOutputType) {
        guard type == .audio else { return }
        // Convert CMSampleBuffer to AVAudioPCMBuffer and forward
        guard let buffer = sampleBuffer.toAudioBuffer() else { return }
        let chunk = AudioChunk(buffer: buffer, timestamp: CACurrentMediaTime())
        delegate?.didCaptureAudio(chunk)

        // Calculate audio level for waveform
        let level = buffer.rmsLevel()
        delegate?.didUpdateLevel(level)
    }
}

enum CaptureError: Error {
    case noAppSelected
    case noDisplayFound
}
```

```swift
// AppAudioPicker.swift
import ScreenCaptureKit
import SwiftUI

struct AppAudioPicker: View {
    @ObservedObject var captureManager: ScreenCaptureManager

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Picker("Audio Source", selection: $captureManager.captureAllAudio) {
                Text("All System Audio").tag(true)
                Text("Specific App").tag(false)
            }
            .pickerStyle(.segmented)

            if !captureManager.captureAllAudio {
                Picker("Application", selection: $captureManager.selectedApp) {
                    Text("Select an app...").tag(nil as SCRunningApplication?)
                    ForEach(captureManager.availableApps, id: \.bundleIdentifier) { app in
                        Text(app.applicationName).tag(app as SCRunningApplication?)
                    }
                }
            }
        }
    }
}
```

**Step 2: Add entitlement for screen recording**

In `Earshot-macOS.entitlements`:
```xml
<key>com.apple.security.screen-recording</key>
<true/>
```

**Step 3: Build macOS target to verify compilation**

```bash
xcodebuild -scheme Earshot-macOS -destination 'platform=macOS' build
```

**Step 4: Commit**

```bash
git add -A && git commit -m "feat: ScreenCaptureKit audio capture with app picker"
```

---

### Task 3.3: AVAudioPCMBuffer Extensions

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Audio/AudioExtensions.swift`
- Test: `EarshotKit/Tests/EarshotKitTests/Audio/AudioExtensionsTests.swift`

**Step 1: Write the failing test**

```swift
// AudioExtensionsTests.swift
import XCTest
import AVFoundation
@testable import EarshotKit

final class AudioExtensionsTests: XCTestCase {
    func testRMSLevelSilence() {
        let format = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: 1600)!
        buffer.frameLength = 1600
        // Buffer is zero-initialized = silence
        XCTAssertEqual(buffer.rmsLevel(), 0.0, accuracy: 0.001)
    }

    func testRMSLevelNonSilence() {
        let format = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: 1600)!
        buffer.frameLength = 1600

        // Fill with non-zero samples
        if let channelData = buffer.floatChannelData?[0] {
            for i in 0..<1600 {
                channelData[i] = 0.5
            }
        }
        XCTAssertGreaterThan(buffer.rmsLevel(), 0.0)
    }
}
```

**Step 2: Run test, verify fail. Step 3: Implement:**

```swift
// AudioExtensions.swift
import AVFoundation
import CoreMedia

extension AVAudioPCMBuffer {
    public func rmsLevel() -> Float {
        guard let channelData = floatChannelData?[0], frameLength > 0 else { return 0 }
        var sum: Float = 0
        for i in 0..<Int(frameLength) {
            sum += channelData[i] * channelData[i]
        }
        return sqrt(sum / Float(frameLength))
    }
}

extension CMSampleBuffer {
    public func toAudioBuffer() -> AVAudioPCMBuffer? {
        guard let formatDesc = formatDescription,
              let asbd = CMAudioFormatDescriptionGetStreamBasicDescription(formatDesc)
        else { return nil }

        guard let avFormat = AVAudioFormat(streamDescription: asbd.pointee) else { return nil }
        guard let blockBuffer = CMSampleBufferGetDataBuffer(self) else { return nil }

        let frameCount = CMSampleBufferGetNumSamples(self)
        guard let pcmBuffer = AVAudioPCMBuffer(pcmFormat: avFormat, frameCapacity: AVAudioFrameCount(frameCount))
        else { return nil }

        pcmBuffer.frameLength = AVAudioFrameCount(frameCount)

        var lengthAtOffset: Int = 0
        var totalLength: Int = 0
        var dataPointer: UnsafeMutablePointer<CChar>?
        CMBlockBufferGetDataPointer(blockBuffer, atOffset: 0, lengthAtOffsetOut: &lengthAtOffset, totalLengthOut: &totalLength, dataPointerOut: &dataPointer)

        guard let source = dataPointer, let dest = pcmBuffer.floatChannelData?[0] else { return nil }
        memcpy(dest, source, totalLength)

        return pcmBuffer
    }
}
```

**Step 4: Run test, verify pass. Step 5: Commit.**

---

## Phase 4: WhisperKit Transcription

Milestone: Can transcribe an audio buffer and get timestamped segments.

### Task 4.1: TranscriptionEngine

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Transcription/TranscriptionEngine.swift`
- Test: `EarshotKit/Tests/EarshotKitTests/Transcription/TranscriptionEngineTests.swift`

**Step 1: Write the failing test**

```swift
// TranscriptionEngineTests.swift
import XCTest
@testable import EarshotKit

final class TranscriptionEngineTests: XCTestCase {
    func testEngineInitialization() async throws {
        // This test verifies the engine can be created
        // Full transcription tests require a downloaded model
        let engine = TranscriptionEngine(model: .tiny)
        XCTAssertEqual(engine.modelSize, .tiny)
        XCTAssertFalse(engine.isLoaded)
    }
}
```

**Step 2: Run test, verify fail. Step 3: Implement:**

```swift
// TranscriptionEngine.swift
import Foundation
import WhisperKit

public actor TranscriptionEngine {
    public let modelSize: WhisperModel
    private var whisperKit: WhisperKit?

    public var isLoaded: Bool { whisperKit != nil }

    public init(model: WhisperModel) {
        self.modelSize = model
    }

    public func loadModel() async throws {
        let modelName = "openai_whisper-\(modelSize.rawValue)"
        whisperKit = try await WhisperKit(
            model: modelName,
            verbose: false,
            prewarm: true
        )
    }

    public func transcribe(audioURL: URL) async throws -> Transcript {
        if !isLoaded { try await loadModel() }
        guard let kit = whisperKit else {
            throw TranscriptionError.modelNotLoaded
        }

        let results = try await kit.transcribe(audioPath: audioURL.path())

        let segments = results.flatMap { result in
            (result.segments ?? []).map { seg in
                Segment(
                    text: seg.text.trimmingCharacters(in: .whitespaces),
                    start: TimeInterval(seg.start),
                    end: TimeInterval(seg.end)
                )
            }
        }

        return Transcript(segments: segments)
    }

    public func transcribe(buffer: AVAudioPCMBuffer) async throws -> Transcript {
        if !isLoaded { try await loadModel() }
        guard let kit = whisperKit else {
            throw TranscriptionError.modelNotLoaded
        }

        let floatArray = Array(UnsafeBufferPointer(
            start: buffer.floatChannelData?[0],
            count: Int(buffer.frameLength)
        ))

        let results = try await kit.transcribe(audioArray: floatArray)

        let segments = results.flatMap { result in
            (result.segments ?? []).map { seg in
                Segment(
                    text: seg.text.trimmingCharacters(in: .whitespaces),
                    start: TimeInterval(seg.start),
                    end: TimeInterval(seg.end)
                )
            }
        }

        return Transcript(segments: segments)
    }
}

public enum TranscriptionError: Error, LocalizedError {
    case modelNotLoaded
    case transcriptionFailed(String)

    public var errorDescription: String? {
        switch self {
        case .modelNotLoaded: "Whisper model not loaded"
        case .transcriptionFailed(let msg): "Transcription failed: \(msg)"
        }
    }
}
```

**Step 4: Run test, verify pass. Step 5: Commit.**

```bash
git add -A && git commit -m "feat: WhisperKit transcription engine"
```

---

## Phase 5: macOS UI

Milestone: Working macOS app with floating window, waveform, recording, transcript display.

### Task 5.1: FloatingPanel (NSPanel)

**Files:**
- Create: `Earshot-macOS/App/FloatingPanel.swift`

**Step 1: Implement**

```swift
// FloatingPanel.swift
import AppKit
import SwiftUI

class FloatingPanel: NSPanel {
    init(contentRect: NSRect) {
        super.init(
            contentRect: contentRect,
            styleMask: [.titled, .closable, .resizable, .nonactivatingPanel, .utilityWindow],
            backing: .buffered,
            defer: false
        )

        // Always on top
        level = .floating
        isFloatingPanel = true

        // Keep visible on all spaces
        collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]

        // Allow key events even when app is not frontmost
        becomesKeyOnlyIfNeeded = false

        // Translucent background
        isOpaque = false
        backgroundColor = .clear

        // Standard window behavior
        isMovableByWindowBackground = true
        titlebarAppearsTransparent = true
        titleVisibility = .hidden

        // Minimum size
        minSize = NSSize(width: 340, height: 500)
    }

    // Allow the panel to become key to receive keyboard input
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
}
```

**Step 2: Build to verify. Step 3: Commit.**

---

### Task 5.2: WaveformView (SwiftUI)

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Views/WaveformView.swift`

**Step 1: Implement**

```swift
// WaveformView.swift
import SwiftUI

public struct WaveformView: View {
    @Binding var levels: [Float]
    var accentColor: Color = .blue
    var barCount: Int = 40

    public init(levels: Binding<[Float]>, accentColor: Color = .blue) {
        self._levels = levels
        self.accentColor = accentColor
    }

    public var body: some View {
        GeometryReader { geometry in
            HStack(spacing: 2) {
                ForEach(0..<barCount, id: \.self) { index in
                    let level = index < levels.count ? levels[index] : 0
                    RoundedRectangle(cornerRadius: 2)
                        .fill(
                            LinearGradient(
                                colors: [accentColor.opacity(0.6), accentColor],
                                startPoint: .bottom,
                                endPoint: .top
                            )
                        )
                        .frame(
                            width: max(2, (geometry.size.width - CGFloat(barCount) * 2) / CGFloat(barCount)),
                            height: max(4, geometry.size.height * CGFloat(level))
                        )
                        .frame(maxHeight: geometry.size.height, alignment: .bottom)
                }
            }
        }
        .frame(height: 80)
    }
}
```

**Step 2: Build to verify. Step 3: Commit.**

---

### Task 5.3: MainView (SwiftUI)

**Files:**
- Create: `Earshot-macOS/Views/MainView.swift`
- Create: `Earshot-macOS/ViewModels/RecordingViewModel.swift`

**Step 1: Implement ViewModel**

```swift
// RecordingViewModel.swift
import SwiftUI
import Combine
import EarshotKit

@MainActor
final class RecordingViewModel: ObservableObject {
    @Published var isRecording = false
    @Published var audioLevels: [Float] = Array(repeating: 0, count: 40)
    @Published var elapsedTime: TimeInterval = 0
    @Published var status: String = "Ready"
    @Published var transcript: Transcript?
    @Published var sessions: [RecordingSession] = []
    @Published var currentSessionIndex = 0

    let captureManager = ScreenCaptureManager()
    private var timer: Timer?
    private var recordingStart: Date?

    var formattedTime: String {
        let mins = Int(elapsedTime) / 60
        let secs = Int(elapsedTime) % 60
        return String(format: "%02d:%02d", mins, secs)
    }

    func toggleRecording() async {
        if isRecording {
            await stopRecording()
        } else {
            await startRecording()
        }
    }

    private func startRecording() async {
        do {
            try await captureManager.startCapture()
            isRecording = true
            status = "Recording"
            recordingStart = Date()
            startTimer()
        } catch {
            status = "Error: \(error.localizedDescription)"
        }
    }

    private func stopRecording() async {
        do {
            try await captureManager.stopCapture()
            isRecording = false
            status = "Transcribing..."
            stopTimer()
            // Transcription will be triggered by the pipeline
        } catch {
            status = "Error: \(error.localizedDescription)"
        }
    }

    private func startTimer() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            guard let self, let start = self.recordingStart else { return }
            Task { @MainActor in
                self.elapsedTime = Date().timeIntervalSince(start)
            }
        }
    }

    private func stopTimer() {
        timer?.invalidate()
        timer = nil
    }
}
```

**Step 2: Implement MainView**

```swift
// MainView.swift
import SwiftUI
import EarshotKit

struct MainView: View {
    @StateObject private var viewModel = RecordingViewModel()
    @State private var showSettings = false

    var body: some View {
        VStack(spacing: 16) {
            // Waveform
            WaveformView(levels: $viewModel.audioLevels, accentColor: .accentColor)
                .padding(.horizontal)

            // Timer
            Text(viewModel.formattedTime)
                .font(.system(size: 40, weight: .light, design: .monospaced))

            // Status
            Text(viewModel.status)
                .font(.caption)
                .foregroundStyle(.secondary)
                .textCase(.uppercase)

            // Record button
            Button {
                Task { await viewModel.toggleRecording() }
            } label: {
                Text(viewModel.isRecording ? "Stop" : "Record")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
            }
            .buttonStyle(.borderedProminent)
            .tint(viewModel.isRecording ? .red : .accentColor)
            .clipShape(Capsule())
            .padding(.horizontal, 40)

            Divider()

            // App audio source picker
            AppAudioPicker(captureManager: viewModel.captureManager)
                .padding(.horizontal)

            Divider()

            // Transcript
            if let transcript = viewModel.transcript {
                ScrollView {
                    Text(transcript.fullText)
                        .font(.body)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                }
            } else {
                Text("Transcript will appear here")
                    .foregroundStyle(.tertiary)
                    .frame(maxHeight: .infinity)
            }

            // Bottom toolbar
            HStack {
                Button("Settings") { showSettings = true }
                Spacer()
                // History navigation
                HStack(spacing: 4) {
                    Button("<") { viewModel.currentSessionIndex -= 1 }
                        .disabled(viewModel.currentSessionIndex <= 0)
                    Button(">") { viewModel.currentSessionIndex += 1 }
                        .disabled(viewModel.currentSessionIndex >= viewModel.sessions.count - 1)
                }
            }
            .padding(.horizontal)
            .padding(.bottom, 8)
        }
        .padding(.top, 20)
        .frame(minWidth: 340, minHeight: 500)
        .sheet(isPresented: $showSettings) {
            SettingsView()
        }
        .task {
            try? await viewModel.captureManager.refreshApps()
        }
    }
}
```

**Step 3: Build macOS target to verify. Step 4: Commit.**

---

### Task 5.4: EarshotApp with MenuBarExtra

**Files:**
- Create: `Earshot-macOS/App/EarshotApp.swift`

**Step 1: Implement**

```swift
// EarshotApp.swift
import SwiftUI

@main
struct EarshotApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        MenuBarExtra("Earshot", systemImage: "waveform") {
            Button("Show Window") {
                appDelegate.showPanel()
            }
            .keyboardShortcut("e", modifiers: [.command, .shift])
            Divider()
            Button("Quit Earshot") {
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q")
        }
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var panel: FloatingPanel?

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Hide dock icon - menu bar app only
        NSApp.setActivationPolicy(.accessory)
        showPanel()
    }

    func showPanel() {
        if panel == nil {
            let panel = FloatingPanel(contentRect: NSRect(x: 0, y: 0, width: 360, height: 600))
            let hostingView = NSHostingView(rootView: MainView())
            panel.contentView = hostingView
            self.panel = panel
        }
        panel?.center()
        panel?.makeKeyAndOrderFront(nil)
    }
}
```

**Step 2: Build and run macOS target. Verify:**
- Menu bar icon appears
- Floating window opens
- Window stays on top of other apps
- Settings sheet stays on top of floating window

**Step 3: Commit**

```bash
git add -A && git commit -m "feat: macOS app with floating panel and menu bar"
```

---

### Task 5.5: SettingsView

**Files:**
- Create: `Earshot-macOS/Views/SettingsView.swift`

**Step 1: Implement**

```swift
// SettingsView.swift
import SwiftUI
import EarshotKit

struct SettingsView: View {
    @AppStorage("modelSize") private var modelSize: String = WhisperModel.small.rawValue
    @AppStorage("alwaysOnTop") private var alwaysOnTop = true
    @AppStorage("outputDir") private var outputDir = "~/Documents/Earshot"
    @AppStorage("format_json") private var formatJSON = true
    @AppStorage("format_txt") private var formatTXT = true
    @AppStorage("format_srt") private var formatSRT = true

    @Environment(\.dismiss) var dismiss

    var body: some View {
        Form {
            Section("Audio & Transcription") {
                Picker("Whisper Model", selection: $modelSize) {
                    ForEach(WhisperModel.allCases, id: \.rawValue) { model in
                        Text(model.rawValue).tag(model.rawValue)
                    }
                }
            }

            Section("Output") {
                TextField("Save Location", text: $outputDir)
                Toggle("JSON", isOn: $formatJSON)
                Toggle("TXT", isOn: $formatTXT)
                Toggle("SRT", isOn: $formatSRT)
            }

            Section("Appearance") {
                Toggle("Always on Top", isOn: $alwaysOnTop)
            }
        }
        .formStyle(.grouped)
        .frame(width: 400, height: 350)
        .toolbar {
            ToolbarItem(placement: .confirmationAction) {
                Button("Done") { dismiss() }
            }
        }
    }
}
```

**Step 2: Build, verify settings sheet. Step 3: Commit.**

---

## Phase 6: CoreML Diarization

Milestone: Speaker identification works on transcribed segments.

### Task 6.1: CoreML Diarization Model Integration

**Files:**
- Create: `EarshotKit/Sources/EarshotKit/Diarization/SpeakerIdentifier.swift`
- Create: `EarshotKit/Sources/EarshotKit/Diarization/SpeakerEmbedding.swift`

> Note: Requires a pyannote-based CoreML model. This task covers the Swift wrapper.
> Model conversion (Python pyannote -> CoreML) is a separate prerequisite task.

**Step 1: Implement the wrapper**

```swift
// SpeakerIdentifier.swift
import CoreML
import AVFoundation

public actor SpeakerIdentifier {
    private var model: MLModel?
    private var knownSpeakers: [String: [Float]] = [:] // name -> embedding

    public init() {}

    public func loadModel() async throws {
        let config = MLModelConfiguration()
        config.computeUnits = .cpuAndNeuralEngine
        // Model will be bundled in the app or downloaded on first use
        guard let modelURL = Bundle.main.url(forResource: "SpeakerDiarization", withExtension: "mlmodelc") else {
            throw DiarizationError.modelNotFound
        }
        model = try MLModel(contentsOf: modelURL, configuration: config)
    }

    public func identify(segments: [Segment], audioBuffer: AVAudioPCMBuffer) async throws -> [Segment] {
        guard model != nil else { throw DiarizationError.modelNotLoaded }

        // Process each segment's audio to get speaker embedding
        // Compare embeddings to identify unique speakers
        // This is a simplified version - real implementation needs
        // audio slicing per segment and embedding comparison

        var labeled = segments
        // TODO: Implement actual embedding extraction and clustering
        // For now, return segments unchanged
        return labeled
    }
}

public enum DiarizationError: Error, LocalizedError {
    case modelNotFound
    case modelNotLoaded
    case processingFailed(String)

    public var errorDescription: String? {
        switch self {
        case .modelNotFound: "Diarization model not found"
        case .modelNotLoaded: "Diarization model not loaded"
        case .processingFailed(let msg): "Diarization failed: \(msg)"
        }
    }
}
```

**Step 2: Build to verify. Step 3: Commit.**

> The actual CoreML model conversion and embedding logic will need refinement
> once we have the model file. The interface is stable.

---

## Phase 7: iOS App

Milestone: iOS app records via Broadcast Extension, transcribes, shows transcript.

### Task 7.1: iOS Broadcast Extension

**Files:**
- Create: `Earshot-iOS/BroadcastExt/SampleHandler.swift`
- Create: `Earshot-iOS/BroadcastExt/Info.plist`

**Step 1: Create Broadcast Upload Extension target in Xcode**

Add new target: File > New > Target > Broadcast Upload Extension

**Step 2: Implement SampleHandler**

```swift
// SampleHandler.swift
import ReplayKit
import AVFoundation

class SampleHandler: RPBroadcastSampleHandler {
    private let appGroupID = "group.com.earshot.shared"
    private var audioFile: AVAudioFile?
    private var sampleCount: Int = 0

    override func broadcastStarted(withSetupInfo setupInfo: [String: NSObject]?) {
        // Create shared audio file in App Group container
        guard let containerURL = FileManager.default.containerURL(
            forSecurityApplicationGroupIdentifier: appGroupID
        ) else { return }

        let audioURL = containerURL.appendingPathComponent("broadcast_audio.wav")
        let format = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!

        do {
            audioFile = try AVAudioFile(forWriting: audioURL, settings: format.settings)
        } catch {
            finishBroadcastWithError(error)
        }
    }

    override func processSampleBuffer(_ sampleBuffer: CMSampleBuffer, with type: RPSampleBufferType) {
        switch type {
        case .audioApp, .audioMic:
            // Write audio samples to shared file
            guard let buffer = sampleBuffer.toAudioBuffer() else { return }
            try? audioFile?.write(from: buffer)
            sampleCount += Int(buffer.frameLength)

            // Signal main app that new audio is available
            let defaults = UserDefaults(suiteName: appGroupID)
            defaults?.set(sampleCount, forKey: "audioSampleCount")

        case .video:
            break // Ignore video

        @unknown default:
            break
        }
    }

    override func broadcastFinished() {
        audioFile = nil
        // Signal main app that broadcast ended
        let defaults = UserDefaults(suiteName: appGroupID)
        defaults?.set(true, forKey: "broadcastFinished")
    }
}
```

**Step 3: Configure App Group entitlement for both main app and extension.**

**Step 4: Build iOS target. Step 5: Commit.**

---

### Task 7.2: iOS RecordingView

**Files:**
- Create: `Earshot-iOS/Views/RecordingView.swift`
- Create: `Earshot-iOS/App/EarshotApp.swift`

**Step 1: Implement**

```swift
// RecordingView.swift (iOS)
import SwiftUI
import ReplayKit
import EarshotKit

struct RecordingView: View {
    @StateObject private var viewModel = iOSRecordingViewModel()

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                WaveformView(levels: $viewModel.audioLevels)
                    .padding()

                Text(viewModel.formattedTime)
                    .font(.system(size: 48, weight: .light, design: .monospaced))

                Text(viewModel.status)
                    .font(.caption)
                    .foregroundStyle(.secondary)

                // System broadcast picker
                BroadcastPickerRepresentable()
                    .frame(width: 60, height: 60)

                if let transcript = viewModel.transcript {
                    ScrollView {
                        Text(transcript.fullText)
                            .padding()
                    }
                }

                Spacer()
            }
            .navigationTitle("Earshot")
        }
    }
}

struct BroadcastPickerRepresentable: UIViewRepresentable {
    func makeUIView(context: Context) -> RPSystemBroadcastPickerView {
        let picker = RPSystemBroadcastPickerView()
        picker.preferredExtension = "com.earshot.BroadcastExt"
        picker.showsMicrophoneButton = true
        return picker
    }

    func updateUIView(_ uiView: RPSystemBroadcastPickerView, context: Context) {}
}
```

```swift
// EarshotApp.swift (iOS)
import SwiftUI

@main
struct EarshotApp: App {
    var body: some Scene {
        WindowGroup {
            TabView {
                RecordingView()
                    .tabItem { Label("Record", systemImage: "waveform") }
                HistoryView()
                    .tabItem { Label("History", systemImage: "clock") }
                SettingsView()
                    .tabItem { Label("Settings", systemImage: "gear") }
            }
        }
    }
}
```

**Step 2: Build iOS target. Step 3: Commit.**

---

## Phase 8: Integration & Polish

Milestone: End-to-end flow works on macOS. iOS compiles and basic flow works.

### Task 8.1: Wire Up Full Pipeline (macOS)

Connect ScreenCaptureManager -> AudioMixer -> TranscriptionEngine -> ExportManager in RecordingViewModel.

### Task 8.2: Keyboard Shortcuts

Add macOS keyboard shortcuts:
- Cmd+Shift+R: Toggle recording
- Cmd+Shift+E: Show/hide window
- Cmd+,: Open settings

### Task 8.3: History View

Implement session browsing for both platforms using SessionManager.

### Task 8.4: App Icon & Polish

- Add macOS/iOS app icons
- Add launch screen for iOS
- Test dark/light mode on both platforms
- Accessibility labels on all controls

### Task 8.5: Final Testing & Commit

```bash
cd EarshotKit && swift test
xcodebuild test -scheme Earshot-macOS -destination 'platform=macOS'
xcodebuild build -scheme Earshot-iOS -destination 'generic/platform=iOS'
git add -A && git commit -m "feat: Earshot Swift v1.0 - native macOS + iOS"
```

---

## Dependency Summary

```
Phase 1 (Models) <- no dependencies
Phase 2 (Export) <- Phase 1
Phase 3 (Audio)  <- Phase 1
Phase 4 (Whisper)<- Phase 1
Phase 5 (macOS UI) <- Phase 1, 2, 3, 4
Phase 6 (Diarization) <- Phase 1
Phase 7 (iOS) <- Phase 1, 2, 4
Phase 8 (Integration) <- All phases
```

Phases 2, 3, 4, 6 can run in parallel after Phase 1.
