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
