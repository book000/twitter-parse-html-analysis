#!/usr/bin/env python3
"""
Utility functions for Twitter data extraction and analysis.

This module provides common utility functions used throughout the
Twitter parsing and analysis system.
"""

import re
from typing import Any, Union


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
    Extract hashtags from text.

    Args:
        text: Text to extract hashtags from

    Returns:
        List of hashtags (without # symbol)
    """
    if not text:
        return []

    # Support Unicode characters in hashtags
    pattern = r"#([\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]+)"
    matches = re.findall(pattern, text)
    return matches


def extract_mentions(text: str) -> list:
    """
    Extract mentions from text.

    Args:
        text: Text to extract mentions from

    Returns:
        List of mentioned usernames (without @ symbol)
    """
    if not text:
        return []

    pattern = r"@(\w+)"
    matches = re.findall(pattern, text)
    return matches


def extract_urls(text: str) -> list:
    """
    Extract URLs from text.

    Args:
        text: Text to extract URLs from

    Returns:
        List of URLs
    """
    if not text:
        return []

    pattern = r"https?://\S+"
    matches = re.findall(pattern, text)
    return matches


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
