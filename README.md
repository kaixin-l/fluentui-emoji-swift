# Fluent UI Emoji Swift Package

![Fluent UI Emoji Banner](art/readme_banner.webp)

A Swift Package Manager (SPM) package for Microsoft's Fluent UI Emoji, providing type-safe access to 3D emoji assets with camelCase naming. This package is automatically generated from the [microsoft/fluentui-emoji](https://github.com/microsoft/fluentui-emoji) repository and updated daily via GitHub Actions to ensure the latest emoji assets are available.

## Features

- **Type-Safe Emoji Access**: Use the `FluentEmoji` enum with camelCase names (e.g., `grinningFace`) to access emoji assets.
- **3D PNG Assets**: Includes only high-quality 3D PNG emojis from the Fluent UI Emoji collection.
- **SPM Compatibility**: Seamlessly integrates with Swift projects on iOS 13+ and macOS 10.15+.
- **Non-SPM Support**: Fallback to `Bundle.main` for resource access in non-SPM contexts.
- **Automated Updates**: GitHub Actions workflow ensures the package stays up-to-date with the upstream repository.
- **Lightweight**: Optimized to include only 3D PNG assets, minimizing package size.

## Installation

To use the Fluent UI Emoji Swift Package in your project, add it as a dependency in your `Package.swift`. Replace `EmojiApp` and `AppTarget` with your project's name and target name, respectively:

```swift
// swift-tools-version:5.5
import PackageDescription

let package = Package(
    name: "EmojiApp", // Replace with your project name
    platforms: [
        .iOS(.v13)
    ],
    dependencies: [
        .package(url: "https://github.com/kaixin-l/fluentui-emoji-swift.git", from: "1.0.0")
    ],
    targets: [
        .target(
            name: "AppTarget", // Replace with your target name
            dependencies: ["FluentEmoji"]
        )
    ]
)
```

Then, run `swift package resolve` or update your project in Xcode to fetch the package.

### Using Xcode
1. Open your project in Xcode.
2. Navigate to `File > Add Packages`.
3. Enter `https://github.com/kaixin-l/fluentui-emoji-swift.git` and select version `1.0.0` or later.
4. Add the `FluentEmoji` library to your target.

## Usage

The package provides a `FluentEmoji` enum for type-safe access to emoji assets. Each enum case corresponds to an emoji, with a camelCase name (e.g., `grinningFace` for "Grinning Face") and a `url` property to access the 3D PNG asset.

### Example: Accessing a Specific Emoji

```swift
import FluentEmoji

if let url = FluentEmoji.grinningFace.url {
    print("Grinning Face URL: \(url)")
    // Load the image in an iOS app
    // let image = UIImage(contentsOfFile: url.path)
}
```

### Example: Iterating Over All Emojis

```swift
import FluentEmoji

for emoji in FluentEmoji.allCases {
    if let url = emoji.url {
        print("Emoji: \(emoji.rawValue), URL: \(url.absoluteString)")
    }
}
```

## Requirements

- Swift 5.5 or later
- iOS 13.0 or later
- macOS 10.15 or later

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit them (`git commit -m "Add your feature"`).
4. Push to your branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

Please ensure your changes align with the project's goal of providing a lightweight, type-safe SPM package for Fluent UI Emoji assets. For issues or feature requests, open an issue on the [GitHub repository](https://github.com/kaixin-l/fluentui-emoji-swift).

## License

This project is licensed under the MIT License, as per the original [microsoft/fluentui-emoji](https://github.com/microsoft/fluentui-emoji) repository. See the [LICENSE](LICENSE) file for details.

## Credits

- **Emoji Assets**: Sourced from [microsoft/fluentui-emoji](https://github.com/microsoft/fluentui-emoji).
- **Automation**: Generated and updated using a Python script (`generate_spm_package.py`) and GitHub Actions.
- **Maintainers**: [kaixin-l]

## Contact

For questions or support, please open an issue on the [GitHub repository](https://github.com/kaixin-l/fluentui-emoji-swift).