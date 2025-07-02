
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
