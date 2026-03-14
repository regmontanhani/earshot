// NOTE: This file belongs to the Earshot-macOS target.
// AudioExtensions (rmsLevel, toAudioBuffer) come from EarshotKit.

#if os(macOS)
import ScreenCaptureKit
import AVFoundation
import CoreMedia
import Combine
import EarshotKit

@MainActor
final class ScreenCaptureManager: NSObject, ObservableObject {
    @Published var availableApps: [SCRunningApplication] = []
    @Published var isCapturing = false
    @Published var captureAllAudio = true
    @Published var selectedApp: SCRunningApplication?

    @Published var isMicMonitoring = false

    private var stream: SCStream?
    private var audioEngine: AVAudioEngine?

    // Use nonisolated(unsafe) so the SCStreamOutput callback can access these
    nonisolated(unsafe) var onAudioLevel: ((Float) -> Void)?
    nonisolated(unsafe) var onAudioBuffer: ((AVAudioPCMBuffer) -> Void)?

    @Published var screenRecordingGranted = false

    /// Start mic monitoring on launch - NO screen recording APIs touched
    func startMicMonitoringOnly() async {
        let micGranted = await AVCaptureDevice.requestAccess(for: .audio)
        guard micGranted, !isMicMonitoring else { return }
        do {
            let engine = AVAudioEngine()
            let inputNode = engine.inputNode
            let format = inputNode.outputFormat(forBus: 0)

            inputNode.installTap(onBus: 0, bufferSize: 4096, format: format) { [weak self] buffer, _ in
                let level = buffer.rmsLevel()
                self?.onAudioLevel?(level)
            }

            engine.prepare()
            try engine.start()
            self.audioEngine = engine
            isMicMonitoring = true
        } catch {
            print("Mic monitoring failed: \(error)")
        }
    }

    /// Check screen recording access without triggering any system prompts.
    func ensureScreenRecordingAccess() async -> Bool {
        // CGPreflightScreenCaptureAccess does NOT trigger a prompt
        guard CGPreflightScreenCaptureAccess() else {
            screenRecordingGranted = false
            return false
        }
        // Only touch ScreenCaptureKit AFTER we know permission is granted
        screenRecordingGranted = true
        if availableApps.isEmpty {
            try? await refreshApps()
        }
        return true
    }

    func stopMicMonitoring() {
        guard isMicMonitoring, !isCapturing else { return }
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        audioEngine = nil
        isMicMonitoring = false
    }

    func refreshApps() async throws {
        let content = try await SCShareableContent.excludingDesktopWindows(
            false, onScreenWindowsOnly: false
        )
        availableApps = content.applications
            .filter { $0.bundleIdentifier != Bundle.main.bundleIdentifier }
            .sorted { $0.applicationName < $1.applicationName }
    }

    func startCapture() async throws {
        let content = try await SCShareableContent.excludingDesktopWindows(
            false, onScreenWindowsOnly: false
        )

        guard let display = content.displays.first else {
            throw CaptureError.noDisplayFound
        }

        let filter: SCContentFilter
        if captureAllAudio {
            let excluded = content.applications.filter {
                $0.bundleIdentifier == Bundle.main.bundleIdentifier
            }
            filter = SCContentFilter(
                display: display,
                excludingApplications: excluded,
                exceptingWindows: []
            )
        } else if let app = selectedApp {
            filter = SCContentFilter(
                display: display,
                including: [app],
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
        // We only want audio, but SCStream requires valid video dimensions
        config.width = 2
        config.height = 2
        config.minimumFrameInterval = CMTime(value: 1, timescale: 1) // 1 fps minimum
        config.showsCursor = false

        let stream = SCStream(filter: filter, configuration: config, delegate: self)
        try stream.addStreamOutput(self, type: .audio, sampleHandlerQueue: .global(qos: .userInteractive))
        try stream.addStreamOutput(self, type: .screen, sampleHandlerQueue: .global(qos: .background))
        try await stream.startCapture()
        self.stream = stream
        isCapturing = true

        // Upgrade mic tap to also send buffers for transcription
        if isMicMonitoring {
            audioEngine?.inputNode.removeTap(onBus: 0)
            if let engine = audioEngine {
                let format = engine.inputNode.outputFormat(forBus: 0)
                engine.inputNode.installTap(onBus: 0, bufferSize: 4096, format: format) { [weak self] buffer, _ in
                    self?.onAudioBuffer?(buffer)
                    let level = buffer.rmsLevel()
                    self?.onAudioLevel?(level)
                }
            }
        } else {
            try await startMicrophoneCapture()
        }
    }

    func stopCapture() async throws {
        try await stream?.stopCapture()
        stream = nil
        isCapturing = false

        // Downgrade mic tap back to level-only monitoring
        if let engine = audioEngine {
            engine.inputNode.removeTap(onBus: 0)
            let format = engine.inputNode.outputFormat(forBus: 0)
            engine.inputNode.installTap(onBus: 0, bufferSize: 4096, format: format) { [weak self] buffer, _ in
                let level = buffer.rmsLevel()
                self?.onAudioLevel?(level)
            }
        }
    }

    private func startMicrophoneCapture() async throws {
        let granted = await AVCaptureDevice.requestAccess(for: .audio)
        guard granted else {
            throw CaptureError.microphoneAccessDenied
        }

        let engine = AVAudioEngine()
        let inputNode = engine.inputNode
        let format = inputNode.outputFormat(forBus: 0)

        inputNode.installTap(onBus: 0, bufferSize: 4096, format: format) { [weak self] buffer, _ in
            self?.onAudioBuffer?(buffer)
            let level = buffer.rmsLevel()
            self?.onAudioLevel?(level)
        }

        engine.prepare()
        try engine.start()
        self.audioEngine = engine
    }
}

extension ScreenCaptureManager: SCStreamOutput {
    nonisolated func stream(_ stream: SCStream, didOutputSampleBuffer sampleBuffer: CMSampleBuffer, of type: SCStreamOutputType) {
        // Discard video frames - we only want audio
        guard type == .audio else { return }
        guard let buffer = sampleBuffer.toAudioBuffer() else { return }
        onAudioBuffer?(buffer)
        let level = buffer.rmsLevel()
        onAudioLevel?(level)
    }
}

extension ScreenCaptureManager: SCStreamDelegate {
    nonisolated func stream(_ stream: SCStream, didStopWithError error: any Error) {
        print("SCStream stopped with error: \(error)")
    }
}

enum CaptureError: LocalizedError {
    case noAppSelected
    case noDisplayFound
    case microphoneAccessDenied

    var errorDescription: String? {
        switch self {
        case .noAppSelected: "No app selected for audio capture"
        case .noDisplayFound: "No display found"
        case .microphoneAccessDenied: "Microphone access denied - check System Settings > Privacy"
        }
    }
}
#endif
