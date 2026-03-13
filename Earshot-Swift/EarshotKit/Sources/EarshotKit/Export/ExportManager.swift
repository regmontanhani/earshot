import Foundation

public enum ExportManager {
    public static func export(
        _ transcript: Transcript,
        to directory: URL,
        name: String,
        formats: Set<ExportFormat>
    ) throws -> [URL] {
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        var urls: [URL] = []
        for format in formats {
            let url: URL
            switch format {
            case .json: url = try JSONExporter.export(transcript, to: directory, name: name)
            case .txt:  url = try TextExporter.export(transcript, to: directory, name: name)
            case .srt:  url = try SRTExporter.export(transcript, to: directory, name: name)
            }
            urls.append(url)
        }
        return urls
    }
}
