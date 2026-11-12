#!/usr/bin/env python3
"""
Command-line interface for Twitter data extraction.

Simple CLI script for running the Twitter data extractor with various options.
"""

import argparse
import sys
from pathlib import Path

# Add the repository root to the path so the `src` package imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.analyzer import VideoMisuseAnalyzer  # noqa: E402
from src.parser import TwitterDataExtractor  # noqa: E402
from src.utils import format_time_duration  # noqa: E402


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Twitter HTML Parser & Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic extraction
  python extract_tweets.py --input downloads --output parsed

  # With consolidated file
  python extract_tweets.py --input downloads --output parsed --consolidated

  # Analyze video misuse after extraction
  python extract_tweets.py --input downloads --output parsed --analyze-misuse
        """,
    )

    # Input/Output options
    parser.add_argument(
        "--input",
        "--input-dir",
        "-i",
        default="downloads",
        help="Input directory containing Twitter export JSON files (default: downloads)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="parsed",
        help="Output directory for extracted data (default: parsed)",
    )
    parser.add_argument(
        "--reports", default="reports", help="Reports directory (default: reports)"
    )

    # Processing options
    parser.add_argument(
        "--consolidated",
        "-c",
        action="store_true",
        help="Create consolidated output file with all tweets",
    )
    parser.add_argument(
        "--analyze-misuse",
        action="store_true",
        help="Run video misuse analysis after extraction",
    )

    # Logging options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress most output"
    )

    args = parser.parse_args()

    # Determine log level
    if args.quiet:
        import logging

        log_level = logging.WARNING
    elif args.verbose:
        import logging

        log_level = logging.DEBUG
    else:
        import logging

        log_level = logging.INFO

    try:
        # Initialize extractor
        print("🚀 Twitter データ抽出・分析ツール")
        print("=" * 50)

        extractor = TwitterDataExtractor(
            input_dir=args.input,
            output_dir=args.output,
            reports_dir=args.reports,
            create_consolidated=args.consolidated,
            log_level=log_level,
        )

        # Run extraction
        print(f"📂 入力: {args.input}")
        print(f"📂 出力: {args.output}")
        print(f"📊 統合ファイル: {'有効' if args.consolidated else '無効'}")
        print()

        stats = extractor.extract_all()

        if stats:
            # Print summary
            duration = stats.get("processing_duration", 0)
            success_rate = (
                (stats["successful_extractions"] / stats["total_tweets"] * 100)
                if stats["total_tweets"] > 0
                else 0
            )

            print("\n" + "=" * 50)
            print("✅ 処理完了統計")
            print("=" * 50)
            print(
                f"📁 処理ファイル数: {stats['processed_files']:,}/{stats['total_files']:,}"
            )
            print(f"📄 総ツイート数: {stats['total_tweets']:,}")
            print(f"✅ 成功抽出数: {stats['successful_extractions']:,}")
            print(f"❌ エラー数: {stats['error_count']:,}")
            print(f"📈 成功率: {success_rate:.1f}%")
            print(f"⏱️  処理時間: {format_time_duration(duration)}")

            # Video misuse statistics
            if stats["videos_found"] > 0:
                video_misuse_rate = (
                    stats["video_misuse_detected"] / stats["videos_found"] * 100
                )
                print(f"\n🎥 動画関連統計:")
                print(f"   動画付きツイート: {stats['videos_found']:,}")
                print(f"   無断使用検出: {stats['video_misuse_detected']:,}")
                print(f"   無断使用率: {video_misuse_rate:.1f}%")

        # Run video misuse analysis if requested
        if args.analyze_misuse:
            print(f"\n🔍 動画無断使用分析を開始...")

            analyzer = VideoMisuseAnalyzer(
                input_dir=args.output,
                output_dir="video_misuse_analysis",
                log_level=log_level,
            )

            analysis_results = analyzer.analyze_all()
            print("✅ 動画無断使用分析完了")

            # Show analysis summary
            if analysis_results:
                print(f"📊 分析結果ファイル:")
                for result_type, file_path in analysis_results.items():
                    print(f"   {result_type}: {file_path}")

        print(f"\n🎉 全処理完了!")

    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによって処理が中断されました")
        return 1
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
