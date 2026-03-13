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
