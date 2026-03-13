#if os(macOS)
import SwiftUI
import Combine
import AVFoundation

@MainActor
final class RecordingViewModel: ObservableObject {
    @Published var isRecording = false
    @Published var audioLevels: [Float] = Array(repeating: 0, count: 40)
    @Published var elapsedTime: TimeInterval = 0
    @Published var status: String = "Ready"
    @Published var transcriptText: String = ""
    @Published var currentSessionIndex = 0

    let captureManager = ScreenCaptureManager()
    private var timer: Timer?
    private var recordingStart: Date?

    var formattedTime: String {
        let mins = Int(elapsedTime) / 60
        let secs = Int(elapsedTime) % 60
        return String(format: "%02d:%02d", mins, secs)
    }

    init() {
        captureManager.onAudioLevel = { [weak self] level in
            Task { @MainActor in
                guard let self else { return }
                self.audioLevels.append(level)
                if self.audioLevels.count > 40 {
                    self.audioLevels.removeFirst(self.audioLevels.count - 40)
                }
            }
        }
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
            elapsedTime = 0
            startTimer()
        } catch {
            status = "Error: \(error.localizedDescription)"
        }
    }

    private func stopRecording() async {
        do {
            try await captureManager.stopCapture()
            isRecording = false
            status = "Processing..."
            stopTimer()
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
#endif
