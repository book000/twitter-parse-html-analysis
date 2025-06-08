#!/usr/bin/env python3
"""
Security-focused tests for utility functions.
"""

import pytest
import json
import tempfile
import os
from src.utils import (
    safe_json_load,
    safe_json_loads,
    sanitize_html_content,
    safe_extract_hashtags,
    safe_extract_mentions,
    safe_extract_urls,
    is_safe_url,
    safe_file_path,
    sanitize_log_message,
)


class TestJSONSecurity:
    """Test JSON loading security measures."""

    def test_safe_json_load_size_limit(self):
        """Test file size limit enforcement."""
        # Create a temporary large file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            large_data = {"data": "x" * (10 * 1024 * 1024)}  # 10MB+ content
            json.dump(large_data, f)
            temp_path = f.name

        try:
            # Should raise ValueError for files larger than default limit
            with pytest.raises(ValueError, match="File too large"):
                safe_json_load(temp_path, max_size_mb=1)
        finally:
            os.unlink(temp_path)

    def test_safe_json_loads_length_limit(self):
        """Test JSON string length limit."""
        large_json = '{"data": "' + "x" * (2 * 1024 * 1024) + '"}'

        with pytest.raises(ValueError, match="JSON string too long"):
            safe_json_loads(large_json, max_length=1024 * 1024)

    def test_safe_json_structure_validation(self):
        """Test JSON structure validation."""
        with pytest.raises(ValueError, match="JSON must be object or array"):
            safe_json_loads('"simple string"')

        with pytest.raises(ValueError, match="JSON must be object or array"):
            safe_json_loads("123")


class TestHTMLSecurity:
    """Test HTML sanitization security measures."""

    def test_sanitize_dangerous_tags(self):
        """Test removal of dangerous HTML tags."""
        malicious_html = """
        <div>Safe content</div>
        <script>alert('xss')</script>
        <iframe src="evil.com"></iframe>
        <object data="malware.exe"></object>
        """

        sanitized = sanitize_html_content(malicious_html)

        assert "<script>" not in sanitized
        assert "<iframe>" not in sanitized
        assert "<object>" not in sanitized
        assert "<div>Safe content</div>" in sanitized

    def test_sanitize_dangerous_attributes(self):
        """Test removal of dangerous HTML attributes."""
        malicious_html = """
        <div onclick="alert('xss')" onload="malicious()">Content</div>
        <img src="image.jpg" onerror="steal_data()">
        """

        sanitized = sanitize_html_content(malicious_html)

        assert "onclick=" not in sanitized
        assert "onload=" not in sanitized
        assert "onerror=" not in sanitized

    def test_sanitize_javascript_urls(self):
        """Test neutralization of javascript: URLs."""
        malicious_html = "<a href=\"javascript:alert('xss')\">Click</a>"

        sanitized = sanitize_html_content(malicious_html)

        assert "javascript:" not in sanitized
        # Check that the URL was neutralized somehow (could be blocked: or removed)
        assert "alert(" not in sanitized or "blocked:" in sanitized


class TestReDoSProtection:
    """Test ReDoS (Regular Expression DoS) protection."""

    def test_safe_hashtag_extraction(self):
        """Test hashtag extraction with ReDoS protection."""
        # Normal case
        text = "Check out #python and #security"
        hashtags = safe_extract_hashtags(text)
        assert "python" in hashtags
        assert "security" in hashtags

        # Large input protection
        large_text = "#" + "a" * 10000 + " more text"
        hashtags = safe_extract_hashtags(large_text, max_text_length=100)
        assert len(hashtags) <= 50

    def test_safe_mention_extraction(self):
        """Test mention extraction with ReDoS protection."""
        # Normal case
        text = "Hello @user1 and @user2"
        mentions = safe_extract_mentions(text)
        assert "user1" in mentions
        assert "user2" in mentions

        # Large input protection
        large_text = "@" + "a" * 1000 + " more text"
        mentions = safe_extract_mentions(large_text, max_text_length=100)
        assert len(mentions) <= 50

    def test_safe_url_extraction(self):
        """Test URL extraction with ReDoS protection."""
        # Normal case
        text = "Visit https://example.com and http://test.org"
        urls = safe_extract_urls(text)
        assert len(urls) == 2

        # Malicious URL filtering
        malicious_text = 'Visit javascript:alert("xss") and https://safe.com'
        urls = safe_extract_urls(malicious_text)
        assert "https://safe.com" in urls
        assert all("javascript:" not in url for url in urls)


class TestPathSecurity:
    """Test path traversal protection."""

    def test_safe_file_path_traversal_protection(self):
        """Test protection against directory traversal."""
        base_dir = "/safe/directory"

        # Normal case should work
        safe_path = safe_file_path("file.txt", base_dir)
        assert safe_path.startswith(base_dir)

        # Traversal attempts should fail
        with pytest.raises(ValueError, match="Unsafe path detected"):
            safe_file_path("../../../etc/passwd", base_dir)

        with pytest.raises(ValueError, match="Unsafe path detected"):
            safe_file_path("/etc/passwd", base_dir)


class TestLogSecurity:
    """Test log injection protection."""

    def test_sanitize_log_message(self):
        """Test log message sanitization."""
        # Normal message should pass through
        clean_msg = "User logged in successfully"
        sanitized = sanitize_log_message(clean_msg)
        assert sanitized == clean_msg

        # Malicious message should be sanitized
        malicious_msg = "User\r\nFAKE LOG ENTRY: Admin logged in\nReal log continues"
        sanitized = sanitize_log_message(malicious_msg)
        assert "\r" not in sanitized
        assert "\n" not in sanitized

        # Length limit should be enforced
        long_msg = "x" * 2000
        sanitized = sanitize_log_message(long_msg, max_length=100)
        assert len(sanitized) <= 120  # 100 + truncation message


class TestURLSecurity:
    """Test URL safety validation."""

    def test_is_safe_url(self):
        """Test URL safety validation."""
        # Safe URLs
        assert is_safe_url("https://example.com") is True
        assert is_safe_url("http://subdomain.example.com/path") is True

        # Dangerous URLs
        assert is_safe_url("javascript:alert('xss')") is False
        assert is_safe_url("vbscript:malicious_code") is False
        assert is_safe_url("data:text/html,<script>alert('xss')</script>") is False
        assert is_safe_url("file:///etc/passwd") is False

        # URLs with embedded scripts
        assert is_safe_url("https://evil.com/<script>alert('xss')</script>") is False
        assert is_safe_url("https://evil.com?onload=steal()") is False
