import XCTest
import AVFoundation
@testable import EarshotKit

final class AudioChunkTests: XCTestCase {
    func testAudioChunkCreation() {
        let format = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: 16000)!
        buffer.frameLength = 16000

        let chunk = AudioChunk(buffer: buffer, timestamp: 0.0)
        XCTAssertEqual(chunk.sampleRate, 16000)
        XCTAssertEqual(chunk.duration, 1.0, accuracy: 0.01)
    }

    func testAudioChunkTimestamp() {
        let format = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: 16000)!
        buffer.frameLength = 16000

        let chunk = AudioChunk(buffer: buffer, timestamp: 30.5)
        XCTAssertEqual(chunk.timestamp, 30.5)
    }

    func testRMSLevelSilence() {
        let format = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: 1600)!
        buffer.frameLength = 1600
        XCTAssertEqual(buffer.rmsLevel(), 0.0, accuracy: 0.001)
    }

    func testRMSLevelNonSilence() {
        let format = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1)!
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: 1600)!
        buffer.frameLength = 1600

        if let channelData = buffer.floatChannelData?[0] {
            for i in 0..<1600 {
                channelData[i] = 0.5
            }
        }
        XCTAssertGreaterThan(buffer.rmsLevel(), 0.0)
    }
}
