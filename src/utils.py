#!/usr/bin/env python3
"""
Utility functions for Twitter data extraction and analysis.

This module provides common utility functions used throughout the
Twitter parsing and analysis system.
"""

import json
import re
from typing import Any, Union, Dict, Optional


def format_time_duration(seconds: float) -> str:
    """
    Convert seconds to human-readable time format.

    Args:
        seconds: Time duration in seconds

    Returns:
        Human-readable time string (e.g., "2.5分", "1.2時間")
    """
    if seconds < 60:
        return f"{seconds:.0f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}時間"


def safe_int_convert(value: Any) -> int:
    """
    Safely convert value to integer.

    Args:
        value: Value to convert

    Returns:
        Integer value or 0 if conversion fails
    """
    try:
        if value is None:
            return 0
        return int(value)
    except (ValueError, TypeError):
        return 0


def safe_float_convert(value: Any) -> float:
    """
    Safely convert value to float.

    Args:
        value: Value to convert

    Returns:
        Float value or 0.0 if conversion fails
    """
    try:
        if value is None:
            return 0.0
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def extract_domain_from_url(url: str) -> str:
    """
    Extract domain from URL.

    Args:
        url: Full URL string

    Returns:
        Domain part of the URL or empty string if extraction fails
    """
    try:
        match = re.search(r"https?://([^/]+)", url)
        return match.group(1) if match else ""
    except:
        return ""


def clean_text(text: str) -> str:
    """
    Clean and normalize text for analysis.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove extra whitespace
    cleaned = re.sub(r"\s+", " ", text.strip())

    # Remove control characters
    cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", cleaned)

    return cleaned


def extract_hashtags(text: str) -> list:
    """
    Extract hashtags from text with ReDoS protection.

    Args:
        text: Text to extract hashtags from

    Returns:
        List of hashtags (without # symbol)
    """
    if not text:
        return []

    # ReDoS-safe pattern with length limit and possessive quantifiers
    pattern = r"#([\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]{1,100}?)(?=\s|$|[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF])"
    matches = re.findall(pattern, text[:10000])  # Limit input length
    return matches[:50]  # Limit number of matches


def extract_mentions(text: str) -> list:
    """
    Extract mentions from text with ReDoS protection.

    Args:
        text: Text to extract mentions from

    Returns:
        List of mentioned usernames (without @ symbol)
    """
    if not text:
        return []

    # ReDoS-safe pattern with length limit
    pattern = r"@(\w{1,50}?)(?=\s|$|[^\w])"
    matches = re.findall(pattern, text[:10000])  # Limit input length
    return matches[:50]  # Limit number of matches


def extract_urls(text: str) -> list:
    """
    Extract URLs from text with ReDoS protection.

    Args:
        text: Text to extract URLs from

    Returns:
        List of URLs
    """
    if not text:
        return []

    # ReDoS-safe pattern with length limit
    pattern = r"https?://[^\s]{1,500}?"
    matches = re.findall(pattern, text[:10000])  # Limit input length
    return matches[:20]  # Limit number of matches


def calculate_text_stats(text: str) -> dict:
    """
    Calculate basic text statistics.

    Args:
        text: Text to analyze

    Returns:
        Dictionary containing text statistics
    """
    if not text:
        return {
            "char_count": 0,
            "word_count": 0,
            "sentence_count": 0,
            "line_count": 0,
            "avg_word_length": 0.0,
        }

    char_count = len(text)
    words = text.split()
    word_count = len(words)

    # Count sentences (rough estimation)
    sentence_endings = r"[.!?。！？]"
    sentence_count = len(re.findall(sentence_endings, text))
    if sentence_count == 0 and text.strip():
        sentence_count = 1

    line_count = len(text.splitlines())

    avg_word_length = (
        sum(len(word) for word in words) / word_count if word_count > 0 else 0.0
    )

    return {
        "char_count": char_count,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "line_count": line_count,
        "avg_word_length": avg_word_length,
    }


def is_likely_spam(text: str, engagement_metrics: dict = None) -> dict:
    """
    Simple spam detection based on text patterns and engagement.

    Args:
        text: Tweet text to analyze
        engagement_metrics: Dictionary with engagement data

    Returns:
        Dictionary with spam probability and reasons
    """
    if not text:
        return {"is_spam": False, "confidence": 0.0, "reasons": []}

    spam_indicators = []
    spam_score = 0.0

    # Check for excessive capitalization
    if len(text) > 10:
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
        if caps_ratio > 0.7:
            spam_indicators.append("excessive_caps")
            spam_score += 0.3

    # Check for excessive repetition
    words = text.lower().split()
    if len(words) > 3:
        unique_words = set(words)
        repetition_ratio = 1 - (len(unique_words) / len(words))
        if repetition_ratio > 0.5:
            spam_indicators.append("excessive_repetition")
            spam_score += 0.4

    # Check for excessive punctuation
    punct_ratio = sum(1 for c in text if c in "!?.,;:") / len(text) if text else 0
    if punct_ratio > 0.3:
        spam_indicators.append("excessive_punctuation")
        spam_score += 0.2

    # Check for suspicious patterns
    suspicious_patterns = [
        r"click\s+here",
        r"buy\s+now",
        r"limited\s+time",
        r"act\s+fast",
        r"free\s+money",
        r"make\s+money\s+fast",
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, text.lower()):
            spam_indicators.append(f"suspicious_pattern: {pattern}")
            spam_score += 0.3

    # Check engagement anomalies (if provided)
    if engagement_metrics:
        total_engagement = engagement_metrics.get("total_engagement", 0)
        like_count = engagement_metrics.get("like_count", 0)

        # Very low engagement might indicate spam
        if total_engagement == 0 and len(text) > 50:
            spam_indicators.append("no_engagement")
            spam_score += 0.1

    # Cap the spam score
    spam_score = min(spam_score, 1.0)

    return {
        "is_spam": spam_score > 0.5,
        "confidence": spam_score,
        "reasons": spam_indicators,
    }


def normalize_username(username: str) -> str:
    """
    Normalize username by removing @ symbol and converting to lowercase.

    Args:
        username: Raw username

    Returns:
        Normalized username
    """
    if not username:
        return ""

    # Remove @ symbol if present
    username = username.lstrip("@")

    # Convert to lowercase
    username = username.lower()

    # Remove any remaining special characters
    username = re.sub(r"[^\w]", "", username)

    return username


def calculate_engagement_rate(metrics: dict, follower_count: int = None) -> float:
    """
    Calculate engagement rate based on metrics.

    Args:
        metrics: Dictionary containing engagement metrics
        follower_count: Number of followers (optional)

    Returns:
        Engagement rate as a float
    """
    total_engagement = metrics.get("total_engagement", 0)

    if follower_count and follower_count > 0:
        return total_engagement / follower_count

    # If no follower count, use total engagement as baseline metric
    return total_engagement


def format_large_number(number: Union[int, float]) -> str:
    """
    Format large numbers with appropriate suffixes (K, M, B).

    Args:
        number: Number to format

    Returns:
        Formatted number string
    """
    if not isinstance(number, (int, float)):
        return str(number)

    if number >= 1_000_000_000:
        return f"{number / 1_000_000_000:.1f}B"
    elif number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(int(number))


def validate_tweet_data(tweet_data: dict) -> dict:
    """
    Validate and clean tweet data.

    Args:
        tweet_data: Raw tweet data dictionary

    Returns:
        Dictionary with validation results and cleaned data
    """
    validation_results = {
        "is_valid": True,
        "warnings": [],
        "errors": [],
        "cleaned_data": tweet_data.copy(),
    }

    # Check required fields
    required_fields = ["tweet_id", "tweet_text", "file_source"]
    for field in required_fields:
        if field not in tweet_data or not tweet_data[field]:
            validation_results["errors"].append(f"Missing required field: {field}")
            validation_results["is_valid"] = False

    # Validate numeric fields
    numeric_fields = ["like_count", "retweet_count", "reply_count", "quote_count"]
    for field in numeric_fields:
        if field in tweet_data:
            cleaned_value = safe_int_convert(tweet_data[field])
            if cleaned_value != tweet_data[field]:
                validation_results["warnings"].append(
                    f"Converted {field} to integer: {tweet_data[field]} -> {cleaned_value}"
                )
                validation_results["cleaned_data"][field] = cleaned_value

    # Validate text length
    tweet_text = tweet_data.get("tweet_text", "")
    if len(tweet_text) > 2000:  # Reasonable upper limit
        validation_results["warnings"].append(
            f"Tweet text unusually long: {len(tweet_text)} characters"
        )

    # Check for potential encoding issues
    if tweet_text and any(ord(char) > 65535 for char in tweet_text):
        validation_results["warnings"].append("Tweet contains high Unicode characters")

    return validation_results


# Security utility functions


def safe_json_load(file_path: str, max_size_mb: int = 50) -> dict:
    """
    Safely load JSON file with size and content validation.

    Args:
        file_path: Path to JSON file
        max_size_mb: Maximum file size in MB

    Returns:
        Parsed JSON data

    Raises:
        ValueError: If file is too large or contains invalid data
        json.JSONDecodeError: If JSON parsing fails
    """
    import os
    import json

    # Check file size
    file_size = os.path.getsize(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        raise ValueError(f"File too large: {file_size} bytes (max: {max_size_bytes})")

    # Load and validate JSON
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Basic structure validation
    if not isinstance(data, (dict, list)):
        raise ValueError("JSON must be object or array")

    return data


def safe_json_loads(json_str: str, max_length: int = 1024 * 1024) -> dict:
    """
    Safely parse JSON string with length validation.

    Args:
        json_str: JSON string to parse
        max_length: Maximum string length

    Returns:
        Parsed JSON data

    Raises:
        ValueError: If string is too long or contains invalid data
    """
    import json

    if len(json_str) > max_length:
        raise ValueError(
            f"JSON string too long: {len(json_str)} chars (max: {max_length})"
        )

    data = json.loads(json_str)

    if not isinstance(data, (dict, list)):
        raise ValueError("JSON must be object or array")

    return data


def sanitize_html_content(html: str, max_length: int = 500 * 1024) -> str:
    """
    Sanitize HTML content to prevent XSS attacks.

    Args:
        html: HTML content to sanitize
        max_length: Maximum content length

    Returns:
        Sanitized HTML
    """
    if len(html) > max_length:
        html = html[:max_length]

    # Remove dangerous tags
    dangerous_tags = ["script", "iframe", "object", "embed", "form", "meta", "link"]
    for tag in dangerous_tags:
        html = re.sub(f"<{tag}.*?</{tag}>", "", html, flags=re.IGNORECASE | re.DOTALL)
        html = re.sub(f"<{tag}.*?>", "", html, flags=re.IGNORECASE)

    # Remove dangerous attributes
    dangerous_attrs = ["onclick", "onload", "onerror", "onmouseover", "onmouseout"]
    for attr in dangerous_attrs:
        html = re.sub(
            f"{attr}\\s*=\\s*[\"'][^\"']*[\"']", "", html, flags=re.IGNORECASE
        )

    # Remove javascript: and vbscript: URLs
    html = re.sub(r"(javascript|vbscript):", "blocked:", html, flags=re.IGNORECASE)

    return html


def safe_extract_hashtags(
    text: str, max_text_length: int = 10000, max_hashtag_length: int = 100
) -> list:
    """
    Safely extract hashtags with ReDoS protection.

    Args:
        text: Text to extract hashtags from
        max_text_length: Maximum text length to process
        max_hashtag_length: Maximum hashtag length

    Returns:
        List of hashtags without # symbol
    """
    if len(text) > max_text_length:
        text = text[:max_text_length]

    # Use non-backtracking pattern with length limit
    pattern = (
        r"#([a-zA-Z0-9_\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]{1,"
        + str(max_hashtag_length)
        + r"})"
    )
    matches = re.findall(pattern, text)

    # Limit number of results
    return matches[:50]


def safe_extract_mentions(
    text: str, max_text_length: int = 10000, max_mention_length: int = 50
) -> list:
    """
    Safely extract mentions with ReDoS protection.

    Args:
        text: Text to extract mentions from
        max_text_length: Maximum text length to process
        max_mention_length: Maximum mention length

    Returns:
        List of mentions without @ symbol
    """
    if len(text) > max_text_length:
        text = text[:max_text_length]

    # Use non-backtracking pattern with length limit
    pattern = r"@([a-zA-Z0-9_]{1," + str(max_mention_length) + r"})"
    matches = re.findall(pattern, text)

    # Limit number of results
    return matches[:50]


def safe_extract_urls(
    text: str, max_text_length: int = 10000, max_url_length: int = 500
) -> list:
    """
    Safely extract URLs with ReDoS protection.

    Args:
        text: Text to extract URLs from
        max_text_length: Maximum text length to process
        max_url_length: Maximum URL length

    Returns:
        List of URLs
    """
    if len(text) > max_text_length:
        text = text[:max_text_length]

    # Use non-backtracking pattern with length limit
    pattern = r"https?://[^\s]{1," + str(max_url_length) + r"}"
    matches = re.findall(pattern, text)

    # Limit number of results and validate each URL
    valid_urls = []
    for url in matches[:20]:
        if is_safe_url(url):
            valid_urls.append(url)

    return valid_urls


def is_safe_url(url: str) -> bool:
    """
    Check if URL is safe (no malicious patterns).

    Args:
        url: URL to check

    Returns:
        True if URL appears safe
    """
    # Block javascript: and other dangerous schemes
    dangerous_schemes = ["javascript:", "vbscript:", "data:", "file:"]
    for scheme in dangerous_schemes:
        if url.lower().startswith(scheme):
            return False

    # Block obvious malicious patterns
    malicious_patterns = ["<script", "javascript:", "onload=", "onerror="]
    for pattern in malicious_patterns:
        if pattern.lower() in url.lower():
            return False

    return True


def safe_file_path(file_path: str, base_dir: str) -> str:
    """
    Safely resolve file path to prevent directory traversal.

    Args:
        file_path: File path to resolve
        base_dir: Base directory to constrain to

    Returns:
        Safe resolved path

    Raises:
        ValueError: If path tries to escape base directory
    """
    import os.path

    # Detect obvious traversal attempts
    if ".." in file_path or file_path.startswith("/"):
        raise ValueError(f"Unsafe path detected: {file_path}")

    # Normalize and resolve path
    full_path = os.path.abspath(os.path.join(base_dir, file_path))
    base_path = os.path.abspath(base_dir)

    # Ensure resolved path is within base directory
    if not full_path.startswith(base_path + os.sep):
        raise ValueError(f"Path escapes base directory: {file_path}")

    return full_path


def sanitize_log_message(message: str, max_length: int = 1000) -> str:
    """
    Sanitize log message to prevent log injection.

    Args:
        message: Log message to sanitize
        max_length: Maximum message length

    Returns:
        Sanitized log message
    """
    if len(message) > max_length:
        message = message[:max_length] + "... (truncated)"

    # Remove control characters that could break log format
    message = re.sub(r"[\r\n\t\x00-\x1f\x7f-\x9f]", " ", message)

    # Replace multiple spaces with single space
    message = re.sub(r"\s+", " ", message)

    return message.strip()


def validate_html_size(html_content: str, max_size: int = 500000) -> bool:
    """
    Validate HTML content size to prevent DoS attacks.

    Args:
        html_content: HTML content to validate
        max_size: Maximum allowed size in bytes

    Returns:
        True if size is acceptable, False otherwise
    """
    if not html_content:
        return True

    return len(html_content.encode("utf-8")) <= max_size
