import XCTest
@testable import EarshotKit

final class EarshotKitTests: XCTestCase {
    func testVersionIsSet() {
        XCTAssertFalse(EarshotKit.version.isEmpty)
    }
}

