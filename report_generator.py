from providers import get_provider
from providers.prompts import build_user_content, system_prompt_for


def generate_report(claim_data: dict, report_type: str) -> str:
    """report_type: "社外用" または "社内用"

    実際にどの生成AIサービスを使うかは環境変数 AI_PROVIDER（.env）で切り替える。
    """
    system_prompt = system_prompt_for(report_type)
    user_content = build_user_content(claim_data)
    provider = get_provider()
    return provider.generate(system_prompt, user_content)
