#!/usr/bin/env python3
"""
Core Twitter data extraction and parsing functionality.

This module provides the main TwitterDataExtractor class for processing
Twitter export JSON files and extracting comprehensive tweet data.
"""

import json
import logging
import os
import re
import unicodedata
from collections import defaultdict
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

from .language_detector import LanguageDetector
from .utils import (
    format_time_duration,
    safe_file_path,
    safe_int_convert,
    safe_json_load,
    safe_json_loads,
    sanitize_html_content,
    sanitize_log_message,
    validate_html_size,
)


class TwitterDataExtractor:
    """
    Main class for extracting comprehensive data from Twitter export JSON files.

    Features:
    - Tweet content and metadata extraction
    - User information and verification status
    - Engagement metrics analysis
    - Media content detection
    - Video misuse detection
    - Advanced language detection
    - Real-time processing with ETA
    """

    def __init__(
        self,
        input_dir: str = "downloads",
        output_dir: str = "parsed",
        reports_dir: str = "reports",
        create_consolidated: bool = False,
        log_level: int = logging.INFO,
    ):
        """
        Initialize TwitterDataExtractor.

        Args:
            input_dir: Directory containing Twitter export JSON files
            output_dir: Directory for parsed output files
            reports_dir: Directory for analysis reports
            create_consolidated: Whether to create consolidated output file
            log_level: Logging level
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.reports_dir = Path(reports_dir)
        self.create_consolidated = create_consolidated

        # Setup logging
        self.logger = self._setup_logging(log_level)

        # Initialize language detector
        self.language_detector = LanguageDetector()

        # Statistics
        self.stats = {
            "total_files": 0,
            "processed_files": 0,
            "total_tweets": 0,
            "successful_extractions": 0,
            "error_count": 0,
            "start_time": None,
            "videos_found": 0,
            "video_misuse_detected": 0,
            "video_detection_methods": defaultdict(int),
        }

        # Setup output directories
        self._setup_output_directories()

    def _setup_logging(self, log_level: int) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("twitter_data_extractor.log", encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        return logging.getLogger(__name__)

    def _setup_output_directories(self) -> None:
        """Create necessary output directories."""
        for directory in [self.output_dir, self.reports_dir]:
            directory.mkdir(exist_ok=True)

    def extract_all(self) -> Dict[str, Any]:
        """
        Main extraction method - processes all JSON files in input directory.

        Returns:
            Dictionary containing processing statistics
        """
        self.logger.info("=== Twitter データ抽出・JSON変換システム開始 ===")
        self.logger.info(
            f"統合ファイル作成: {'有効' if self.create_consolidated else '無効'}"
        )

        # Validate input directory
        if not self.input_dir.exists():
            self.logger.error(f"入力ディレクトリが見つかりません: {self.input_dir}")
            return self.stats

        # Find JSON files
        json_files = sorted(self.input_dir.glob("*.json"))
        if not json_files:
            self.logger.error("JSONファイルが見つかりません")
            return self.stats

        self.stats["total_files"] = len(json_files)
        self.stats["start_time"] = datetime.now()
        self.logger.info(f"処理対象ファイル数: {len(json_files)}")

        # Process files
        all_tweets_data = []
        file_summaries = []
        error_reports = []

        for i, file_path in enumerate(json_files):
            try:
                # Progress logging
                self._log_progress(i, len(json_files))

                # Process single file
                file_data = self._process_single_file(file_path)

                if file_data:
                    # Output individual file immediately
                    self._output_individual_file(file_data["tweets"], file_path)

                    # Update statistics
                    file_summaries.append(file_data["summary"])
                    self.stats["processed_files"] += 1
                    self.stats["total_tweets"] += len(file_data["tweets"])
                    self.stats["successful_extractions"] += file_data["summary"][
                        "successful_tweets"
                    ]

                    # Collect video statistics
                    self._update_video_stats(file_data["tweets"])

                    # Store for consolidated file if requested
                    if self.create_consolidated:
                        all_tweets_data.extend(file_data["tweets"])

            except Exception as e:
                error_msg = f"ファイル処理エラー {sanitize_log_message(file_path.name)}: {sanitize_log_message(str(e))}"
                self.logger.error(error_msg)
                error_reports.append(
                    {
                        "file": file_path.name,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                self.stats["error_count"] += 1

        # Finalize processing
        self.stats["end_time"] = datetime.now()
        self.stats["processing_duration"] = (
            self.stats["end_time"] - self.stats["start_time"]
        ).total_seconds()

        # Output final results
        self._output_final_results(all_tweets_data, file_summaries, error_reports)

        self.logger.info("=== Twitter データ抽出・JSON変換システム完了 ===")
        return self.stats

    def _process_single_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Process a single JSON file."""
        try:
            data = safe_json_load(str(file_path))

            if "data" not in data or not isinstance(data["data"], list):
                self.logger.warning(f"不正なファイル構造: {file_path.name}")
                return None

            tweets = data["data"]
            extracted_tweets = []
            successful_count = 0
            error_count = 0

            for tweet_index, tweet in enumerate(tweets):
                try:
                    tweet_data = self._extract_comprehensive_tweet_data(
                        tweet, file_path.name, tweet_index
                    )
                    extracted_tweets.append(tweet_data)

                    if tweet_data.get("data_quality_score", 0) > 50:
                        successful_count += 1
                    else:
                        error_count += 1

                except Exception as e:
                    error_data = self._create_error_record(
                        file_path.name, tweet_index, str(e)
                    )
                    extracted_tweets.append(error_data)
                    error_count += 1

            # File summary
            file_summary = {
                "filename": file_path.name,
                "total_tweets": len(tweets),
                "successful_tweets": successful_count,
                "error_tweets": error_count,
                "success_rate": successful_count / len(tweets) if tweets else 0,
                "file_size": file_path.stat().st_size,
                "processing_timestamp": datetime.now().isoformat(),
            }

            return {"tweets": extracted_tweets, "summary": file_summary}

        except ValueError as e:
            # Safe JSON loading errors
            self.logger.error(
                f"JSON読み込みエラー {sanitize_log_message(file_path.name)}: {sanitize_log_message(str(e))}"
            )
            return None
        except Exception as e:
            self.logger.error(
                f"ファイル読み込みエラー {sanitize_log_message(file_path.name)}: {sanitize_log_message(str(e))}"
            )
            return None

    def _extract_comprehensive_tweet_data(
        self, tweet: Dict, file_source: str, tweet_index: int
    ) -> Dict[str, Any]:
        """Extract comprehensive data from a single tweet."""
        data = {
            "file_source": file_source,
            "tweet_id": tweet.get("tweetId", ""),
            "tweet_index": tweet_index,
            "processing_timestamp": datetime.now().isoformat(),
            "extraction_errors": [],
            "data_quality_score": 0,
        }

        try:
            # Parse HTML content with security validation
            html_content = tweet.get("elementHtml", "")
            if html_content:
                # Validate HTML size to prevent DoS
                if not validate_html_size(html_content):
                    data["extraction_errors"].append(
                        "HTML content too large, truncated"
                    )
                    html_content = html_content[:100000]  # Truncate if too large

                # Sanitize HTML content to prevent XSS
                html_content = sanitize_html_content(html_content)

            soup = BeautifulSoup(html_content, "html.parser") if html_content else None
            tweet_text = tweet.get("tweetText", "")

            quality_score = 0

            # Extract various data components
            self._extract_user_information(soup, tweet, data)
            quality_score += 20

            self._extract_verification_status(soup, data)
            quality_score += 15

            self._extract_content_data(tweet_text, data)
            quality_score += 25

            self._extract_interaction_data(tweet, data)
            quality_score += 15

            self._extract_metadata(soup, tweet, data)
            quality_score += 10

            self._extract_media_content(soup, data)
            quality_score += 5

            # Video misuse detection
            if data.get("has_videos"):
                self._detect_video_misuse(soup, tweet, data)

            self._extract_linguistic_features(tweet_text, data)
            quality_score += 5

            self._extract_ui_information(soup, data)
            quality_score += 5

            # Additional analysis
            self._extract_sentiment_analysis(tweet_text, data)
            self._extract_network_elements(tweet, data)

            data["data_quality_score"] = quality_score

        except Exception as e:
            data["extraction_errors"].append(str(e))
            data["data_quality_score"] = 0

        # Convert error list to string
        data["extraction_errors"] = "; ".join(data["extraction_errors"])

        return data

    def _extract_user_information(
        self, soup: BeautifulSoup, tweet: Dict, data: Dict
    ) -> None:
        """Extract user information from tweet data."""
        try:
            # Screen name
            screen_name = tweet.get("screenName", "")
            if not screen_name and soup:
                avatar_elements = soup.find_all(
                    "div", {"data-testid": re.compile(r"UserAvatar-Container-.*")}
                )
                for elem in avatar_elements:
                    testid = elem.get("data-testid", "")
                    if testid.startswith("UserAvatar-Container-"):
                        screen_name = testid.replace("UserAvatar-Container-", "")
                        break

            data["screen_name"] = screen_name

            # User ID extraction from Twitter export data
            user_id = ""

            # Extract from user action buttons data-testid
            # Pattern: {user_id}-(follow|unfollow|block|unblock)
            if soup:
                # Look for user buttons with the ID pattern
                find_pattern = re.compile(r"^\d+-(follow|unfollow|block|unblock)$")
                user_buttons = soup.find_all(attrs={"data-testid": find_pattern})
                for button in user_buttons:
                    testid = button.get("data-testid", "")
                    match_pattern = r"^(\d+)-(follow|unfollow|block|unblock)$"
                    match = re.search(match_pattern, testid)
                    if match:
                        user_id = match.group(1)
                        break

            # If no user_id found from buttons, set to empty string (null equivalent)
            if not user_id:
                error_msg = (
                    "No user_id found in HTML - "
                    "no follow/unfollow/block/unblock buttons detected"
                )
                if "extraction_errors" not in data:
                    data["extraction_errors"] = []
                data["extraction_errors"].append(error_msg)

            data["user_id"] = user_id

            # Display name
            display_name = ""
            if soup:
                name_candidates = []

                # Extract from aria-label
                aria_elements = soup.find_all(attrs={"aria-label": True})
                for elem in aria_elements:
                    aria_label = elem.get("aria-label", "")
                    if "さんのプロフィール" in aria_label:
                        name_candidates.append(
                            aria_label.replace("さんのプロフィール", "").strip()
                        )

                # Extract from span elements
                span_elements = soup.find_all("span")
                for elem in span_elements:
                    text = elem.get_text(strip=True)
                    if (
                        text
                        and len(text) > 1
                        and len(text) < 50
                        and not text.startswith("@")
                    ):
                        name_candidates.append(text)

                if name_candidates:
                    display_name = max(name_candidates, key=len)

            data["display_name"] = display_name

            # Profile image URL
            profile_image_url = ""
            if soup:
                avatar_img = soup.find("img", src=re.compile(r"profile_images"))
                if avatar_img:
                    profile_image_url = avatar_img.get("src", "")

            data["profile_image_url"] = profile_image_url
            data["estimated_followers"] = 0  # Could be enhanced

        except Exception as e:
            if "extraction_errors" not in data:
                data["extraction_errors"] = []
            data["extraction_errors"].append(f"User info error: {e}")

    def _extract_verification_status(self, soup: BeautifulSoup, data: Dict) -> None:
        """Extract verification status information."""
        data["is_verified"] = False
        data["verification_type"] = "none"
        data["verification_confidence"] = 0
        data["verification_details"] = {}

        if not soup:
            return

        try:
            # Check for verification indicators
            aria_elements = soup.find_all(
                attrs={"aria-label": re.compile(r"認証済み|verified", re.IGNORECASE)}
            )
            if aria_elements:
                data["is_verified"] = True
                data["verification_confidence"] = 0.95

                # Analyze SVG elements for verification type
                svg_elements = soup.find_all("svg")
                for svg in svg_elements:
                    svg_str = str(svg)

                    colors = re.findall(r'fill="([^"]+)"', svg_str)
                    paths = re.findall(r'd="([^"]+)"', svg_str)

                    # Determine verification type based on colors and paths
                    if "#d18800" in colors and len(paths) >= 6:
                        data["verification_type"] = "gold_verified"
                        data["verification_details"]["color"] = "gold"
                    elif "#829aab" in colors:
                        data["verification_type"] = "gray_verified"
                        data["verification_details"]["color"] = "gray"
                    elif len(paths) == 2:
                        data["verification_type"] = "blue_verified"
                        data["verification_details"]["color"] = "blue"
                    else:
                        data["verification_type"] = "verified_unknown"

                    data["verification_details"]["path_count"] = len(paths)
                    data["verification_details"]["colors"] = "; ".join(colors)
                    break

                if data["verification_type"] == "none":
                    data["verification_type"] = "blue_verified"

        except Exception as e:
            data["extraction_errors"].append(f"Verification error: {e}")

    def _extract_content_data(self, tweet_text: str, data: Dict) -> None:
        """Extract content data and perform language analysis."""
        try:
            data["tweet_text"] = tweet_text
            data["text_length"] = len(tweet_text)
            data["word_count"] = len(tweet_text.split())

            # Advanced language detection
            language_info = self.language_detector.detect_languages(tweet_text)
            data["language_detected"] = language_info["primary"]
            data["language_confidence"] = language_info["confidence"]
            data["language_details"] = language_info["details"]
            data["script_analysis"] = language_info["script_analysis"]
            data["linguistic_features"] = language_info["linguistic_features"]

            # Hashtag analysis - ReDoS-safe pattern
            hashtags = re.findall(
                r"#[\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]{1,100}?(?=\s|$|[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF])",
                tweet_text[:5000],  # Limit input length
            )
            data["hashtag_count"] = len(hashtags)
            data["hashtags"] = "; ".join(hashtags)
            data["unique_hashtags"] = len(set(hashtags))

            # Mention analysis - ReDoS-safe pattern
            mentions = re.findall(r"@\w{1,50}?(?=\s|$|[^\w])", tweet_text[:5000])
            data["mention_count"] = len(mentions)
            data["mentions"] = "; ".join(mentions)
            data["unique_mentions"] = len(set(mentions))

            # URL analysis - ReDoS-safe pattern
            urls = re.findall(r"https?://[^\s]{1,500}?", tweet_text[:5000])
            data["url_count"] = len(urls)
            data["urls"] = "; ".join(urls)

            # Domain analysis
            domains = []
            for url in urls:
                match = re.search(r"https?://([^/]+)", url)
                if match:
                    domains.append(match.group(1))
            data["domains"] = "; ".join(set(domains))

            # Emoji analysis
            unicode_emojis = self._extract_unicode_emojis(tweet_text)
            data["emoji_count_unicode"] = len(unicode_emojis)
            data["unique_emojis"] = len(set(unicode_emojis))

            # Special character analysis
            data["special_char_count"] = self._count_special_characters(tweet_text)

        except Exception as e:
            data["extraction_errors"].append(f"Content error: {e}")

    def _extract_interaction_data(self, tweet: Dict, data: Dict) -> None:
        """Extract engagement and interaction data."""
        try:
            # Basic engagement metrics
            like_count = safe_int_convert(tweet.get("likeCount", 0))
            retweet_count = safe_int_convert(tweet.get("retweetCount", 0))
            reply_count = safe_int_convert(tweet.get("replyCount", 0))
            quote_count = safe_int_convert(tweet.get("quoteCount", 0))

            data["like_count"] = like_count
            data["retweet_count"] = retweet_count
            data["reply_count"] = reply_count
            data["quote_count"] = quote_count
            data["total_engagement"] = (
                like_count + retweet_count + reply_count + quote_count
            )

            # Engagement ratios
            total = data["total_engagement"]
            if total > 0:
                data["like_ratio"] = like_count / total
                data["retweet_ratio"] = retweet_count / total
                data["reply_ratio"] = reply_count / total
            else:
                data["like_ratio"] = 0
                data["retweet_ratio"] = 0
                data["reply_ratio"] = 0

            # Viral score calculation
            data["viral_score"] = (
                (retweet_count * 3) + (like_count * 1) + (reply_count * 2)
            )

        except Exception as e:
            data["extraction_errors"].append(f"Interaction error: {e}")

    def _extract_metadata(self, soup: BeautifulSoup, tweet: Dict, data: Dict) -> None:
        """Extract metadata including timestamps and permalinks."""
        try:
            if soup:
                time_tag = soup.find("time")
                if time_tag and time_tag.get("datetime"):
                    try:
                        timestamp_str = time_tag.get("datetime")
                        timestamp = datetime.fromisoformat(
                            timestamp_str.replace("Z", "+00:00")
                        )
                        data["timestamp"] = timestamp.isoformat()
                        data["post_hour"] = timestamp.hour
                        data["post_day_of_week"] = timestamp.weekday()
                        data["post_month"] = timestamp.month
                        data["post_year"] = timestamp.year
                    except:
                        pass

                if time_tag:
                    data["relative_time"] = time_tag.get_text(strip=True)

                # Tweet permalink
                parent_link = time_tag.find_parent("a") if time_tag else None
                if parent_link:
                    relative_path = parent_link.get("href", "")
                    data["tweet_permalink_relative"] = relative_path

                    screen_name = data.get("screen_name", "")
                    tweet_id = data.get("tweet_id", "")
                    if screen_name and tweet_id:
                        data["tweet_permalink_absolute"] = (
                            f"https://x.com/{screen_name}/status/{tweet_id}"
                        )

        except Exception as e:
            data["extraction_errors"].append(f"Metadata error: {e}")

    def _extract_media_content(self, soup: BeautifulSoup, data: Dict) -> None:
        """Extract media content information."""
        try:
            if not soup:
                return

            # Images
            images = soup.find_all("img")
            media_images = [
                img for img in images if "pbs.twimg.com/media/" in img.get("src", "")
            ]
            data["has_attached_media"] = len(media_images) > 0
            data["attached_media_count"] = len(media_images)
            data["attached_media_urls"] = "; ".join(
                [img.get("src", "") for img in media_images]
            )

            # Emoji images
            emoji_images = [img for img in images if "emoji" in img.get("src", "")]
            data["has_emoji_images"] = len(emoji_images) > 0
            data["emoji_image_count"] = len(emoji_images)

            # Videos
            videos = soup.find_all("video")
            data["has_videos"] = len(videos) > 0
            data["video_count"] = len(videos)

            # Image alt texts
            alt_texts = [img.get("alt", "") for img in images if img.get("alt")]
            data["image_alt_texts"] = "; ".join(alt_texts)

            # Media types
            media_types = []
            if media_images:
                media_types.append("image")
            if videos:
                media_types.append("video")
            data["media_types"] = "; ".join(media_types)

        except Exception as e:
            data["extraction_errors"].append(f"Media error: {e}")

    def _detect_video_misuse(
        self, soup: BeautifulSoup, tweet: Dict, data: Dict
    ) -> None:
        """Detect potential video misuse."""
        try:
            # Initialize detection fields
            data["video_misuse_detected"] = False
            data["video_creator"] = ""
            data["video_detection_method"] = ""
            data["is_quote_tweet"] = False
            data["is_retweet"] = False
            data["video_misuse_confidence"] = 0
            data["video_attribution_text"] = ""
            data["video_source_info"] = ""

            html_content = str(soup) if soup else ""
            screen_name = data.get("screen_name", "").lower()

            # Check for retweets/quotes (not considered misuse)
            if soup:
                retweet_indicators = soup.find_all(
                    attrs={"data-testid": "socialContext"}
                )
                if retweet_indicators:
                    data["is_retweet"] = True
                    return

                quoted_tweet = soup.find("div", {"role": "blockquote"})
                if quoted_tweet:
                    data["is_quote_tweet"] = True

            # Method 1: cslt_tweet_info analysis
            video_creator = self._parse_cslt_tweet_info_for_video(html_content)
            if video_creator and video_creator.lower() != screen_name:
                data["video_misuse_detected"] = True
                data["video_creator"] = video_creator
                data["video_detection_method"] = "cslt_tweet_info"
                data["video_misuse_confidence"] = 0.9

                cslt_match = re.search(r'cslt_tweet_info="([^"]*)"', html_content)
                if cslt_match:
                    data["video_source_info"] = unescape(cslt_match.group(1))[:200]
                return

            # Method 2: HTML attribution analysis
            video_creator = self._detect_video_creator_from_html(html_content)
            if video_creator and video_creator.lower() != screen_name:
                data["video_misuse_detected"] = True
                data["video_creator"] = video_creator
                data["video_detection_method"] = "html_attribution"
                data["video_misuse_confidence"] = 0.8
                data["video_attribution_text"] = self._extract_attribution_text(
                    html_content
                )
                return

            # Method 3: Pattern matching
            attribution_patterns = [
                r'投稿者:\s*.*?href="/([^"]+)"',
                r'aria-label="([^"]+)さんから"',
                r"Video\s+by\s+@?([a-zA-Z0-9_]+)",
                r"Original\s+video\s+by\s+@?([a-zA-Z0-9_]+)",
            ]

            for pattern in attribution_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    if match.lower() != screen_name:
                        data["video_misuse_detected"] = True
                        data["video_creator"] = match
                        data["video_detection_method"] = "pattern_matching"
                        data["video_misuse_confidence"] = 0.7
                        return

        except Exception as e:
            data["extraction_errors"].append(f"Video misuse detection error: {e}")

    def _parse_cslt_tweet_info_for_video(self, html_content: str) -> Optional[str]:
        """Parse cslt_tweet_info for video creator information."""
        try:
            # ReDoS-safe pattern with length limit
            pattern = r'cslt_tweet_info="([^"]{0,10000}?)"'
            match = re.search(pattern, html_content[:50000])  # Limit input length

            if not match:
                return None

            json_str = unescape(match.group(1))
            tweet_info = safe_json_loads(json_str)

            video_info_list = tweet_info.get("tweet_video_info", [])
            for video_info in video_info_list:
                if "video_source_user_info" in video_info:
                    source_user = video_info["video_source_user_info"]
                    if "user_data" in source_user:
                        user_data = source_user["user_data"]
                        return user_data.get(
                            "screen_name",
                            "Different user (from video_source_user_info)",
                        )

            return None

        except Exception:
            return None

    def _detect_video_creator_from_html(self, html_content: str) -> Optional[str]:
        """Detect video creator from HTML content patterns."""
        try:
            # Japanese attribution pattern
            creator_pattern = r"投稿者:\s*<a[^>]*>.*?<span[^>]*>([^<]+)</span>"
            match = re.search(creator_pattern, html_content, re.DOTALL)

            if match:
                return match.group(1).strip()

            # Other attribution patterns
            patterns = [
                r'<div[^>]*aria-label="([^"]+)さんから"',
                r"video\s+by\s+@?([a-zA-Z0-9_]+)",
                r"original\s+video\s+by\s+@?([a-zA-Z0-9_]+)",
                r"created\s+by\s+@?([a-zA-Z0-9_]+)",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    return matches[0].strip()

            return None

        except Exception:
            return None

    def _extract_attribution_text(self, html_content: str) -> str:
        """Extract attribution text from HTML content."""
        try:
            attribution_patterns = [
                r"投稿者:[^<]*<[^>]*>([^<]+)",
                r'aria-label="([^"]*さんから[^"]*)"',
                r"(Video by [^<>\n]*)",
                r"(Original video by [^<>\n]*)",
            ]

            for pattern in attribution_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                if matches:
                    return matches[0].strip()

            return ""

        except Exception:
            return ""

    def _extract_linguistic_features(self, tweet_text: str, data: Dict) -> None:
        """Extract linguistic and cultural features."""
        try:
            # Character analysis
            kanji_count = 0
            hiragana_count = 0
            katakana_count = 0
            ascii_count = 0

            for char in tweet_text:
                name = unicodedata.name(char, "")
                if "CJK" in name:
                    kanji_count += 1
                elif "HIRAGANA" in name:
                    hiragana_count += 1
                elif "KATAKANA" in name:
                    katakana_count += 1
                elif ord(char) < 128:
                    ascii_count += 1

            total_chars = len(tweet_text)
            data["kanji_count"] = kanji_count
            data["hiragana_count"] = hiragana_count
            data["katakana_count"] = katakana_count
            data["ascii_count"] = ascii_count
            data["kanji_ratio"] = kanji_count / total_chars if total_chars > 0 else 0
            data["hiragana_ratio"] = (
                hiragana_count / total_chars if total_chars > 0 else 0
            )

            # Politeness level
            polite_indicators = ["です", "ます", "ございます", "であります"]
            politeness_score = sum(
                tweet_text.count(indicator) for indicator in polite_indicators
            )

            if politeness_score >= 3:
                data["politeness_level"] = "very_high"
            elif politeness_score >= 2:
                data["politeness_level"] = "high"
            elif politeness_score >= 1:
                data["politeness_level"] = "medium"
            else:
                data["politeness_level"] = "low"

            # Cultural terms
            cultural_terms = [
                "ありがとう",
                "すみません",
                "お疲れ",
                "よろしく",
                "さん",
                "ちゃん",
                "お世話になっております",
            ]
            found_terms = [term for term in cultural_terms if term in tweet_text]
            data["cultural_terms"] = "; ".join(found_terms)
            data["cultural_terms_count"] = len(found_terms)

            # Time expressions
            time_expressions = [
                "朝",
                "昼",
                "夜",
                "今日",
                "昨日",
                "明日",
                "今週",
                "来週",
                "今月",
                "来月",
            ]
            found_time = [expr for expr in time_expressions if expr in tweet_text]
            data["time_expressions"] = "; ".join(found_time)
            data["time_expressions_count"] = len(found_time)

            # Location references
            locations = [
                "東京",
                "大阪",
                "日本",
                "関東",
                "関西",
                "九州",
                "北海道",
                "沖縄",
            ]
            found_locations = [loc for loc in locations if loc in tweet_text]
            data["location_references"] = "; ".join(found_locations)
            data["location_references_count"] = len(found_locations)

        except Exception as e:
            data["extraction_errors"].append(f"Linguistic error: {e}")

    def _extract_sentiment_analysis(self, tweet_text: str, data: Dict) -> None:
        """Simple sentiment analysis."""
        try:
            positive_words = [
                "good",
                "great",
                "love",
                "awesome",
                "excellent",
                "素晴らしい",
                "良い",
                "最高",
            ]
            negative_words = [
                "bad",
                "hate",
                "terrible",
                "awful",
                "worst",
                "ひどい",
                "悪い",
                "最悪",
            ]

            text_lower = tweet_text.lower()
            positive_count = sum(word in text_lower for word in positive_words)
            negative_count = sum(word in text_lower for word in negative_words)

            if positive_count > negative_count:
                data["sentiment"] = "positive"
                data["sentiment_score"] = positive_count - negative_count
            elif negative_count > positive_count:
                data["sentiment"] = "negative"
                data["sentiment_score"] = negative_count - positive_count
            else:
                data["sentiment"] = "neutral"
                data["sentiment_score"] = 0

        except Exception as e:
            data["extraction_errors"].append(f"Sentiment error: {e}")

    def _extract_network_elements(self, tweet: Dict, data: Dict) -> None:
        """Extract network analysis elements."""
        try:
            # Reply information
            data["is_reply"] = bool(tweet.get("inReplyToTweetId"))
            data["reply_to_tweet_id"] = tweet.get("inReplyToTweetId", "")
            data["reply_to_user"] = tweet.get("inReplyToUser", "")

            # Quote tweet information
            data["is_quote_tweet"] = bool(tweet.get("quotedTweet"))
            data["quoted_tweet_id"] = (
                tweet.get("quotedTweet", {}).get("tweetId", "")
                if tweet.get("quotedTweet")
                else ""
            )

            # Retweet information
            data["is_retweet"] = bool(tweet.get("retweetedTweet"))
            data["retweeted_tweet_id"] = (
                tweet.get("retweetedTweet", {}).get("tweetId", "")
                if tweet.get("retweetedTweet")
                else ""
            )

        except Exception as e:
            data["extraction_errors"].append(f"Network error: {e}")

    def _extract_ui_information(self, soup: BeautifulSoup, data: Dict) -> None:
        """Extract UI and technical information."""
        try:
            if not soup:
                return

            # CSS classes analysis
            all_classes = []
            for element in soup.find_all(class_=True):
                all_classes.extend(element.get("class", []))
            data["css_classes_count"] = len(set(all_classes))
            data["total_css_classes"] = len(all_classes)

            # data-testid attributes
            testid_elements = soup.find_all(attrs={"data-testid": True})
            testids = [elem.get("data-testid") for elem in testid_elements]
            data["data_testids"] = "; ".join(list(set(testids)))
            data["data_testids_count"] = len(set(testids))

            # aria-label count
            aria_elements = soup.find_all(attrs={"aria-label": True})
            data["aria_labels_count"] = len(aria_elements)

            # HTML structure analysis
            all_elements = soup.find_all()
            data["total_elements"] = len(all_elements)

            # Tag types
            tag_types = [elem.name for elem in all_elements]
            unique_tags = set(tag_types)
            data["unique_tag_types"] = len(unique_tags)
            data["tag_types"] = "; ".join(sorted(unique_tags))

            # Maximum depth
            max_depth = 0
            for element in all_elements:
                depth = len(list(element.parents))
                max_depth = max(max_depth, depth)
            data["html_depth"] = max_depth

        except Exception as e:
            data["extraction_errors"].append(f"UI info error: {e}")

    def _extract_unicode_emojis(self, text: str) -> List[str]:
        """Extract Unicode emojis from text."""
        emoji_pattern = re.compile(
            "["
            "\U0001f600-\U0001f64f"  # emoticons
            "\U0001f300-\U0001f5ff"  # symbols & pictographs
            "\U0001f680-\U0001f6ff"  # transport & map
            "\U0001f1e0-\U0001f1ff"  # flags
            "\U00002600-\U000027bf"  # misc symbols
            "\U0001f900-\U0001f9ff"  # supplemental symbols
            "]+",
            flags=re.UNICODE,
        )
        return emoji_pattern.findall(text)

    def _count_special_characters(self, text: str) -> int:
        """Count special characters in text."""
        special_chars = re.findall(
            r"[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]", text
        )
        return len(special_chars)

    def _create_error_record(
        self, file_source: str, tweet_index: int, error_message: str
    ) -> Dict[str, Any]:
        """Create error record for failed tweet processing."""
        return {
            "file_source": file_source,
            "tweet_index": tweet_index,
            "extraction_errors": error_message,
            "data_quality_score": 0,
            "processing_timestamp": datetime.now().isoformat(),
        }

    def _log_progress(self, current: int, total: int) -> None:
        """Log processing progress with ETA."""
        should_log = (
            (current < 100 and current % 10 == 0)
            or (current >= 100 and current % 50 == 0)
            or current == 0
        )

        if should_log:
            progress = (current + 1) / total * 100
            elapsed_time = (datetime.now() - self.stats["start_time"]).total_seconds()

            if current > 0:
                avg_time_per_file = elapsed_time / current
                remaining_files = total - current
                eta_seconds = avg_time_per_file * remaining_files
                eta_str = format_time_duration(eta_seconds)
                files_per_second = current / elapsed_time

                self.logger.info(
                    f"処理進捗: {current+1}/{total} ({progress:.1f}%) | "
                    f"経過時間: {format_time_duration(elapsed_time)} | "
                    f"推定残り時間: {eta_str} | "
                    f"処理速度: {files_per_second:.2f}ファイル/秒 | "
                    f"累計ツイート数: {self.stats['total_tweets']} | "
                    f"動画: {self.stats['videos_found']}件 | "
                    f"無断使用: {self.stats['video_misuse_detected']}件"
                )
            else:
                self.logger.info(f"処理開始: {current+1}/{total} ({progress:.1f}%)")

    def _update_video_stats(self, tweets: List[Dict]) -> None:
        """Update video-related statistics."""
        for tweet in tweets:
            if tweet.get("has_videos"):
                self.stats["videos_found"] += 1
            if tweet.get("video_misuse_detected"):
                self.stats["video_misuse_detected"] += 1
                method = tweet.get("video_detection_method", "unknown")
                self.stats["video_detection_methods"][method] += 1

    def _output_individual_file(self, tweets_data: List[Dict], file_path: Path) -> None:
        """Output individual JSON file immediately."""
        try:
            output_filename = file_path.stem + "_extracted.json"
            # Use safe file path to prevent directory traversal
            safe_output_path = safe_file_path(output_filename, str(self.output_dir))
            output_file = Path(safe_output_path)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(tweets_data, f, ensure_ascii=False, indent=2)

            self.logger.debug(
                f"個別ファイル出力完了: {output_file} ({len(tweets_data)}件)"
            )

        except Exception as e:
            self.logger.error(f"個別ファイル出力エラー {file_path.name}: {e}")

    def _output_final_results(
        self,
        all_tweets_data: List[Dict],
        file_summaries: List[Dict],
        error_reports: List[Dict],
    ) -> None:
        """Output final results including consolidated file and reports."""
        try:
            # Consolidated file (if requested)
            if self.create_consolidated and all_tweets_data:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                consolidated_file = (
                    self.output_dir / f"all_extracted_tweets_{timestamp}.json"
                )

                with open(consolidated_file, "w", encoding="utf-8") as f:
                    json.dump(all_tweets_data, f, ensure_ascii=False, indent=2)

                self.logger.info(
                    f"統合ファイル出力完了: {consolidated_file} ({len(all_tweets_data)}件)"
                )
            elif self.create_consolidated:
                self.logger.info(
                    "統合ファイルの作成が要求されましたが、データがありません"
                )
            else:
                self.logger.info("統合ファイル作成はスキップされました")

            # Summary report
            self._output_summary_report(file_summaries)

            # Error report
            if error_reports:
                self._output_error_report(error_reports)

            # Statistics
            self._output_statistics()

        except Exception as e:
            self.logger.error(f"最終結果出力エラー: {e}")

    def _output_summary_report(self, file_summaries: List[Dict]) -> None:
        """Output summary report."""
        try:
            report_file = (
                self.reports_dir
                / f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            report_data = {
                "overall_statistics": self.stats,
                "file_summaries": file_summaries,
                "top_performing_files": sorted(
                    file_summaries, key=lambda x: x["success_rate"], reverse=True
                )[:10],
            }

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)

            self.logger.info(f"サマリーレポート出力完了: {report_file}")

        except Exception as e:
            self.logger.error(f"サマリーレポート出力エラー: {e}")

    def _output_error_report(self, error_reports: List[Dict]) -> None:
        """Output error report."""
        try:
            error_file = (
                self.reports_dir
                / f"error_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            with open(error_file, "w", encoding="utf-8") as f:
                json.dump(error_reports, f, ensure_ascii=False, indent=2)

            self.logger.info(f"エラーレポート出力完了: {error_file}")

        except Exception as e:
            self.logger.error(f"エラーレポート出力エラー: {e}")

    def _output_statistics(self) -> None:
        """Output processing statistics."""
        try:
            stats_file = (
                self.reports_dir
                / f"processing_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            # Convert datetime objects to strings
            stats_output = {}
            for key, value in self.stats.items():
                if isinstance(value, datetime):
                    stats_output[key] = value.isoformat()
                else:
                    stats_output[key] = value

            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(stats_output, f, ensure_ascii=False, indent=2)

            self.logger.info(f"統計情報出力完了: {stats_file}")

        except Exception as e:
            self.logger.error(f"統計情報出力エラー: {e}")
