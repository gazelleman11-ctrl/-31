from datetime import date

import anthropic
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from report_generator import generate_report  # noqa: E402 (must load .env first)
from word_export import build_docx_bytes, build_filename  # noqa: E402

st.set_page_config(page_title="クレーム報告書自動整形アプリ")


def _isoformat_or_none(value):
    return value.isoformat() if value else None


def _try_generate(report_type):
    """成功時は (text, None)、失敗時は (None, エラーメッセージ) を返す。"""
    try:
        return generate_report(st.session_state["claim_data"], report_type), None
    except anthropic.AuthenticationError:
        return (
            None,
            "AIへの接続に失敗しました。.env のAPIキーが正しく設定されているか確認してください。",
        )
    except anthropic.APIError as e:
        return None, f"AIによる報告書生成でエラーが発生しました: {e}"
    except NotImplementedError as e:
        return None, str(e)
    except Exception as e:
        return None, f"想定外のエラーが発生しました: {e}"


STATUS_OPTIONS = ["未対応", "対応中", "対応済み"]
REQUEST_OPTIONS = ["返金", "交換", "謝罪", "説明", "再発防止策の提示", "その他"]
SHARE_OPTIONS = ["品質管理部", "営業部", "上長", "その他"]
IMPORTANCE_OPTIONS = ["高", "中", "低"]
OUTPUT_OPTIONS = ["社外用", "社内用", "両方"]

st.title("クレーム報告書自動整形アプリ")
st.caption("* は必須項目です。入力後「AIで報告書を生成」を押してください。")

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

        report_types = {"社外用": ["社外用"], "社内用": ["社内用"], "両方": ["社外用", "社内用"]}[
            output_type
        ]
        generated_reports = {}
        with st.spinner("AIが報告書を作成しています…"):
            for report_type in report_types:
                text, error = _try_generate(report_type)
                if error:
                    st.error(error)
                    break
                generated_reports[report_type] = text
                st.session_state[f"edited_{report_type}"] = text

        if generated_reports:
            st.session_state["generated_reports"] = generated_reports
            st.success("報告書を生成しました。内容を確認・編集してください。")

if "claim_data" in st.session_state:
    st.subheader("保持されている入力内容（確認用）")
    st.json(st.session_state["claim_data"])

if "generated_reports" in st.session_state:
    report_types = list(st.session_state["generated_reports"].keys())

    # 再生成ボタンの処理は、対応するtext_areaウィジェットを生成する前に行う。
    # （生成済みウィジェットのsession_stateを後から書き換えるとStreamlitがエラーになるため）
    for report_type in report_types:
        pending_key = f"pending_regenerate_{report_type}"
        if st.session_state.get(pending_key):
            st.session_state[pending_key] = False
            with st.spinner(f"{report_type}報告書を再生成しています…"):
                text, error = _try_generate(report_type)
            if error:
                st.session_state[f"regen_error_{report_type}"] = error
            else:
                st.session_state["generated_reports"][report_type] = text
                st.session_state[f"edited_{report_type}"] = text

    st.subheader("AIが生成した報告書")
    st.caption("内容を確認し、必要に応じて編集してください。編集した内容がWord出力に使用されます。")

    tabs = st.tabs(report_types) if len(report_types) > 1 else [st.container()]
    for report_type, tab in zip(report_types, tabs):
        with tab:
            edit_key = f"edited_{report_type}"
            if edit_key not in st.session_state:
                st.session_state[edit_key] = st.session_state["generated_reports"][report_type]

            error_key = f"regen_error_{report_type}"
            if st.session_state.get(error_key):
                st.error(st.session_state[error_key])
                st.session_state[error_key] = None

            st.text_area(f"{report_type}報告書の内容", height=350, key=edit_key)

            if st.button(f"🔄 {report_type}報告書を再生成", key=f"regenerate_btn_{report_type}"):
                st.session_state[f"pending_regenerate_{report_type}"] = True
                st.rerun()

    st.subheader("Word出力")
    for report_type in report_types:
        edited_text = st.session_state[f"edited_{report_type}"]
        docx_bytes = build_docx_bytes(edited_text)
        filename = build_filename(st.session_state["claim_data"], report_type)
        st.download_button(
            label=f"⬇ {report_type}報告書（{filename}）をダウンロード",
            data=docx_bytes,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"download_{report_type}",
        )
