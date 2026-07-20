# CLAUDE.md

このファイルは、このプロジェクトでClaude Code（AIアシスタント）と開発を進める際の方針・ルールをまとめたものです。

## プロジェクト概要

クレーム内容の要点を入力すると、生成AIが社外用・社内用の報告書文面を自動整形し、Word形式（.docx）で出力するアプリを開発する。

詳細は以下を参照：
- 要件定義：[requirements.md](requirements.md)
- 入力項目：[input_items.md](input_items.md)
- 出力フォーマット：[output_format.md](output_format.md)
- 画面設計：[ui_design.md](ui_design.md)
- 開発手順：[development_procedure.md](development_procedure.md)

## 現在のフェーズ

**[development_procedure.md](development_procedure.md) Phase 4（AI生成機能の実装）完了、Phase 5（プレビュー・編集画面の実装）着手前**

- Phase 2で `app.py` / `requirements.txt` / `.env.example` / `.gitignore` / `pyproject.toml` を整備済み。
- Phase 3で `app.py` に [input_items.md](input_items.md) の全入力項目のフォームを実装済み（必須項目バリデーションつき）。
- Phase 4で `report_generator.py` を新規作成し、Anthropic Claude API（`claude-haiku-4-5`。コスト最優先で採用、今後のモデル選定に応じて変更予定）を使って社外用・社内用の報告書文面を生成する処理を実装した。
  - [output_format.md](output_format.md) の文体・構成ルールをシステムプロンプトに反映（社外用＝丁寧語・お詫び中心、社内用＝である調・事実区分）。
  - `app.py` の送信成功時に、選択された出力設定（社外用／社内用／両方）に応じて生成を呼び出し、結果を `st.session_state["generated_reports"]` に保持して画面に表示する。
  - `anthropic.AuthenticationError` / `anthropic.APIError` を捕捉し、APIキー未設定時にも分かりやすいエラーメッセージを表示する（実際に無効なキーでAPIへ到達しエラーハンドリングを確認済み）。
  - **重要な修正**：`from report_generator import ...` が `load_dotenv()` より先に実行されると `.env` のAPIキー読み込み前にクライアントが初期化されてしまうバグを発見し、クライアント生成を呼び出し時（関数内）に遅延させる形で修正した。
  - 実際の報告書生成（有効なAPIキーでの成功パス）は、この開発環境に実キーが設定されていないため未検証。ユーザー側で `.env` に実際のAPIキーを設定のうえ、動作確認が必要。

次に取り組むのは Phase 5：プレビュー・編集画面の実装。

## 開発方針（実装フェーズに入ったら）

- 要件定義書（3ファイル）の内容と矛盾する実装をしない。仕様に迷ったら、まず該当するMarkdownファイルを確認・更新してから実装する。
- 段階的に小さく作る。いきなり全機能を実装せず、まずは「入力→AIによる文面生成→画面表示」までの最小構成（MVP）を優先する。Word出力は次のステップとする。
- 過剰な抽象化・将来を見越した汎用設計はしない。今必要な機能だけをシンプルに実装する。
- クレーム内容には個人情報・機微情報が含まれる可能性があるため、取り扱いには十分注意する（ログ出力やAIへの送信内容に個人情報を含めないなど）。

## 技術スタック（Phase 1で決定・2026-07-19時点）

- [x] アプリ形態／UI形式：**Streamlit（Python）による社内向けWebアプリ**
  - フロントエンドとバックエンドを分けず、1つのPythonアプリとして実装する。
  - `ui_design.md` のカレンダー入力・チェックボックス・ラジオボタン・タブ切り替えは、いずれもStreamlit標準コンポーネント（`st.date_input` / `st.multiselect` / `st.radio` / `st.tabs` 等）で実現する。
- [x] バックエンド言語・フレームワーク：**Python 3系 + Streamlit**（上記と同一。別途バックエンドは持たない）
- [x] 利用する生成AI（API）：**Anthropic Claude API**
  - 現時点では**プロトタイプ・テスト用の採用**であり、本番運用でこのまま使うかは未確定。[requirements.md](requirements.md) 9章の「利用する生成AIサービスの選定（社内のセキュリティポリシー含む）」が正式決定するまでは、テスト用途に留める。
  - APIキーは環境変数（例：`ANTHROPIC_API_KEY`）で管理し、リポジトリにはコミットしない（Phase 2で `.env` 運用と `.gitignore` を整備する）。
- [x] Word（.docx）生成方法：**`python-docx` ライブラリ**（Python/Streamlit構成と親和性が高いため採用）

> 生成AIの本番採用可否・セキュリティ確認は未完了のため、[requirements.md](requirements.md) 9章のチェック項目として引き続き管理する。

## コーディング規約

- 言語：Python 3系。命名規則はPEP 8に従う（変数・関数は `snake_case`）。
- フォーマッタ／Lint：`black` と `ruff`（設定は [pyproject.toml](pyproject.toml)）。コミット前に整形・Lintを通す。
- ディレクトリ構成：現時点ではMVPのため `app.py` 1ファイルに集約する。機能が増えて肥大化してきたら、その時点でモジュール分割を検討する（先回りした分割はしない）。
- 秘匿情報：APIキー等は `.env`（Git管理外）で管理し、コード中にハードコーディングしない。

## Claude Codeへの依頼時の注意事項

- このプロジェクトはまだ要件定義段階のため、「実装して」と明示的に依頼されない限り、コードは書かずMarkdownドキュメントの整理・提案にとどめること。
- 要件が曖昧な場合は、推測で仕様を決めずに確認・質問すること。
- クレーム対応という性質上、生成する文面の正確性・丁寧さは特に重視すること。

## 今後の更新予定

- 技術スタックが決まり次第、このファイルに追記する。
- 実装フェーズに入ったら、ディレクトリ構成・ビルド／実行コマンド・テスト方法などを追記する。
