# AGENTS.md

Guidance for AI coding agents working in this repository. `CLAUDE.md` only points here.

## Language

- Write all deliverables in English: README and other docs, `AGENTS.md`, code comments and docstrings, commit descriptions, PR and Issue titles and bodies, and review comments.
- Log messages and error messages are English.
- Exceptions kept as is: the Japanese console output of `scripts/extract_tweets.py` and the Japanese unit labels returned by `format_time_duration`, Japanese keyword lists and Twitter UI strings matched in `src/` (for example `さんのプロフィール`), and Japanese test fixtures.
- Never rewrite Git history.

## Project

Python tool that parses Twitter/X export JSON (tweet text plus rendered `elementHtml`) with BeautifulSoup and extracts user, verification, engagement, language and video-misuse information. See `README.md` for usage and the input format.

- `src/parser.py`: `TwitterDataExtractor`, the extraction engine.
- `src/analyzer.py`: `VideoMisuseAnalyzer`, aggregates `*_extracted.json` into CSV/JSON reports.
- `src/language_detector.py`: `LanguageDetector`.
- `src/utils.py`: safe JSON loading, HTML and log sanitizing, small helpers.
- `scripts/extract_tweets.py`: CLI. It adds the repository root to `sys.path` itself, so it runs without `PYTHONPATH`.
- `tests/`, `examples/`, `docker/README.md`, `compose.yaml` (services `twitter-parser`, `twitter-parser-dev`, `twitter-parser-test`).

## Commands

```bash
pip install -r requirements.txt -r dev-requirements.txt
pytest tests/ --cov=src --cov-report=term-missing
black src scripts tests examples
isort src scripts tests examples
flake8 src scripts examples --max-complexity=10 --max-line-length=127
mypy src --ignore-missing-imports --no-strict-optional
```

CI (`.github/workflows/ci.yml`) fails on black, isort, flake8 syntax/undefined-name errors (`E9,F63,F7,F82`) and pytest. The complexity/line-length flake8 run and mypy do not fail the build. Run black and isort before committing.

## Conventions

- Black (line length 88) and isort (Black profile), configured in `pyproject.toml`. Use type hints and docstrings.
- Naming: `snake_case` functions and variables, `PascalCase` classes, `UPPER_SNAKE_CASE` constants, `_private` helpers.
- Comments explain intent and constraints, not what the code already says.
- Add unit tests for new features and update `tests/` when parser behavior changes, and `README.md` / `docker/README.md` when CLI flags, public API or Docker usage change.
- Conventional Commits and Conventional Branch (`feat/...`, `fix/...`, `docs/...`).

## Safety

- Twitter export data is personal data. Anonymize any sample data you add and never commit real data (`*.json`, `*.csv`, `*.xlsx`, `*.xls` and the output directories `parsed/`, `reports/`, `output/`, `results/`, `downloads/` are in `.gitignore`).
- Do not commit credentials, and do not log personal data. Use `sanitize_log_message` for externally derived strings in logs.
