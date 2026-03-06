# AGENTS.md

## 目的

このファイルは、このリポジトリで作業する一般的な AI エージェント向けの基本方針を定義します。

## 基本方針

### 会話言語

- すべての会話は日本語で行う。

### コード内コメント

- コード内のコメントは日本語で記載する。

### エラーメッセージ

- エラーメッセージは英語を原則とする。
- 必要に応じて日本語の説明を追加する。

### 日本語と英数字の間隔

- 日本語と英数字の間には半角スペースを挿入する。

### コミット規約

- コミットメッセージは [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) に従う。
- `<type>(<scope>): <description>` 形式を使用する（`<scope>` は任意）。
- `<description>` は日本語で記載する。
- 例: `feat(app): ツイート抽出機能を追加`

### ブランチ命名

- ブランチ命名は [Conventional Branch](https://conventional-branch.github.io) に従う。
- `<type>/<description>` 形式を使用する。
- `<type>` は短縮形（feat, fix）を使用する。
- 例: `feat/add-tweet-extraction`

## 判断記録のルール

判断は必ずレビュー可能な形で記録すること。

1. **判断内容の要約**: 何を決定したかを明確に記述する。
2. **検討した代替案**: どのような選択肢があったかを列挙する。
3. **採用しなかった案とその理由**: なぜその選択肢を選ばなかったかを説明する。
4. **前提条件・仮定・不確実性**: 判断の前提となる条件や仮定を明示する。
5. **他エージェントによるレビュー可否**: 他の AI エージェントがこの判断をレビューできるかを示す。

**重要**: 前提・仮定・不確実性を明示すること。仮定を事実のように扱ってはならない。

## 開発手順（概要）

### 1. プロジェクト理解

- リポジトリの構造を確認する。
- README.md、CLAUDE.md、その他のドキュメントを読む。
- 主要なソースコードファイルを確認する（`src/parser.py`, `src/analyzer.py`, `src/language_detector.py`, `src/utils.py`）。

### 2. 依存関係インストール

```bash
# 実行時依存関係
pip install -r requirements.txt

# 開発依存関係
pip install -r dev-requirements.txt
```

### 3. 変更実装

- PEP 8 に準拠したコードを記述する。
- 型ヒントを積極的に使用する。
- docstring は必ず日本語で記載する。
- 日本語コメントを推奨する。
- Black (行長: 88 文字) でフォーマットする。
- isort で インポートを整理する。

### 4. テストと Lint/Format 実行

```bash
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
```

### 5. コミットと PR

- コミットメッセージは Conventional Commits に従う。
- PR 作成前に全テストがパスすることを確認する。
- センシティブな情報が含まれていないことを確認する。

## セキュリティ / 機密情報

### 認証情報のコミット禁止

- API キー、パスワード、トークンなどの認証情報を Git にコミットしない。
- `.env`, `.env.local`, `*.pem`, `*.key` などのファイルは `.gitignore` に含まれている。

### ログへの機密情報出力禁止

- ログに個人情報、認証情報、API キーを出力しない。
- Twitter エクスポートデータには個人情報が含まれるため、ログ出力時は注意する。

### データファイルの取り扱い

- Twitter エクスポートデータは個人情報を含む。
- サンプルデータを追加する際は必ず匿名化する。
- 以下のファイルは Git にコミットしない：
  - `*.json`, `*.csv`, `*.xlsx`, `*.xls`
  - `parsed/`, `reports/`, `output/`, `results/`, `downloads/` ディレクトリ

## リポジトリ固有

### プロジェクト概要

twitter-parse-html-analysis は、Twitter/X のエクスポートデータを HTML レベルで解析し、通常の API では取得できない詳細情報を抽出する Python ライブラリです。

**主な機能**:

- HTML コンテンツからの高精度データ抽出
- 多言語対応の言語検出システム（日本語、英語、中国語、韓国語、アラビア語、ロシア語）
- 動画無断使用の検出
- エンゲージメント分析
- リアルタイム処理とバッチ処理

### 技術スタック

- 言語: Python 3.9, 3.10, 3.11, 3.12
- HTML パース: BeautifulSoup4, lxml
- CLI フレームワーク: Click
- プログレスバー: tqdm
- テストフレームワーク: pytest
- フォーマッター: Black
- Lint: flake8
- 型チェック: mypy
- セキュリティ: bandit, safety

### ディレクトリ構造

```
twitter-parse-html-analysis/
├── src/                           # ソースコード
│   ├── parser.py                  # メイン処理（TwitterDataExtractor）
│   ├── analyzer.py                # 分析機能（VideoMisuseAnalyzer）
│   ├── language_detector.py       # 言語検出（LanguageDetector）
│   └── utils.py                   # ユーティリティ関数
├── scripts/
│   └── extract_tweets.py          # CLI インターフェース
├── tests/                          # テストコード
│   ├── test_parser.py             # Parser テスト
│   ├── test_analyzer.py           # Analyzer テスト
│   ├── test_language_detector.py  # LanguageDetector テスト
│   ├── test_utils.py              # Utils テスト
│   └── test_security.py           # セキュリティテスト
├── examples/                       # 使用例
│   ├── basic_usage.py             # 基本的な使用例
│   └── video_analysis.py          # 動画分析の使用例
├── docker/                         # Docker 関連
│   └── README.md                  # Docker 使用ガイド
├── .github/workflows/              # CI/CD
│   ├── ci.yml                     # CI パイプライン
│   └── docker.yml                 # Docker イメージビルド
├── requirements.txt                # 実行時依存関係
├── dev-requirements.txt            # 開発依存関係
├── setup.py                        # パッケージ設定
├── pyproject.toml                  # Black/isort 設定
├── Dockerfile                      # 本番用 Docker イメージ
├── Dockerfile.test                 # テスト用 Docker イメージ
├── compose.yaml                    # Docker Compose 設定
└── README.md                       # プロジェクト説明書
```

### 重要な注意事項

#### プライバシー

- Twitter エクスポートデータは個人情報を含む。
- サンプルデータを追加する際は必ず匿名化する。

#### API 変更への対応

- Twitter のエクスポートフォーマットは API の変更により変わる可能性がある。
- 定期的な動作確認が必要。
- パーサーの実装変更時は必ずテストケースを更新する。

#### ライセンス確認

- 本プロジェクト: MIT License
- 依存ライブラリのライセンスも確認する。

### コーディング規約

- PEP 8 に準拠する。
- 型ヒントを積極的に使用する。
- docstring は必須（日本語で記述）。
- 日本語コメントを推奨する。
- フォーマット: Black (行長: 88 文字)
- インポート整理: isort (Black プロファイル)

### テスト方針

- 新機能には必ずユニットテストを追加する。
- pytest を使用する。
- カバレッジ 80% 以上を維持する。

### パフォーマンス

- 大量ファイル処理を想定した効率的な実装を行う。
- メモリ使用量に配慮する。
- 並列処理の活用を検討する。

### よくあるタスク

#### 新しい抽出フィールドの追加

1. `src/parser.py` の `_extract_comprehensive_tweet_data` メソッドに追加する。
2. 対応する抽出メソッドを実装する。
3. テストケースを追加する。

#### 新しい言語のサポート追加

1. `src/language_detector.py` に言語パターンを追加する。
2. スコアリングロジックを更新する。
3. テストデータを追加する。

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
