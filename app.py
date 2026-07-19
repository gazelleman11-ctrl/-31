import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="クレーム報告書自動整形アプリ")

st.title("クレーム報告書自動整形アプリ")
st.write("開発環境構築（Phase 2）の動作確認用ページです。入力フォーム等はPhase 3以降で実装します。")

api_key_set = bool(os.environ.get("ANTHROPIC_API_KEY"))
st.write(f"ANTHROPIC_API_KEY: {'設定済み' if api_key_set else '未設定（.envを確認してください）'}")
