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

**[development_procedure.md](development_procedure.md) Phase 5（プレビュー・編集画面の実装）完了、Phase 6（Word出力機能の実装）着手前**

- Phase 5で `app.py` にプレビュー・編集画面を実装した。
  - 出力設定が「両方」の場合は `st.tabs` で社外用／社内用を切り替え表示、1種類のみの場合はタブなしで表示する。
  - 生成結果は `st.text_area`（`key="edited_{報告書種別}"`）で直接編集可能。編集内容はセッション中保持され、以後のWord出力（Phase 6）で参照する想定。
  - 報告書種別ごとに「🔄 再生成」ボタンを実装。クリック時は `pending_regenerate_{報告書種別}` フラグを立てて `st.rerun()` し、text_areaウィジェットを生成する**前**に再生成処理を行う設計にしている（生成済みウィジェットのsession_stateを直接書き換えるとStreamlitが例外を出すための回避策）。
  - `report_generator.generate_report` をモック化した `streamlit.testing.v1.AppTest` で、1種類のみ生成時の編集保持、2種類（タブ）生成時の相互独立性、再生成ボタンが他方の編集内容を壊さないことを確認済み。

- Phase 2で `app.py` / `requirements.txt` / `.env.example` / `.gitignore` / `pyproject.toml` を整備済み。
- Phase 3で `app.py` に [input_items.md](input_items.md) の全入力項目のフォームを実装済み（必須項目バリデーションつき）。
- Phase 4で `report_generator.py` を新規作成し、生成AIを使って社外用・社内用の報告書文面を生成する処理を実装した。
  - [output_format.md](output_format.md) の文体・構成ルールをシステムプロンプトに反映（社外用＝丁寧語・お詫び中心、社内用＝である調・事実区分）。
  - `app.py` の送信成功時に、選択された出力設定（社外用／社内用／両方）に応じて生成を呼び出し、結果を `st.session_state["generated_reports"]` に保持して画面に表示する。
  - **プロバイダー切り替えの受け皿**：`providers/` パッケージを新設し、生成AIの呼び出し部分をプロバイダーごとのモジュールに分離した（`providers/anthropic_provider.py` / `providers/openai_provider.py` / `providers/gemini_provider.py`）。現在は環境変数 `AI_PROVIDER`（.env、デフォルト `anthropic`）で選択し、Anthropic Claude API（`claude-haiku-4-5`、コスト最優先で検証段階として採用）のみ実装済み。OpenAI・Geminiは未実装のスタブ（呼び出すと分かりやすいメッセージ付きの `NotImplementedError`）。精度・金額感を検証した結果、別プロバイダーに切り替える場合は該当モジュールの `generate(system_prompt, user_content) -> str` を実装し、`.env` の `AI_PROVIDER` を切り替えるだけでよい構成にしてある。プロンプト生成ロジック（`providers/prompts.py`）はプロバイダー非依存で共通利用する。
  - `anthropic.AuthenticationError` / `anthropic.APIError` に加え、`NotImplementedError`（未実装プロバイダー）・その他の例外も `app.py` 側で捕捉し、分かりやすいエラーメッセージを表示する（実際に無効なキーでAPIへ到達しエラーハンドリングを確認済み）。
  - **重要な修正**：`from report_generator import ...` が `load_dotenv()` より先に実行されると `.env` のAPIキー読み込み前にクライアントが初期化されてしまうバグを発見し、クライアント生成を呼び出し時（関数内）に遅延させる形で修正した。
  - 実際の報告書生成（有効なAPIキーでの成功パス）は、この開発環境に実キーが設定されていないため未検証。ユーザー側で `.env` に実際のAPIキーを設定のうえ、動作確認が必要。

次に取り組むのは Phase 6：Word出力機能の実装。

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
- [x] 利用する生成AI（API）：**Anthropic Claude API（`claude-haiku-4-5`）を検証段階として採用**
  - 現時点では**プロトタイプ・テスト用の採用**であり、本番運用でこのまま使うかは未確定。精度・金額感を検証したうえで、OpenAI APIやGemini APIへの切り替えを検討する可能性がある。
  - そのため `providers/` パッケージでプロバイダー切り替えの受け皿を用意済み（詳細は上記「現在のフェーズ」参照）。切り替え時は `providers/openai_provider.py` または `providers/gemini_provider.py` の `generate()` を実装し、`.env` の `AI_PROVIDER` を変更するだけでよい。
  - [requirements.md](requirements.md) 9章の「利用する生成AIサービスの選定（社内のセキュリティポリシー含む）」が正式決定するまでは、テスト用途に留める。
  - APIキーは環境変数（例：`ANTHROPIC_API_KEY`）で管理し、リポジトリにはコミットしない（Phase 2で `.env` 運用と `.gitignore` を整備する）。
- [x] Word（.docx）生成方法：**`python-docx` ライブラリ**（Python/Streamlit構成と親和性が高いため採用）

> 生成AIの本番採用可否・セキュリティ確認は未完了のため、[requirements.md](requirements.md) 9章のチェック項目として引き続き管理する。

## コーディング規約

- 言語：Python 3系。命名規則はPEP 8に従う（変数・関数は `snake_case`）。
- フォーマッタ／Lint：`black` と `ruff`（設定は [pyproject.toml](pyproject.toml)）。コミット前に整形・Lintを通す。
- ディレクトリ構成：画面ロジックは `app.py` に集約する。生成AI呼び出しのみ `providers/` パッケージに分離済み（プロバイダー切り替えのため）。それ以外は機能が増えて肥大化してきた時点でモジュール分割を検討する（先回りした分割はしない）。
- 秘匿情報：APIキー等は `.env`（Git管理外）で管理し、コード中にハードコーディングしない。

## Claude Codeへの依頼時の注意事項

- このプロジェクトはまだ要件定義段階のため、「実装して」と明示的に依頼されない限り、コードは書かずMarkdownドキュメントの整理・提案にとどめること。
- 要件が曖昧な場合は、推測で仕様を決めずに確認・質問すること。
- クレーム対応という性質上、生成する文面の正確性・丁寧さは特に重視すること。

## 今後の更新予定

- 技術スタックが決まり次第、このファイルに追記する。
- 実装フェーズに入ったら、ディレクトリ構成・ビルド／実行コマンド・テスト方法などを追記する。
