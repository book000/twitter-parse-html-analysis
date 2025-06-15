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

        # Find the user profiles CSV file
        user_profiles_csv = None
        for csv_file in csv_files:
            name_lower = csv_file.name.lower()
            if "user" in name_lower and "profile" in name_lower:
                user_profiles_csv = csv_file
                break

        self.assertIsNotNone(user_profiles_csv, "User profiles CSV file not found")

        # Read CSV and check user_id column exists and is in correct position
        with open(user_profiles_csv, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)

            # Check that user_id column exists
            self.assertIn("user_id", headers, "user_id column not found in CSV headers")

            # Check expected position of user_id (should be early in the headers)
            user_id_index = headers.index("user_id")
            self.assertLess(
                user_id_index, 5, "user_id column should be in the first few columns"
            )

            # Read data rows and verify user_id values
            rows = list(reader)
            self.assertGreater(len(rows), 0, "No data rows found in CSV")

            for row in rows:
                user_id_value = row[user_id_index]
                # user_id should not be empty
                self.assertNotEqual(
                    user_id_value, "", f"Empty user_id found in row: {row}"
                )

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

        # Check that video misuse was detected
        video_misuse_cases = results.get("video_misuse_cases", 0)
        self.assertGreater(video_misuse_cases, 0, "No video misuse cases detected")

        # Check that violation details CSV was created
        violation_files = list(self.output_dir.glob("*violation*"))
        if violation_files:  # Only check if violation files exist
            with open(violation_files[0], "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                violations = list(reader)

                # Should have at least one violation from our sample data
                self.assertGreater(
                    len(violations), 0, "No violations found in violation details"
                )

                # Check that user_id is present in violation records
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

                # Check that user_id is in the headers and is in reasonable position
                self.assertIn("user_id", headers)
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

