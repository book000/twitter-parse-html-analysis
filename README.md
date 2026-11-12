# Twitter Parse HTML Analysis

A Python tool that parses Twitter/X tweet data saved as JSON (with the tweet's rendered HTML) and extracts details that are not available from plain text: user and verification information, engagement metrics, language, media, and suspected video misuse.

## Features

- **Tweet and user extraction**: screen name, display name, user ID, profile image, verification status (blue, gold or gray badge detected from the badge SVG), text, timestamps, and reply/quote/retweet context.
- **Engagement metrics**: like, retweet, reply and quote counts, total engagement, ratios, and a simple viral score.
- **Language detection**: script-based detection (Japanese hiragana/katakana/kanji, Latin, Korean, Chinese, Arabic, Cyrillic and others) combined with word and pattern heuristics.
- **Media analysis**: image and video detection, plus heuristics that flag video posts that credit another creator.
- **Video misuse analysis**: aggregates the extraction output into per-user violation lists, rankings, victim creator rankings and summary statistics.
- **Progress logging**: periodic progress, ETA and throughput logs. Files are processed sequentially, one at a time.

`src/utils.py` also contains `is_likely_spam`, a small text-pattern heuristic. It is not a machine learning model and the CLI does not call it.

## Requirements

- Python 3.9 or later (CI runs the tests on 3.9 to 3.12)
- Runtime dependencies from `requirements.txt` (`beautifulsoup4`, `lxml`, `tqdm`, `click`, `typing_extensions`)

## Input format

Each `*.json` file in the input directory must be an object with a `data` list. Each item is a tweet object. These keys are read:

| Key | Description |
|-----|-------------|
| `tweetId` | Tweet ID |
| `tweetText` | Plain tweet text |
| `elementHtml` | Rendered HTML of the tweet element (HTML over 500,000 bytes in UTF-8 is truncated to its first 100,000 bytes and an error is recorded) |
| `screenName` | Optional; otherwise derived from the HTML |
| `likeCount`, `retweetCount`, `replyCount`, `quoteCount` | Engagement counts |
| `inReplyToTweetId`, `inReplyToUser`, `quotedTweet`, `retweetedTweet` | Optional context |

Files without a `data` list are skipped with a warning.

## Installation

```bash
git clone https://github.com/book000/twitter-parse-html-analysis.git
cd twitter-parse-html-analysis
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

The project is run from a source checkout. `setup.py` exists, but the built package does not contain the `src` modules and the `twitter-parse` console script it declares is not usable.

## Usage

### Command line

Run `scripts/extract_tweets.py` from a source checkout. It adds the repository root to `sys.path` itself, so no `PYTHONPATH` setting is needed.

```bash
# Basic extraction
python scripts/extract_tweets.py --input downloads --output parsed

# Also write one consolidated file with all tweets
python scripts/extract_tweets.py --input downloads --output parsed --consolidated

# Also run the video misuse analysis (results go to ./video_misuse_analysis)
mkdir -p video_misuse_analysis
python scripts/extract_tweets.py --input downloads --output parsed --analyze-misuse
```

| Option | Default | Description |
|--------|---------|-------------|
| `--input`, `--input-dir`, `-i` | `downloads` | Directory containing the JSON files |
| `--output`, `-o` | `parsed` | Output directory for extracted data |
| `--reports` | `reports` | Output directory for reports |
| `--consolidated`, `-c` | off | Also write `all_extracted_tweets_<timestamp>.json` |
| `--analyze-misuse` | off | Run `VideoMisuseAnalyzer` on the output directory afterwards |
| `--sample` | off | Currently has no effect other than printing a message |
| `--verbose`, `-v` / `--quiet`, `-q` | | Debug or warning-only logging |

The CLI console output is in Japanese. Log messages are in English. A log file `twitter_data_extractor.log` is written to the current directory.

The `video_misuse_analysis` directory must exist before `--analyze-misuse` runs, because the analyzer creates its log file there before it creates the directory.

### Python API

```python
from src.parser import TwitterDataExtractor

extractor = TwitterDataExtractor(
    input_dir="downloads",      # directory with the JSON files
    output_dir="parsed",        # one <name>_extracted.json per input file
    reports_dir="reports",      # summary, statistics and error reports
    create_consolidated=True,   # also write all_extracted_tweets_<timestamp>.json
)
stats = extractor.extract_all()
print(stats["processed_files"], stats["total_tweets"])
```

```python
from src.analyzer import VideoMisuseAnalyzer

# Reads *_extracted.json files from input_dir (default "output").
analyzer = VideoMisuseAnalyzer(input_dir="parsed", output_dir="video_misuse_analysis")
results = analyzer.analyze_all()
```

```python
from src.language_detector import LanguageDetector

result = LanguageDetector().detect_languages("こんにちは！Hello!")
print(result["primary"])          # "japanese"
print(result["script_analysis"])  # per-script character counts and ratios
```

See `examples/basic_usage.py` and `examples/video_analysis.py` for complete scripts. Both read from a `data/` directory.

### Docker

```bash
mkdir -p data output reports
cp /path/to/tweets-*.json data/
docker compose build
docker compose run --rm twitter-parser \
  python scripts/extract_tweets.py --input /app/data --output /app/output --reports /app/reports
```

See [docker/README.md](docker/README.md) for details.

## Output

### Extracted tweets

`<input name>_extracted.json` contains one object per tweet. An excerpt:

```json
{
  "file_source": "tweets-1.json",
  "tweet_id": "1234567890",
  "screen_name": "username",
  "user_id": "1111111111",
  "display_name": "Display Name",
  "tweet_text": "Tweet text",
  "timestamp": "2024-01-01T12:00:00+00:00",
  "like_count": 100,
  "retweet_count": 50,
  "reply_count": 10,
  "total_engagement": 160,
  "is_verified": true,
  "verification_type": "blue_verified",
  "language_detected": "english",
  "has_attached_media": true,
  "video_misuse_detected": false,
  "data_quality_score": 85,
  "extraction_errors": ""
}
```

`user_id` is extracted from follow/unfollow/block/unblock buttons in the HTML and is an empty string when none is present. `data_quality_score` is a 0-100 score based on which extraction steps succeeded.

### Reports (`--reports` directory)

- `summary_report_<timestamp>.json`: per-file summaries and overall statistics
- `processing_statistics_<timestamp>.json`: overall statistics
- `error_report_<timestamp>.json`: only written if an unexpected exception escaped file processing. Files that cannot be read, are not valid JSON, or lack a `data` list are only logged (see the log file), not listed here.

### Video misuse analysis (`video_misuse_analysis` by default)

- `video_misuse_users_<timestamp>.csv`: per-user violation statistics
- `violation_details_<timestamp>.csv`: individual violation records
- `user_rankings_<timestamp>.json`: user rankings by several metrics
- `summary_statistics_<timestamp>.json`: overall analysis results
- `victim_creators_ranking_<timestamp>.csv`: creators whose videos were reused most often

## Notes

- Twitter export data is personal data. Do not commit it, and be careful when sharing analysis results.
- Video misuse detection is heuristic and can produce false positives and false negatives.

## Behavior change: analyzer default directory

The default `input_dir` of `VideoMisuseAnalyzer` is `output`. Pass `input_dir="parsed"` explicitly to read the CLI's default output directory.

## Development

```bash
pip install -r requirements.txt -r dev-requirements.txt

pytest tests/ --cov=src --cov-report=term-missing   # tests
black src scripts tests examples                    # formatting
isort src scripts tests examples                    # import order
flake8 src scripts examples --max-complexity=10 --max-line-length=127
mypy src --ignore-missing-imports --no-strict-optional
```

## License

MIT License. See [LICENSE](LICENSE).

## Contributing

Pull requests are welcome. For large changes, please open an issue first to discuss them. Report problems at [Issues](https://github.com/book000/twitter-parse-html-analysis/issues).
