# CLAUDE.md

このファイルは、このリポジトリでコードを扱う際のClaude Code (claude.ai/code) 向けのガイダンスを提供します。

## 会話言語

**すべての会話は日本語で行ってください。** All conversations should be conducted in Japanese.

## プロジェクト概要

twitter-parse-html-analysisは、Twitter/XのエクスポートデータをHTMLレベルで解析し、通常のAPIでは取得できない詳細情報を抽出するPythonライブラリです。

### 主な機能
- HTMLコンテンツからの高精度データ抽出
- 多言語対応の言語検出システム
- 動画無断使用の検出
- エンゲージメント分析
- リアルタイム処理とバッチ処理

## 開発方針

### コーディング規約
- PEP 8に準拠
- 型ヒントを積極的に使用
- docstringは必須（日本語で記述）
- 日本語コメントを推奨

### テスト
- 新機能には必ずユニットテストを追加
- pytestを使用
- カバレッジ80%以上を維持

### パフォーマンス
- 大量ファイル処理を想定した効率的な実装
- メモリ使用量に配慮
- 並列処理の活用

## ディレクトリ構造

```
repo/
├── src/              # ソースコード
│   ├── parser.py     # メイン処理
│   ├── analyzer.py   # 分析機能
│   └── language_detector.py  # 言語検出
├── scripts/          # CLIスクリプト
├── tests/            # テストコード
├── examples/         # 使用例
└── data/            # サンプルデータ
```

## 重要な注意事項

1. **プライバシー**: Twitterエクスポートデータは個人情報を含みます。サンプルデータを追加する際は必ず匿名化してください。

2. **APIの変更**: TwitterのエクスポートフォーマットはAPIの変更により変わる可能性があります。定期的な動作確認が必要です。

3. **ライセンス**: MITライセンスですが、依存ライブラリのライセンスも確認してください。

## よくあるタスク

### 新しい抽出フィールドの追加
1. `src/parser.py`の`_extract_comprehensive_tweet_data`メソッドに追加
2. 対応する抽出メソッドを実装
3. テストケースを追加

### 新しい言語のサポート
1. `src/language_detector.py`に言語パターンを追加
2. スコアリングロジックを更新
3. テストデータを追加

### パフォーマンス改善
1. プロファイリングで ボトルネックを特定
2. 並列処理やキャッシュの活用を検討
3. メモリ使用量をモニタリング

## デバッグのヒント

- ログレベルをDEBUGに設定して詳細情報を確認
- 個別ファイルの処理結果を確認
- HTMLパース結果を視覚的に確認（BeautifulSoupのprettify()）

## リリース前チェックリスト

- [ ] 全テストがパスすること
- [ ] ドキュメントが最新であること
- [ ] サンプルコードが動作すること
- [ ] requirements.txtが最新であること
- [ ] CHANGELOGを更新