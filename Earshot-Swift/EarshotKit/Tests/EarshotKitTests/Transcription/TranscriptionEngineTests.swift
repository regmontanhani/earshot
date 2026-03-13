import XCTest
@testable import EarshotKit

final class TranscriptionEngineTests: XCTestCase {
    func testEngineInitialization() async throws {
        let engine = TranscriptionEngine(model: .tiny)
        let isLoaded = await engine.isLoaded
        XCTAssertFalse(isLoaded)
    }

    func testEngineModelSize() async {
        let engine = TranscriptionEngine(model: .largeV3)
        let size = await engine.modelSize
        XCTAssertEqual(size, .largeV3)
    }
}
