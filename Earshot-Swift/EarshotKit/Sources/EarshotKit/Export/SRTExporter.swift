import Foundation

public enum SRTExporter {
    public static func export(_ transcript: Transcript, to directory: URL, name: String) throws -> URL {
        var srt = ""
        for (index, segment) in transcript.segments.enumerated() {
            let start = formatTimestamp(segment.start)
            let end = formatTimestamp(segment.end)
            srt += "\(index + 1)\n\(start) --> \(end)\n\(segment.text)\n\n"
        }

        let url = directory.appendingPathComponent("\(name).srt")
        try srt.write(to: url, atomically: true, encoding: .utf8)
        return url
    }

    public static func formatTimestamp(_ seconds: TimeInterval) -> String {
        let hours = Int(seconds) / 3600
        let minutes = (Int(seconds) % 3600) / 60
        let secs = Int(seconds) % 60
        let millis = Int((seconds.truncatingRemainder(dividingBy: 1)) * 1000)
        return String(format: "%02d:%02d:%02d,%03d", hours, minutes, secs, millis)
    }
}
