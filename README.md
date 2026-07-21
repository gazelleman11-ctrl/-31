# クレーム報告書自動整形アプリ

## このプロジェクトについて

お客様からのクレーム内容の要点を入力すると、生成AIが**社外用**と**社内用**の報告書文面を自動整形し、最終的に**Word形式（.docx）**で出力できるようにするアプリです。

要件定義・仕様整理（Phase 0）〜結合テスト・受け入れ確認（Phase 7）まで完了しています（[development_procedure.md](development_procedure.md)）。技術スタックは Streamlit（Python）＋ Anthropic Claude API（`claude-haiku-4-5`、検証段階として採用）＋ `python-docx` です（詳細は [CLAUDE.md](CLAUDE.md)）。生成AIは `providers/` パッケージで切り替え可能な構成にしており、将来OpenAI APIやGemini APIへ切り替える余地を残しています。

## フォルダ構成とファイルの役割

| ファイル | 役割 |
|---|---|
| [README.md](README.md) | このファイル。プロジェクト全体の案内役 |
| [requirements.md](requirements.md) | アプリの目的・利用シーン・機能要件/非機能要件をまとめる |
| [input_items.md](input_items.md) | ユーザーが入力する項目（クレーム内容の要点など）を定義する |
| [output_format.md](output_format.md) | AIが生成する報告書（社外用/社内用）の文面構成とWord出力仕様を定義する |
| [ui_design.md](ui_design.md) | 入力〜確認〜出力の画面構成・画面遷移・ワイヤーフレームを定義する |
| [development_procedure.md](development_procedure.md) | 実装フェーズで何をどの順番で進めるかをまとめた開発手順書 |
| [CLAUDE.md](CLAUDE.md) | 今後Claude Code等のAIアシスタントと開発を進める際の方針・ルールをまとめる |
| [app.py](app.py) | Streamlitアプリのエントリーポイント（Phase 2時点では動作確認用の最小画面） |
| [requirements.txt](requirements.txt) | Pythonの依存パッケージ一覧 |
| [.env.example](.env.example) | 環境変数（APIキー等）のひな形。コピーして `.env` を作成する |
| [pyproject.toml](pyproject.toml) | black／ruff（フォーマッタ・Lint）の設定 |
| [report_generator.py](report_generator.py) | 入力内容から報告書文面を生成する処理の呼び出し口（プロバイダーへディスパッチ） |
| [providers/](providers/) | 生成AIプロバイダーの切り替え口。`prompts.py`（共通プロンプト生成）、`anthropic_provider.py`（実装済み）、`openai_provider.py`／`gemini_provider.py`（未実装スタブ） |
| [word_export.py](word_export.py) | 編集済みの報告書文面から `.docx` ファイル（A4・MS明朝）を生成する処理 |
| [tests/](tests/) | 結合テスト（`pytest` + Streamlit AppTest）。正常系3パターン・異常系2パターンを自動検証 |
| [requirements-dev.txt](requirements-dev.txt) | 開発用の追加依存（`pytest` / `black` / `ruff`） |

### 読む順番（初めての方向け）

1. **requirements.md** — まず「何のためのアプリか」「誰が使うか」「どんな機能が必要か」を確認します。
2. **input_items.md** — ユーザーがアプリに何を入力するのかを具体化します。
3. **output_format.md** — AIが出力する報告書がどんな形式・構成になるかを確認します。
4. **ui_design.md** — 入力から出力までの画面イメージを確認します。
5. **development_procedure.md** — 実装をどのフェーズ・順番で進めるかを確認します。
6. **CLAUDE.md** — 実装フェーズに入るときの開発ルール・進め方を確認します。

## アプリの起動方法（Phase 2で構築した開発環境）

```bash
# 1. 仮想環境を作成・有効化（初回のみ作成）
python -m venv .venv
source .venv/Scripts/activate   # Windows(Git Bash)の場合。PowerShellなら .venv\Scripts\Activate.ps1

# 2. 依存パッケージをインストール
pip install -r requirements.txt

# 3. 環境変数ファイルを用意（初回のみ）
cp .env.example .env
# .env を開き、ANTHROPIC_API_KEY に実際のAPIキーを設定する
# （AI_PROVIDER で使用する生成AIプロバイダーを切り替え可能。現在は anthropic のみ実装済み）

# 4. アプリを起動
streamlit run app.py
```

起動後、ブラウザで `http://localhost:8501` を開くとアプリが表示されます。

### テストの実行方法

```bash
pip install -r requirements-dev.txt
pytest tests/
```

AI生成部分はモック化されているため、実際のAPIキーがなくてもテストは実行できます。

## 現在のステータス

- [x] プロジェクトフォルダ作成
- [x] 要件定義ドキュメントの初期ドラフト作成
- [x] 使用する生成AI・技術スタックの選定（Phase 1）
- [x] 開発環境構築（Phase 2：`app.py` / `requirements.txt` / `.env.example` / `.gitignore` / `pyproject.toml`）
- [x] 入力画面の実装（Phase 3：`app.py` に全入力項目のフォームを実装、バリデーション動作を確認済み）
- [x] AI生成機能の実装（Phase 4：`report_generator.py` + `providers/` を実装、Claude API（`claude-haiku-4-5`）で社外用・社内用の文面を生成。プロバイダー切り替え可能な構成）
- [x] プレビュー・編集画面の実装（Phase 5：タブ切り替え・編集可能なtext_area・再生成ボタンを実装）
- [x] Word出力機能の実装（Phase 6：`word_export.py` を実装、編集済み文面から `.docx` をダウンロード可能に）
- [x] 結合テスト・受け入れ確認（Phase 7：`tests/test_end_to_end.py` に正常系3・異常系2パターンの自動テストを実装。実利用者レビューは未対応）
- [ ] リリース準備（Phase 8）

## 次にやること（Next Steps）

[development_procedure.md](development_procedure.md) の **Phase 8：リリース準備** に進みます。

> **要対応（ユーザー側）**
> 1. `.env` の `ANTHROPIC_API_KEY` に実際のAPIキーを設定し、実際に報告書が生成されることを確認してください（この開発環境には実キーがなく、成功パスは未検証です）。
> 2. 実際のクレーム対応担当者にアプリをレビューしてもらい、フィードバックを反映してください（AIアシスタントでは代行できません）。

> 迷ったときは、まず `requirements.md` に立ち返り、「このアプリは何のために存在するか」を確認してください。
