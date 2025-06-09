# Docker Usage Guide

このドキュメントでは、TwitterHTMLパーサーをDockerで実行する方法を説明します。

## クイックスタート

### 1. データの準備

```bash
# データディレクトリを作成
mkdir -p data output reports

# TwitterエクスポートJSONファイルをdataディレクトリに配置
cp /path/to/tweets-*.json data/
```

### 2. Dockerビルド

```bash
# イメージをビルド
docker build -t twitter-html-parser .

# または docker compose を使用
docker compose build
```

### 3. 実行

```bash
# 基本的な実行
docker run --rm \
  -v $(pwd)/data:/app/data:ro \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/reports:/app/reports \
  twitter-html-parser \
  python scripts/extract_tweets.py --input-dir /app/data --output-dir /app/output

# docker compose を使用
docker compose run --rm twitter-parser \
  python scripts/extract_tweets.py --input-dir /app/data --output-dir /app/output
```

## 使用例

### データ抽出

```bash
# 基本的なデータ抽出
docker compose run --rm twitter-parser \
  python scripts/extract_tweets.py \
  --input-dir /app/data \
  --output-dir /app/output \
  --reports-dir /app/reports

# 統合ファイル作成有効
docker compose run --rm twitter-parser \
  python scripts/extract_tweets.py \
  --input-dir /app/data \
  --output-dir /app/output \
  --consolidated
```

### 動画無断使用分析

```bash
# 動画分析の実行
docker compose run --rm twitter-parser \
  python examples/video_analysis.py
```

### テスト実行

```bash
# テストコンテナでテスト実行
docker compose run --rm twitter-parser-test

# または直接テスト実行
docker compose run --rm twitter-parser \
  python -m pytest tests/ -v
```

### 開発モード

```bash
# 開発モードで起動（ソースコードがマウントされる）
docker compose run --rm twitter-parser-dev

# コンテナ内でインタラクティブに作業
root@container:/app# python scripts/extract_tweets.py --help
root@container:/app# python -m pytest tests/
root@container:/app# python examples/basic_usage.py
```

## カスタマイズ

### 環境変数

| 変数名 | 説明 | デフォルト |
|--------|------|-----------|
| `LOG_LEVEL` | ログレベル (DEBUG, INFO, WARNING, ERROR) | INFO |
| `PYTHONUNBUFFERED` | Python出力のバッファリング無効化 | 1 |

### ボリューム設定

| ホストパス | コンテナパス | 説明 |
|------------|--------------|------|
| `./data` | `/app/data` | 入力JSONファイル（読み取り専用） |
| `./output` | `/app/output` | 処理結果の出力先 |
| `./reports` | `/app/reports` | レポートファイルの出力先 |

### ポート設定

現在のバージョンではWebサーバー機能はありませんが、将来的にAPI機能を追加する場合:

```yaml
services:
  twitter-parser:
    ports:
      - "8000:8000"  # API サーバー用
```

## トラブルシューティング

### 権限エラー

```bash
# 出力ディレクトリの権限を確認
ls -la output/ reports/

# 必要に応じて権限変更
sudo chown -R $(id -u):$(id -g) output/ reports/
```

### メモリ不足

大量のJSONファイルを処理する場合:

```yaml
services:
  twitter-parser:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

### ログの確認

```bash
# コンテナのログを確認
docker compose logs twitter-parser

# リアルタイムでログを表示
docker compose logs -f twitter-parser
```

## パフォーマンスチューニング

### マルチステージビルド（本番用）

```dockerfile
# 本番用により軽量なイメージ
FROM python:3.10-alpine AS builder
# ... ビルド処理

FROM python:3.10-alpine AS runtime
# ... 実行用設定
```

### 並列処理

```bash
# 複数コンテナでの並列処理
docker compose up --scale twitter-parser=3
```

## セキュリティ

- 非rootユーザーでコンテナを実行
- 読み取り専用でデータをマウント
- 必要最小限のパッケージのみインストール
- セキュリティアップデートの定期適用