import Foundation

public final class SessionManager: Sendable {
    private let directory: URL

    public init(directory: URL) {
        self.directory = directory
    }

    public func scan() -> [RecordingSession] {
        guard let contents = try? FileManager.default.contentsOfDirectory(
            at: directory,
            includingPropertiesForKeys: [.contentModificationDateKey],
            options: [.skipsHiddenFiles]
        ) else { return [] }

        return contents
            .filter { $0.pathExtension == "json" }
            .compactMap { url -> RecordingSession? in
                guard let data = try? Data(contentsOf: url),
                      let session = try? JSONDecoder().decode(RecordingSession.self, from: data)
                else { return nil }
                return session
            }
            .sorted { $0.createdAt > $1.createdAt }
    }
}
