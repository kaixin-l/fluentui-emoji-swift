
// swift-tools-version:5.5
// Generated automatically by generate_spm_package.py

import PackageDescription

let package = Package(
    name: "FluentEmoji",
    platforms: [
        .iOS(.v13),
        .macOS(.v10_15)
    ],
    products: [
        .library(
            name: "FluentEmoji",
            targets: ["FluentEmoji"]
        ),
    ],
    targets: [
        .target(
            name: "FluentEmoji",
            path: "Sources/FluentEmoji",
            resources: [
                .process("Resources")
            ]
        ),
        .testTarget(
            name: "FluentEmojiTests",
            dependencies: ["FluentEmoji"]
        )
    ]
)
