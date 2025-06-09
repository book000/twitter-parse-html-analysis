#!/usr/bin/env python3
"""
Tests for LanguageDetector
"""

import unittest

from src.language_detector import LanguageDetector


class TestLanguageDetector(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.detector = LanguageDetector()

    def test_japanese_detection(self):
        """Test Japanese language detection."""
        text = "これは日本語のテストです。ひらがなとカタカナと漢字が含まれています。"
        result = self.detector.detect_languages(text)

        self.assertEqual(result["primary"], "japanese")
        self.assertGreater(result["confidence"], 0.7)

        # Check script analysis
        script_analysis = result["script_analysis"]
        self.assertGreater(script_analysis["hiragana"], 0)
        self.assertGreater(script_analysis["katakana"], 0)
        self.assertGreater(script_analysis["kanji"], 0)

    def test_english_detection(self):
        """Test English language detection."""
        text = "This is an English test sentence with multiple words and punctuation."
        result = self.detector.detect_languages(text)

        self.assertEqual(result["primary"], "english")
        self.assertGreater(result["confidence"], 0.7)

        # Check script analysis
        script_analysis = result["script_analysis"]
        self.assertGreater(script_analysis["latin"], 0)
        self.assertEqual(script_analysis["hiragana"], 0)

    def test_mixed_language_detection(self):
        """Test mixed language detection."""
        text = "Hello world! こんにちは世界！ 안녕하세요 세계!"
        result = self.detector.detect_languages(text)

        # Should detect mixed content
        self.assertIn(result["primary"], ["mixed", "japanese", "english"])

        # Check that multiple scripts are detected
        script_analysis = result["script_analysis"]
        self.assertGreater(script_analysis["latin"], 0)
        self.assertGreater(script_analysis["hiragana"], 0)
        self.assertGreater(script_analysis["korean"], 0)

    def test_emoji_heavy_content(self):
        """Test emoji-heavy content detection."""
        text = "🎉🎊🌟✨🎈🎂🍰🎁🎀🎪"
        result = self.detector.detect_languages(text)

        # Should detect emoji content
        script_analysis = result["script_analysis"]
        self.assertGreater(script_analysis["emoji"], 0)
        self.assertGreater(script_analysis["emoji_ratio"], 0.5)

    def test_chinese_detection(self):
        """Test Chinese language detection (kanji without Japanese features)."""
        text = "这是中文测试文本。包含简体中文字符。"
        result = self.detector.detect_languages(text)

        # Should detect Chinese or kanji-heavy content
        self.assertIn(result["primary"], ["chinese", "japanese"])

        script_analysis = result["script_analysis"]
        self.assertGreater(script_analysis["kanji"], 0)
        self.assertEqual(script_analysis["hiragana"], 0)  # No hiragana
        self.assertEqual(script_analysis["katakana"], 0)  # No katakana

    def test_korean_detection(self):
        """Test Korean language detection."""
        text = "안녕하세요. 이것은 한국어 테스트 문장입니다."
        result = self.detector.detect_languages(text)

        self.assertEqual(result["primary"], "korean")

        script_analysis = result["script_analysis"]
        self.assertGreater(script_analysis["korean"], 0)
        self.assertGreater(script_analysis["korean_ratio"], 0.5)

    def test_arabic_detection(self):
        """Test Arabic language detection."""
        text = "هذا اختبار للغة العربية. يحتوي على نص باللغة العربية."
        result = self.detector.detect_languages(text)

        self.assertEqual(result["primary"], "arabic")

        script_analysis = result["script_analysis"]
        self.assertGreater(script_analysis["arabic"], 0)
        self.assertGreater(script_analysis["arabic_ratio"], 0.5)

    def test_empty_text(self):
        """Test empty text handling."""
        result = self.detector.detect_languages("")

        self.assertEqual(result["primary"], "unknown")
        self.assertEqual(result["confidence"], 0)

    def test_whitespace_only(self):
        """Test whitespace-only text."""
        result = self.detector.detect_languages("   \n\t  ")

        self.assertEqual(result["primary"], "unknown")
        self.assertEqual(result["confidence"], 0)

    def test_numbers_and_symbols(self):
        """Test text with numbers and symbols only."""
        text = "123456789 @#$%^&*() https://example.com"
        result = self.detector.detect_languages(text)

        # Should be detected as unknown or have low confidence
        # Note: URLs may trigger English detection due to Latin characters
        if result["primary"] not in ["unknown", "english"]:
            self.assertLess(result["confidence"], 0.5)

    def test_linguistic_features_japanese(self):
        """Test Japanese linguistic features detection."""
        text = "おはようございます。今日は良い天気ですね。"
        result = self.detector.detect_languages(text)

        linguistic_features = result["linguistic_features"]
        self.assertGreater(linguistic_features["japanese_particles"], 0)
        self.assertGreater(linguistic_features["japanese_copula"], 0)

    def test_linguistic_features_english(self):
        """Test English linguistic features detection."""
        text = "The quick brown fox jumps over the lazy dog in the park."
        result = self.detector.detect_languages(text)

        linguistic_features = result["linguistic_features"]
        self.assertGreater(linguistic_features["english_articles"], 0)
        self.assertGreater(linguistic_features["english_prepositions"], 0)

    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        # High confidence Japanese
        japanese_text = "これは明らかに日本語のテキストです。ひらがな、カタカナ、漢字が含まれています。"
        result = self.detector.detect_languages(japanese_text)
        japanese_confidence = result["confidence"]

        # Low confidence mixed text
        mixed_text = "Hello こんにちは 123 #hashtag"
        result = self.detector.detect_languages(mixed_text)
        mixed_confidence = result["confidence"]

        # Japanese should have higher confidence
        self.assertGreater(japanese_confidence, mixed_confidence)

    def test_script_ratios(self):
        """Test script ratio calculations."""
        text = "Hello こんにちは"  # 50% Latin, 50% Hiragana
        result = self.detector.detect_languages(text)

        script_analysis = result["script_analysis"]

        # Check that ratios add up correctly
        latin_ratio = script_analysis.get("latin_ratio", 0)
        hiragana_ratio = script_analysis.get("hiragana_ratio", 0)

        self.assertGreater(latin_ratio, 0)
        self.assertGreater(hiragana_ratio, 0)

        # Ratios should be reasonable (not exact due to spaces/punctuation)
        self.assertLess(abs(latin_ratio - hiragana_ratio), 0.3)


if __name__ == "__main__":
    unittest.main()
