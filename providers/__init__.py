"""生成AIプロバイダーの切り替え口。

環境変数 AI_PROVIDER（.env）で使用するプロバイダーを選択する。
デフォルトは "anthropic"。新プロバイダーを追加する際は、
providers/base.py のインターフェースに沿ったモジュールを作成し、
下記 PROVIDERS に登録するだけでよい。
"""

import os

from providers import anthropic_provider, gemini_provider, openai_provider

PROVIDERS = {
    "anthropic": anthropic_provider,
    "openai": openai_provider,
    "gemini": gemini_provider,
}


def get_provider():
    provider_name = os.environ.get("AI_PROVIDER", "anthropic")
    try:
        return PROVIDERS[provider_name]
    except KeyError:
        raise ValueError(
            f"未対応のAI_PROVIDERです: '{provider_name}'。"
            f"対応プロバイダー: {', '.join(PROVIDERS.keys())}"
        )
