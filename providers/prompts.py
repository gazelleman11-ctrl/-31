"""プロバイダーに依存しない、プロンプト生成ロジック（output_format.md の文体・構成ルールに基づく）。"""

EXTERNAL_SYSTEM_PROMPT = """あなたは日本企業のカスタマーサポート部門で、クレーム対応の社外向け報告書（お詫び状）を作成する担当者です。
以下の文体・構成ルールに従って、丁寧で誠実な社外向け報告書の本文を作成してください。

【文体・トーン】
- 丁寧語・敬語を用いる（お客様向けのビジネス文書として失礼のない表現）
- 専門用語・社内用語は避け、簡潔で分かりやすい表現にする
- お詫びの意を適切に含める
- 社内の原因分析・内部事情など、社外に開示すべきでない情報は含めない

【構成】
1. 表題（例：ご報告とお詫び）
2. 宛名（お客様名／取引先名）
3. 挨拶文
4. 発生事象の説明（簡潔に）
5. お詫びの言葉
6. 対応内容・今後の対応予定
7. 締めの挨拶
8. 差出人（会社名・部署名・担当者名）
9. 発行日

報告書の本文のみを出力してください。前置きや説明文は不要です。"""

INTERNAL_SYSTEM_PROMPT = """あなたは日本企業の品質管理部門で、クレーム対応の社内向け報告書を作成する担当者です。
以下の文体・構成ルールに従って、簡潔で客観的な社内向け報告書の本文を作成してください。

【文体・トーン】
- 簡潔・客観的な「である調」
- 事実・経緯・原因・対応・再発防止策を明確に区分して記載する
- 推測部分は「推測」「暫定」であることが分かるように明記する

【構成】
1. 表題（例：クレーム報告書（社内用））
2. 報告日／報告者
3. 基本情報（受付日、発生日、お客様名、対象商品・サービス名 等）
4. クレーム内容の詳細
5. 発生経緯
6. 原因分析（暫定含む）
7. 対応状況・対応予定
8. 再発防止策（暫定含む）
9. 影響範囲
10. 共有先・重要度

報告書の本文のみを出力してください。前置きや説明文は不要です。"""


def format_claim_data(claim_data: dict) -> str:
    lines = [
        f"受付日: {claim_data['received_date']}",
        f"発生日: {claim_data['occurred_date'] or '不明・未確定'}",
        f"お客様名／取引先名: {claim_data['customer_name']}",
        f"対応担当者: {claim_data['assignee']}",
        f"対象商品・サービス名: {claim_data['product_name']}",
        f"クレームの概要: {claim_data['summary']}",
        f"発生経緯: {claim_data['background']}",
    ]

    requests_text = "、".join(claim_data["customer_requests"])
    if claim_data.get("customer_request_other"):
        requests_text += f"（{claim_data['customer_request_other']}）"
    lines.append(f"お客様の要望: {requests_text}")

    status_text = claim_data["current_status"]
    if claim_data.get("current_status_detail"):
        status_text += f" / {claim_data['current_status_detail']}"
    lines.append(f"現在の対応状況: {status_text}")

    plan_text = claim_data["future_plan"]
    if claim_data.get("plan_date"):
        plan_text += f"（対応予定日: {claim_data['plan_date']}）"
    lines.append(f"今後の対応予定: {plan_text}")

    if claim_data.get("cause_analysis"):
        lines.append(f"原因分析（暫定）: {claim_data['cause_analysis']}")
    if claim_data.get("prevention"):
        lines.append(f"再発防止策（暫定）: {claim_data['prevention']}")
    if claim_data.get("impact_scope"):
        lines.append(f"影響範囲: {claim_data['impact_scope']}")
    if claim_data.get("share_targets"):
        targets_text = "、".join(claim_data["share_targets"])
        if claim_data.get("share_other"):
            targets_text += f"、{claim_data['share_other']}"
        lines.append(f"社内共有先: {targets_text}")

    lines.append(f"重要度／緊急度: {claim_data['importance']}")
    return "\n".join(lines)


def build_user_content(claim_data: dict) -> str:
    return "以下のクレーム情報をもとに、報告書を作成してください。\n\n" + format_claim_data(
        claim_data
    )


def system_prompt_for(report_type: str) -> str:
    """report_type: "社外用" または "社内用" """
    return EXTERNAL_SYSTEM_PROMPT if report_type == "社外用" else INTERNAL_SYSTEM_PROMPT
