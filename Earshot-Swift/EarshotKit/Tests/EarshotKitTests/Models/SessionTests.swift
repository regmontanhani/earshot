import XCTest
@testable import EarshotKit

final class SessionTests: XCTestCase {
    func testSessionCreation() {
        let session = RecordingSession(
            name: "Meeting 2026-03-13",
            transcript: Transcript(segments: [
                Segment(text: "Hello", start: 0, end: 1)
            ])
        )
        XCTAssertEqual(session.name, "Meeting 2026-03-13")
        XCTAssertEqual(session.transcript.segments.count, 1)
        XCTAssertNotNil(session.createdAt)
        XCTAssertTrue(session.outputFiles.isEmpty)
    }

    func testSessionCodable() throws {
        let session = RecordingSession(
            name: "Test Session",
            transcript: Transcript(segments: [
                Segment(text: "Hi", start: 0, end: 1, speaker: "Alice")
            ]),
            outputFiles: ["test.json", "test.txt"]
        )
        let data = try JSONEncoder().encode(session)
        let decoded = try JSONDecoder().decode(RecordingSession.self, from: data)
        XCTAssertEqual(decoded.name, "Test Session")
        XCTAssertEqual(decoded.outputFiles.count, 2)
        XCTAssertEqual(decoded.transcript.segments[0].speaker, "Alice")
    }

    func testSessionManagerScanEmpty() throws {
        let tempDir = FileManager.default.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
        try FileManager.default.createDirectory(at: tempDir, withIntermediateDirectories: true)
        defer { try? FileManager.default.removeItem(at: tempDir) }

        let manager = SessionManager(directory: tempDir)
        let sessions = manager.scan()
        XCTAssertTrue(sessions.isEmpty)
    }
}
