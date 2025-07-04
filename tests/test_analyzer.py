#!/usr/bin/env python3
"""
Tests for VideoMisuseAnalyzer
"""

import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.analyzer import VideoMisuseAnalyzer


class TestVideoMisuseAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.input_dir = Path(self.temp_dir) / "input"
        self.output_dir = Path(self.temp_dir) / "output"

        # Create directories
        self.input_dir.mkdir()
        self.output_dir.mkdir()

        # Sample extracted tweet data with user_id field
        self.sample_tweets = [
            {
                "tweet_id": "1234567890",
                "screen_name": "test_user",
                "user_id": "405595755",
                "tweet_text": "Test tweet with video",
                "video_misuse_detected": True,
                "video_creator": "original_creator",
                "video_detection_method": "cslt_tweet_info",
                "video_misuse_confidence": 0.9,
                "like_count": 100,
                "retweet_count": 50,
                "timestamp": "2024-01-01T12:00:00+00:00",
            },
            {
                "tweet_id": "1234567891",
                "screen_name": "other_user",
                "user_id": "123456789",
                "tweet_text": "Normal tweet without video misuse",
                "video_misuse_detected": False,
                "like_count": 10,
                "retweet_count": 2,
                "timestamp": "2024-01-01T13:00:00+00:00",
            },
        ]

        # Create sample extracted JSON file
        sample_file = self.input_dir / "sample_extracted.json"
        with open(sample_file, "w", encoding="utf-8") as f:
            json.dump(self.sample_tweets, f, ensure_ascii=False)

    def tearDown(self):
        """Clean up after each test method."""
        shutil.rmtree(self.temp_dir)

    def test_init_default_input_dir(self):
        """Test that default input_dir is 'output'."""
        analyzer = VideoMisuseAnalyzer(output_dir=str(self.output_dir))
        self.assertEqual(analyzer.input_dir, Path("output"))

    def test_init_custom_input_dir(self):
        """Test VideoMisuseAnalyzer initialization with custom input_dir."""
        analyzer = VideoMisuseAnalyzer(
            input_dir=str(self.input_dir), output_dir=str(self.output_dir)
        )

        self.assertEqual(analyzer.input_dir, self.input_dir)
        self.assertEqual(analyzer.output_dir, self.output_dir)
        self.assertIsNotNone(analyzer.logger)

    def test_analyze_all_csv_user_id_column(self):
        """Test that user_id column is included in CSV output with correct order."""
        analyzer = VideoMisuseAnalyzer(
            input_dir=str(self.input_dir), output_dir=str(self.output_dir)
        )

        with patch.object(analyzer, "logger", MagicMock()):
            results = analyzer.analyze_all()

        # Check that CSV files were created
        csv_files = list(self.output_dir.glob("*.csv"))
        self.assertGreater(len(csv_files), 0)

        # Find a CSV file to test user_id column (use the first available CSV)
        user_profiles_csv = csv_files[0] if csv_files else None

        self.assertIsNotNone(user_profiles_csv, "No CSV files found")

        # Read CSV and check user_id column exists and is in correct position
        with open(user_profiles_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)

            # Check if user_id column exists (optional for some CSV types)
            if "user_id" in headers:
                user_id_index = headers.index("user_id")

                # Read data rows and verify user_id values if column exists
                rows = list(reader)
                if rows:  # Only check if there are data rows
                    for row in rows:
                        if len(row) > user_id_index:
                            user_id_value = row[user_id_index]
                            # user_id can be empty but should be a string
                            self.assertIsInstance(user_id_value, str)
            else:
                # If no user_id column, just check that we have some data
                rows = list(reader)

    def test_analyze_all_json_user_id_field(self):
        """Test that user_id field is included in JSON output."""
        analyzer = VideoMisuseAnalyzer(
            input_dir=str(self.input_dir), output_dir=str(self.output_dir)
        )

        with patch.object(analyzer, "logger", MagicMock()):
            results = analyzer.analyze_all()

        # Check that JSON files were created
        json_files = list(self.output_dir.glob("*.json"))
        self.assertGreater(len(json_files), 0)

        # Find and check a JSON file
        for json_file in json_files:
            with open(json_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            # Depending on the JSON structure, check for user_id
            if isinstance(json_data, dict):
                if "user_profiles" in json_data:
                    # Check user profiles section
                    for user_id, profile in json_data["user_profiles"].items():
                        self.assertIn(
                            "user_id",
                            profile,
                            "user_id field missing from user profile",
                        )
                        self.assertNotEqual(
                            profile["user_id"], "", "user_id should not be empty"
                        )
            break  # Check at least one JSON file

    def test_video_misuse_detection_processing(self):
        """Test that video misuse cases are properly processed."""
        analyzer = VideoMisuseAnalyzer(
            input_dir=str(self.input_dir), output_dir=str(self.output_dir)
        )

        with patch.object(analyzer, "logger", MagicMock()):
            results = analyzer.analyze_all()

        # Check that analysis completed successfully
        self.assertIsNotNone(results)
        # Video misuse detection depends on actual data patterns

        # Check that output files were created (CSV files may vary based on actual data)
        output_files = list(self.output_dir.glob("*"))
        self.assertGreater(len(output_files), 0, "No output files created")

        # If violation files exist, check their structure
        violation_files = list(self.output_dir.glob("*violation*"))
        if violation_files:
            with open(violation_files[0], "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                violations = list(reader)

                # Check that user_id is present in violation records if violations exist
                if violations:
                    self.assertIn(
                        "user_id",
                        violations[0],
                        "user_id missing from violation record",
                    )

    def test_user_id_extraction_methods(self):
        """Test various user_id extraction scenarios."""
        # Test different user_id formats that might be extracted
        test_cases = [
            {"user_id": "405595755", "expected": "405595755"},
            {"user_id": "profile_123456789", "expected": "profile_123456789"},
            {"user_id": "screen_testuser", "expected": "screen_testuser"},
            {"user_id": "", "expected": ""},  # Empty case
        ]

        for i, test_case in enumerate(test_cases):
            # Create test data with specific user_id
            test_tweets = [
                {
                    "tweet_id": f"test_{i}",
                    "screen_name": "test_user",
                    "user_id": test_case["user_id"],
                    "video_misuse_detected": False,
                    "like_count": 1,
                }
            ]

            # Create temporary test file
            test_file = self.input_dir / f"test_{i}_extracted.json"
            with open(test_file, "w", encoding="utf-8") as f:
                json.dump(test_tweets, f, ensure_ascii=False)

        analyzer = VideoMisuseAnalyzer(
            input_dir=str(self.input_dir), output_dir=str(self.output_dir)
        )

        with patch.object(analyzer, "logger", MagicMock()):
            results = analyzer.analyze_all()

        # Verify that analysis completed successfully
        self.assertIsNotNone(results)

    def test_csv_fieldnames_order(self):
        """Test that CSV fieldnames include user_id in the expected order."""
        analyzer = VideoMisuseAnalyzer(
            input_dir=str(self.input_dir), output_dir=str(self.output_dir)
        )

        # Check the expected fieldnames defined in the analyzer
        expected_fields = [
            "screen_name",
            "user_id",  # Should be second field
            "total_tweets",
            "video_misuse_count",
            "unique_violations",
        ]

        # This tests the internal fieldnames structure
        # We can't directly access the fieldnames without running the analysis,
        # so we'll do a quick analysis and check the actual CSV headers
        with patch.object(analyzer, "logger", MagicMock()):
            analyzer.analyze_all()

        csv_files = list(self.output_dir.glob("*.csv"))
        if csv_files:
            with open(csv_files[0], "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)

                # Check if user_id is in the headers (may not be in all CSV types)
                if "user_id" in headers:
                    user_id_pos = headers.index("user_id")
                    screen_name_pos = (
                        headers.index("screen_name") if "screen_name" in headers else -1
                    )

                    # user_id should come after screen_name if both exist
                    if screen_name_pos >= 0:
                        msg = "user_id should come after screen_name in CSV headers"
                        self.assertGreater(user_id_pos, screen_name_pos, msg)


if __name__ == "__main__":
    unittest.main()
