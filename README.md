# クレーム報告書自動整形アプリ

## このプロジェクトについて

お客様からのクレーム内容の要点を入力すると、生成AIが**社外用**と**社内用**の報告書文面を自動整形し、最終的に**Word形式（.docx）**で出力できるようにするアプリです。

要件定義・仕様整理（Phase 0）と技術スタック選定（Phase 1）は完了し、現在は [development_procedure.md](development_procedure.md) の **Phase 2：開発環境構築** まで完了しています。技術スタックは Streamlit（Python）＋ Anthropic Claude API（プロトタイプ採用）＋ `python-docx` です（詳細は [CLAUDE.md](CLAUDE.md)）。

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

# 4. アプリを起動
streamlit run app.py
```

起動後、ブラウザで `http://localhost:8501` を開くと、動作確認用のトップページ（Phase 2時点ではまだ入力フォーム等はなし）が表示されます。

## 現在のステータス

- [x] プロジェクトフォルダ作成
- [x] 要件定義ドキュメントの初期ドラフト作成
- [x] 使用する生成AI・技術スタックの選定（Phase 1）
- [x] 開発環境構築（Phase 2：`app.py` / `requirements.txt` / `.env.example` / `.gitignore` / `pyproject.toml`）
- [ ] 入力画面の実装（Phase 3）
- [ ] AI生成機能の実装（Phase 4）

## 次にやること（Next Steps）

[development_procedure.md](development_procedure.md) の **Phase 3：入力画面の実装** に進みます。[ui_design.md](ui_design.md) の画面1のワイヤーフレームと [input_items.md](input_items.md) の入力形式に沿って、Streamlitの入力フォームを実装します。

> 迷ったときは、まず `requirements.md` に立ち返り、「このアプリは何のために存在するか」を確認してください。
