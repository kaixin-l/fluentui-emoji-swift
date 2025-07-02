Fluent UI Emoji Swift Package
A Swift Package Manager (SPM) package for Microsoft's Fluent UI Emoji, providing type-safe access to 3D emoji assets with camelCase naming.
Installation
Add the package to your Package.swift:
dependencies: [
    .package(url: "https://github.com/your-username/fluentui-emoji-swift.git", from: "1.0.0")
]

Usage
import FluentEmoji

// Access a specific emoji
if let url = FluentEmoji.grinningFace.url {
    // Use the URL (e.g., load into UIImage)
    print("Grinning Face URL: \(url)")
}

// Iterate over all emojis
for emoji in FluentEmoji.allCases {
    print("Emoji: \(emoji.rawValue), URL: \(emoji.url?.absoluteString ?? "Not found")")
}

License
This project is licensed under the MIT License, as per the original microsoft/fluentui-emoji repository.
Credits

Emoji assets are sourced from microsoft/fluentui-emoji.
This package is automatically generated and updated using GitHub Actions.
