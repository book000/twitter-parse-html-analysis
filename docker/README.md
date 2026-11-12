# Docker Usage Guide

How to run the extractor with Docker. The image (`Dockerfile`) is based on `python:3.15-slim`, runs as the non-root user `twitter-parser` (UID 1000), and sets `PYTHONPATH=/app`.

## Quick start

```bash
# Create the data directories and add your Twitter export JSON files
mkdir -p data output reports
cp /path/to/tweets-*.json data/

# Build the image
docker compose build

# Extract data
docker compose run --rm twitter-parser \
  python scripts/extract_tweets.py \
  --input /app/data \
  --output /app/output \
  --reports /app/reports
```

Without Compose:

```bash
docker build -t twitter-html-parser .
docker run --rm \
  -v $(pwd)/data:/app/data:ro \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/reports:/app/reports \
  twitter-html-parser \
  python scripts/extract_tweets.py --input /app/data --output /app/output --reports /app/reports
```

The CLI options are `--input` (alias `--input-dir`), `--output`, `--reports`, `--consolidated`, `--analyze-misuse`, `--verbose` and `--quiet`. There is no `--output-dir` or `--reports-dir` option. See the [main README](../README.md#command-line) for the full table.

## Examples

```bash
# Also write one consolidated file with all tweets
docker compose run --rm twitter-parser \
  python scripts/extract_tweets.py --input /app/data --output /app/output --consolidated

# Run the video misuse analysis example (reads /app/data, writes inside the container)
docker compose run --rm twitter-parser python examples/video_analysis.py

# Run the tests
docker compose run --rm twitter-parser-test

# Development shell with src/, scripts/, examples/ and tests/ mounted
docker compose run --rm twitter-parser-dev
```

`--analyze-misuse` fails inside the container unless `/app/video_misuse_analysis` already exists (see the [main README](../README.md#command-line)). Mounting a host directory there creates it and keeps the results:

```bash
mkdir -p video_misuse_analysis
docker compose run --rm -v $(pwd)/video_misuse_analysis:/app/video_misuse_analysis twitter-parser \
  python scripts/extract_tweets.py --input /app/data --output /app/output --analyze-misuse
```

Otherwise use `examples/video_analysis.py`.

## Configuration

Volumes defined in `compose.yaml` (`twitter-parser` service):

| Host path | Container path | Description |
|-----------|----------------|-------------|
| `./data` | `/app/data` | Input JSON files (read-only) |
| `./output` | `/app/output` | Extraction output |
| `./reports` | `/app/reports` | Reports |

`compose.yaml` also sets `PYTHONUNBUFFERED=1` and `LOG_LEVEL`, but the application does not read `LOG_LEVEL`. Use `--verbose` or `--quiet` to change the log level.

## Troubleshooting

If the output directories are not writable by the container user (UID 1000), fix their ownership on the host:

```bash
sudo chown -R 1000:1000 output/ reports/
```

Show container logs:

```bash
docker compose logs twitter-parser
```
