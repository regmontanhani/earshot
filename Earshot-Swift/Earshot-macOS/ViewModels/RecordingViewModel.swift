#if os(macOS)
import SwiftUI
import Combine
import AVFoundation
import EarshotKit

@MainActor
final class RecordingViewModel: ObservableObject {
    @Published var isRecording = false
    @Published var audioLevels: [Float] = Array(repeating: 0, count: 40)
    @Published var elapsedTime: TimeInterval = 0
    @Published var status: String = "Loading model..."
    @Published var transcriptText: String = ""
    @Published var segments: [Segment] = []
    @Published var currentSessionIndex = 0
    @Published var showScreenRecordingAlert = false
    @Published var isTranscribing = false

    let captureManager = ScreenCaptureManager()
    private let engine = TranscriptionEngine(model: .base)
    private var timer: Timer?
    private var recordingStart: Date?
    private var lastTranscript: Transcript?

    var formattedTime: String {
        let mins = Int(elapsedTime) / 60
        let secs = Int(elapsedTime) % 60
        return String(format: "%02d:%02d", mins, secs)
    }

    init() {
        captureManager.onAudioLevel = { [weak self] level in
            let amplified = min(1.0, level * 15)
            Task { @MainActor in
                guard let self else { return }
                withAnimation(.linear(duration: 0.05)) {
                    self.audioLevels.append(amplified)
                    if self.audioLevels.count > 40 {
                        self.audioLevels.removeFirst(self.audioLevels.count - 40)
                    }
                }
            }
        }

        // Load whisper model in background
        Task {
            do {
                try await engine.loadModel()
                status = "Ready"
            } catch {
                status = "Model load failed: \(error.localizedDescription)"
                print("Model load error: \(error)")
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
        let hasAccess = await captureManager.ensureScreenRecordingAccess()
        guard hasAccess else {
            status = "Screen Recording permission needed"
            showScreenRecordingAlert = true
            return
        }

        transcriptText = ""
        segments = []
        lastTranscript = nil

        do {
            try await captureManager.startCapture()
            isRecording = true
            status = "Recording"
            recordingStart = Date()
            elapsedTime = 0
            startTimer()
        } catch {
            status = "Error: \(error.localizedDescription)"
            print("Start capture error: \(error)")
        }
    }

    private func stopRecording() async {
        do {
            try await captureManager.stopCapture()
            isRecording = false
            stopTimer()
            let duration = formattedTime

            // Get accumulated audio and transcribe
            let samples = captureManager.drainAudioSamples()
            guard !samples.isEmpty else {
                status = "No audio captured (\(duration))"
                return
            }

            let sampleCount = samples.count
            let audioDuration = Double(sampleCount) / 16000.0
            status = "Transcribing \(String(format: "%.0f", audioDuration))s of audio..."
            isTranscribing = true

            do {
                let transcript = try await engine.transcribe(audioSamples: samples)
                lastTranscript = transcript
                segments = transcript.segments
                transcriptText = transcript.fullText
                status = transcript.segments.isEmpty
                    ? "No speech detected (\(duration))"
                    : "Done - \(transcript.segments.count) segments"
            } catch {
                status = "Transcription error: \(error.localizedDescription)"
                print("Transcription error: \(error)")
            }

            isTranscribing = false
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
