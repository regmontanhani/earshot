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
        .package(url: "https://github.com/argmaxinc/WhisperKit.git", from: "0.9.0"),
    ],
    targets: [
        .target(
            name: "EarshotKit",
            dependencies: [
                .product(name: "WhisperKit", package: "WhisperKit"),
            ]
        ),
        .testTarget(
            name: "EarshotKitTests",
            dependencies: ["EarshotKit"]
        ),
    ]
)
