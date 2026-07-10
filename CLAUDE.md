# CLAUDE.md

このファイルは、このリポジトリでコードを扱う際の Claude Code (claude.ai/code) 向けのガイダンスを提供します。

## 会話言語

**すべての会話は日本語で行ってください。** 日本語と英数字の間には半角スペースを入れます。

## プロジェクト概要

twitter-parse-html-analysis は、Twitter/X のエクスポートデータを HTML レベルで解析し、通常の API では取得できない詳細情報を抽出する Python ライブラリです。主な機能は、HTML からの高精度データ抽出、多言語対応の言語検出、動画無断使用の検出、エンゲージメント分析、バッチ処理です。

## 開発コマンド

```bash
# 依存関係のインストール
pip install -r requirements.txt        # 実行時依存
pip install -r dev-requirements.txt    # 開発依存

# テスト（カバレッジ付き）
pytest tests/ --cov=src --cov-report=term-missing

# フォーマット / インポート整理
black src scripts tests examples
isort src scripts tests examples

# Lint / 型チェック（CI と同じ設定）
flake8 src scripts examples --max-complexity=10 --max-line-length=127
mypy src --ignore-missing-imports --no-strict-optional

# CLI 実行（--input-dir も別名として利用可）
python scripts/extract_tweets.py --input downloads --output parsed
python scripts/extract_tweets.py --input downloads --output parsed --consolidated
python scripts/extract_tweets.py --input downloads --output parsed --analyze-misuse

# Docker（compose.yaml のサービス名: twitter-parser / -dev / -test）
docker compose build
docker compose run --rm twitter-parser-test
```

## アーキテクチャ / 主要ファイル

- `src/parser.py`: `TwitterDataExtractor` — メインの抽出エンジン。
- `src/analyzer.py`: `VideoMisuseAnalyzer` — 動画無断使用分析。
- `src/language_detector.py`: `LanguageDetector` — 多言語検出。
- `src/utils.py`: ユーティリティ（JSON 安全読み込み、HTML サニタイズなど）。
- `scripts/extract_tweets.py`: CLI インターフェース（`console_scripts` の `twitter-parse` から呼ばれる）。
- `tests/`: `test_parser.py` / `test_analyzer.py` / `test_language_detector.py` / `test_utils.py` / `test_security.py`。
- `examples/`: `basic_usage.py` / `video_analysis.py`。

## コーディング規約

- PEP 8 に準拠。フォーマットは Black（行長 88）、インポート整理は isort（Black プロファイル、`pyproject.toml` で設定）。
- 型ヒントを積極的に使用する。関数の引数・戻り値には型ヒントを付ける。
- docstring は必須。docstring とコード内コメントは日本語で記述する。
- エラーメッセージは英語を原則とし、必要に応じて日本語の説明を添える。
- 命名: 変数・関数は `snake_case`、クラスは `PascalCase`、定数は `UPPER_SNAKE_CASE`、プライベートメソッドは `_method_name`。

## テスト方針

- pytest を使用。新機能には必ずユニットテストを追加する。
- カバレッジ 80% 以上を維持する。
- パーサーの実装を変更したら、対応するテストケースを必ず更新する。

## セキュリティ / データ取り扱い

- Twitter エクスポートデータは個人情報を含む。サンプルデータを追加する際は必ず匿名化する。
- API キー・パスワード・トークンなどの認証情報を Git にコミットしない（`.env`, `*.pem`, `*.key` は `.gitignore` 済み）。
- ログに個人情報・認証情報を出力しない。
- 実データファイル（`*.json`, `*.csv`, `*.xlsx`, `*.xls`）および出力ディレクトリ（`parsed/`, `reports/`, `output/`, `results/`, `downloads/`）はコミットしない（`.gitignore` 済み）。

## Git 運用

- コミットは [Conventional Commits](https://www.conventionalcommits.org/)（`<type>(<scope>): <description>`、`<description>` は日本語）。例: `feat(parser): ツイート抽出機能を追加`。
- ブランチは [Conventional Branch](https://conventional-branch.github.io) の短縮形（`feat`, `fix` など）。例: `feat/add-tweet-extraction`。

## ドキュメント更新ルール

- CLI フラグ・公開 API・依存関係を変更したら `README.md` を更新する。
- ディレクトリ構成・主要クラス・コマンドを変更したら、この CLAUDE.md の該当箇所を更新する。
- Docker の使い方を変更したら `docker/README.md` を更新する。

## よくあるタスク

- **抽出フィールドの追加**: `src/parser.py` の `_extract_comprehensive_tweet_data` に追加 → 対応する抽出メソッドを実装 → `tests/test_parser.py` にテスト追加。
- **言語サポートの追加**: `src/language_detector.py` に言語パターンを追加 → スコアリングロジックを更新 → `tests/test_language_detector.py` にテストデータ追加。
- **デバッグ**: ログレベルを DEBUG に設定。HTML パース結果は BeautifulSoup の `prettify()` で確認する。
