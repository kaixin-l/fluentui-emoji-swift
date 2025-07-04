
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
    
    func testCategoryDistribution() {
        // Test that each category has at least one emoji
        for category in EmojiCategory.allCases {
            let emojisInCategory = FluentUIEmoji.emojis(in: category)
            XCTAssertFalse(emojisInCategory.isEmpty, "Category \(category.displayName) should not be empty")
        }
    }
}
