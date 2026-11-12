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
from src.utils import safe_json_load as real_safe_json_load


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
        # Check that user_id field is present (may be empty for this simple test)
        self.assertIn("user_id", data)

    def test_user_id_extraction_follow_button(self):
        """Test user_id extraction from follow button data-testid."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        from bs4 import BeautifulSoup

        # Test follow button pattern
        html = """
        <div>
            <button data-testid="405595755-follow">Follow</button>
            <img src="https://pbs.twimg.com/profile_images/123/test.jpg" />
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        data = {"extraction_errors": []}
        tweet = {"screenName": "testuser"}

        extractor._extract_user_information(soup, tweet, data)

        self.assertEqual(data["user_id"], "405595755")

    def test_user_id_extraction_unfollow_button(self):
        """Test user_id extraction from unfollow button data-testid."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        from bs4 import BeautifulSoup

        # Test unfollow button pattern
        html = """
        <div>
            <button data-testid="123456789-unfollow">Unfollow</button>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        data = {"extraction_errors": []}
        tweet = {"screenName": "testuser"}

        extractor._extract_user_information(soup, tweet, data)

        self.assertEqual(data["user_id"], "123456789")

    def test_user_id_extraction_block_button(self):
        """Test user_id extraction from block button data-testid."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        from bs4 import BeautifulSoup

        # Test block button pattern
        html = """
        <div>
            <button data-testid="987654321-block">Block</button>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        data = {"extraction_errors": []}
        tweet = {"screenName": "testuser"}

        extractor._extract_user_information(soup, tweet, data)

        self.assertEqual(data["user_id"], "987654321")

    def test_user_id_extraction_unblock_button(self):
        """Test user_id extraction from unblock button data-testid."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        from bs4 import BeautifulSoup

        # Test unblock button pattern
        html = """
        <div>
            <button data-testid="555666777-unblock">Unblock</button>
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        data = {"extraction_errors": []}
        tweet = {"screenName": "testuser"}

        extractor._extract_user_information(soup, tweet, data)

        self.assertEqual(data["user_id"], "555666777")

    def test_user_id_extraction_no_buttons(self):
        """Test user_id extraction when no action buttons are present (should be empty)."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

        from bs4 import BeautifulSoup

        # No user button patterns
        html = """
        <div>
            <span>No user ID patterns here</span>
            <img src="https://pbs.twimg.com/profile_images/123456789/test.jpg" />
        </div>
        """
        soup = BeautifulSoup(html, "html.parser")

        data = {"extraction_errors": []}
        tweet = {"screenName": "testuser"}

        extractor._extract_user_information(soup, tweet, data)

        # Should be empty string when no buttons found
        self.assertEqual(data["user_id"], "")
        # Should have error message
        self.assertIn("No user_id found in HTML", data["extraction_errors"][0])

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

        self.assertEqual(stats["processed_files"], 1)
        self.assertEqual(stats["error_count"], 1)

    def _run_extract_all(self):
        """Run extract_all with a silenced logger and return its stats."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )
        with patch.object(extractor, "logger", MagicMock()):
            return extractor.extract_all()

    def _load_single_error_report(self):
        """Return the entries of the only error report in the reports dir."""
        report_files = list(self.reports_dir.glob("error_report_*.json"))
        self.assertEqual(len(report_files), 1)
        with open(report_files[0], "r", encoding="utf-8") as f:
            return json.load(f)

    def test_invalid_json_file_is_reported(self):
        """A file with invalid JSON is counted and listed in the error report."""
        (self.input_dir / "broken.json").write_text("{not json", encoding="utf-8")

        stats = self._run_extract_all()

        self.assertEqual(stats["processed_files"], 1)
        self.assertEqual(stats["error_count"], 1)
        entries = self._load_single_error_report()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["file"], "broken.json")

    def test_invalid_structure_file_is_reported(self):
        """A file without a data list is counted and listed in the error report."""
        (self.input_dir / "bad.json").write_text('{"invalid": 1}', encoding="utf-8")

        stats = self._run_extract_all()

        self.assertEqual(stats["processed_files"], 1)
        self.assertEqual(stats["error_count"], 1)
        entries = self._load_single_error_report()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["file"], "bad.json")
        self.assertEqual(entries[0]["error"], "Invalid file structure: bad.json")

    def test_unreadable_file_is_reported(self):
        """A file that fails to read is counted and listed in the error report."""
        shutil.copy(self.input_dir / "sample.json", self.input_dir / "unreadable.json")

        def fail_for_unreadable(path, *args, **kwargs):
            if str(path).endswith("unreadable.json"):
                raise OSError("disk error")
            return real_safe_json_load(path, *args, **kwargs)

        with patch("src.parser.safe_json_load", side_effect=fail_for_unreadable):
            stats = self._run_extract_all()

        self.assertEqual(stats["processed_files"], 1)
        self.assertEqual(stats["error_count"], 1)
        entries = self._load_single_error_report()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["file"], "unreadable.json")
        self.assertEqual(entries[0]["error"], "disk error")

    def test_valid_files_only_write_no_error_report(self):
        """A run with only valid files has no errors and no error report."""
        stats = self._run_extract_all()

        self.assertEqual(stats["processed_files"], 1)
        self.assertEqual(stats["error_count"], 0)
        self.assertEqual(list(self.reports_dir.glob("error_report_*.json")), [])

    def _make_extractor(self):
        return TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )

    def test_individual_output_error_log_is_sanitized(self):
        """File names and exceptions in the output-error log must be sanitized."""
        extractor = self._make_extractor()
        mock_logger = MagicMock()
        with (
            patch.object(extractor, "logger", mock_logger),
            patch("src.parser.safe_file_path", side_effect=ValueError("boom\nFAKE")),
        ):
            extractor._output_individual_file([], Path("evil\nname.json"))

        mock_logger.error.assert_called_once_with(
            "Individual file output error evil name.json: boom FAKE"
        )

    def test_oversized_multibyte_html_truncated_by_bytes(self):
        """Oversized multibyte HTML is truncated to at most 100,000 bytes."""
        extractor = TwitterDataExtractor(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir),
            reports_dir=str(self.reports_dir),
        )
        # 3 bytes per char: 200,000 chars = 600,000 bytes (> 500,000 limit)
        tweet = {"tweetId": "1", "elementHtml": "<p>" + "あ" * 200000 + "</p>"}

        with patch(
            "src.parser.sanitize_html_content", side_effect=lambda h: h
        ) as sanitize:
            data = extractor._extract_comprehensive_tweet_data(tweet, "f.json", 0)

        truncated = sanitize.call_args[0][0]
        # "<p>" (3 bytes) + 33,332 three-byte chars; the char split at byte
        # 100,000 is dropped
        self.assertEqual(truncated, "<p>" + "あ" * 33332)
        self.assertEqual(len(truncated.encode("utf-8")), 99999)
        self.assertIn("HTML content too large, truncated", data["extraction_errors"])


if __name__ == "__main__":
    unittest.main()
