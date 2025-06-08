#!/usr/bin/env python3
"""
Video Misuse Analysis and User Profiling

This module provides comprehensive analysis capabilities for video misuse
detection results and user behavior profiling.
"""

import csv
import json
import logging
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .utils import safe_json_load, sanitize_log_message


class VideoMisuseAnalyzer:
    """
    Analyzer for video misuse detection results with comprehensive user profiling
    and violation analysis capabilities.
    """

    def __init__(
        self,
        input_dir: str = "parsed",
        output_dir: str = "video_misuse_analysis",
        log_level: int = logging.INFO,
    ):
        """
        Initialize VideoMisuseAnalyzer.

        Args:
            input_dir: Directory containing parsed tweet JSON files
            output_dir: Directory for analysis output files
            log_level: Logging level
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

        # Setup logging
        self.logger = self._setup_logging(log_level)

        # Setup output directory
        self.output_dir.mkdir(exist_ok=True)

        # Analysis data storage
        self.video_misuse_data = []
        self.user_profiles = defaultdict(
            lambda: {
                "screen_name": "",
                "display_name": "",
                "violations": [],
                "total_violations": 0,
                "total_engagement": 0,
                "avg_engagement": 0,
                "max_engagement": 0,
                "detection_methods": set(),
                "video_creators_used": set(),
                "first_violation_date": None,
                "last_violation_date": None,
                "violation_frequency": 0,  # violations per day
            }
        )

        self.creator_victims = defaultdict(
            lambda: {
                "misuse_count": 0,
                "misusers": set(),
                "total_engagement_on_misuse": 0,
                "avg_engagement_per_misuse": 0,
            }
        )

    def _setup_logging(self, log_level: int) -> logging.Logger:
        """Setup logging configuration."""
        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(
                    self.output_dir / "video_misuse_analyzer.log", encoding="utf-8"
                ),
                logging.StreamHandler(),
            ],
        )
        return logging.getLogger(__name__)

    def analyze_all(self) -> Dict[str, Any]:
        """
        Perform comprehensive video misuse analysis.

        Returns:
            Dictionary containing analysis results and statistics
        """
        self.logger.info("=== 動画無断使用分析開始 ===")

        # Load and process data
        self._load_parsed_data()
        self._analyze_user_behaviors()
        self._analyze_creator_victims()

        # Generate outputs
        results = self._generate_all_outputs()

        self.logger.info("=== 動画無断使用分析完了 ===")
        return results

    def _load_parsed_data(self) -> None:
        """Load parsed tweet data from JSON files."""
        if not self.input_dir.exists():
            self.logger.error(f"入力ディレクトリが見つかりません: {self.input_dir}")
            return

        json_files = list(self.input_dir.glob("*_extracted.json"))
        if not json_files:
            self.logger.error("抽出済みJSONファイルが見つかりません")
            return

        self.logger.info(f"分析対象ファイル数: {len(json_files)}")

        total_tweets = 0
        video_tweets = 0
        misuse_tweets = 0

        for file_path in json_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    tweets = safe_json_load(f)

                for tweet in tweets:
                    total_tweets += 1

                    # Check for video content
                    if tweet.get("has_videos", False):
                        video_tweets += 1

                        # Check for video misuse
                        if tweet.get("video_misuse_detected", False):
                            misuse_tweets += 1
                            self.video_misuse_data.append(tweet)

            except Exception as e:
                self.logger.error(
                    f"ファイル読み込みエラー {sanitize_log_message(file_path.name)}: {sanitize_log_message(str(e))}"
                )

        self.logger.info(f"総ツイート数: {total_tweets:,}")
        self.logger.info(f"動画付きツイート数: {video_tweets:,}")
        self.logger.info(f"動画無断使用検出数: {misuse_tweets:,}")

        if video_tweets > 0:
            misuse_rate = (misuse_tweets / video_tweets) * 100
            self.logger.info(f"無断使用率: {misuse_rate:.2f}%")

    def _analyze_user_behaviors(self) -> None:
        """Analyze user behavior patterns for video misuse."""
        self.logger.info("ユーザー行動分析を開始")

        for tweet in self.video_misuse_data:
            screen_name = tweet.get("screen_name", "").lower()
            if not screen_name:
                continue

            profile = self.user_profiles[screen_name]

            # Basic profile info
            profile["screen_name"] = screen_name
            profile["display_name"] = tweet.get("display_name", "")

            # Violation details
            violation = {
                "tweet_id": tweet.get("tweet_id", ""),
                "video_creator": tweet.get("video_creator", ""),
                "detection_method": tweet.get("video_detection_method", ""),
                "confidence": tweet.get("video_misuse_confidence", 0),
                "timestamp": tweet.get("timestamp", ""),
                "engagement": tweet.get("total_engagement", 0),
                "like_count": tweet.get("like_count", 0),
                "retweet_count": tweet.get("retweet_count", 0),
                "reply_count": tweet.get("reply_count", 0),
            }

            profile["violations"].append(violation)
            profile["total_violations"] += 1

            # Engagement analysis
            engagement = tweet.get("total_engagement", 0)
            profile["total_engagement"] += engagement
            profile["max_engagement"] = max(profile["max_engagement"], engagement)

            # Detection methods
            method = tweet.get("video_detection_method", "")
            if method:
                profile["detection_methods"].add(method)

            # Video creators used
            creator = tweet.get("video_creator", "")
            if creator:
                profile["video_creators_used"].add(creator)

            # Timestamp analysis
            timestamp = tweet.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    if (
                        profile["first_violation_date"] is None
                        or dt < profile["first_violation_date"]
                    ):
                        profile["first_violation_date"] = dt
                    if (
                        profile["last_violation_date"] is None
                        or dt > profile["last_violation_date"]
                    ):
                        profile["last_violation_date"] = dt
                except:
                    pass

        # Calculate derived metrics
        for screen_name, profile in self.user_profiles.items():
            if profile["total_violations"] > 0:
                profile["avg_engagement"] = (
                    profile["total_engagement"] / profile["total_violations"]
                )

                # Calculate violation frequency
                if profile["first_violation_date"] and profile["last_violation_date"]:
                    time_span = (
                        profile["last_violation_date"] - profile["first_violation_date"]
                    ).days
                    if time_span > 0:
                        profile["violation_frequency"] = (
                            profile["total_violations"] / time_span
                        )
                    else:
                        profile["violation_frequency"] = profile[
                            "total_violations"
                        ]  # All in one day

        self.logger.info(f"分析完了: {len(self.user_profiles)} ユーザーを分析")

    def _analyze_creator_victims(self) -> None:
        """Analyze which creators are most victimized."""
        self.logger.info("被害クリエイター分析を開始")

        for tweet in self.video_misuse_data:
            creator = tweet.get("video_creator", "").strip()
            if not creator:
                continue

            victim_profile = self.creator_victims[creator]
            victim_profile["misuse_count"] += 1

            # Track misusers
            screen_name = tweet.get("screen_name", "").lower()
            if screen_name:
                victim_profile["misusers"].add(screen_name)

            # Engagement analysis
            engagement = tweet.get("total_engagement", 0)
            victim_profile["total_engagement_on_misuse"] += engagement

        # Calculate averages
        for creator, profile in self.creator_victims.items():
            if profile["misuse_count"] > 0:
                profile["avg_engagement_per_misuse"] = (
                    profile["total_engagement_on_misuse"] / profile["misuse_count"]
                )

        self.logger.info(
            f"被害分析完了: {len(self.creator_victims)} クリエイターを分析"
        )

    def _generate_all_outputs(self) -> Dict[str, Any]:
        """Generate all analysis output files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results = {}

        # 1. User violations list (CSV)
        results["users_csv"] = self._output_user_violations_csv(timestamp)

        # 2. Detailed violations (CSV)
        results["violations_csv"] = self._output_violation_details_csv(timestamp)

        # 3. User rankings (JSON)
        results["rankings_json"] = self._output_user_rankings_json(timestamp)

        # 4. Summary statistics (JSON)
        results["summary_json"] = self._output_summary_statistics_json(timestamp)

        # 5. Creator victims ranking (CSV)
        results["victims_csv"] = self._output_creator_victims_csv(timestamp)

        return results

    def _output_user_violations_csv(self, timestamp: str) -> Path:
        """Output user violations summary to CSV."""
        output_file = self.output_dir / f"video_misuse_users_{timestamp}.csv"

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "screen_name",
                "display_name",
                "violation_count",
                "total_engagement",
                "avg_engagement",
                "max_engagement",
                "detection_methods",
                "video_creators_used",
                "first_violation_date",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # Sort by violation count (descending)
            sorted_users = sorted(
                self.user_profiles.items(),
                key=lambda x: x[1]["total_violations"],
                reverse=True,
            )

            for screen_name, profile in sorted_users:
                if profile["total_violations"] > 0:
                    row = {
                        "screen_name": profile["screen_name"],
                        "display_name": profile["display_name"],
                        "violation_count": profile["total_violations"],
                        "total_engagement": profile["total_engagement"],
                        "avg_engagement": round(profile["avg_engagement"], 1),
                        "max_engagement": profile["max_engagement"],
                        "detection_methods": ", ".join(profile["detection_methods"]),
                        "video_creators_used": ", ".join(
                            list(profile["video_creators_used"])[:10]
                        ),  # Limit length
                        "first_violation_date": (
                            profile["first_violation_date"].isoformat()
                            if profile["first_violation_date"]
                            else ""
                        ),
                    }
                    writer.writerow(row)

        self.logger.info(f"ユーザー違反リスト出力完了: {output_file}")
        return output_file

    def _output_violation_details_csv(self, timestamp: str) -> Path:
        """Output detailed violation information to CSV."""
        output_file = self.output_dir / f"violation_details_{timestamp}.csv"

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "screen_name",
                "display_name",
                "tweet_id",
                "video_creator",
                "detection_method",
                "confidence",
                "timestamp",
                "total_engagement",
                "like_count",
                "retweet_count",
                "reply_count",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # Write all violations
            for screen_name, profile in self.user_profiles.items():
                for violation in profile["violations"]:
                    row = {
                        "screen_name": profile["screen_name"],
                        "display_name": profile["display_name"],
                        "tweet_id": violation["tweet_id"],
                        "video_creator": violation["video_creator"],
                        "detection_method": violation["detection_method"],
                        "confidence": violation["confidence"],
                        "timestamp": violation["timestamp"],
                        "total_engagement": violation["engagement"],
                        "like_count": violation["like_count"],
                        "retweet_count": violation["retweet_count"],
                        "reply_count": violation["reply_count"],
                    }
                    writer.writerow(row)

        self.logger.info(f"詳細違反リスト出力完了: {output_file}")
        return output_file

    def _output_user_rankings_json(self, timestamp: str) -> Path:
        """Output user rankings and analysis to JSON."""
        output_file = self.output_dir / f"user_rankings_{timestamp}.json"

        # Prepare rankings data
        rankings = {
            "by_violation_count": [],
            "by_total_engagement": [],
            "by_avg_engagement": [],
            "by_max_engagement": [],
            "by_creators_used": [],
        }

        # Convert user profiles to list format
        users_list = []
        for screen_name, profile in self.user_profiles.items():
            if profile["total_violations"] > 0:
                user_data = {
                    "screen_name": profile["screen_name"],
                    "display_name": profile["display_name"],
                    "violation_count": profile["total_violations"],
                    "total_engagement": profile["total_engagement"],
                    "avg_engagement": round(profile["avg_engagement"], 1),
                    "max_engagement": profile["max_engagement"],
                    "detection_methods": list(profile["detection_methods"]),
                    "video_creators_used": list(profile["video_creators_used"]),
                    "creators_count": len(profile["video_creators_used"]),
                    "violation_frequency": round(profile["violation_frequency"], 3),
                    "first_violation_date": (
                        profile["first_violation_date"].isoformat()
                        if profile["first_violation_date"]
                        else None
                    ),
                }
                users_list.append(user_data)

        # Generate rankings
        rankings["by_violation_count"] = sorted(
            users_list, key=lambda x: x["violation_count"], reverse=True
        )[:20]

        rankings["by_total_engagement"] = sorted(
            users_list, key=lambda x: x["total_engagement"], reverse=True
        )[:20]

        rankings["by_avg_engagement"] = sorted(
            users_list, key=lambda x: x["avg_engagement"], reverse=True
        )[:20]

        rankings["by_max_engagement"] = sorted(
            users_list, key=lambda x: x["max_engagement"], reverse=True
        )[:20]

        rankings["by_creators_used"] = sorted(
            users_list, key=lambda x: x["creators_count"], reverse=True
        )[:20]

        # Add metadata
        analysis_data = {
            "generated_at": datetime.now().isoformat(),
            "total_violating_users": len(users_list),
            "total_violations": sum(user["violation_count"] for user in users_list),
            "rankings": rankings,
            "statistics": {
                "avg_violations_per_user": (
                    round(
                        sum(user["violation_count"] for user in users_list)
                        / len(users_list),
                        2,
                    )
                    if users_list
                    else 0
                ),
                "most_violated_user": (
                    users_list[0]["screen_name"] if users_list else None
                ),
                "highest_engagement_violation": max(
                    (user["max_engagement"] for user in users_list), default=0
                ),
            },
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"ユーザーランキング出力完了: {output_file}")
        return output_file

    def _output_summary_statistics_json(self, timestamp: str) -> Path:
        """Output summary statistics to JSON."""
        output_file = self.output_dir / f"summary_statistics_{timestamp}.json"

        # Calculate comprehensive statistics
        total_violations = len(self.video_misuse_data)
        total_users = len(
            [p for p in self.user_profiles.values() if p["total_violations"] > 0]
        )

        if total_users > 0:
            violation_counts = [
                p["total_violations"]
                for p in self.user_profiles.values()
                if p["total_violations"] > 0
            ]
            avg_violations_per_user = sum(violation_counts) / len(violation_counts)
            max_violations_per_user = max(violation_counts)

            engagement_totals = [
                p["total_engagement"]
                for p in self.user_profiles.values()
                if p["total_violations"] > 0
            ]
            avg_engagement_per_user = sum(engagement_totals) / len(engagement_totals)

            # Detection method distribution
            method_counts = Counter()
            for tweet in self.video_misuse_data:
                method = tweet.get("video_detection_method", "unknown")
                method_counts[method] += 1

            # Creator analysis
            creator_counts = Counter()
            for tweet in self.video_misuse_data:
                creator = tweet.get("video_creator", "").strip()
                if creator:
                    creator_counts[creator] += 1
        else:
            avg_violations_per_user = 0
            max_violations_per_user = 0
            avg_engagement_per_user = 0
            method_counts = Counter()
            creator_counts = Counter()

        summary = {
            "generated_at": datetime.now().isoformat(),
            "overview": {
                "total_violations_detected": total_violations,
                "total_violating_users": total_users,
                "total_victimized_creators": len(self.creator_victims),
                "avg_violations_per_user": round(avg_violations_per_user, 2),
                "max_violations_per_user": max_violations_per_user,
                "avg_engagement_per_user": round(avg_engagement_per_user, 1),
            },
            "detection_methods": {
                "distribution": dict(method_counts),
                "most_common_method": (
                    method_counts.most_common(1)[0] if method_counts else None
                ),
            },
            "top_victimized_creators": creator_counts.most_common(10),
            "user_behavior_patterns": self._analyze_user_patterns(),
            "temporal_analysis": self._analyze_temporal_patterns(),
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        self.logger.info(f"統計サマリー出力完了: {output_file}")
        return output_file

    def _output_creator_victims_csv(self, timestamp: str) -> Path:
        """Output creator victims ranking to CSV."""
        output_file = self.output_dir / f"victim_creators_ranking_{timestamp}.csv"

        with open(output_file, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["video_creator", "misuse_count", "percentage"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            # Sort by misuse count
            total_misuses = sum(
                profile["misuse_count"] for profile in self.creator_victims.values()
            )
            sorted_victims = sorted(
                self.creator_victims.items(),
                key=lambda x: x[1]["misuse_count"],
                reverse=True,
            )

            for creator, profile in sorted_victims:
                percentage = (
                    (profile["misuse_count"] / total_misuses * 100)
                    if total_misuses > 0
                    else 0
                )
                row = {
                    "video_creator": creator,
                    "misuse_count": profile["misuse_count"],
                    "percentage": f"{percentage:.2f}%",
                }
                writer.writerow(row)

        self.logger.info(f"被害クリエイターランキング出力完了: {output_file}")
        return output_file

    def _analyze_user_patterns(self) -> Dict[str, Any]:
        """Analyze user behavior patterns."""
        patterns = {
            "repeat_offenders": 0,  # Users with 3+ violations
            "high_engagement_violators": 0,  # Users with avg engagement > 1000
            "multi_creator_abusers": 0,  # Users who abuse multiple creators
            "method_preferences": Counter(),
        }

        for profile in self.user_profiles.values():
            if profile["total_violations"] == 0:
                continue

            if profile["total_violations"] >= 3:
                patterns["repeat_offenders"] += 1

            if profile["avg_engagement"] > 1000:
                patterns["high_engagement_violators"] += 1

            if len(profile["video_creators_used"]) >= 3:
                patterns["multi_creator_abusers"] += 1

            # Method preferences
            for method in profile["detection_methods"]:
                patterns["method_preferences"][method] += 1

        return {
            "repeat_offenders_count": patterns["repeat_offenders"],
            "high_engagement_violators_count": patterns["high_engagement_violators"],
            "multi_creator_abusers_count": patterns["multi_creator_abusers"],
            "detection_method_preferences": dict(patterns["method_preferences"]),
        }

    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in violations."""
        dates = []
        hours = []

        for tweet in self.video_misuse_data:
            timestamp = tweet.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    dates.append(dt.date())
                    hours.append(dt.hour)
                except:
                    pass

        if not dates:
            return {"daily_distribution": {}, "hourly_distribution": {}}

        # Daily distribution
        date_counts = Counter(dates)
        daily_dist = {str(date): count for date, count in date_counts.most_common(10)}

        # Hourly distribution
        hour_counts = Counter(hours)
        hourly_dist = {
            f"{hour:02d}:00": count for hour, count in sorted(hour_counts.items())
        }

        return {
            "daily_distribution": daily_dist,
            "hourly_distribution": hourly_dist,
            "peak_violation_hour": (
                hour_counts.most_common(1)[0][0] if hour_counts else None
            ),
            "date_range": {
                "earliest": str(min(dates)),
                "latest": str(max(dates)),
                "span_days": (max(dates) - min(dates)).days,
            },
        }
