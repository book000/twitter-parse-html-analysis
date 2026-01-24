# GEMINI.md

## 目的
- Gemini CLI 向けのコンテキストと作業方針を定義する。

## 出力スタイル
- 言語: 日本語
- トーン: 簡潔で事実ベース
- 形式: Markdown

## 共通ルール
- 会話は日本語で行う。
- PR とコミットは Conventional Commits に従う。
- PR タイトルとコミット本文の言語: PR タイトルは Conventional Commits 形式（英語推奨）。PR 本文は日本語。コミットは Conventional Commits 形式（description は日本語）。
- 日本語と英数字の間には半角スペースを入れる。

## プロジェクト概要
Parse Twitter/X export data at HTML level to extract detailed information (user data, engagement metrics, language detection, video misuse analysis) not available via APIs.

### 技術スタック
- **言語**: Python
- **フレームワーク**: BeautifulSoup4, Click
- **パッケージマネージャー**: pip
- **主要な依存関係**:
  - beautifulsoup4>=4.12.0
  - lxml>=4.9.0
  - tqdm>=4.65.0
  - click>=8.1.0

## コーディング規約
- フォーマット: 既存設定（ESLint / Prettier / formatter）に従う。
- 命名規則: 既存のコード規約に従う。
- コメント言語: 日本語
- エラーメッセージ: 英語

### 開発コマンド
```bash
# install
pip install -r requirements.txt

# dev
python -m pytest

# build
python setup.py build

# test
pytest with coverage

# lint
black src/ && isort src/

```

## 注意事項
- 認証情報やトークンはコミットしない。
- ログに機密情報を出力しない。
- 既存のプロジェクトルールがある場合はそれを優先する。

## リポジトリ固有
- **entry_point**: twitter-parse console script
- **docker_support**: Dockerfile and compose.yaml included
- **output_formats**: JSON (structured), CSV (analytics), HTML (reports)
**capabilities:**
  - User info extraction (name, screen name, verification badges)
  - Engagement analytics (likes, retweets, replies, quotes)
  - Language detection (Japanese character analysis)
  - Media detection (images/videos)
  - Video misuse detection
  - Time series analysis
- **breaking_changes**: v1.1.0 - VideoMisuseAnalyzer default input changed to 'output'