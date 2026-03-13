import AVFoundation

public struct AudioChunk: Sendable {
    public let buffer: AVAudioPCMBuffer
    public let timestamp: TimeInterval

    public init(buffer: AVAudioPCMBuffer, timestamp: TimeInterval) {
        self.buffer = buffer
        self.timestamp = timestamp
    }

    public var sampleRate: Double { buffer.format.sampleRate }
    public var duration: TimeInterval {
        Double(buffer.frameLength) / sampleRate
    }
}
