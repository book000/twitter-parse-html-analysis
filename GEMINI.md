# GEMINI.md

## 目的

このファイルは、Gemini CLI 向けのコンテキストと作業方針を定義します。

## 出力スタイル

### 言語

- すべての会話は日本語で行う。
- コード内のコメントは日本語で記載する。
- エラーメッセージは英語を原則とし、必要に応じて日本語の説明を追加する。

### トーン

- 技術的に正確で客観的な情報を提供する。
- 簡潔でわかりやすい表現を心がける。
- 不確実性がある場合は明示する。

### 形式

- マークダウン形式で出力する。
- コードブロックには適切な言語タグを付ける（`python`, `bash` など）。
- 日本語と英数字の間には半角スペースを入れる。

## 共通ルール

### 会話言語

- すべての会話は日本語で行う。

### コミット規約

- コミットメッセージは [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) に従う。
- `<type>(<scope>): <description>` 形式を使用する（`<scope>` は任意）。
- `<description>` は日本語で記載する。
- 例: `feat(lang-detection): 言語検出機能を改善`

### ブランチ命名

- ブランチ命名は [Conventional Branch](https://conventional-branch.github.io) に従う。
- `<type>/<description>` 形式を使用する。
- `<type>` は短縮形（feat, fix）を使用する。
- 例: `feat/improve-language-detection`

### 日本語と英数字の間隔

- 日本語と英数字の間には半角スペースを挿入する。
- 例: `Python 3.9 以上`、`BeautifulSoup4 ライブラリ`

## プロジェクト概要

### 目的

twitter-parse-html-analysis は、Twitter/X のエクスポートデータを HTML レベルで解析し、通常の API では取得できない詳細情報を抽出する Python ライブラリです。

### 主な機能

- **HTML コンテンツからの高精度データ抽出**: BeautifulSoup4 と lxml を使用して、ツイートの詳細情報を抽出します。
- **多言語対応の言語検出システム**: 日本語、英語、中国語、韓国語、アラビア語、ロシア語をサポートし、言語混在コンテンツも検出します。
- **動画無断使用の検出**: ツイート内の動画コンテンツの無断使用を検出し、パターン分析を行います。
- **エンゲージメント分析**: リツイート、いいね、返信などのエンゲージメント指標を分析します。
- **リアルタイム処理とバッチ処理**: 単一ファイルの処理と大量ファイルのバッチ処理の両方に対応します。

### 対象ユーザー

- 開発者
- データアナリスト
- 研究者

## コーディング規約

### フォーマット

- PEP 8 に準拠する。
- Black を使用してコードをフォーマットする（行長: 88 文字）。
- isort を使用してインポートを整理する（Black プロファイル）。

### 命名規則

- 変数名、関数名: `snake_case`（例: `extract_tweet_data`）
- クラス名: `PascalCase`（例: `TwitterDataExtractor`）
- 定数: `UPPER_SNAKE_CASE`（例: `MAX_FILE_SIZE`）
- プライベートメソッド: `_method_name`（例: `_extract_content`）

### コメント言語

- コード内のコメントは日本語で記載する。
- docstring は必ず日本語で記述する。

### エラーメッセージ言語

- エラーメッセージは英語を原則とする。
- 必要に応じて日本語の説明を追加する。

### 型ヒント

- 型ヒントを積極的に使用する。
- 関数の引数と戻り値には必ず型ヒントを付ける。

### docstring

- すべての関数、クラス、メソッドに docstring を記載する。
- docstring は日本語で記述する。
- 引数、戻り値、例外を明記する。

## 開発コマンド

### 依存関係のインストール

```bash
# 実行時依存関係
pip install -r requirements.txt

# 開発依存関係
pip install -r dev-requirements.txt
```

### テスト実行

```bash
# 全テスト
pytest tests/ --cov=src --cov-report=xml --cov-report=html

# 特定テストファイル
pytest tests/test_parser.py -v

# カバレッジ表示
pytest tests/ --cov=src --cov-report=term-missing
```

### コード品質チェック

```bash
# Black フォーマット
black src scripts tests examples

# isort インポート整理
isort src scripts tests examples

# flake8 Lint チェック
flake8 src scripts examples --max-complexity=10 --max-line-length=127

# mypy 型チェック
mypy src --ignore-missing-imports --no-strict-optional

# bandit セキュリティスキャン
bandit -r src

# safety 依存関係チェック
safety check
```

### Docker

```bash
# ビルド
docker compose build

# 実行
docker compose run --rm twitter-parser \
  python scripts/extract_tweets.py --input-dir /app/data --output-dir /app/output

# テスト
docker compose run --rm twitter-parser-test

# 開発
docker compose run --rm twitter-parser-dev
```

### CLI 実行

```bash
# 基本的な抽出
python scripts/extract_tweets.py --input downloads --output parsed

# 統合ファイル付き
python scripts/extract_tweets.py --input downloads --output parsed --consolidated

# 動画分析を含む
python scripts/extract_tweets.py --input downloads --output parsed --analyze-misuse

# サンプルモード
python scripts/extract_tweets.py --input downloads --output parsed --sample
```

## 注意事項

### 認証情報のコミット禁止

- API キー、パスワード、トークンなどの認証情報を Git にコミットしない。
- `.env`, `.env.local`, `*.pem`, `*.key` などのファイルは `.gitignore` に含まれている。

### ログへの機密情報出力禁止

- ログに個人情報、認証情報、API キーを出力しない。
- Twitter エクスポートデータには個人情報が含まれるため、ログ出力時は特に注意する。

### 既存ルールの優先

- プロジェクトの既存のコーディング規約、フォーマット、テスト方針に従う。
- 新しいパターンを導入する前に、既存のコードベースを確認する。

### 既知の制約

#### プライバシー

- Twitter エクスポートデータは個人情報を含む。
- サンプルデータを追加する際は必ず匿名化する。
- 以下のファイルは Git にコミットしない：
  - `*.json`, `*.csv`, `*.xlsx`, `*.xls`
  - `parsed/`, `reports/`, `output/`, `results/`, `downloads/` ディレクトリ

#### API 変更への対応

- Twitter のエクスポートフォーマットは API の変更により変わる可能性がある。
- 定期的な動作確認が必要。
- パーサーの実装変更時は必ずテストケースを更新する。

#### ライセンス確認

- 本プロジェクト: MIT License
- 依存ライブラリのライセンスも確認する。

## リポジトリ固有

### 技術スタック

- **言語**: Python 3.9, 3.10, 3.11, 3.12
- **HTML パース**: BeautifulSoup4 (>=4.12.0), lxml (>=4.9.0)
- **CLI フレームワーク**: Click (>=8.1.0)
- **プログレスバー**: tqdm (>=4.65.0)
- **型チェック**: typing, typing_extensions (>=4.5.0)
- **テストフレームワーク**: pytest (>=7.0.0)
- **カバレッジ計測**: pytest-cov (>=4.0.0)
- **モック機能**: pytest-mock (>=3.10.0)
- **非同期テスト**: pytest-asyncio (>=0.21.0)
- **フォーマッター**: Black (>=23.0.0)
- **インポート整理**: isort (>=5.12.0)
- **Lint**: flake8 (>=6.0.0)
- **型チェッカー**: mypy (>=1.0.0)
- **セキュリティ**: bandit (>=1.7.0), safety (>=2.3.0)
- **Docker**: Python 3.12-slim ベースイメージ

### 主要ファイル

- **src/parser.py**: `TwitterDataExtractor` - メイン処理エンジン
- **src/analyzer.py**: `VideoMisuseAnalyzer` - 動画無断使用分析
- **src/language_detector.py**: `LanguageDetector` - 多言語言語検出
- **src/utils.py**: ユーティリティ関数（JSON 安全読み込み、HTML サニタイズなど）
- **scripts/extract_tweets.py**: CLI インターフェース

### テスト構成

- **tests/test_parser.py**: TwitterDataExtractor のテスト
- **tests/test_analyzer.py**: VideoMisuseAnalyzer のテスト
- **tests/test_language_detector.py**: LanguageDetector のテスト
- **tests/test_utils.py**: ユーティリティ関数のテスト
- **tests/test_security.py**: セキュリティテスト

### CI/CD

- **GitHub Actions**: `.github/workflows/ci.yml`
  - quality ジョブ: Black, isort, flake8, mypy チェック
  - test ジョブ: Python 3.9, 3.10, 3.11, 3.12 でテスト実行
  - build ジョブ: Python パッケージビルド
  - finished-build ジョブ: 全ジョブの成功確認
- **Docker イメージビルド**: `.github/workflows/docker.yml`

### よくあるタスク

#### 新しい抽出フィールドの追加

1. `src/parser.py` の `_extract_comprehensive_tweet_data` メソッドに追加する。
2. 対応する抽出メソッドを実装する。
3. テストケースを `tests/test_parser.py` に追加する。

#### 新しい言語のサポート追加

1. `src/language_detector.py` に言語パターンを追加する。
2. スコアリングロジックを更新する。
3. テストデータを `tests/test_language_detector.py` に追加する。

#### パフォーマンス改善

1. プロファイリングでボトルネックを特定する。
2. 並列処理やキャッシュの活用を検討する。
3. メモリ使用量をモニタリングする。

### デバッグのヒント

- ログレベルを DEBUG に設定して詳細情報を確認する。
- 個別ファイルの処理結果を確認する。
- HTML パース結果を視覚的に確認する（BeautifulSoup の `prettify()`）。

### リリース前チェックリスト

- [ ] 全テストがパスすること
- [ ] ドキュメントが最新であること
- [ ] サンプルコードが動作すること
- [ ] requirements.txt が最新であること
- [ ] CHANGELOG を更新
