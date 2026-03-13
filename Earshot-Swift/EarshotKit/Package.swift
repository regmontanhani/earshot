// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "EarshotKit",
    platforms: [
        .macOS(.v14),
        .iOS(.v17),
    ],
    products: [
        .library(
            name: "EarshotKit",
            targets: ["EarshotKit"]
        ),
    ],
    dependencies: [
        // WhisperKit will be added when building the transcription engine
        // .package(url: "https://github.com/argmaxinc/WhisperKit.git", from: "0.9.0"),
    ],
    targets: [
        .target(
            name: "EarshotKit",
            dependencies: []
        ),
        .testTarget(
            name: "EarshotKitTests",
            dependencies: ["EarshotKit"]
        ),
    ]
)
