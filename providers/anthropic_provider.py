"""Anthropic Claude APIを使った報告書生成（現在の検証段階での採用プロバイダー）。"""

import anthropic

# コスト最優先で検証段階はHaiku 4.5を採用。精度・金額感の検証結果に応じて変更する。
MODEL_ID = "claude-haiku-4-5"


def generate(system_prompt: str, user_content: str) -> str:
    # .env の読み込みタイミングに依存しないよう、クライアントは呼び出し時に生成する
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL_ID,
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return next(block.text for block in response.content if block.type == "text")
