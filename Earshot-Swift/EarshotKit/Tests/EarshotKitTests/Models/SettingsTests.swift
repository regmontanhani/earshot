import XCTest
@testable import EarshotKit

final class SettingsTests: XCTestCase {
    func testDefaultSettings() {
        let settings = EarshotSettings()
        XCTAssertEqual(settings.modelSize, .small)
        XCTAssertTrue(settings.outputFormats.contains(.json))
        XCTAssertTrue(settings.outputFormats.contains(.txt))
        XCTAssertTrue(settings.outputFormats.contains(.srt))
        XCTAssertTrue(settings.alwaysOnTop)
        XCTAssertEqual(settings.audioSource, .systemAudio)
        XCTAssertNil(settings.selectedAppBundleID)
        XCTAssertEqual(settings.chunkDuration, 30)
        XCTAssertEqual(settings.silenceTimeout, 60)
    }

    func testSettingsCodable() throws {
        var settings = EarshotSettings()
        settings.modelSize = .largeV3
        settings.alwaysOnTop = false
        settings.audioSource = .specificApp
        settings.selectedAppBundleID = "us.zoom.xos"

        let data = try JSONEncoder().encode(settings)
        let decoded = try JSONDecoder().decode(EarshotSettings.self, from: data)
        XCTAssertEqual(decoded.modelSize, .largeV3)
        XCTAssertFalse(decoded.alwaysOnTop)
        XCTAssertEqual(decoded.audioSource, .specificApp)
        XCTAssertEqual(decoded.selectedAppBundleID, "us.zoom.xos")
    }

    func testWhisperModelRawValues() {
        XCTAssertEqual(WhisperModel.tiny.rawValue, "tiny")
        XCTAssertEqual(WhisperModel.largeV3.rawValue, "large-v3")
        XCTAssertEqual(WhisperModel.turbo.rawValue, "turbo")
    }

    func testExportFormatAllCases() {
        XCTAssertEqual(ExportFormat.allCases.count, 3)
        XCTAssertTrue(ExportFormat.allCases.contains(.json))
        XCTAssertTrue(ExportFormat.allCases.contains(.txt))
        XCTAssertTrue(ExportFormat.allCases.contains(.srt))
    }
}
