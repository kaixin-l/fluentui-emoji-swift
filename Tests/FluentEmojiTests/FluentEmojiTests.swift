
// FluentEmojiTests.swift
// Generated automatically by generate_spm_package.py

import XCTest
@testable import FluentEmoji

final class FluentEmojiTests: XCTestCase {
    func testEmojiURLs() {
        for emoji in FluentEmoji.allCases {
            XCTAssertNotNil(emoji.url, "URL for \(emoji.rawValue) should not be nil")
        }
    }
}
