import XCTest
@testable import EarshotKit

final class JSONExporterTests: XCTestCase {
    func testExportProducesValidJSON() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Hello world", start: 0.0, end: 2.5, speaker: "Alice"),
            Segment(text: "How are you", start: 3.0, end: 5.0, speaker: "Bob"),
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let url = try JSONExporter.export(transcript, to: tempDir, name: "test")
        XCTAssertEqual(url.pathExtension, "json")

        let data = try Data(contentsOf: url)
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        let decoded = try decoder.decode(Transcript.self, from: data)
        XCTAssertEqual(decoded.segments.count, 2)
        XCTAssertEqual(decoded.segments[0].speaker, "Alice")
    }

    func testExportCreatesFile() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Test", start: 0.0, end: 1.0)
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let url = try JSONExporter.export(transcript, to: tempDir, name: "meeting")
        XCTAssertTrue(FileManager.default.fileExists(atPath: url.path))
        XCTAssertTrue(url.lastPathComponent == "meeting.json")
    }
}
