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
