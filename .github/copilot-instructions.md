# GitHub Copilot code review instructions

このリポジトリは Twitter/X エクスポートデータを HTML 解析する Python ライブラリです。以下の観点でレビューしてください。レビューコメントは日本語で記述し、日本語と英数字の間には半角スペースを入れてください。

## 強制されているスタイル規約

- フォーマットは Black（行長 88）。isort は Black プロファイル（`pyproject.toml` 参照）。フォーマットずれは flag する。
- flake8 は `--max-complexity=10 --max-line-length=127`。複雑度超過や `E9,F63,F7,F82`（構文エラー・未定義名）は必ず flag する。
- 関数の引数・戻り値に型ヒントが無い箇所を flag する。
- 公開関数・クラス・メソッドに docstring が無い箇所を flag する。docstring とコメントは日本語。

## 重点的に確認すること

- **PII / プライバシー**: Twitter エクスポートデータは個人情報を含む。スクリーンネーム・表示名などがログ出力・エラーメッセージ・コミット対象データに混入していないか確認する。
- **機密情報**: API キー・トークン・パスワードのハードコードや、実データファイル（`*.json`, `*.csv`, `*.xlsx`, `*.xls`）・出力ディレクトリ（`parsed/`, `reports/`, `output/`, `results/`, `downloads/`）のコミットを flag する。
- **エラーハンドリング**: ファイル I/O・HTML パース・JSON 読み込みで例外を握りつぶしていないか。ユーザー向けエラーメッセージは英語になっているか。
- **HTML パースの堅牢性**: BeautifulSoup での要素取得が `None` を考慮しているか（属性・子要素が存在しない前提のアクセスは flag する）。
- **テスト**: `src/` の挙動変更に対応するテストが `tests/` に追加・更新されているか。特にパーサー変更時のテスト欠落を flag する。
- **後方互換性**: 公開 API（`TwitterDataExtractor`, `VideoMisuseAnalyzer`, `LanguageDetector`）のシグネチャやデフォルト引数の破壊的変更は、README への記載有無とあわせて指摘する。

## 誤検知しやすい既知パターン（flag しない）

- 日本語の docstring・コメント・ログメッセージ。このプロジェクトの規約であり誤りではない。
- flake8 の style 系警告のうち、CI が `--exit-zero`（警告扱い）としているもの。ビルドは失敗しないため、必須修正としては扱わない。
- `--input` と `--input-dir` のように意図的に用意された CLI 別名。
