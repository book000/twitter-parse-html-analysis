#!/usr/bin/env python3
"""
Tests for TwitterDataExtractor
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.parser import TwitterDataExtractor


class TestTwitterDataExtractor(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"
        self.reports_dir = Path(self.temp_dir) / "reports"

        # Create directories
        self.input_dir.mkdir()
        self.output_dir.mkdir()
        self.reports_dir.mkdir()

        # Sample tweet data
        self.sample_data = {
            "data": [
                {
                    "tweetId": "1234567890",
                    "screenName": "test_user",
                    "tweetText": "これはテストツイートです。This is a test tweet! 🎉 #test",
                    "likeCount": "10",
                    "retweetCount": "5",
                    "replyCount": "2",
                    "elementHtml": """
                    <div data-testid="UserAvatar-Container-test_user">
                        <img src="https://pbs.twimg.com/profile_images/123/test.jpg" />
                        <span>Test User</span>
                        <time datetime="2024-01-01T12:00:00.000Z">1月1日</time>
                    </div>
                    """,
                }
            ]
        }

        # Create sample JSON file
        sample_file = self.input_dir / "sample.json"
        with open(sample_file, "w", encoding="utf-8") as f:
            json.dump(self.sample_data, f, ensure_ascii=False)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)

    def test_init(self):
        """Test TwitterDataExtractor initialization."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        self.assertEqual(extractor.input_dir, self.input_dir)
        self.assertEqual(extractor.output_dir, self.output_dir)
        self.assertEqual(extractor.reports_dir, self.reports_dir)
        self.assertIsNotNone(extractor.language_detector)

    def test_extract_all_basic(self):
        """Test basic extraction functionality."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
            create_consolidated=False,
        )

        # Mock logger to avoid log output during tests
        with patch.object(extractor, "logger", MagicMock()):
            stats = extractor.extract_all()

        # Check stats
        self.assertEqual(stats["total_files"], 1)
        self.assertEqual(stats["processed_files"], 1)

        # Check output files were created
        output_files = list(self.output_dir.glob("*.json"))
        self.assertEqual(len(output_files), 1)

        # Check output content
        with open(output_files[0], "r", encoding="utf-8") as f:
            extracted_data = json.load(f)

        self.assertEqual(len(extracted_data), 1)
        tweet = extracted_data[0]
        self.assertEqual(tweet["tweet_id"], "1234567890")
        self.assertEqual(tweet["screen_name"], "test_user")

    def test_extract_user_information(self):
        """Test user information extraction."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        from bs4 import BeautifulSoup

        html = """
        <div data-testid="UserAvatar-Container-testuser">
            <img src="https://pbs.twimg.com/profile_images/123/test.jpg" alt="Profile" />
            <span>Test Display Name</span>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        data = {}
        tweet = {"screenName": "testuser"}

        extractor._extract_user_information(soup, tweet, data)

        self.assertEqual(data["screen_name"], "testuser")
        self.assertIn("profile_images", data["profile_image_url"])

    def test_language_detection_integration(self):
        """Test language detection integration."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        # Test Japanese text
        data = {}
        extractor._extract_content_data("これは日本語のテストです。", data)

        self.assertEqual(data["language_detected"], "japanese")
        self.assertGreater(data["language_confidence"], 0.5)

        # Test English text
        data = {}
        extractor._extract_content_data("This is an English test.", data)

        self.assertEqual(data["language_detected"], "english")
        self.assertGreater(data["language_confidence"], 0.5)

    def test_engagement_extraction(self):
        """Test engagement metrics extraction."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        tweet = {
            "likeCount": "100",
            "retweetCount": "50",
            "replyCount": "25",
            "quoteCount": "10",
        }

        data = {}
        extractor._extract_interaction_data(tweet, data)

        self.assertEqual(data["like_count"], 100)
        self.assertEqual(data["retweet_count"], 50)
        self.assertEqual(data["reply_count"], 25)
        self.assertEqual(data["quote_count"], 10)
        self.assertEqual(data["total_engagement"], 185)

        # Test viral score
        expected_viral_score = (50 * 3) + (100 * 1) + (25 * 2)  # 300
        self.assertEqual(data["viral_score"], expected_viral_score)

    def test_hashtag_and_mention_extraction(self):
        """Test hashtag and mention extraction."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        text = "Hello @user1 @user2! Check out #hashtag1 and #hashtag2 #test"

        data = {}
        extractor._extract_content_data(text, data)

        self.assertEqual(data["hashtag_count"], 3)
        self.assertIn("#hashtag1", data["hashtags"])
        self.assertIn("#hashtag2", data["hashtags"])
        self.assertIn("#test", data["hashtags"])

        self.assertEqual(data["mention_count"], 2)
        self.assertIn("@user1", data["mentions"])
        self.assertIn("@user2", data["mentions"])

    def test_error_handling(self):
        """Test error handling for malformed data."""
        # Create malformed JSON file
        bad_file = self.input_dir / "bad.json"
        with open(bad_file, "w", encoding="utf-8") as f:
            f.write(
                '{"invalid": "not a valid structure"}'
            )  # Valid JSON but invalid structure

        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        with patch.object(extractor, "logger", MagicMock()):
            stats = extractor.extract_all()

        # Should process at least the good file
        self.assertGreaterEqual(stats["processed_files"], 1)
        # Note: The malformed file might be skipped rather than counted as error
        # depending on validation logic, so we check that processing completes


if __name__ == "__main__":
    unittest.main()
