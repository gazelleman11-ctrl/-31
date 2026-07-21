"""Phase 7: 結合テスト・受け入れ確認

複数パターンのダミークレームで、入力→AI生成→編集→Word出力までの一連の流れと、
必須項目未入力時の異常系を確認する。実際の生成AI呼び出しはモック化し（本開発環境に
実APIキーがないため）、それ以外のアプリの挙動（バリデーション、状態管理、
Word出力の中身）は実コードをそのまま通す。
"""

import io
import sys
from pathlib import Path

import pytest
from docx import Document
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
APP_PATH = str(ROOT / "app.py")


@pytest.fixture
def fake_ai(monkeypatch):
    """report_generator.generate_report をダミー実装に差し替える。"""
    import report_generator

    calls = []

    def _fake(claim_data, report_type):
        calls.append(report_type)
        return f"【ダミー生成文面:{report_type}】\n\n本文サンプル（{len(calls)}回目の呼び出し）"

    monkeypatch.setattr(report_generator, "generate_report", _fake)
    return calls


@pytest.fixture
def word_export_spy(monkeypatch):
    """word_export.build_docx_bytes / build_filename の呼び出しを記録しつつ、
    実装自体はそのまま実行する（Word出力の中身も実コードで検証するため）。"""
    import word_export

    docx_calls = []
    filename_calls = []
    real_build_docx_bytes = word_export.build_docx_bytes
    real_build_filename = word_export.build_filename

    def spy_build_docx_bytes(text):
        docx_calls.append(text)
        return real_build_docx_bytes(text)

    def spy_build_filename(claim_data, report_type):
        filename_calls.append(report_type)
        return real_build_filename(claim_data, report_type)

    monkeypatch.setattr(word_export, "build_docx_bytes", spy_build_docx_bytes)
    monkeypatch.setattr(word_export, "build_filename", spy_build_filename)
    return {"docx_calls": docx_calls, "filename_calls": filename_calls}


def _radio(at, label):
    for r in at.radio:
        if r.label == label:
            return r
    raise AssertionError(f"radio not found: {label}")


def fill_required_fields(
    at, customer_name="株式会社テスト", assignee="山田 太郎", product_name="テスト商品A"
):
    at.text_input[0].set_value(customer_name).run()
    at.text_input[1].set_value(assignee).run()
    at.text_input[2].set_value(product_name).run()
    at.text_area[0].set_value("商品に傷があった").run()
    at.text_area[1].set_value("配送中に破損した可能性").run()
    at.multiselect[0].set_value(["返金", "交換"]).run()
    at.text_area[3].set_value("来週までに交換品を発送予定").run()


def submit(at):
    at.button[0].click().run(timeout=30)


# --- シナリオ1: 出力設定「両方」、任意項目もすべて入力するパターン ---
def test_full_flow_both_report_types(fake_ai, word_export_spy):
    at = AppTest.from_file(APP_PATH)
    at.run()

    fill_required_fields(at, customer_name="株式会社サンプル")
    # 任意項目（社内向け補足）も入力する
    at.text_area[4].set_value("検品工程での見落としの可能性").run()  # 原因分析
    at.text_area[5].set_value("検品項目の追加").run()  # 再発防止策
    at.text_area[6].set_value("同ロットの他出荷分は確認中").run()  # 影響範囲
    at.multiselect[1].set_value(["品質管理部"]).run()  # 社内共有先
    _radio(at, "出力する報告書の種類 *").set_value("両方").run()

    submit(at)

    assert len(at.error) == 0, [e.value for e in at.error]
    assert set(at.session_state["generated_reports"].keys()) == {"社外用", "社内用"}
    assert at.session_state["claim_data"]["customer_name"] == "株式会社サンプル"

    # プレビュー編集: 社外用の文面を編集する
    at.text_area(key="edited_社外用").set_value("編集後の社外用本文\n差出人：品質管理部").run()

    # Word出力: 編集済みテキストがbuild_docx_bytesに渡っていること
    assert "編集後の社外用本文\n差出人：品質管理部" in word_export_spy["docx_calls"]
    assert set(word_export_spy["filename_calls"][-2:]) == {"社外用", "社内用"}

    # ダウンロードボタンのファイル名が命名規則通りであること
    labels = [b.label for b in at.download_button]
    assert any("クレーム報告書_社外用_株式会社サンプル.docx" in label for label in labels), labels
    assert any("クレーム報告書_社内用.docx" in label for label in labels), labels

    # 実際に生成された.docxが正しく開けること（社内用＝未編集のためAI生成文面のまま）
    from word_export import build_docx_bytes

    docx_bytes = build_docx_bytes(at.session_state["edited_社内用"])
    doc = Document(io.BytesIO(docx_bytes))
    paragraphs = [p.text for p in doc.paragraphs]
    assert "【ダミー生成文面:社内用】" in paragraphs, paragraphs


# --- シナリオ2: 出力設定「社外用」のみ、必須項目のみ入力するパターン ---
def test_minimal_flow_external_only(fake_ai, word_export_spy):
    at = AppTest.from_file(APP_PATH)
    at.run()

    fill_required_fields(at)
    _radio(at, "出力する報告書の種類 *").set_value("社外用").run()

    submit(at)

    assert len(at.error) == 0, [e.value for e in at.error]
    assert list(at.session_state["generated_reports"].keys()) == ["社外用"]
    # タブは1種類のみのため st.tabs は使われない
    assert len(at.tabs) == 0

    labels = [b.label for b in at.download_button]
    assert len(labels) == 1
    assert "社外用報告書" in labels[0]


# --- シナリオ3: 出力設定「社内用」のみ、発生日が不明なパターン ---
def test_minimal_flow_internal_only_with_unknown_occurred_date(fake_ai, word_export_spy):
    at = AppTest.from_file(APP_PATH)
    at.run()

    fill_required_fields(at)
    at.checkbox[0].set_value(True).run()  # 発生日は不明・未確定
    _radio(at, "出力する報告書の種類 *").set_value("社内用").run()

    submit(at)

    assert len(at.error) == 0, [e.value for e in at.error]
    assert at.session_state["claim_data"]["occurred_date"] is None
    assert list(at.session_state["generated_reports"].keys()) == ["社内用"]


# --- シナリオ4（異常系）: 必須項目がすべて未入力 ---
def test_all_required_fields_empty_shows_all_errors():
    at = AppTest.from_file(APP_PATH)
    at.run()

    submit(at)

    error_messages = {e.value for e in at.error}
    expected = {
        "お客様名／取引先名を入力してください。",
        "対応担当者を入力してください。",
        "対象商品・サービス名を入力してください。",
        "クレームの概要を入力してください。",
        "発生経緯を入力してください。",
        "お客様の要望を1つ以上選択してください。",
        "今後の対応予定を入力してください。",
    }
    assert error_messages == expected
    assert "claim_data" not in at.session_state
    assert "generated_reports" not in at.session_state


# --- シナリオ5（異常系）: 一部の必須項目のみ未入力 ---
def test_partial_required_fields_shows_only_relevant_errors():
    at = AppTest.from_file(APP_PATH)
    at.run()

    # customer_name と summary 以外の必須項目を埋める
    at.text_input[1].set_value("山田 太郎").run()
    at.text_input[2].set_value("テスト商品A").run()
    at.text_area[1].set_value("配送中に破損した可能性").run()
    at.multiselect[0].set_value(["返金"]).run()
    at.text_area[3].set_value("来週までに交換品を発送予定").run()

    submit(at)

    error_messages = {e.value for e in at.error}
    assert error_messages == {
        "お客様名／取引先名を入力してください。",
        "クレームの概要を入力してください。",
    }
    assert "claim_data" not in at.session_state
