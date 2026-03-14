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
        whisperKit = try await WhisperKit(
            model: "openai_whisper-\(modelSize.rawValue)",
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
        return buildTranscript(from: results)
    }

    public func transcribe(audioSamples: [Float]) async throws -> Transcript {
        if !isLoaded { try await loadModel() }
        guard let kit = whisperKit else {
            throw TranscriptionError.modelNotLoaded
        }

        let results = try await kit.transcribe(audioArray: audioSamples)
        return buildTranscript(from: results)
    }

    private func buildTranscript(from results: [TranscriptionResult]) -> Transcript {
        let segments = results.flatMap { result in
            (result.segments ?? []).compactMap { seg -> Segment? in
                let cleaned = cleanText(seg.text)
                guard !cleaned.isEmpty else { return nil }
                return Segment(
                    text: cleaned,
                    start: TimeInterval(seg.start),
                    end: TimeInterval(seg.end)
                )
            }
        }
        return Transcript(segments: segments)
    }

    private func cleanText(_ text: String) -> String {
        var result = text
        // Strip WhisperKit tokens like <|en|>, <|0.00|>, <|startoftranscript|>, etc.
        result = result.replacingOccurrences(
            of: "<\\|[^|]*\\|>",
            with: "",
            options: .regularExpression
        )
        // Strip non-speech markers
        let markers = ["[BLANK_AUDIO]", "[MUSIC]", "[SILENCE]", "[NOISE]", "(music)", "(silence)"]
        for marker in markers {
            result = result.replacingOccurrences(of: marker, with: "", options: .caseInsensitive)
        }
        // Strip >> speaker markers from raw output
        result = result.replacingOccurrences(of: ">>", with: "")
        // Clean up whitespace
        result = result.trimmingCharacters(in: .whitespacesAndNewlines)
        result = result.replacingOccurrences(
            of: "\\s+", with: " ", options: .regularExpression
        )
        return result
    }
}

public enum TranscriptionError: LocalizedError {
    case modelNotLoaded
    case transcriptionFailed(String)

    public var errorDescription: String? {
        switch self {
        case .modelNotLoaded: "Whisper model not loaded"
        case .transcriptionFailed(let msg): "Transcription failed: \(msg)"
        }
    }
}
