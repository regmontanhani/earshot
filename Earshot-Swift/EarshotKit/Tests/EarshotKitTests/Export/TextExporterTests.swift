import XCTest
@testable import EarshotKit

final class TextExporterTests: XCTestCase {
    func testExportPlainText() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Hello world", start: 0.0, end: 2.5),
            Segment(text: "How are you", start: 3.0, end: 5.0),
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let url = try TextExporter.export(transcript, to: tempDir, name: "test")
        let content = try String(contentsOf: url, encoding: .utf8)
        XCTAssertTrue(content.contains("Hello world"))
        XCTAssertTrue(content.contains("How are you"))
    }

    func testExportWithSpeakers() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Hi", start: 0.0, end: 1.0, speaker: "Alice"),
            Segment(text: "Hey", start: 1.0, end: 2.0, speaker: "Bob"),
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let url = try TextExporter.export(transcript, to: tempDir, name: "test")
        let content = try String(contentsOf: url, encoding: .utf8)
        XCTAssertTrue(content.contains("[Alice]"))
        XCTAssertTrue(content.contains("[Bob]"))
    }

    func testExportSameSpeakerGrouped() throws {
        let transcript = Transcript(segments: [
            Segment(text: "First line", start: 0.0, end: 1.0, speaker: "Alice"),
            Segment(text: "Second line", start: 1.0, end: 2.0, speaker: "Alice"),
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let url = try TextExporter.export(transcript, to: tempDir, name: "test")
        let content = try String(contentsOf: url, encoding: .utf8)
        // Should only have one [Alice] header, not two
        let aliceCount = content.components(separatedBy: "[Alice]").count - 1
        XCTAssertEqual(aliceCount, 1)
    }
}
