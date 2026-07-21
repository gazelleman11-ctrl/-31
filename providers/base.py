"""生成AIプロバイダーが実装すべき共通インターフェース。

新しいプロバイダーを追加する場合は、この関数シグネチャに合わせて
`generate(system_prompt, user_content) -> str` を実装したモジュールを作成し、
providers/__init__.py の PROVIDERS に登録する。
"""

from typing import Protocol


class ReportProvider(Protocol):
    def generate(self, system_prompt: str, user_content: str) -> str:
        """system_prompt・user_content から報告書の本文（プレーンテキスト）を生成して返す。"""
        ...
