import XCTest
@testable import EarshotKit

final class SRTExporterTests: XCTestCase {
    func testSRTFormat() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Hello world", start: 0.0, end: 2.5),
            Segment(text: "How are you", start: 3.0, end: 5.123),
        ])

        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let url = try SRTExporter.export(transcript, to: tempDir, name: "test")
        let content = try String(contentsOf: url, encoding: .utf8)

        XCTAssertTrue(content.contains("1\n00:00:00,000 --> 00:00:02,500\nHello world"))
        XCTAssertTrue(content.contains("2\n00:00:03,000 --> 00:00:05,123\nHow are you"))
    }

    func testSRTTimestampFormat() {
        XCTAssertEqual(SRTExporter.formatTimestamp(0.0), "00:00:00,000")
        XCTAssertEqual(SRTExporter.formatTimestamp(3723.456), "01:02:03,456")
        XCTAssertEqual(SRTExporter.formatTimestamp(59.999), "00:00:59,999")
    }
}
