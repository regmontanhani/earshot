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
