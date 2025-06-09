#!/usr/bin/env python3
"""
Test module for utility functions.
"""

import pytest

from src.utils import (calculate_engagement_rate, calculate_text_stats,
                       clean_text, extract_domain_from_url, extract_hashtags,
                       extract_mentions, extract_urls, format_large_number,
                       format_time_duration, is_likely_spam,
                       normalize_username, safe_float_convert,
                       safe_int_convert)


class TestTimeUtils:
    """Test time-related utility functions."""

    def test_format_time_duration(self):
        """Test time duration formatting."""
        assert format_time_duration(0) == "0秒"
        assert format_time_duration(30) == "30秒"
        assert format_time_duration(60) == "1.0分"
        assert format_time_duration(90) == "1.5分"
        assert format_time_duration(3600) == "1.0時間"


class TestUrlUtils:
    """Test URL-related utility functions."""

    def test_extract_domain_from_url(self):
        """Test domain extraction from URLs."""
        assert extract_domain_from_url("https://example.com/path") == "example.com"
        assert (
            extract_domain_from_url("http://subdomain.example.com")
            == "subdomain.example.com"
        )
        assert (
            extract_domain_from_url("https://example.com:8080/path")
            == "example.com:8080"
        )
        assert extract_domain_from_url("invalid-url") == ""
        assert extract_domain_from_url("") == ""

    def test_extract_urls(self):
        """Test URL extraction from text."""
        text = "Check out https://example.com and http://test.org"
        urls = extract_urls(text)
        assert len(urls) == 2
        assert "https://example.com" in urls
        assert "http://test.org" in urls


class TestTextUtils:
    """Test text processing utility functions."""

    def test_clean_text(self):
        """Test text cleaning."""
        assert clean_text("  hello   world  ") == "hello world"
        assert clean_text("hello\n\tworld") == "hello world"
        assert clean_text("") == ""

    def test_normalize_username(self):
        """Test username normalization."""
        assert normalize_username("@username") == "username"
        assert normalize_username("USERNAME") == "username"
        assert normalize_username("@User_Name") == "user_name"
        assert normalize_username("") == ""

    def test_extract_hashtags(self):
        """Test hashtag extraction."""
        text = "This is a #test tweet with #multiple #hashtags"
        hashtags = extract_hashtags(text)
        assert "test" in hashtags
        assert "multiple" in hashtags
        assert "hashtags" in hashtags
        assert len(hashtags) == 3

    def test_extract_mentions(self):
        """Test mention extraction."""
        text = "Hello @user1 and @user2!"
        mentions = extract_mentions(text)
        assert "user1" in mentions
        assert "user2" in mentions
        assert len(mentions) == 2


class TestNumberUtils:
    """Test number utility functions."""

    def test_safe_int_convert(self):
        """Test safe integer conversion."""
        assert safe_int_convert("123") == 123
        assert safe_int_convert(123.5) == 123
        assert safe_int_convert("invalid") == 0
        assert safe_int_convert(None) == 0

    def test_safe_float_convert(self):
        """Test safe float conversion."""
        assert safe_float_convert("123.5") == 123.5
        assert safe_float_convert(123) == 123.0
        assert safe_float_convert("invalid") == 0.0
        assert safe_float_convert(None) == 0.0

    def test_format_large_number(self):
        """Test large number formatting."""
        assert format_large_number(1000) == "1.0K"
        assert format_large_number(1500) == "1.5K"
        assert format_large_number(1000000) == "1.0M"
        assert format_large_number(1200000000) == "1.2B"
        assert format_large_number(500) == "500"


class TestAnalysisUtils:
    """Test analysis utility functions."""

    def test_calculate_text_stats(self):
        """Test text statistics calculation."""
        text = "Hello world! This is a test."
        stats = calculate_text_stats(text)
        assert isinstance(stats, dict)
        assert "char_count" in stats
        assert "word_count" in stats
        assert stats["word_count"] == 6

    def test_calculate_engagement_rate(self):
        """Test engagement rate calculation."""
        metrics = {"likes": 100, "retweets": 50, "replies": 25}
        rate = calculate_engagement_rate(metrics, follower_count=1000)
        assert rate >= 0  # Should return valid rate

        # Test with no follower count
        rate = calculate_engagement_rate(metrics)
        assert rate >= 0

    def test_is_likely_spam(self):
        """Test spam detection."""
        spam_text = "FREE MONEY!!! CLICK HERE NOW!!!"
        result = is_likely_spam(spam_text)
        assert isinstance(result, dict)
        assert "is_spam" in result
        assert "confidence" in result

        normal_text = "Just had a great day at the park."
        result = is_likely_spam(normal_text)
        assert isinstance(result, dict)
