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

    private var stream: SCStream?
    private var audioEngine: AVAudioEngine?

    // Use nonisolated(unsafe) so the SCStreamOutput callback can access these
    nonisolated(unsafe) var onAudioLevel: ((Float) -> Void)?
    nonisolated(unsafe) var onAudioBuffer: ((AVAudioPCMBuffer) -> Void)?

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
        config.width = 1
        config.height = 1

        let stream = SCStream(filter: filter, configuration: config, delegate: nil)
        try stream.addStreamOutput(self, type: .audio, sampleHandlerQueue: .global(qos: .userInteractive))
        try await stream.startCapture()
        self.stream = stream
        isCapturing = true

        try startMicrophoneCapture()
    }

    func stopCapture() async throws {
        try await stream?.stopCapture()
        stream = nil
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        audioEngine = nil
        isCapturing = false
    }

    private func startMicrophoneCapture() throws {
        let engine = AVAudioEngine()
        let inputNode = engine.inputNode
        let format = inputNode.outputFormat(forBus: 0)

        inputNode.installTap(onBus: 0, bufferSize: 4096, format: format) { [weak self] buffer, _ in
            self?.onAudioBuffer?(buffer)
        }

        engine.prepare()
        try engine.start()
        self.audioEngine = engine
    }
}

extension ScreenCaptureManager: SCStreamOutput {
    nonisolated func stream(_ stream: SCStream, didOutputSampleBuffer sampleBuffer: CMSampleBuffer, of type: SCStreamOutputType) {
        guard type == .audio else { return }
        guard let buffer = sampleBuffer.toAudioBuffer() else { return }
        onAudioBuffer?(buffer)
        let level = buffer.rmsLevel()
        onAudioLevel?(level)
    }
}

enum CaptureError: LocalizedError {
    case noAppSelected
    case noDisplayFound

    var errorDescription: String? {
        switch self {
        case .noAppSelected: "No app selected for audio capture"
        case .noDisplayFound: "No display found"
        }
    }
}
#endif
