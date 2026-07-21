import io

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

# output_format.md 4章「Word（.docx）出力仕様（案）」に準拠
FONT_NAME = "MS明朝"
FONT_SIZE = Pt(10.5)
PAGE_WIDTH = Cm(21.0)  # A4
PAGE_HEIGHT = Cm(29.7)  # A4


def _set_style_east_asian_font(style, font_name):
    """python-docxのFont.nameは英数字用フォントのみ設定するため、
    日本語（東アジア文字）用フォントも別途 w:eastAsia 属性として設定する。

    Style.font の内部要素はスタイル自体（<w:style>）であり、rFontsは
    その子であるrPrの、さらに子として存在するため get_or_add_rPr() 経由で辿る。"""
    style.font.name = font_name
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is not None:
        rfonts.set(qn("w:eastAsia"), font_name)


def build_filename(claim_data: dict, report_type: str) -> str:
    """report_type: "社外用" または "社内用" """
    custom_name = (claim_data.get("file_name") or "").strip()
    if custom_name:
        base = custom_name
        if base.lower().endswith(".docx"):
            base = base[: -len(".docx")]
        return f"{base}_{report_type}.docx"

    date_str = claim_data["received_date"].replace("-", "")
    if report_type == "社外用":
        customer = claim_data["customer_name"].replace(" ", "").replace("　", "")
        return f"{date_str}_クレーム報告書_社外用_{customer}.docx"
    return f"{date_str}_クレーム報告書_社内用.docx"


def build_docx_bytes(report_text: str) -> bytes:
    document = Document()

    section = document.sections[0]
    section.page_width = PAGE_WIDTH
    section.page_height = PAGE_HEIGHT
    section.orientation = WD_ORIENT.PORTRAIT

    normal_style = document.styles["Normal"]
    _set_style_east_asian_font(normal_style, FONT_NAME)
    normal_style.font.size = FONT_SIZE

    for line in report_text.split("\n"):
        document.add_paragraph(line)

    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()
