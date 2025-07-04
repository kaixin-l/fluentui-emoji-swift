import os
import shutil
import urllib.request
import zipfile
import re
from pathlib import Path
from collections import defaultdict

# Configuration
UPSTREAM_REPO = "https://github.com/microsoft/fluentui-emoji/archive/refs/heads/main.zip"
OUTPUT_DIR = "fluentui-emoji-swift"
ASSETS_DIR = f"{OUTPUT_DIR}/Sources/FluentUIEmoji/Resources"
SOURCES_DIR = f"{OUTPUT_DIR}/Sources/FluentUIEmoji"
PACKAGE_SWIFT = f"{OUTPUT_DIR}/Package.swift"
SWIFT_FILE = f"{SOURCES_DIR}/FluentUIEmoji.swift"
TESTS_DIR = f"{OUTPUT_DIR}/Tests/FluentUIEmojiTests"

# Prepositions that should not be capitalized in display names
PREPOSITIONS = {'of', 'the', 'in', 'on', 'at', 'by',
                'for', 'with', 'to', 'from', 'and', 'or', 'but'}


def standardize_filename(filename):
    """Convert filename to standard format: lowercase letters, numbers, underscores only."""
    # Remove file extension
    name = filename.replace('.png', '').replace('_3d', '')
    # Convert to lowercase and replace non-alphanumeric characters with underscores
    name = re.sub(r'[^a-z0-9_]', '_', name.lower())
    # Remove multiple consecutive underscores
    name = re.sub(r'_+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    return name


def generate_display_name(standardized_name):
    """Generate display name from standardized filename."""
    words = standardized_name.split('_')
    display_words = []

    for i, word in enumerate(words):
        if i == 0:  # First word is always capitalized
            display_words.append(word.capitalize())
        elif word.lower() in PREPOSITIONS:  # Prepositions remain lowercase
            display_words.append(word.lower())
        else:
            display_words.append(word.capitalize())

    return ' '.join(display_words)


def to_camel_case(name):
    """Convert a string like 'Grinning Face' to 'grinningFace'."""
    words = re.sub(r'[^a-zA-Z0-9\s]', ' ', name).split()
    if not words:
        return name.lower()
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def categorize_emoji(name):
    """Categorize emoji based on simplified name patterns."""
    name_lower = name.lower()

    # Symbols (includes Faces & Emotions, Symbols & Flags)
    symbol_keywords = ['face', 'smile', 'grin', 'laugh', 'cry', 'tear', 'wink', 'kiss', 'angry', 'sad',
                       'happy', 'eyes', 'mouth', 'tongue', 'flag', 'heart', 'symbol', 'sign', 'arrow',
                       'cross', 'star', 'circle', 'square', 'triangle', 'diamond', 'button', 'mark']
    if any(keyword in name_lower for keyword in symbol_keywords):
        return 'symbols'

    # Animals & Nature
    animal_keywords = ['cat', 'dog', 'bird', 'fish', 'bear', 'pig', 'cow', 'horse', 'monkey', 'lion',
                       'tiger', 'elephant', 'mouse', 'rabbit', 'fox', 'wolf', 'frog', 'snake', 'dragon',
                       'turtle', 'whale', 'dolphin', 'shark', 'octopus', 'butterfly', 'bee', 'spider',
                       'ant', 'bug', 'tree', 'flower', 'plant', 'leaf', 'mushroom']
    if any(keyword in name_lower for keyword in animal_keywords):
        return 'animals'

    # Food & Drink
    food_keywords = ['food', 'drink', 'coffee', 'tea', 'wine', 'beer', 'cake', 'bread', 'pizza',
                     'burger', 'fruit', 'apple', 'banana', 'grape', 'strawberry', 'cherry', 'peach',
                     'lemon', 'watermelon', 'pineapple', 'coconut', 'avocado', 'tomato', 'carrot',
                     'corn', 'potato', 'cheese', 'meat', 'chicken', 'fish', 'egg', 'milk', 'honey',
                     'salt', 'pepper', 'ice', 'cream']
    if any(keyword in name_lower for keyword in food_keywords):
        return 'food'

    # Activities (includes Activities & Sports, Travel & Places)
    activity_keywords = ['sport', 'ball', 'game', 'play', 'run', 'swim', 'ski', 'bike', 'car', 'plane',
                         'train', 'boat', 'ship', 'rocket', 'music', 'guitar', 'piano', 'drum', 'dance',
                         'party', 'celebration', 'house', 'building', 'city', 'country', 'map', 'hotel',
                         'school', 'hospital', 'church', 'castle', 'bridge', 'tower', 'mountain', 'beach',
                         'desert', 'forest', 'island']
    if any(keyword in name_lower for keyword in activity_keywords):
        return 'activities'

    # Objects
    object_keywords = ['phone', 'computer', 'book', 'pen', 'key', 'lock', 'tool', 'hammer', 'knife',
                       'gun', 'bomb', 'money', 'coin', 'gem', 'ring', 'crown', 'hat', 'shirt', 'dress',
                       'shoe', 'bag', 'watch', 'glasses', 'umbrella', 'light', 'fire', 'water', 'earth',
                       'moon', 'sun', 'star', 'cloud', 'rainbow', 'lightning', 'snow', 'wind']
    if any(keyword in name_lower for keyword in object_keywords):
        return 'objects'

    # Default to objects
    return 'objects'


def generate_search_tags(name):
    """Generate simplified search tags from emoji name only."""
    name_lower = name.lower()
    words = re.sub(r'[^a-zA-Z0-9\s]', ' ', name_lower).split()
    # Only use words from the name, no synonyms
    return sorted(list(set(words)))


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
    """Copy 3D PNG assets to Resources/ and standardize filenames."""
    assets_path = f"{repo_dir}/assets"
    copied_files = 0
    filename_counts = defaultdict(int)

    # First pass: collect all files and their standardized names
    files_to_copy = []
    for emoji_dir in Path(assets_path).iterdir():
        if emoji_dir.is_dir():
            for file in emoji_dir.glob("3D/*_3d.png"):
                standardized_name = standardize_filename(file.name)
                files_to_copy.append((file, standardized_name))

    # Second pass: handle duplicates and copy files
    for file, standardized_name in files_to_copy:
        filename_counts[standardized_name] += 1

        # Handle duplicates by adding suffix
        if filename_counts[standardized_name] > 1:
            final_name = f"{standardized_name}_{filename_counts[standardized_name]:02d}_3d.png"
        else:
            final_name = f"{standardized_name}_3d.png"

        dest_file = Path(ASSETS_DIR) / final_name
        shutil.copy(file, dest_file)
        print(f"Copied {file} to {dest_file}")
        copied_files += 1

    print(f"Total files copied: {copied_files}")


def generate_swift_file():
    """Generate a Swift enum with camelCase cases for each emoji based on actual files."""
    emoji_cases = []
    emoji_data = []
    generated_emojis = set()

    # Process actual files in the assets directory
    for file in Path(ASSETS_DIR).glob("*_3d.png"):
        # Get the standardized name without _3d.png
        standardized_name = file.stem.replace('_3d', '')

        # Generate display name
        display_name = generate_display_name(standardized_name)

        # Generate camelCase name
        camel_name = to_camel_case(display_name)

        # Ensure valid Swift identifier
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', camel_name):
            camel_name = f"_{camel_name}"

        # Handle duplicate camelCase names
        original_camel_name = camel_name
        counter = 1
        while camel_name in generated_emojis:
            camel_name = f"{original_camel_name}_{counter:02d}"
            counter += 1

        emoji_cases.append((camel_name, standardized_name))
        emoji_data.append({
            'camel_name': camel_name,
            'display_name': display_name,
            'standardized_name': standardized_name,
            'category': categorize_emoji(display_name),
            'search_tags': generate_search_tags(display_name)
        })
        generated_emojis.add(camel_name)
        print(
            f"Generated emoji: {camel_name} -> {standardized_name}_3d.png (Display: {display_name})")

    # Log the number of generated cases for debugging
    print(f"Generated {len(emoji_cases)} emoji cases")

    cases = "\n    ".join(
        f'case {name} = "{identifier}"' for name, identifier in emoji_cases)

    # Generate search tag mappings with commas
    search_mappings = []
    for data in emoji_data:
        tags_str = ', '.join(f'"{tag}"' for tag in data['search_tags'])
        search_mappings.append(f'        .{data["camel_name"]}: [{tags_str}]')

    # Define popular emojis, only including those that exist in generated_emojis
    candidate_popular_emojis = [
        'grinningFace', 'smilingFaceWithHeartEyes', 'winkingFace', 'thumbsUp', 'redHeart'
    ]
    popular_emojis = [
        f'.{camel_name}' for camel_name in candidate_popular_emojis if camel_name in generated_emojis]
    if not popular_emojis:
        # Fallback to first few emojis if none of the candidates exist
        popular_emojis = [f'.{data["camel_name"]}' for data in emoji_data[:5]]
    popular_emojis_code = ', '.join(popular_emojis)
    print(f"Popular emojis included: {popular_emojis}")

    swift_content = f"""
// FluentUIEmoji.swift
// Generated automatically by generate_spm_package.py

import Foundation

public enum FluentUIEmoji: String, CaseIterable {{
    {cases}

    /// Returns the camelCase identifier for the emoji (same as case name).
    public var identifier: String {{
        return self.rawValue
    }}
    
    /// Returns the human-readable display name for the emoji.
    public var displayName: String {{
        // Convert standardized name to display name
        let words = self.rawValue.split(separator: "_").map(String.init)
        var displayWords: [String] = []
        
        for (index, word) in words.enumerated() {{
            if index == 0 {{
                displayWords.append(word.capitalized)
            }} else if ["of", "the", "in", "on", "at", "by", "for", "with", "to", "from", "and", "or", "but"].contains(word.lowercased()) {{
                displayWords.append(word.lowercased())
            }} else {{
                displayWords.append(word.capitalized)
            }}
        }}
        
        return displayWords.joined(separator: " ")
    }}

    /// Returns the URL for the emoji's 3D PNG asset.
    public var url: URL? {{
        // Use the standardized name directly
        let fileName = self.rawValue + "_3d"
        
        if let url = Bundle.module.url(forResource: fileName, withExtension: "png") {{
            return url
        }}
        return nil
    }}
    
    /// Returns the category of the emoji.
    public var category: EmojiCategory {{
        switch self {{
{_generate_category_switch_cases(emoji_data)}
        }}
    }}
    
    /// Returns search tags for the emoji.
    public var searchTags: [String] {{
        return Self.searchTagsMap[self] ?? []
    }}
    
    /// Map of emojis to their search tags.
    private static let searchTagsMap: [FluentUIEmoji: [String]] = [
{',\n'.join(search_mappings)}
    ]
    
    /// Returns emojis in the specified category.
    public static func emojis(in category: EmojiCategory) -> [FluentUIEmoji] {{
        return allCases.filter {{ $0.category == category }}
    }}
    
    /// Returns a list of popular emojis for quick access.
    public static let popular: [FluentUIEmoji] = [
        {popular_emojis_code}
    ].compactMap {{ emoji in
        // Only include if the emoji actually exists in our cases
        return allCases.contains(emoji) ? emoji : nil
    }}
    
    /// Search emojis by text query.
    public static func search(_ query: String) -> [FluentUIEmoji] {{
        let lowercaseQuery = query.lowercased().trimmingCharacters(in: .whitespacesAndNewlines)
        guard !lowercaseQuery.isEmpty else {{ return [] }}
        
        return allCases.filter {{ emoji in
            // Check display name
            if emoji.displayName.lowercased().contains(lowercaseQuery) {{
                return true
            }}
            
            // Check search tags
            return emoji.searchTags.contains {{ tag in
                tag.lowercased().contains(lowercaseQuery)
            }}
        }}
    }}
}}

/// Categories for organizing emojis.
public enum EmojiCategory: String, CaseIterable {{
    case symbols = "Symbols"
    case animals = "Animals & Nature"
    case food = "Food & Drink"
    case activities = "Activities"
    case objects = "Objects"
    
    /// Display name for the category.
    public var displayName: String {{
        return self.rawValue
    }}
    
    /// Icon emoji for the category.
    public var icon: String {{
        switch self {{
        case .symbols: return "😀"
        case .animals: return "🐶"
        case .food: return "🍎"
        case .activities: return "⚽"
        case .objects: return "📱"
        }}
    }}
}}
"""

    with open(SWIFT_FILE, "w") as f:
        f.write(swift_content)


def _generate_category_switch_cases(emoji_data):
    """Generate switch cases for category mapping."""
    category_groups = {}
    for data in emoji_data:
        category = data['category']
        if category not in category_groups:
            category_groups[category] = []
        category_groups[category].append(data['camel_name'])

    cases = []
    for category, emojis in category_groups.items():
        emoji_list = ', '.join(f'.{emoji}' for emoji in emojis)
        cases.append(
            f'        case {emoji_list}:\n            return .{category}')

    return '\n'.join(cases)


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
            XCTAssertNotNil(emoji.url, "URL for \(emoji.displayName) should not be nil")
        }
    }
    
    func testEmojiIdentifiers() {
        for emoji in FluentUIEmoji.allCases {
            XCTAssertFalse(emoji.identifier.isEmpty, "Identifier should not be empty")
            XCTAssertEqual(emoji.identifier, emoji.rawValue, "Identifier should match rawValue")
        }
    }
    
    func testEmojiDisplayNames() {
        for emoji in FluentUIEmoji.allCases {
            XCTAssertFalse(emoji.displayName.isEmpty, "Display name should not be empty")
        }
    }
    
    func testEmojiCategories() {
        for emoji in FluentUIEmoji.allCases {
            XCTAssertTrue(EmojiCategory.allCases.contains(emoji.category), "Category should be valid")
        }
    }
    
    func testSearchFunctionality() {
        let results = FluentUIEmoji.search("face")
        XCTAssertFalse(results.isEmpty, "Search for 'face' should return results")
        
        let emptyResults = FluentUIEmoji.search("")
        XCTAssertTrue(emptyResults.isEmpty, "Empty search should return no results")
    }
    
    func testPopularEmojis() {
        XCTAssertFalse(FluentUIEmoji.popular.isEmpty, "Popular emojis list should not be empty")
        for emoji in FluentUIEmoji.popular {
            XCTAssertTrue(FluentUIEmoji.allCases.contains(emoji), "Popular emoji should exist in allCases")
        }
    }
    
    func testCategoryFiltering() {
        for category in EmojiCategory.allCases {
            let emojis = FluentUIEmoji.emojis(in: category)
            for emoji in emojis {
                XCTAssertEqual(emoji.category, category, "Emoji should belong to correct category")
            }
        }
    }
    
    func testFilenameStandardization() {
        // Test that all emojis have valid URLs
        for emoji in FluentUIEmoji.allCases {
            XCTAssertNotNil(emoji.url, "Emoji \(emoji.rawValue) should have a valid URL")
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
