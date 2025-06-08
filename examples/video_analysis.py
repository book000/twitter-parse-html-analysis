#!/usr/bin/env python3
"""
Video misuse analysis example for twitter-parse-html-analysis

This example demonstrates how to analyze video misuse patterns
using the VideoMisuseAnalyzer.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.append(str(Path(__file__).parent.parent))

from src.analyzer import VideoMisuseAnalyzer
from src.parser import TwitterDataExtractor


def main():
    """Main video analysis example."""
    print("=== Video Misuse Analysis Example ===")

    # Step 1: Extract data with video analysis enabled
    print("Step 1: Extracting tweet data...")

    input_dir = "data"
    parsed_dir = "example_parsed"
    analysis_dir = "example_video_analysis"

    # Create directories
    Path(parsed_dir).mkdir(exist_ok=True)
    Path(analysis_dir).mkdir(exist_ok=True)

    # Extract tweets first
    extractor = TwitterDataExtractor(
        input_dir=input_dir, output_dir=parsed_dir, create_consolidated=False
    )

    stats = extractor.extract_all()
    print(
        f"Extraction completed: {stats['processed_files']} files, {stats['total_tweets']} tweets"
    )

    # Step 2: Analyze video misuse
    print("\nStep 2: Analyzing video misuse patterns...")

    analyzer = VideoMisuseAnalyzer(input_dir=parsed_dir, output_dir=analysis_dir)

    results = analyzer.analyze_all()

    # Step 3: Display results
    print("\n=== Analysis Results ===")

    # Show generated files
    output_files = list(Path(analysis_dir).glob("*"))
    if output_files:
        print("Generated analysis files:")
        for file_path in sorted(output_files):
            if file_path.is_file():
                file_size = file_path.stat().st_size
                print(f"  {file_path.name} ({file_size:,} bytes)")

    # Load and display summary statistics if available
    summary_files = list(Path(analysis_dir).glob("summary_statistics_*.json"))
    if summary_files:
        print("\n=== Summary Statistics ===")
        with open(summary_files[0], "r", encoding="utf-8") as f:
            summary = json.load(f)

        overview = summary.get("overview", {})
        print(
            f"Total violations detected: {overview.get('total_violations_detected', 0)}"
        )
        print(f"Total violating users: {overview.get('total_violating_users', 0)}")
        print(
            f"Total victimized creators: {overview.get('total_victimized_creators', 0)}"
        )
        print(
            f"Average violations per user: {overview.get('avg_violations_per_user', 0)}"
        )

        # Detection methods
        detection_methods = summary.get("detection_methods", {})
        if detection_methods.get("distribution"):
            print("\nDetection method distribution:")
            for method, count in detection_methods["distribution"].items():
                print(f"  {method}: {count}")

        # Top victimized creators
        top_creators = summary.get("top_victimized_creators", [])
        if top_creators:
            print("\nTop victimized creators:")
            for creator, count in top_creators[:5]:
                print(f"  {creator}: {count} violations")

    # Load and display user rankings if available
    ranking_files = list(Path(analysis_dir).glob("user_rankings_*.json"))
    if ranking_files:
        print("\n=== Top Violators ===")
        with open(ranking_files[0], "r", encoding="utf-8") as f:
            rankings = json.load(f)

        top_violators = rankings.get("rankings", {}).get("by_violation_count", [])
        if top_violators:
            print("Users with most violations:")
            for i, user in enumerate(top_violators[:5], 1):
                print(
                    f"  {i}. @{user['screen_name']}: {user['violation_count']} violations, "
                    f"{user['total_engagement']} total engagement"
                )


def demonstrate_pattern_analysis():
    """Demonstrate pattern analysis capabilities."""
    print("\n=== Pattern Analysis Example ===")

    # This would typically analyze real data, but for demonstration
    # we'll show the types of patterns that can be detected

    patterns = {
        "repeat_offenders": "Users with 3+ violations",
        "high_engagement_violators": "Users with avg engagement > 1000",
        "multi_creator_abusers": "Users who abuse multiple creators",
        "temporal_patterns": "Time-based violation patterns",
    }

    print("Available analysis patterns:")
    for pattern, description in patterns.items():
        print(f"  • {pattern}: {description}")

    print("\nTemporal analysis can identify:")
    print("  • Peak violation hours")
    print("  • Daily distribution patterns")
    print("  • Date ranges of activity")
    print("  • Violation frequency trends")

    print("\nUser behavior analysis includes:")
    print("  • Violation frequency per user")
    print("  • Engagement patterns on violated content")
    print("  • Detection method preferences")
    print("  • Diversity of creators targeted")


def create_sample_video_data():
    """Create sample data with video misuse for demonstration."""
    print("\n=== Creating Sample Video Data ===")

    sample_data = [
        {
            "tweet_id": "sample_video_1",
            "screen_name": "user1",
            "display_name": "User One",
            "has_videos": True,
            "video_misuse_detected": True,
            "video_creator": "original_creator1",
            "video_detection_method": "cslt_tweet_info",
            "video_misuse_confidence": 0.9,
            "total_engagement": 500,
            "like_count": 300,
            "retweet_count": 150,
            "reply_count": 50,
            "timestamp": "2024-01-01T12:00:00+00:00",
        },
        {
            "tweet_id": "sample_video_2",
            "screen_name": "user1",
            "display_name": "User One",
            "has_videos": True,
            "video_misuse_detected": True,
            "video_creator": "original_creator2",
            "video_detection_method": "html_attribution",
            "video_misuse_confidence": 0.8,
            "total_engagement": 750,
            "like_count": 400,
            "retweet_count": 250,
            "reply_count": 100,
            "timestamp": "2024-01-02T15:30:00+00:00",
        },
    ]

    # Save sample data
    sample_file = Path("example_parsed") / "sample_video_extracted.json"
    Path("example_parsed").mkdir(exist_ok=True)

    with open(sample_file, "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)

    print(f"Sample video data created: {sample_file}")
    print(f"Contains {len(sample_data)} sample violations for demonstration")


if __name__ == "__main__":
    # Create sample data first
    create_sample_video_data()

    # Run main analysis
    main()

    # Show pattern analysis capabilities
    demonstrate_pattern_analysis()

    print("\nVideo analysis example completed!")
    print("Check the 'example_video_analysis' directory for detailed results.")
