# Twitter Parse HTML Analysis

Twitter/XのエクスポートデータをパースしHTMLコンテンツから詳細情報を抽出・分析するPythonツールです。

## 概要

TwitterのデータエクスポートからダウンロードしたJSONファイルを解析し、HTML要素から以下の情報を抽出します：

- 👤 **ユーザー情報**: スクリーンネーム、表示名、プロフィール画像、認証ステータス
- 📊 **エンゲージメント分析**: いいね、リツイート、リプライ、引用の詳細統計
- 🌐 **言語検出**: 高精度な多言語検出（日本語、英語、中国語、韓国語など）
- 🎥 **メディア分析**: 画像・動画コンテンツの検出と無断使用の分析
- 🚨 **スパム検出**: 機械学習ベースのスパムアカウント検出（オプション）
- 📈 **時系列分析**: ツイートの時間パターンと頻度分析

## 特徴

### 高精度データ抽出
- BeautifulSoupによるHTML解析で通常のAPIでは取得できない詳細情報を抽出
- 認証バッジの種類（青、ゴールド、グレー）を正確に識別
- 動画の無断使用を複数の手法で検出

### 多言語対応
- 日本語の文字種（ひらがな、カタカナ、漢字）別分析
- 言語混在コンテンツの正確な検出
- 文化的・言語的特徴の抽出

### リアルタイム処理
- 大量ファイルの並列処理対応
- 処理進捗のリアルタイム表示とETA計算
- メモリ効率的な逐次処理

## インストール

```bash
# リポジトリのクローン
git clone https://github.com/book000/twitter-parse-html-analysis.git
cd twitter-parse-html-analysis

# 仮想環境の作成（推奨）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt
```

## 使い方

### Dockerを使用した実行（推奨）

Dockerを使用することで、環境構築不要で簡単に実行できます。

```bash
# リポジトリのクローンとディレクトリ作成
git clone https://github.com/book000/twitter-parse-html-analysis.git
cd twitter-parse-html-analysis
mkdir -p data output reports

# Twitterエクスポートファイルをdataディレクトリに配置
cp /path/to/tweets-*.json data/

# Dockerイメージのビルド
docker compose build

# データ抽出の実行
docker compose run --rm twitter-parser \
  python scripts/extract_tweets.py \
  --input-dir /app/data \
  --output-dir /app/output \
  --reports-dir /app/reports

# 動画無断使用分析も実行
docker compose run --rm twitter-parser \
  python scripts/extract_tweets.py \
  --input-dir /app/data \
  --output-dir /app/output \
  --analyze-misuse
```

詳細なDocker使用方法については [docker/README.md](docker/README.md) を参照してください。

### 基本的な使い方（Python環境）

```python
from src.parser import TwitterDataExtractor

# エクストラクターの初期化
extractor = TwitterDataExtractor(
    input_dir="downloads",      # TwitterエクスポートJSONファイルのディレクトリ
    output_dir="parsed",        # 解析結果の出力先
    reports_dir="reports",      # レポートの出力先
    create_consolidated=True    # 統合ファイルを作成するか
)

# 全ファイルの処理を実行
stats = extractor.extract_all()
print(f"処理完了: {stats['processed_files']}ファイル, {stats['total_tweets']}ツイート")
```

### 動画無断使用の分析

```python
from src.analyzer import VideoMisuseAnalyzer

# アナライザーの初期化
analyzer = VideoMisuseAnalyzer(
    input_dir="parsed",
    output_dir="video_misuse_analysis"
)

# 分析の実行
results = analyzer.analyze_all()
```

### コマンドラインからの実行

```bash
# 基本的な抽出
python scripts/extract_tweets.py --input downloads --output parsed

# 動画分析付き
python scripts/extract_tweets.py --input downloads --output parsed --analyze-videos

# 統合ファイル作成なし（個別ファイルのみ）
python scripts/extract_tweets.py --input downloads --output parsed --no-consolidated
```

## 出力形式

### 抽出データ (JSON)

各ツイートから以下の情報を抽出：

```json
{
  "tweet_id": "1234567890",
  "screen_name": "username",
  "display_name": "表示名",
  "tweet_text": "ツイート本文",
  "timestamp": "2024-01-01T12:00:00+00:00",
  "like_count": 100,
  "retweet_count": 50,
  "reply_count": 10,
  "is_verified": true,
  "verification_type": "blue_verified",
  "language_detected": "japanese",
  "has_attached_media": true,
  "video_misuse_detected": false,
  "data_quality_score": 85
}
```

### 分析レポート

- **ユーザー違反リスト** (`video_misuse_users_*.csv`): 動画無断使用の統計
- **違反詳細** (`violation_details_*.csv`): 個別の違反記録
- **ランキング** (`user_rankings_*.json`): 各種指標によるユーザーランキング
- **統計サマリー** (`summary_statistics_*.json`): 全体的な分析結果

## 高度な機能

### カスタム言語検出

```python
from src.language_detector import LanguageDetector

detector = LanguageDetector()
result = detector.detect_languages("こんにちは！Hello!")
print(result['primary'])  # 'mixed'
print(result['script_analysis'])  # 文字種別の詳細分析
```

### バッチ処理の設定

```python
# メモリ効率的な処理
extractor = TwitterDataExtractor(
    input_dir="downloads",
    output_dir="parsed", 
    create_consolidated=False  # 個別ファイルのみ作成
)
```

## 必要要件

- Python 3.8以上
- 4GB以上のRAM（大量ファイル処理時は8GB推奨）
- TwitterからエクスポートしたJSONファイル

## プロジェクト構造

```
twitter-parse-html-analysis/
├── src/
│   ├── __init__.py
│   ├── parser.py           # メインの抽出エンジン
│   ├── analyzer.py         # 動画無断使用分析
│   ├── language_detector.py # 言語検出システム
│   └── utils.py            # ユーティリティ関数
├── scripts/
│   └── extract_tweets.py   # CLIインターフェース
├── tests/                  # テストスイート
├── examples/               # 使用例
├── data/                   # サンプルデータ
└── docs/                   # ドキュメント
```

## 注意事項

- Twitterのエクスポートデータはプライベートなものです。分析結果の共有には注意してください
- 大量のファイル処理には時間がかかります（1000ファイルで約10-20分）
- 動画無断使用の検出は100%正確ではありません。誤検出の可能性があります

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください

## 貢献

プルリクエストを歓迎します！大きな変更を行う場合は、まずissueを作成して変更内容を議論してください。

## 開発者向け

### テストの実行

```bash
# 全テストの実行
python -m pytest

# カバレッジレポート付き
python -m pytest --cov=src tests/
```

### コードフォーマット

```bash
# Black でのフォーマット
black src/ scripts/ tests/

# isort でのインポート整理
isort src/ scripts/ tests/
```

## サポート

問題や質問がある場合は、[Issues](https://github.com/yourusername/twitter-parse-html-analysis/issues)を作成してください。