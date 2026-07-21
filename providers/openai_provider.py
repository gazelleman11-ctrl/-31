"""OpenAI APIを使った報告書生成（未実装・将来の切り替え用の受け皿）。

実装する場合の想定手順:
  1. requirements.txt に `openai` を追加し `pip install -r requirements.txt`
  2. .env に OPENAI_API_KEY を設定
  3. 以下の generate() を openai.OpenAI().chat.completions.create(...) 等で実装する
     （system_prompt と user_content を渡し、生成テキストを文字列で返すこと）
"""


def generate(system_prompt: str, user_content: str) -> str:
    raise NotImplementedError(
        "OpenAI APIプロバイダーは未実装です。providers/openai_provider.py を実装し、"
        "requirements.txt に openai を追加、.env に OPENAI_API_KEY を設定してください。"
    )
