import Foundation

public enum WhisperModel: String, Codable, CaseIterable, Sendable {
    case tiny, base, small, medium
    case largeV3 = "large-v3"
    case turbo
}

public enum ExportFormat: String, Codable, CaseIterable, Sendable {
    case json, txt, srt
}

public enum AudioSource: String, Codable, Sendable {
    case systemAudio = "system"
    case specificApp = "app"
}

public struct EarshotSettings: Codable, Sendable {
    public var modelSize: WhisperModel
    public var outputFormats: Set<ExportFormat>
    public var outputDirectory: String
    public var alwaysOnTop: Bool
    public var audioSource: AudioSource
    public var selectedAppBundleID: String?
    public var silenceTimeout: TimeInterval
    public var chunkDuration: TimeInterval

    public init(
        modelSize: WhisperModel = .small,
        outputFormats: Set<ExportFormat> = [.json, .txt, .srt],
        outputDirectory: String = "~/Documents/Earshot",
        alwaysOnTop: Bool = true,
        audioSource: AudioSource = .systemAudio,
        selectedAppBundleID: String? = nil,
        silenceTimeout: TimeInterval = 60,
        chunkDuration: TimeInterval = 30
    ) {
        self.modelSize = modelSize
        self.outputFormats = outputFormats
        self.outputDirectory = outputDirectory
        self.alwaysOnTop = alwaysOnTop
        self.audioSource = audioSource
        self.selectedAppBundleID = selectedAppBundleID
        self.silenceTimeout = silenceTimeout
        self.chunkDuration = chunkDuration
    }
}
