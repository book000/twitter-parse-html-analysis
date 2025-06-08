#!/usr/bin/env python3
"""
Basic usage example for twitter-parse-html-analysis

This example demonstrates how to use the TwitterDataExtractor to process
Twitter export JSON files and extract comprehensive data.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.append(str(Path(__file__).parent.parent))

from src.parser import TwitterDataExtractor


def main():
    """Main example function."""
    print("=== Twitter Parse HTML Analysis - Basic Usage Example ===")

    # Setup directories
    input_dir = "data"  # Directory containing sample data
    output_dir = "example_output"
    reports_dir = "example_reports"

    # Create output directories if they don't exist
    Path(output_dir).mkdir(exist_ok=True)
    Path(reports_dir).mkdir(exist_ok=True)

    # Initialize the extractor
    extractor = TwitterDataExtractor(
        input_dir=input_dir,
        output_dir=output_dir,
        reports_dir=reports_dir,
        create_consolidated=True,  # Create a single consolidated file
    )

    print(f"Processing files from: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Reports directory: {reports_dir}")
    print()

    # Run the extraction
    stats = extractor.extract_all()

    # Display results
    print("=== Extraction Results ===")
    print(f"Files processed: {stats['processed_files']}/{stats['total_files']}")
    print(f"Total tweets: {stats['total_tweets']}")
    print(f"Successful extractions: {stats['successful_extractions']}")
    print(f"Errors: {stats['error_count']}")

    if stats.get("processing_duration"):
        print(f"Processing time: {stats['processing_duration']:.2f} seconds")

    if stats.get("videos_found", 0) > 0:
        print(f"Videos found: {stats['videos_found']}")
        print(f"Video misuse detected: {stats['video_misuse_detected']}")

    print()

    # Show sample extracted data
    output_files = list(Path(output_dir).glob("*.json"))
    if output_files:
        print("=== Sample Extracted Data ===")
        with open(output_files[0], "r", encoding="utf-8") as f:
            sample_data = json.load(f)

        if sample_data:
            tweet = sample_data[0]
            print(f"Tweet ID: {tweet.get('tweet_id', 'N/A')}")
            print(f"User: @{tweet.get('screen_name', 'N/A')}")
            print(f"Display Name: {tweet.get('display_name', 'N/A')}")
            print(f"Text: {tweet.get('tweet_text', 'N/A')[:100]}...")
            print(
                f"Language: {tweet.get('language_detected', 'N/A')} "
                f"(confidence: {tweet.get('language_confidence', 0):.2f})"
            )
            print(f"Verified: {tweet.get('is_verified', False)}")
            print(
                f"Engagement: {tweet.get('total_engagement', 0)} "
                f"(likes: {tweet.get('like_count', 0)}, "
                f"retweets: {tweet.get('retweet_count', 0)})"
            )
            print(f"Data Quality Score: {tweet.get('data_quality_score', 0)}")

    print()
    print("=== Output Files ===")
    for output_file in sorted(Path(output_dir).glob("*.json")):
        file_size = output_file.stat().st_size
        print(f"  {output_file.name} ({file_size:,} bytes)")

    # Show reports
    report_files = list(Path(reports_dir).glob("*.json"))
    if report_files:
        print()
        print("=== Reports Generated ===")
        for report_file in sorted(report_files):
            file_size = report_file.stat().st_size
            print(f"  {report_file.name} ({file_size:,} bytes)")


def demonstrate_language_detection():
    """Demonstrate the language detection capabilities."""
    print("\n=== Language Detection Example ===")

    from src.language_detector import LanguageDetector

    detector = LanguageDetector()

    test_texts = [
        "これは日本語のテストです。ひらがなと漢字が含まれています。",
        "This is an English test sentence with multiple words.",
        "Hello world! こんにちは世界！ Mixed language content.",
        "🎉🎊 Emoji-heavy content! 🌟✨🎈",
        "안녕하세요. 한국어 테스트입니다.",
        "这是中文测试文本。",
    ]

    for i, text in enumerate(test_texts, 1):
        result = detector.detect_languages(text)
        print(f"{i}. Text: {text[:50]}...")
        print(
            f"   Language: {result['primary']} (confidence: {result['confidence']:.2f})"
        )

        # Show script breakdown for interesting cases
        scripts = result["script_analysis"]
        if scripts.get("hiragana", 0) > 0 or scripts.get("kanji", 0) > 0:
            print(
                f"   Scripts: Hiragana={scripts.get('hiragana', 0)}, "
                f"Katakana={scripts.get('katakana', 0)}, "
                f"Kanji={scripts.get('kanji', 0)}"
            )
        print()


if __name__ == "__main__":
    main()
    demonstrate_language_detection()

    print("Example completed successfully!")
    print("Check the 'example_output' and 'example_reports' directories for results.")
