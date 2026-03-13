import XCTest
@testable import EarshotKit

final class TranscriptTests: XCTestCase {
    func testSegmentCreation() {
        let segment = Segment(text: "Hello world", start: 0.0, end: 2.5)
        XCTAssertEqual(segment.text, "Hello world")
        XCTAssertEqual(segment.start, 0.0)
        XCTAssertEqual(segment.end, 2.5)
        XCTAssertNil(segment.speaker)
    }

    func testSegmentWithSpeaker() {
        let segment = Segment(text: "Hi", start: 1.0, end: 1.5, speaker: "Alice")
        XCTAssertEqual(segment.speaker, "Alice")
    }

    func testSegmentDuration() {
        let segment = Segment(text: "Test", start: 1.5, end: 4.0)
        XCTAssertEqual(segment.duration, 2.5)
    }

    func testTranscriptFullText() {
        let segments = [
            Segment(text: "Hello", start: 0.0, end: 1.0),
            Segment(text: "World", start: 1.0, end: 2.0),
        ]
        let transcript = Transcript(segments: segments)
        XCTAssertEqual(transcript.fullText, "Hello World")
    }

    func testTranscriptDuration() {
        let segments = [
            Segment(text: "A", start: 0.0, end: 1.0),
            Segment(text: "B", start: 5.0, end: 8.5),
        ]
        let transcript = Transcript(segments: segments)
        XCTAssertEqual(transcript.duration, 8.5)
    }

    func testTranscriptCodable() throws {
        let transcript = Transcript(segments: [
            Segment(text: "Test", start: 0.0, end: 1.0, speaker: "Bob")
        ])
        let data = try JSONEncoder().encode(transcript)
        let decoded = try JSONDecoder().decode(Transcript.self, from: data)
        XCTAssertEqual(decoded.segments.count, 1)
        XCTAssertEqual(decoded.segments[0].speaker, "Bob")
    }

    func testEmptyTranscript() {
        let transcript = Transcript(segments: [])
        XCTAssertEqual(transcript.fullText, "")
        XCTAssertEqual(transcript.duration, 0)
    }
}
