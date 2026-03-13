import Foundation

public enum JSONExporter {
    public static func export(_ transcript: Transcript, to directory: URL, name: String) throws -> URL {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        let data = try encoder.encode(transcript)
        let url = directory.appendingPathComponent("\(name).json")
        try data.write(to: url)
        return url
    }
}
