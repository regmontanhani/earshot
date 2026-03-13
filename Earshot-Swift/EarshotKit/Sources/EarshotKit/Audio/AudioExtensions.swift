import AVFoundation
import CoreMedia

extension AVAudioPCMBuffer {
    public func rmsLevel() -> Float {
        guard let channelData = floatChannelData?[0], frameLength > 0 else { return 0 }
        var sum: Float = 0
        for i in 0..<Int(frameLength) {
            sum += channelData[i] * channelData[i]
        }
        return sqrt(sum / Float(frameLength))
    }
}

extension CMSampleBuffer {
    public func toAudioBuffer() -> AVAudioPCMBuffer? {
        guard let formatDesc = formatDescription,
              let asbd = CMAudioFormatDescriptionGetStreamBasicDescription(formatDesc)
        else { return nil }

        guard let avFormat = AVAudioFormat(streamDescription: asbd) else { return nil }
        guard let blockBuffer = CMSampleBufferGetDataBuffer(self) else { return nil }

        let frameCount = CMSampleBufferGetNumSamples(self)
        guard let pcmBuffer = AVAudioPCMBuffer(
            pcmFormat: avFormat,
            frameCapacity: AVAudioFrameCount(frameCount)
        ) else { return nil }

        pcmBuffer.frameLength = AVAudioFrameCount(frameCount)

        var lengthAtOffset: Int = 0
        var totalLength: Int = 0
        var dataPointer: UnsafeMutablePointer<CChar>?
        CMBlockBufferGetDataPointer(
            blockBuffer,
            atOffset: 0,
            lengthAtOffsetOut: &lengthAtOffset,
            totalLengthOut: &totalLength,
            dataPointerOut: &dataPointer
        )

        guard let source = dataPointer, let dest = pcmBuffer.floatChannelData?[0] else {
            return nil
        }
        memcpy(dest, source, totalLength)

        return pcmBuffer
    }
}
