#!/usr/bin/env python3
"""
Advanced Language Detection System

High-precision multi-language detection with support for:
- Japanese (hiragana, katakana, kanji)
- English
- Chinese (simplified/traditional)
- Korean
- Arabic
- Russian
- Mixed language content
- Emoji-heavy content
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional


class LanguageDetector:
    """
    Advanced language detection system with high precision for multiple languages
    and detailed script analysis.
    """

    def __init__(self):
        """Initialize language detector with patterns and rules."""
        self.japanese_particles = [
            "は",
            "が",
            "を",
            "に",
            "へ",
            "で",
            "と",
            "から",
            "まで",
            "より",
            "の",
            "も",
            "しか",
            "だけ",
        ]

        self.japanese_copula = ["です", "である", "だ", "であり", "ます", "でしょう"]

        self.english_articles = ["the", "a", "an"]
        self.english_prepositions = ["in", "on", "at", "to", "for", "of", "with", "by"]

    def detect_languages(self, text: str) -> Dict[str, Any]:
        """
        Detect languages in the given text with detailed analysis.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary containing:
            - primary: Primary detected language
            - confidence: Confidence score (0.0 - 1.0)
            - details: Detailed analysis results
            - script_analysis: Character script breakdown
            - linguistic_features: Language-specific features
        """
        try:
            if not text or len(text.strip()) == 0:
                return {
                    "primary": "unknown",
                    "confidence": 0,
                    "details": {},
                    "script_analysis": {},
                    "linguistic_features": {},
                }

            # Limit input text length to prevent DoS
            if len(text) > 10000:
                text = text[:10000]

            # Preprocess text
            clean_text = text.strip()
            total_chars = len(clean_text)

            # Analyze different aspects
            script_analysis = self._analyze_character_scripts(clean_text)
            word_analysis = self._analyze_words_and_patterns(clean_text)
            linguistic_features = self._extract_linguistic_features(clean_text)

            # Calculate language scores
            language_scores = self._calculate_language_scores(
                script_analysis, word_analysis, linguistic_features
            )

            # Determine primary language
            primary_language = self._determine_primary_language(
                language_scores, script_analysis
            )
            confidence = self._calculate_confidence(language_scores, primary_language)

            return {
                "primary": primary_language,
                "confidence": confidence,
                "details": {
                    "total_chars": total_chars,
                    "language_scores": language_scores,
                    "top_candidates": sorted(
                        language_scores.items(), key=lambda x: x[1], reverse=True
                    )[:3],
                },
                "script_analysis": script_analysis,
                "linguistic_features": linguistic_features,
            }

        except Exception as e:
            return {
                "primary": "unknown",
                "confidence": 0,
                "details": {"error": str(e)},
                "script_analysis": {},
                "linguistic_features": {},
            }

    def _analyze_character_scripts(self, text: str) -> Dict[str, Any]:
        """Analyze character scripts in the text."""
        scripts = {
            "hiragana": 0,
            "katakana": 0,
            "kanji": 0,
            "latin": 0,
            "cyrillic": 0,
            "arabic": 0,
            "korean": 0,
            "chinese_simplified": 0,
            "chinese_traditional": 0,
            "emoji": 0,
            "numbers": 0,
            "punctuation": 0,
            "symbols": 0,
        }

        total_chars = len(text)

        for char in text:
            code_point = ord(char)

            # Japanese characters
            if 0x3040 <= code_point <= 0x309F:  # Hiragana
                scripts["hiragana"] += 1
            elif 0x30A0 <= code_point <= 0x30FF:  # Katakana
                scripts["katakana"] += 1
            elif 0x4E00 <= code_point <= 0x9FAF:  # CJK Unified Ideographs
                scripts["kanji"] += 1

            # Latin characters
            elif (0x0041 <= code_point <= 0x005A) or (0x0061 <= code_point <= 0x007A):
                scripts["latin"] += 1

            # Cyrillic characters
            elif 0x0400 <= code_point <= 0x04FF:
                scripts["cyrillic"] += 1

            # Arabic characters
            elif 0x0600 <= code_point <= 0x06FF:
                scripts["arabic"] += 1

            # Korean characters (Hangul)
            elif 0xAC00 <= code_point <= 0xD7AF:
                scripts["korean"] += 1

            # Emoji
            elif self._is_emoji_char(char):
                scripts["emoji"] += 1

            # Numbers
            elif char.isdigit():
                scripts["numbers"] += 1

            # Punctuation
            elif char in '。、！？.,!?;:「」()[]{}""' "":
                scripts["punctuation"] += 1

            # Other symbols
            elif not char.isalpha() and not char.isdigit() and not char.isspace():
                scripts["symbols"] += 1

        # Calculate ratios
        if total_chars > 0:
            for script in list(scripts.keys()):
                scripts[f"{script}_ratio"] = scripts[script] / total_chars

        return scripts

    def _analyze_words_and_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze word patterns and structure."""
        analysis = {
            "word_count": 0,
            "avg_word_length": 0,
            "has_spaces": " " in text,
            "url_count": 0,
            "hashtag_count": 0,
            "mention_count": 0,
            "number_sequences": 0,
        }

        # Word analysis
        words = text.split()
        analysis["word_count"] = len(words)
        if words:
            analysis["avg_word_length"] = sum(len(word) for word in words) / len(words)

        # Pattern matching
        analysis["url_count"] = len(re.findall(r"https?://\S+", text))
        analysis["hashtag_count"] = len(re.findall(r"#\w+", text))
        analysis["mention_count"] = len(re.findall(r"@\w+", text))
        analysis["number_sequences"] = len(re.findall(r"\d+", text))

        return analysis

    def _extract_linguistic_features(self, text: str) -> Dict[str, Any]:
        """Extract language-specific linguistic features."""
        features = {
            "japanese_particles": 0,
            "japanese_copula": 0,
            "english_articles": 0,
            "english_prepositions": 0,
            "chinese_measure_words": 0,
            "korean_particles": 0,
            "arabic_features": 0,
            "length_category": "",
        }

        # Japanese features
        for particle in self.japanese_particles:
            features["japanese_particles"] += text.count(particle)

        for copula in self.japanese_copula:
            features["japanese_copula"] += text.count(copula)

        # English features
        english_articles = len(re.findall(r"\b(the|a|an)\b", text.lower()))
        english_prepositions = len(
            re.findall(r"\b(in|on|at|to|for|of|with|by)\b", text.lower())
        )

        features["english_articles"] = english_articles
        features["english_prepositions"] = english_prepositions

        # Text length category
        length = len(text)
        if length < 20:
            features["length_category"] = "short"
        elif length < 100:
            features["length_category"] = "medium"
        else:
            features["length_category"] = "long"

        return features

    def _calculate_language_scores(
        self, script_analysis: Dict, word_analysis: Dict, linguistic_features: Dict
    ) -> Dict[str, float]:
        """Calculate scores for each potential language."""
        scores = {
            "japanese": 0.0,
            "english": 0.0,
            "chinese": 0.0,
            "korean": 0.0,
            "arabic": 0.0,
            "russian": 0.0,
            "mixed": 0.0,
            "emoji_heavy": 0.0,
            "other": 0.0,
        }

        # Japanese score
        hiragana_score = script_analysis.get("hiragana_ratio", 0) * 3.0
        katakana_score = script_analysis.get("katakana_ratio", 0) * 2.5
        kanji_score = script_analysis.get("kanji_ratio", 0) * 2.0
        jp_particle_score = min(
            linguistic_features.get("japanese_particles", 0) / 10, 1.0
        )
        jp_copula_score = min(linguistic_features.get("japanese_copula", 0) / 5, 1.0)

        scores["japanese"] = (
            hiragana_score
            + katakana_score
            + kanji_score
            + jp_particle_score
            + jp_copula_score
        )

        # English score
        latin_score = script_analysis.get("latin_ratio", 0) * 2.0
        space_score = 1.0 if word_analysis.get("has_spaces") else 0.0
        article_score = min(linguistic_features.get("english_articles", 0) / 5, 1.0)
        preposition_score = min(
            linguistic_features.get("english_prepositions", 0) / 10, 1.0
        )
        word_length_score = (
            1.0 if 3 <= word_analysis.get("avg_word_length", 0) <= 7 else 0.0
        )

        scores["english"] = (
            latin_score
            + space_score
            + article_score
            + preposition_score
            + word_length_score
        )

        # Chinese score (kanji-heavy with few Japanese features)
        chinese_score = script_analysis.get("kanji_ratio", 0) * 2.0
        if (
            script_analysis.get("hiragana_ratio", 0) < 0.05
            and script_analysis.get("katakana_ratio", 0) < 0.05
        ):
            chinese_score *= 1.5
        scores["chinese"] = chinese_score

        # Korean score
        scores["korean"] = script_analysis.get("korean_ratio", 0) * 3.0

        # Arabic score
        scores["arabic"] = script_analysis.get("arabic_ratio", 0) * 3.0

        # Russian score
        scores["russian"] = script_analysis.get("cyrillic_ratio", 0) * 3.0

        # Emoji-heavy content
        scores["emoji_heavy"] = script_analysis.get("emoji_ratio", 0) * 2.0

        # Mixed language detection
        script_diversity = sum(
            1
            for ratio in [
                script_analysis.get("hiragana_ratio", 0),
                script_analysis.get("latin_ratio", 0),
                script_analysis.get("kanji_ratio", 0),
                script_analysis.get("korean_ratio", 0),
            ]
            if ratio > 0.1
        )

        if script_diversity >= 2:
            scores["mixed"] = script_diversity * 0.5

        return scores

    def _determine_primary_language(
        self, language_scores: Dict[str, float], script_analysis: Dict
    ) -> str:
        """Determine the primary language based on scores."""
        max_score = max(language_scores.values())

        if max_score < 0.3:
            return "unknown"

        # Get highest scoring language(s)
        primary_candidates = [
            lang for lang, score in language_scores.items() if score == max_score
        ]

        if len(primary_candidates) == 1:
            return primary_candidates[0]

        # Tie-breaking logic
        if (
            "japanese" in primary_candidates
            and script_analysis.get("hiragana_ratio", 0) > 0.1
        ):
            return "japanese"
        elif (
            "english" in primary_candidates
            and script_analysis.get("latin_ratio", 0) > 0.5
        ):
            return "english"
        else:
            return primary_candidates[0]

    def _calculate_confidence(
        self, language_scores: Dict[str, float], primary_language: str
    ) -> float:
        """Calculate confidence score for the primary language detection."""
        if primary_language == "unknown":
            return 0.0

        primary_score = language_scores.get(primary_language, 0)
        other_scores = [
            score for lang, score in language_scores.items() if lang != primary_language
        ]

        if not other_scores:
            return min(primary_score / 3.0, 1.0)

        max_other_score = max(other_scores)

        if primary_score <= 0:
            return 0.0

        confidence = (primary_score - max_other_score) / primary_score
        return min(max(confidence, 0.0), 1.0)

    def _is_emoji_char(self, char: str) -> bool:
        """Check if character is an emoji."""
        code_point = ord(char)
        return (
            0x1F600 <= code_point <= 0x1F64F  # emoticons
            or 0x1F300 <= code_point <= 0x1F5FF  # symbols & pictographs
            or 0x1F680 <= code_point <= 0x1F6FF  # transport & map
            or 0x1F1E0 <= code_point <= 0x1F1FF  # flags
            or 0x2600 <= code_point <= 0x27BF  # misc symbols
            or 0x1F900 <= code_point <= 0x1F9FF  # supplemental symbols
            or 0x1F018 <= code_point <= 0x1F270  # various symbols
        )
