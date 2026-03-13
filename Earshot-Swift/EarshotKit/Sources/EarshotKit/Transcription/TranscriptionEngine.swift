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
