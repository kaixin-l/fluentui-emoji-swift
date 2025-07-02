// swift-tools-version:5.5
// Generated automatically by generate_spm_package.py

import PackageDescription

let package = Package(
    name: "FluentUIEmoji",
    platforms: [
        .iOS(.v13),
        .macOS(.v10_15),
    ],
    products: [
        .library(
            name: "FluentUIEmoji",
            targets: ["FluentUIEmoji"]
        )
    ],
    targets: [
        .target(
            name: "FluentUIEmoji",
            path: "Sources/FluentUIEmoji",
            resources: [
                .process("Resources")
            ]
        ),
        .testTarget(
            name: "FluentUIEmojiTests",
            dependencies: ["FluentUIEmoji"]
        ),
    ]
)
