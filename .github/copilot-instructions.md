# GitHub Copilot Instructions

## プロジェクト概要
Parse Twitter/X export data at HTML level to extract detailed information (user data, engagement metrics, language detection, video misuse analysis) not available via APIs.

## 共通ルール
- 会話は日本語で行う。
- PR とコミットは Conventional Commits に従う。
- PR タイトルとコミット本文の言語: PR タイトルは Conventional Commits 形式（英語推奨）。PR 本文は日本語。コミットは Conventional Commits 形式（description は日本語）。
- 日本語と英数字の間には半角スペースを入れる。
- 既存のプロジェクトルールがある場合はそれを優先する。

## 技術スタック
- 言語: Python
- パッケージマネージャー: pip

## コーディング規約
- フォーマット: 既存設定（ESLint / Prettier / formatter）に従う。
- 命名規則: 既存のコード規約に従う。
- Lint / Format: 既存の Lint / Format 設定に従う。
- コメント言語: 日本語
- エラーメッセージ: 英語
- TypeScript 使用時は strict 前提とし、`skipLibCheck` で回避しない。
- 関数やインターフェースには docstring（JSDoc など）を記載する。

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

## テスト方針
- 新機能や修正には適切なテストを追加する。

## セキュリティ / 機密情報
- 認証情報やトークンはコミットしない。
- ログに機密情報を出力しない。

## ドキュメント更新
- 実装確定後、同一コミットまたは追加コミットで更新する。
- README、API ドキュメント、コメント等は常に最新状態を保つ。

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