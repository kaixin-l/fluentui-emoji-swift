# Fluent UI Emoji Swift Package

A Swift Package Manager (SPM) package for Microsoft's Fluent UI Emoji, providing type-safe access to 3D emoji assets with camelCase naming. This package is automatically generated from the [microsoft/fluentui-emoji](https://github.com/microsoft/fluentui-emoji) repository and updated daily via GitHub Actions to ensure the latest emoji assets are available.

![Fluent UI Emoji Banner](art/readme_banner.webp)

## Features

- **Type-Safe Emoji Access**: Use the `FluentUIEmoji` enum with camelCase names (e.g., `grinningFace`) to access emoji assets
- **3D PNG Assets**: Includes only high-quality 3D PNG emojis, stored as `<emoji_name>_3d.png` in `Sources/FluentUIEmoji/Resources/`
- **SPM Compatibility**: Seamlessly integrates with Swift projects on iOS 13+ and macOS 10.15+
- **Automated Updates**: GitHub Actions workflow ensures the package stays up-to-date with the upstream repository
- **Lightweight**: Optimized to include only 3D PNG assets, minimizing package size

## Local Development

To generate the SPM package locally from the source:

```bash
python3 generate_spm_package.py
mv fluentui-emoji-swift/* .
rmdir fluentui-emoji-swift
```

This will download the latest Fluent UI Emoji assets from Microsoft's repository and generate the Swift package structure.

## Installation

### Swift Package Manager

Add the following to your `Package.swift` file:

```swift
dependencies: [
    .package(url: "https://github.com/kaixin-l/fluentui-emoji-swift.git", from: "1.0.7")
]
```

### Xcode

1. Open your project in Xcode
2. Navigate to `File > Add Packages`
3. Enter `https://github.com/kaixin-l/fluentui-emoji-swift.git`
4. Select version `1.0.7` or later
5. Add the `FluentUIEmoji` library to your target

## Usage

The package provides a `FluentUIEmoji` enum for type-safe access to emoji assets. Each enum case corresponds to an emoji with a camelCase name and a `url` property to access the 3D PNG asset.

### Basic Usage

```swift
import FluentUIEmoji

if let url = FluentUIEmoji.grinningFace.url {
    print("Grinning Face URL: \(url)")
    // Load the image in an iOS app
    let image = UIImage(contentsOfFile: url.path)
}
```

### Iterating Over All Emojis

```swift
import FluentUIEmoji

for emoji in FluentUIEmoji.allCases {
    if let url = emoji.url {
        print("Emoji: \(emoji.rawValue), URL: \(url.absoluteString)")
    }
}
```

## Troubleshooting

If `emoji.url` returns `nil`:

1. **Check Resources**: Ensure `Sources/FluentUIEmoji/Resources/` contains the required PNG files
2. **Verify Git**: Run `git ls-files | grep Sources/FluentUIEmoji/Resources` to confirm resources are tracked
3. **Debug Output**: The `FluentUIEmoji.url` property logs resource lookup attempts to the console
4. **File Naming**: Ensure the raw value matches the filename pattern (e.g., `Soft ice cream` for `soft_ice_cream_3d.png`)

For additional help, open an issue on the [GitHub repository](https://github.com/kaixin-l/fluentui-emoji-swift).

## Requirements

- Swift 5.5 or later
- iOS 13.0 or later
- macOS 10.15 or later

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Commit your changes (`git commit -m "Add your feature"`)
5. Push to your branch (`git push origin feature/your-feature`)
6. Open a Pull Request

## License

This project is licensed under the MIT License, consistent with the original [microsoft/fluentui-emoji](https://github.com/microsoft/fluentui-emoji) repository. See the [LICENSE](LICENSE) file for details.

## Credits

- **Emoji Assets**: Sourced from [microsoft/fluentui-emoji](https://github.com/microsoft/fluentui-emoji)
- **Automation**: Generated using Python script and GitHub Actions

## Contact

For questions or support, please open an issue on the [GitHub repository](https://github.com/kaixin-l/fluentui-emoji-swift).