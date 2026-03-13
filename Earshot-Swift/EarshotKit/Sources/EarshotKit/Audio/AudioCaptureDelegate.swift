import AVFoundation

public protocol AudioCaptureDelegate: AnyObject, Sendable {
    func didCaptureAudio(_ chunk: AudioChunk)
    func didUpdateLevel(_ level: Float)
    func didEncounterError(_ error: Error)
}
