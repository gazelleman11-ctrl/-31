from datetime import date

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="クレーム報告書自動整形アプリ")


def _isoformat_or_none(value):
    return value.isoformat() if value else None


STATUS_OPTIONS = ["未対応", "対応中", "対応済み"]
REQUEST_OPTIONS = ["返金", "交換", "謝罪", "説明", "再発防止策の提示", "その他"]
SHARE_OPTIONS = ["品質管理部", "営業部", "上長", "その他"]
IMPORTANCE_OPTIONS = ["高", "中", "低"]
OUTPUT_OPTIONS = ["社外用", "社内用", "両方"]

st.title("クレーム報告書自動整形アプリ")
st.caption("* は必須項目です。入力後「AIで報告書を生成」を押してください（現時点ではAIによる生成・Word出力は未接続です）。")

with st.form("claim_input_form"):
    st.subheader("基本情報")
    received_date = st.date_input("受付日 *", value=date.today())
    occurred_date = st.date_input("発生日", value=None)
    occurred_unknown = st.checkbox("発生日は不明・未確定")
    customer_name = st.text_input("お客様名／取引先名 *")
    assignee = st.text_input("対応担当者 *")
    product_name = st.text_input("対象商品・サービス名 *")

    st.subheader("クレーム内容")
    summary = st.text_area("クレームの概要 *")
    background = st.text_area("発生経緯 *")
    customer_requests = st.multiselect("お客様の要望 * （複数選択可）", REQUEST_OPTIONS)
    customer_request_other = st.text_input("お客様の要望（「その他」を選択した場合の内容）")

    st.subheader("対応状況")
    current_status = st.selectbox("現在の対応状況 *", STATUS_OPTIONS, index=1)
    current_status_detail = st.text_area("現在の対応状況の詳細")
    future_plan = st.text_area("今後の対応予定 *")
    plan_date = st.date_input("対応予定日（任意）", value=None)

    with st.expander("社内向け補足（任意）"):
        cause_analysis = st.text_area("原因分析（暫定）")
        prevention = st.text_area("再発防止策（暫定）")
        impact_scope = st.text_area("影響範囲")
        share_targets = st.multiselect("社内共有先（複数選択可）", SHARE_OPTIONS)
        share_other = st.text_input("社内共有先（「その他」を選択した場合の内容）")
        importance = st.radio("重要度／緊急度", IMPORTANCE_OPTIONS, index=1, horizontal=True)

    st.subheader("出力設定")
    output_type = st.radio("出力する報告書の種類 *", OUTPUT_OPTIONS, index=2, horizontal=True)
    file_name = st.text_input("ファイル名（任意指定）")

    submitted = st.form_submit_button("AIで報告書を生成")

if submitted:
    errors = []
    if not customer_name:
        errors.append("お客様名／取引先名を入力してください。")
    if not assignee:
        errors.append("対応担当者を入力してください。")
    if not product_name:
        errors.append("対象商品・サービス名を入力してください。")
    if not summary:
        errors.append("クレームの概要を入力してください。")
    if not background:
        errors.append("発生経緯を入力してください。")
    if not customer_requests:
        errors.append("お客様の要望を1つ以上選択してください。")
    if not future_plan:
        errors.append("今後の対応予定を入力してください。")

    if errors:
        for message in errors:
            st.error(message)
    else:
        st.session_state["claim_data"] = {
            "received_date": received_date.isoformat(),
            "occurred_date": None if occurred_unknown else _isoformat_or_none(occurred_date),
            "customer_name": customer_name,
            "assignee": assignee,
            "product_name": product_name,
            "summary": summary,
            "background": background,
            "customer_requests": customer_requests,
            "customer_request_other": customer_request_other,
            "current_status": current_status,
            "current_status_detail": current_status_detail,
            "future_plan": future_plan,
            "plan_date": _isoformat_or_none(plan_date),
            "cause_analysis": cause_analysis,
            "prevention": prevention,
            "impact_scope": impact_scope,
            "share_targets": share_targets,
            "share_other": share_other,
            "importance": importance,
            "output_type": output_type,
            "file_name": file_name,
        }
        st.success("入力内容を受け付けました。（AIによる文面生成・Word出力はPhase 4以降で実装予定です）")

if "claim_data" in st.session_state:
    st.subheader("保持されている入力内容（確認用）")
    st.json(st.session_state["claim_data"])
