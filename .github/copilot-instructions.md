# GitHub Copilot Instructions

## プロジェクト概要

- 目的: Twitter/X のエクスポートデータを HTML レベルで解析し、通常の API では取得できない詳細情報を抽出する
- 主な機能: HTML コンテンツからの高精度データ抽出、多言語対応の言語検出システム、動画無断使用の検出、エンゲージメント分析、リアルタイム処理とバッチ処理
- 対象ユーザー: 開発者、データアナリスト

## 共通ルール

- 会話は日本語で行う。
- PR とコミットは Conventional Commits に従う。`<description>` は日本語で記載する。
- 日本語と英数字の間には半角スペースを入れる。

## 技術スタック

- 言語: Python 3.9, 3.10, 3.11, 3.12
- HTML パース: BeautifulSoup4 (>=4.12.0), lxml (>=4.9.0)
- CLI フレームワーク: Click (>=8.1.0)
- プログレスバー: tqdm (>=4.65.0)
- 型チェック: typing, typing_extensions (>=4.5.0)
- パッケージマネージャー: pip
- Docker: Python 3.12-slim ベースイメージ

## コーディング規約

- PEP 8 に準拠する。
- 型ヒントを積極的に使用する。
- docstring は必須（日本語で記述）。
- 日本語コメントを推奨する。
- フォーマット: Black (行長: 88 文字)
- インポート整理: isort (Black プロファイル)
- Lint: flake8 (max-complexity=10, max-line-length=127)
- 型チェック: mypy (--ignore-missing-imports --no-strict-optional)

## 開発コマンド

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 開発依存関係のインストール
pip install -r dev-requirements.txt

# テスト実行
pytest tests/ --cov=src --cov-report=xml --cov-report=html

# Black フォーマット
black src scripts tests examples

# isort インポート整理
isort src scripts tests examples

# flake8 Lint チェック
flake8 src scripts examples --max-complexity=10 --max-line-length=127

# mypy 型チェック
mypy src --ignore-missing-imports --no-strict-optional

# Docker ビルド
docker compose build

# Docker でデータ抽出
docker compose run --rm twitter-parser \
  python scripts/extract_tweets.py \
  --input-dir /app/data --output-dir /app/output

# Docker でテスト実行
docker compose run --rm twitter-parser-test

# CLI 実行（基本）
python scripts/extract_tweets.py --input downloads --output parsed

# CLI 実行（統合ファイル付き）
python scripts/extract_tweets.py --input downloads --output parsed --consolidated

# CLI 実行（動画分析を含む）
python scripts/extract_tweets.py --input downloads --output parsed --analyze-misuse
```

## テスト方針

- テストフレームワーク: pytest (>=7.0.0)
- カバレッジ計測: pytest-cov (>=4.0.0)
- モック機能: pytest-mock (>=3.10.0)
- 非同期テスト: pytest-asyncio (>=0.21.0)
- カバレッジ目標: 80% 以上を維持する。
- 新機能には必ずユニットテストを追加する。

## セキュリティ / 機密情報

- Twitter エクスポートデータは個人情報を含むため、サンプルデータ追加時は必ず匿名化する。
- 認証情報や API キーを Git にコミットしない。
- ログに個人情報や認証情報を出力しない。
- セキュリティスキャナー: bandit (>=1.7.0), safety (>=2.3.0)

## ドキュメント更新

変更に応じて以下のドキュメントを更新する：

- README.md: プロジェクト説明、インストール、使用方法
- CLAUDE.md: Claude Code ガイドライン
- docker/README.md: Docker 使用ガイド、トラブルシューティング
- docstring: すべての関数・クラスに日本語で記載

## リポジトリ固有

### プライバシーとセキュリティ

- Twitter エクスポートデータは個人情報を含む。サンプルデータを追加する際は必ず匿名化する。
- 以下のディレクトリとファイルは Git にコミットしない：
  - `parsed/`, `reports/`, `output/`, `results/`, `downloads/`
  - `*.json`, `*.csv`, `*.xlsx`, `*.xls`
  - `.env`, `.env.local`, `*.pem`, `*.key`

### API 変更への対応

- Twitter のエクスポートフォーマットは API の変更により変わる可能性がある。
- 定期的な動作確認が必要。
- パーサーの実装変更時は必ずテストケースを更新する。

### ライセンス確認

- 本プロジェクト: MIT License
- 依存ライブラリのライセンスも確認する。

### 主要ファイル

- `src/parser.py`: TwitterDataExtractor - メイン処理エンジン
- `src/analyzer.py`: VideoMisuseAnalyzer - 動画無断使用分析
- `src/language_detector.py`: LanguageDetector - 多言語言語検出
- `src/utils.py`: ユーティリティ関数（JSON 安全読み込み、HTML サニタイズなど）

### よくあるタスク

#### 新しい抽出フィールドの追加

1. `src/parser.py` の `_extract_comprehensive_tweet_data` メソッドに追加
2. 対応する抽出メソッドを実装
3. テストケースを追加

#### 新しい言語のサポート追加

1. `src/language_detector.py` に言語パターンを追加
2. スコアリングロジックを更新
3. テストデータを追加

#### パフォーマンス改善

1. プロファイリングでボトルネックを特定
2. 並列処理やキャッシュの活用を検討
3. メモリ使用量をモニタリング

### デバッグのヒント

- ログレベルを DEBUG に設定して詳細情報を確認
- 個別ファイルの処理結果を確認
- HTML パース結果を視覚的に確認（BeautifulSoup の `prettify()`）

### リリース前チェックリスト

- [ ] 全テストがパスすること
- [ ] ドキュメントが最新であること
- [ ] サンプルコードが動作すること
- [ ] requirements.txt が最新であること
- [ ] CHANGELOG を更新
