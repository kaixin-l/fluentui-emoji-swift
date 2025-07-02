import os
import shutil
import urllib.request
import zipfile
import re
from pathlib import Path

# Configuration
UPSTREAM_REPO = "https://github.com/microsoft/fluentui-emoji/archive/refs/heads/main.zip"
OUTPUT_DIR = "fluentui-emoji-swift"
ASSETS_DIR = f"{OUTPUT_DIR}/Sources/FluentUIEmoji/Resources"
SOURCES_DIR = f"{OUTPUT_DIR}/Sources/FluentUIEmoji"
PACKAGE_SWIFT = f"{OUTPUT_DIR}/Package.swift"
SWIFT_FILE = f"{SOURCES_DIR}/FluentUIEmoji.swift"
TESTS_DIR = f"{OUTPUT_DIR}/Tests/FluentUIEmojiTests"


def to_camel_case(name):
    """Convert a string like 'Grinning Face' to 'grinningFace'."""
    words = re.sub(r'[^a-zA-Z0-9\s]', ' ', name).split()
    if not words:
        return name.lower()
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def download_and_extract_repo():
    """Download and extract the upstream fluentui-emoji repository."""
    print("Downloading fluentui-emoji repository...")
    urllib.request.urlretrieve(UPSTREAM_REPO, "fluentui-emoji.zip")
    with zipfile.ZipFile("fluentui-emoji.zip", "r") as zip_ref:
        zip_ref.extractall("temp")
    os.remove("fluentui-emoji.zip")
    return "temp/fluentui-emoji-main"


def create_package_structure():
    """Create the SPM package directory structure."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(SOURCES_DIR, exist_ok=True)
    os.makedirs(TESTS_DIR, exist_ok=True)


def copy_emoji_assets(repo_dir):
    """Copy 3D PNG assets to Resources/, keeping original filenames."""
    assets_path = f"{repo_dir}/assets"
    copied_files = 0
    for emoji_dir in Path(assets_path).iterdir():
        if emoji_dir.is_dir():
            for file in emoji_dir.glob("3D/*_3d.png"):
                dest_file = Path(ASSETS_DIR) / file.name
                shutil.copy(file, dest_file)
                print(f"Copied {file} to {dest_file}")
                copied_files += 1
    print(f"Total files copied: {copied_files}")


def generate_swift_file():
    """Generate a Swift enum with camelCase cases for each emoji."""
    emoji_cases = []
    for file in Path(ASSETS_DIR).glob("*_3d.png"):
        # Remove '_3d.png' to get rawValue (e.g., 'soft_ice_cream_3d.png' -> 'Soft ice cream')
        raw_name = file.stem.replace('_3d', '')
        # Convert to title case for rawValue (e.g., 'soft_ice_cream' -> 'Soft ice cream')
        raw_name = ' '.join(word.capitalize() for word in raw_name.split('_'))
        camel_name = to_camel_case(raw_name)
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', camel_name):
            emoji_cases.append((camel_name, raw_name))
        else:
            camel_name = f"_{camel_name}"
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', camel_name):
                emoji_cases.append((camel_name, raw_name))

    cases = "\n    ".join(
        f'case {name} = "{original}"' for name, original in emoji_cases)

    swift_content = r"""
// FluentUIEmoji.swift
// Generated automatically by generate_spm_package.py

import Foundation

public enum FluentUIEmoji: String, CaseIterable {
    %s

    /// Returns the URL for the emoji's 3D PNG asset.
    public var url: URL? {
        // Convert rawValue to lowercase with underscores (e.g., 'Soft ice cream' -> 'soft_ice_cream')
        let fileName = rawValue.lowercased().replacingOccurrences(of: " ", with: "_") + "_3d"
        if let url = Bundle.module.url(forResource: fileName, withExtension: "png") {
            print("Found SPM resource: \(fileName).png at \(url)")
            return url
        }
        print("SPM resource not found for: \(fileName).png")
        return nil
    }
}
""" % cases

    with open(SWIFT_FILE, "w") as f:
        f.write(swift_content)


def generate_package_swift():
    """Generate the Package.swift file for the SPM package."""
    package_content = """
// swift-tools-version:5.5
// Generated automatically by generate_spm_package.py

import PackageDescription

let package = Package(
    name: "FluentUIEmoji",
    platforms: [
        .iOS(.v13),
        .macOS(.v10_15)
    ],
    products: [
        .library(
            name: "FluentUIEmoji",
            targets: ["FluentUIEmoji"]
        ),
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
        )
    ]
)
"""
    with open(PACKAGE_SWIFT, "w") as f:
        f.write(package_content)


def generate_test_file():
    """Generate a basic test file for the SPM package."""
    test_content = r"""
// FluentUIEmojiTests.swift
// Generated automatically by generate_spm_package.py

import XCTest
@testable import FluentUIEmoji

final class FluentUIEmojiTests: XCTestCase {
    func testEmojiURLs() {
        for emoji in FluentUIEmoji.allCases {
            XCTAssertNotNil(emoji.url, "URL for \(emoji.rawValue) should not be nil")
        }
    }
}
"""
    with open(f"{TESTS_DIR}/FluentUIEmojiTests.swift", "w") as f:
        f.write(test_content)


def main():
    """Main function to generate the SPM package."""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    if os.path.exists("temp"):
        shutil.rmtree("temp")

    repo_dir = download_and_extract_repo()
    create_package_structure()
    copy_emoji_assets(repo_dir)
    generate_swift_file()
    generate_package_swift()
    generate_test_file()

    shutil.rmtree("temp")
    print(f"SPM package generated at {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
