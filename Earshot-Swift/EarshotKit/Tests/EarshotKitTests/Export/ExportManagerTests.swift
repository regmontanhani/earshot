import XCTest
@testable import EarshotKit

final class ExportManagerTests: XCTestCase {
    func testExportAllFormats() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Test", start: 0.0, end: 1.0)
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let urls = try ExportManager.export(
            transcript,
            to: tempDir,
            name: "meeting",
            formats: [.json, .txt, .srt]
        )
        XCTAssertEqual(urls.count, 3)
        XCTAssertTrue(urls.contains { $0.pathExtension == "json" })
        XCTAssertTrue(urls.contains { $0.pathExtension == "txt" })
        XCTAssertTrue(urls.contains { $0.pathExtension == "srt" })
    }

    func testExportSubsetOfFormats() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Test", start: 0.0, end: 1.0)
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let urls = try ExportManager.export(
            transcript,
            to: tempDir,
            name: "partial",
            formats: [.txt]
        )
        XCTAssertEqual(urls.count, 1)
        XCTAssertEqual(urls[0].pathExtension, "txt")
    }

    func testExportCreatesDirectory() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Test", start: 0.0, end: 1.0)
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathComponent("nested")
        defer { try? FileManager.default.removeItem(at: tempDir) }

        // Directory doesn't exist yet - ExportManager should create it
        XCTAssertFalse(FileManager.default.fileExists(atPath: tempDir.path))
        let urls = try ExportManager.export(transcript, to: tempDir, name: "test", formats: [.json])
        XCTAssertEqual(urls.count, 1)
        XCTAssertTrue(FileManager.default.fileExists(atPath: tempDir.path))
    }
}
