# AGENTS.md

## 目的
- エージェント共通の作業方針を定義する。

## 基本方針
- 会話言語: 日本語
- コード内コメント: 日本語
- エラーメッセージ: 英語
- PR とコミットは Conventional Commits に従う。
- PR タイトルとコミット本文の言語: PR タイトルは Conventional Commits 形式（英語推奨）。PR 本文は日本語。コミットは Conventional Commits 形式（description は日本語）。
- 日本語と英数字の間には半角スペースを入れる。

## 判断記録のルール
- 判断内容、代替案、採用理由、前提条件、不確実性を明示する。

## 開発手順（概要）
1. プロジェクト理解のために必要なファイルを確認する。
2. 依存関係をインストールする。
3. 変更を実装する。
4. テストと Lint / Format を実行する。

## セキュリティ / 機密情報
- 認証情報やトークンはコミットしない。
- ログに機密情報を出力しない。

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