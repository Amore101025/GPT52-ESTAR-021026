import os
import io
import re
import json
import time
import base64
import random
import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

import streamlit as st
import yaml  # PyYAML
import httpx  # font download

# PDF engines
from fpdf import FPDF  # fpdf2
from pypdf import PdfReader, PdfWriter  # pypdf

# ReportLab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import mm as RL_MM
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="WOW Agentic PDF Studio",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# i18n
# ----------------------------
I18N = {
    "en": {
        "app_title": "WOW Agentic PDF Studio",
        "tagline": "Turn forms or specs into dynamic, fillable PDFs — with an agentic workflow.",
        "nav_dashboard": "Dashboard",
        "nav_form": "Form → Dynamic PDF",
        "nav_pipeline": "Agent Pipeline",
        "nav_spec": "PDF Build Spec → Dynamic PDF",
        "nav_notes": "AI Note Keeper",
        "nav_settings": "Settings & API Keys",
        "nav_history": "History / Versions",
        "ui_language": "Language",
        "ui_theme": "Theme",
        "ui_theme_light": "Light",
        "ui_theme_dark": "Dark",
        "ui_style": "Painter Style",
        "ui_jackpot": "Jackpot",
        "ui_reset": "Reset UI",
        "ui_status": "Status",
        "status_idle": "Idle",
        "status_running": "Running",
        "status_awaiting": "Awaiting review",
        "status_done": "Completed",
        "status_failed": "Failed",
        "providers": "Providers",
        "provider_ready": "Ready",
        "provider_missing": "Missing key",
        "dash_overview": "Overview",
        "dash_recent": "Recent Activity",
        "dash_field_stats": "Field Stats",
        "dash_pipeline_health": "Pipeline Health",
        "dash_latency": "Latency (last run)",
        "dash_tokens": "Token Budget",
        "dash_cost": "Cost Estimate",
        "dash_not_available": "Not available",
        "dash_pdf_ready": "PDF Ready",
        "form_input": "Form Input",
        "form_use_default": "Use default sample (sample.md)",
        "form_use_custom": "Provide new application form",
        "form_paste": "Paste text / Markdown",
        "form_upload": "Upload file (.txt, .md, .docx)",
        "form_loaded": "Loaded content",
        "form_preview": "Preview",
        "form_next": "Proceed to pipeline",
        "pipeline_title": "Agent Pipeline (Step-by-step, editable)",
        "pipeline_model": "Model",
        "pipeline_max_tokens": "Max tokens",
        "pipeline_prompt": "Prompt (editable)",
        "pipeline_output": "Output (editable)",
        "pipeline_run_step": "Run this step",
        "pipeline_run_from_here": "Run from this step onward",
        "pipeline_accept": "Accept output",
        "pipeline_reset_output": "Reset to generated",
        "pipeline_view_text": "Text",
        "pipeline_view_md": "Markdown",
        "notes_title": "AI Note Keeper",
        "notes_paste": "Paste a note (txt / markdown)",
        "notes_transform": "Transform to organized Markdown",
        "notes_keywords": "Keywords highlighting (coral default)",
        "notes_magics": "AI Magics",
        "notes_magic_keywords": "AI Keywords (custom color)",
        "notes_magic_outline": "AI Outline Builder",
        "notes_magic_actions": "AI Action Items Extractor",
        "notes_magic_minutes": "AI Meeting Minutes Formatter",
        "notes_magic_simplify": "AI Simplify & Clarify",
        "notes_magic_qa": "AI Q&A Generator",
        "history_title": "History / Versions",
        "history_empty": "No saved versions yet.",
        "btn_save_version": "Save version",
        "btn_restore": "Restore",
        "btn_delete": "Delete",
        # Spec tab
        "spec_title": "PDF Build Spec → Dynamic PDF",
        "spec_subtitle": "Paste YAML/JSON spec (or Markdown-wrapped) to generate a Unicode-safe fillable PDF.",
        "spec_source": "Spec source",
        "spec_use_last": "Use last valid spec",
        "spec_paste_new": "Paste new spec",
        "spec_load_default": "Load defaultpdfspec.md",
        "spec_editor": "Spec editor (YAML/JSON or Markdown-wrapped)",
        "spec_validate": "Validate spec",
        "spec_generate": "Generate",
        "spec_reset_last_valid": "Reset to last valid spec",
        "spec_strict": "Strict mode (fail on warnings)",
        "spec_units": "Units (input)",
        "spec_unit_mm": "mm",
        "spec_unit_pt": "pt",
        "spec_page_size": "Page size (fallback)",
        "spec_a4": "A4",
        "spec_letter": "Letter",
        "spec_preview": "Preview",
        "spec_download": "Download",
        "spec_open_new_tab": "Open PDF in a new tab",
        "spec_upload_pdf": "Upload modified PDF",
        "spec_reconcile": "Reconcile uploaded PDF vs spec",
        "spec_render_log": "Render log",
        "spec_validation": "Validation report",
        "spec_reconcile_report": "Reconciliation report",
        "spec_no_pdf": "No PDF generated yet.",
        "spec_save_version": "Save version (spec + artifact)",
        # Engine + download format
        "engine": "PDF engine",
        "engine_fpdf2": "fpdf2",
        "engine_reportlab": "ReportLab",
        "download_format": "Download format",
        "download_pdf": "PDF",
        "download_py": "PY (generator script)",
        "download_js": "JS (jsPDF script)",
        "download_artifact": "Download artifact",
        # Fonts
        "font_status": "Unicode fonts",
        "font_ready": "Ready",
        "font_downloading": "Downloading…",
        "font_failed": "Unavailable (will sanitize label text)",
    },
    "zh-TW": {
        "app_title": "WOW 代理式 PDF 工作室",
        "tagline": "把表單或規格轉成動態可填寫 PDF — 以代理式流程逐步完成。",
        "nav_dashboard": "儀表板",
        "nav_form": "表單 → 動態 PDF",
        "nav_pipeline": "代理流程",
        "nav_spec": "PDF 建置規格 → 動態 PDF",
        "nav_notes": "AI 筆記管家",
        "nav_settings": "設定與 API 金鑰",
        "nav_history": "歷史 / 版本",
        "ui_language": "語言",
        "ui_theme": "主題",
        "ui_theme_light": "亮色",
        "ui_theme_dark": "暗色",
        "ui_style": "畫家風格",
        "ui_jackpot": "隨機彩蛋",
        "ui_reset": "重置 UI",
        "ui_status": "狀態",
        "status_idle": "待命",
        "status_running": "執行中",
        "status_awaiting": "等待審核",
        "status_done": "完成",
        "status_failed": "失敗",
        "providers": "供應商",
        "provider_ready": "可用",
        "provider_missing": "缺少金鑰",
        "dash_overview": "總覽",
        "dash_recent": "近期活動",
        "dash_field_stats": "欄位統計",
        "dash_pipeline_health": "流程健康度",
        "dash_latency": "延遲（上次執行）",
        "dash_tokens": "Token 預算",
        "dash_cost": "費用估算",
        "dash_not_available": "不可用",
        "dash_pdf_ready": "PDF 就緒",
        "form_input": "表單輸入",
        "form_use_default": "使用預設範例（sample.md）",
        "form_use_custom": "提供新的申請表",
        "form_paste": "貼上文字 / Markdown",
        "form_upload": "上傳檔案（.txt, .md, .docx）",
        "form_loaded": "已載入內容",
        "form_preview": "預覽",
        "form_next": "前往代理流程",
        "pipeline_title": "代理流程（逐步執行、可編輯）",
        "pipeline_model": "模型",
        "pipeline_max_tokens": "Max tokens",
        "pipeline_prompt": "提示詞（可編輯）",
        "pipeline_output": "輸出（可編輯）",
        "pipeline_run_step": "執行此步驟",
        "pipeline_run_from_here": "從此步驟往後全部執行",
        "pipeline_accept": "接受輸出",
        "pipeline_reset_output": "重置為生成結果",
        "pipeline_view_text": "文字",
        "pipeline_view_md": "Markdown",
        "notes_title": "AI 筆記管家",
        "notes_paste": "貼上筆記（txt / markdown）",
        "notes_transform": "轉為有組織的 Markdown",
        "notes_keywords": "關鍵字標註（預設珊瑚色）",
        "notes_magics": "AI 魔法",
        "notes_magic_keywords": "AI 關鍵字（自訂顏色）",
        "notes_magic_outline": "AI 大綱整理",
        "notes_magic_actions": "AI 行動項目擷取",
        "notes_magic_minutes": "AI 會議記錄格式化",
        "notes_magic_simplify": "AI 精簡與釐清",
        "notes_magic_qa": "AI 問答生成",
        "history_title": "歷史 / 版本",
        "history_empty": "目前尚無已儲存版本。",
        "btn_save_version": "儲存版本",
        "btn_restore": "還原",
        "btn_delete": "刪除",
        # Spec tab
        "spec_title": "PDF 建置規格 → 動態 PDF",
        "spec_subtitle": "貼上 YAML/JSON 規格（可用 Markdown 包住）以生成支援 Unicode 的可填寫 PDF。",
        "spec_source": "規格來源",
        "spec_use_last": "使用上次有效規格",
        "spec_paste_new": "貼上新規格",
        "spec_load_default": "載入 defaultpdfspec.md",
        "spec_editor": "規格編輯器（YAML/JSON 或 Markdown 包裝）",
        "spec_validate": "驗證規格",
        "spec_generate": "生成",
        "spec_reset_last_valid": "重置為上次有效規格",
        "spec_strict": "嚴格模式（有警告就失敗）",
        "spec_units": "單位（輸入）",
        "spec_unit_mm": "mm",
        "spec_unit_pt": "pt",
        "spec_page_size": "紙張大小（備援）",
        "spec_a4": "A4",
        "spec_letter": "Letter",
        "spec_preview": "預覽",
        "spec_download": "下載",
        "spec_open_new_tab": "在新分頁開啟 PDF",
        "spec_upload_pdf": "上傳已修改的 PDF",
        "spec_reconcile": "比對：上傳 PDF vs 規格",
        "spec_render_log": "渲染記錄",
        "spec_validation": "驗證報告",
        "spec_reconcile_report": "比對報告",
        "spec_no_pdf": "尚未生成 PDF。",
        "spec_save_version": "儲存版本（規格 + 產出物）",
        # Engine + download format
        "engine": "PDF 引擎",
        "engine_fpdf2": "fpdf2",
        "engine_reportlab": "ReportLab",
        "download_format": "下載格式",
        "download_pdf": "PDF",
        "download_py": "PY（產生器腳本）",
        "download_js": "JS（jsPDF 腳本）",
        "download_artifact": "下載產出物",
        # Fonts
        "font_status": "Unicode 字型",
        "font_ready": "可用",
        "font_downloading": "下載中…",
        "font_failed": "不可用（將清理文字避免崩潰）",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return I18N.get(lang, I18N["en"]).get(key, key)


# ----------------------------
# Painter styles (20)
# ----------------------------
@dataclass
class PainterStyle:
    key: str
    name_en: str
    name_zh: str
    description: str
    palette_light: Dict[str, str]
    palette_dark: Dict[str, str]
    font_family: str = "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial"


PAINTER_STYLES: List[PainterStyle] = [
    PainterStyle("vangogh", "Vincent van Gogh", "梵谷", "Bold strokes, warmth.",
                 {"bg": "#FBF6EA", "fg": "#1A1A1A", "card": "#FFFFFF", "border": "#E8DCC2", "accent": "#2A6F97", "accent2": "#FCA311"},
                 {"bg": "#0B1320", "fg": "#EDEDED", "card": "#121B2B", "border": "#1E2A44", "accent": "#2A9D8F", "accent2": "#F4D35E"}),
    PainterStyle("monet", "Claude Monet", "莫內", "Soft gradients, calm.",
                 {"bg": "#F4FAFB", "fg": "#14213D", "card": "#FFFFFF", "border": "#D7EEF2", "accent": "#277DA1", "accent2": "#90BE6D"},
                 {"bg": "#09151A", "fg": "#EAF6F7", "card": "#0F222A", "border": "#183642", "accent": "#4D96FF", "accent2": "#6BCB77"}),
    PainterStyle("picasso", "Pablo Picasso", "畢卡索", "Geometric rhythm.",
                 {"bg": "#FAFAFA", "fg": "#111827", "card": "#FFFFFF", "border": "#E5E7EB", "accent": "#2563EB", "accent2": "#F59E0B"},
                 {"bg": "#0B0F19", "fg": "#F3F4F6", "card": "#101827", "border": "#1F2937", "accent": "#60A5FA", "accent2": "#FBBF24"}),
    PainterStyle("dali", "Salvador Dalí", "達利", "Surreal contrast.",
                 {"bg": "#FFF7ED", "fg": "#1F2937", "card": "#FFFFFF", "border": "#FED7AA", "accent": "#7C3AED", "accent2": "#EF4444"},
                 {"bg": "#120B1C", "fg": "#F5F3FF", "card": "#1A1028", "border": "#2B1B3E", "accent": "#A78BFA", "accent2": "#FB7185"}),
    PainterStyle("davinci", "Leonardo da Vinci", "達文西", "Parchment restraint.",
                 {"bg": "#FBF3E4", "fg": "#2B2B2B", "card": "#FFFFFF", "border": "#E7D2B1", "accent": "#6B4F2A", "accent2": "#2F6F6D"},
                 {"bg": "#17120A", "fg": "#F3E9D7", "card": "#1E170D", "border": "#2D2214", "accent": "#D4A373", "accent2": "#4D908E"}),
    PainterStyle("michelangelo", "Michelangelo", "米開朗基羅", "Marble neutrals.",
                 {"bg": "#F7F7F7", "fg": "#111111", "card": "#FFFFFF", "border": "#E2E2E2", "accent": "#374151", "accent2": "#B91C1C"},
                 {"bg": "#0D0F12", "fg": "#F5F5F5", "card": "#141820", "border": "#222833", "accent": "#9CA3AF", "accent2": "#F87171"}),
    PainterStyle("rembrandt", "Rembrandt", "林布蘭", "Chiaroscuro gold.",
                 {"bg": "#FFF8E7", "fg": "#1C1917", "card": "#FFFFFF", "border": "#E7D6B7", "accent": "#92400E", "accent2": "#0F766E"},
                 {"bg": "#0E0B07", "fg": "#F5EBDD", "card": "#15100B", "border": "#2A1D12", "accent": "#F59E0B", "accent2": "#2DD4BF"}),
    PainterStyle("vermeer", "Johannes Vermeer", "維梅爾", "Quiet blues.",
                 {"bg": "#F2F6FF", "fg": "#0F172A", "card": "#FFFFFF", "border": "#DDE6F7", "accent": "#1D4ED8", "accent2": "#EAB308"},
                 {"bg": "#0A1022", "fg": "#E8EEFF", "card": "#0F1935", "border": "#1A2A57", "accent": "#60A5FA", "accent2": "#FDE047"}),
    PainterStyle("klimt", "Gustav Klimt", "克林姆", "Gold ornament.",
                 {"bg": "#FFFBEB", "fg": "#1F2937", "card": "#FFFFFF", "border": "#FDE68A", "accent": "#B45309", "accent2": "#7C3AED"},
                 {"bg": "#130F07", "fg": "#FFF7D6", "card": "#1B150B", "border": "#3B2F16", "accent": "#FBBF24", "accent2": "#C4B5FD"}),
    PainterStyle("kandinsky", "Wassily Kandinsky", "康丁斯基", "Abstract energy.",
                 {"bg": "#F8FAFC", "fg": "#0F172A", "card": "#FFFFFF", "border": "#E2E8F0", "accent": "#EF4444", "accent2": "#3B82F6"},
                 {"bg": "#070B12", "fg": "#E2E8F0", "card": "#0C1220", "border": "#1C2A44", "accent": "#FB7185", "accent2": "#60A5FA"}),
    PainterStyle("pollock", "Jackson Pollock", "波洛克", "High contrast punch.",
                 {"bg": "#FFFFFF", "fg": "#111827", "card": "#FAFAFA", "border": "#E5E7EB", "accent": "#111827", "accent2": "#10B981"},
                 {"bg": "#050505", "fg": "#FAFAFA", "card": "#0E0E0E", "border": "#222222", "accent": "#F97316", "accent2": "#34D399"}),
    PainterStyle("matisse", "Henri Matisse", "馬諦斯", "Warm blocks.",
                 {"bg": "#FFF5F5", "fg": "#1F2937", "card": "#FFFFFF", "border": "#FED7D7", "accent": "#E11D48", "accent2": "#2563EB"},
                 {"bg": "#1A0B0F", "fg": "#FFE4EA", "card": "#241017", "border": "#3B1723", "accent": "#FB7185", "accent2": "#93C5FD"}),
    PainterStyle("munch", "Edvard Munch", "孟克", "Moody alert tones.",
                 {"bg": "#FDF2F8", "fg": "#111827", "card": "#FFFFFF", "border": "#FBCFE8", "accent": "#7F1D1D", "accent2": "#0EA5E9"},
                 {"bg": "#12060C", "fg": "#FCE7F3", "card": "#1C0B12", "border": "#3A1226", "accent": "#F87171", "accent2": "#38BDF8"}),
    PainterStyle("kahlo", "Frida Kahlo", "芙烈達·卡蘿", "Botanical vivid accents.",
                 {"bg": "#F0FDF4", "fg": "#052E16", "card": "#FFFFFF", "border": "#BBF7D0", "accent": "#16A34A", "accent2": "#DC2626"},
                 {"bg": "#05140B", "fg": "#DCFCE7", "card": "#0A1E11", "border": "#12351F", "accent": "#4ADE80", "accent2": "#FB7185"}),
    PainterStyle("warhol", "Andy Warhol", "安迪·沃荷", "Pop neon accents.",
                 {"bg": "#FDF4FF", "fg": "#111827", "card": "#FFFFFF", "border": "#F5D0FE", "accent": "#A21CAF", "accent2": "#2563EB"},
                 {"bg": "#130414", "fg": "#FAE8FF", "card": "#1F0820", "border": "#3B0F3D", "accent": "#E879F9", "accent2": "#93C5FD"}),
    PainterStyle("hokusai", "Hokusai", "北齋", "Wave blues.",
                 {"bg": "#F0F9FF", "fg": "#0F172A", "card": "#FFFFFF", "border": "#BAE6FD", "accent": "#0369A1", "accent2": "#F97316"},
                 {"bg": "#04131C", "fg": "#E0F2FE", "card": "#071E2B", "border": "#0C3144", "accent": "#38BDF8", "accent2": "#FDBA74"}),
    PainterStyle("qibaishi", "Qi Baishi", "齊白石", "Ink simplicity.",
                 {"bg": "#FFFEF7", "fg": "#111111", "card": "#FFFFFF", "border": "#EEE6D9", "accent": "#C1121F", "accent2": "#1D3557"},
                 {"bg": "#0B0A08", "fg": "#F5F1E8", "card": "#141210", "border": "#292420", "accent": "#F87171", "accent2": "#93C5FD"}),
    PainterStyle("zhangdaqian", "Zhang Daqian", "張大千", "Splash-ink elegance.",
                 {"bg": "#F6FFFE", "fg": "#0F172A", "card": "#FFFFFF", "border": "#D1FAE5", "accent": "#065F46", "accent2": "#1D4ED8"},
                 {"bg": "#041310", "fg": "#D1FAE5", "card": "#07241D", "border": "#0E3A2F", "accent": "#34D399", "accent2": "#93C5FD"}),
    PainterStyle("okeeffe", "Georgia O’Keeffe", "喬治亞·歐姬芙", "Modern calm.",
                 {"bg": "#FFF7ED", "fg": "#111827", "card": "#FFFFFF", "border": "#FFEDD5", "accent": "#EA580C", "accent2": "#0F766E"},
                 {"bg": "#160C05", "fg": "#FFEDD5", "card": "#1E1208", "border": "#3A210F", "accent": "#FDBA74", "accent2": "#2DD4BF"}),
    PainterStyle("turner", "J.M.W. Turner", "透納", "Luminous haze.",
                 {"bg": "#FFFAF0", "fg": "#1F2937", "card": "#FFFFFF", "border": "#FDE2C5", "accent": "#F59E0B", "accent2": "#3B82F6"},
                 {"bg": "#100B06", "fg": "#FFF3D6", "card": "#191108", "border": "#2D1E10", "accent": "#FBBF24", "accent2": "#93C5FD"}),
    PainterStyle("studio_minimal", "Studio Minimal (Bonus)", "工作室極簡（加碼）", "Ultra-clean readability.",
                 {"bg": "#F9FAFB", "fg": "#111827", "card": "#FFFFFF", "border": "#E5E7EB", "accent": "#2563EB", "accent2": "#10B981"},
                 {"bg": "#0B1220", "fg": "#E5E7EB", "card": "#0F1A2E", "border": "#1C2B4A", "accent": "#60A5FA", "accent2": "#34D399"}),
]
STYLE_BY_KEY = {s.key: s for s in PAINTER_STYLES}


# ----------------------------
# File defaults
# ----------------------------
DEFAULT_SAMPLE_MD = """# Application Form (Mock Sample)

## Section A - Applicant Information
1. Full Name *Required*
2. Date of Birth (MM/DD/YYYY)
3. Email Address *Required*
4. Phone Number
5. Address (Street, City, State/Province, Postal Code)

## Section B - Submission Details
1. Submission Type (choose one): 510(k), PMA, De Novo
2. Device Name *Required*
3. Submission Date (default: today)

## Section C - Declarations
- [ ] I confirm the information provided is accurate. *Required*
- [ ] I agree to the terms and conditions.

## Section D - Additional Notes
Provide any supporting details (multi-line).

## Section E - Signature
Signature Name (typed)
Date
"""

DEFAULT_PDFSPEC_MD = """# Default PDF Build Spec (YAML)

```yaml
document:
  title: "申請表 — Mock Application (Unicode)"
  page_size: "A4"
  orientation: "portrait"
  unit: "mm"
  margin: { left: 12, top: 12, right: 12, bottom: 12 }
fonts:
  default: { family: "DejaVuSans", size: 11 }
  cjk: { family: "NotoSansTC", size: 11 }

pages:
  - number: 1
    elements:
      - type: "label"
        text: "申請表 — Mock Application (Unicode)"
        x: 12
        y: 14
        size: 14
        style: "B"

      - type: "label"
        text: "Applicant Information / 申請人資料"
        x: 12
        y: 26
        size: 12
        style: "B"

      - type: "label"
        text: "Full Name / 姓名:"
        x: 12
        y: 36
      - type: "field"
        field_type: "text"
        id: "full_name"
        name: "Full_Name"
        x: 55
        y: 33.5
        w: 140
        h: 8
        required: true

      - type: "label"
        text: "Submission Type / 送件類型:"
        x: 12
        y: 48
      - type: "field"
        field_type: "dropdown"
        id: "submission_type"
        name: "Submission_Type"
        x: 55
        y: 45.5
        w: 70
        h: 8
        options: ["510(k)", "PMA", "De Novo"]

      - type: "label"
        text: "Confirm Accuracy / 確認資料正確:"
        x: 12
        y: 60
      - type: "field"
        field_type: "checkbox"
        id: "confirm"
        name: "Confirm"
        x: 75
        y: 58
        w: 5
        h: 5

      - type: "label"
        text: "Additional Notes / 補充說明:"
        x: 12
        y: 72
      - type: "field"
        field_type: "textarea"
        id: "notes"
        name: "Notes"
        x: 12
        y: 76
        w: 183
        h: 40
        multiline: true
```


"""


def ensure_file(path: str, content: str):
    try:
        p = Path(path)
        if not p.exists():
            p.write_text(content, encoding="utf-8")
    except Exception:
        # Some deployments may be read-only; session still works.
        pass


def load_file_or_default(path: str, default: str) -> str:
    try:
        p = Path(path)
        if p.exists():
            return p.read_text(encoding="utf-8")
    except Exception:
        pass
    return default


# ----------------------------
# Unicode fonts (TTF) — used by BOTH engines
# ----------------------------
FONTS_DIR = Path("fonts_cache")
FONTS_DIR.mkdir(exist_ok=True)

# DejaVuSans (Unicode Latin + punctuation)
DEJAVU_URL = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
# Noto Sans TC Regular TTF (Traditional Chinese)
NOTO_TC_TTF_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTC/NotoSansTC-Regular.ttf"

FONT_REGISTRY = {
    "DejaVuSans": {"path": FONTS_DIR / "DejaVuSans.ttf", "url": DEJAVU_URL},
    "NotoSansTC": {"path": FONTS_DIR / "NotoSansTC-Regular.ttf", "url": NOTO_TC_TTF_URL},
}

CJK_RE = re.compile(r"[\u2E80-\u2EFF\u3000-\u303F\u3040-\u30FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")


def download_font_if_missing(font_key: str, timeout_s: float = 30.0) -> bool:
    meta = FONT_REGISTRY.get(font_key)
    if not meta:
        return False
    path: Path = meta["path"]
    if path.exists() and path.stat().st_size > 100_000:
        return True
    url = meta["url"]
    try:
        with httpx.stream("GET", url, timeout=timeout_s, follow_redirects=True) as r:
            r.raise_for_status()
            data = b"".join(r.iter_bytes())
        path.write_bytes(data)
        return True
    except Exception:
        return False


def ensure_unicode_fonts() -> Dict[str, Any]:
    status = {"DejaVuSans": False, "NotoSansTC": False}
    for k in status.keys():
        status[k] = download_font_if_missing(k)
    status["ready_any"] = any(status.values())
    status["ready_all"] = all(status.values())
    return status


def sanitize_to_latin1(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        "—": "-",
        "–": "-",
        "•": "-",
        "…": "...",
        "’": "'",
        "‘": "'",
        "“": '"',
        "”": '"',
        "\u00A0": " ",  # NBSP
    }
    for a, b in replacements.items():
        text = text.replace(a, b)
    return text.encode("latin-1", "replace").decode("latin-1")


# ----------------------------
# Spec parsing/validation
# ----------------------------
MM_PER_PT = 0.3527777778


def extract_structured_block(text: str) -> Tuple[str, str]:
    m = re.search(r"```(?:yaml|yml)\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return "yaml", m.group(1).strip()
    m = re.search(r"```json\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return "json", m.group(1).strip()
    return "raw", (text or "").strip()


def parse_pdfspec(text: str) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    kind, payload = extract_structured_block(text)
    if not payload:
        return None, ["Spec is empty."]
    errors: List[str] = []
    if kind in ("yaml", "raw"):
        try:
            obj = yaml.safe_load(payload)
            if isinstance(obj, dict):
                return obj, []
        except Exception as e:
            errors.append(f"YAML parse error: {e}")
    if kind in ("json", "raw"):
        try:
            obj = json.loads(payload)
            if isinstance(obj, dict):
                return obj, []
        except Exception as e:
            errors.append(f"JSON parse error: {e}")
    return None, errors or ["Parsed content is not an object/dict."]


def normalize_units_in_place(spec: Dict[str, Any], target_unit: str) -> Tuple[List[str], List[str]]:
    warnings, errors = [], []
    doc = spec.get("document", {}) or {}
    unit = (doc.get("unit") or target_unit or "mm").lower()
    if unit not in ("mm", "pt"):
        warnings.append(f"Unknown unit '{unit}', assuming '{target_unit}'.")
        unit = target_unit

    def convert(v: Any) -> Any:
        if isinstance(v, (int, float)):
            if unit == target_unit:
                return float(v)
            if unit == "pt" and target_unit == "mm":
                return float(v) * MM_PER_PT
            if unit == "mm" and target_unit == "pt":
                return float(v) / MM_PER_PT
        return v

    margin = doc.get("margin") or {}
    if isinstance(margin, dict):
        for k in ("left", "top", "right", "bottom"):
            if k in margin:
                margin[k] = convert(margin[k])

    pages = spec.get("pages")
    if isinstance(pages, list):
        for p in pages:
            elements = (p or {}).get("elements")
            if not isinstance(elements, list):
                continue
            for el in elements:
                if not isinstance(el, dict):
                    continue
                for k in ("x", "y", "w", "h"):
                    if k in el:
                        el[k] = convert(el[k])

    doc["unit"] = target_unit
    spec["document"] = doc
    return warnings, errors


def validate_pdfspec(spec: Dict[str, Any], unit_fallback: str, page_fallback: str) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    if not isinstance(spec, dict):
        return {"errors": ["Spec is not an object."], "warnings": [], "normalized": None}

    doc = spec.get("document")
    if not isinstance(doc, dict):
        errors.append("Missing or invalid 'document' object.")
        doc = {}

    page_size = (doc.get("page_size") or page_fallback or "A4").upper()
    if page_size not in ("A4", "LETTER"):
        warnings.append(f"Unsupported page_size '{page_size}', falling back to A4.")
        page_size = "A4"
    doc["page_size"] = page_size

    orientation = (doc.get("orientation") or "portrait").lower()
    if orientation not in ("portrait", "landscape"):
        warnings.append(f"Unsupported orientation '{orientation}', using portrait.")
        orientation = "portrait"
    doc["orientation"] = orientation

    norm_unit = (unit_fallback or "mm").lower()
    if norm_unit not in ("mm", "pt"):
        norm_unit = "mm"

    # Deep copy then normalize
    spec_norm = json.loads(json.dumps(spec))
    spec_norm.setdefault("document", {})
    spec_norm["document"].update(doc)
    w2, e2 = normalize_units_in_place(spec_norm, target_unit=norm_unit)
    warnings.extend(w2)
    errors.extend(e2)

    pages = spec_norm.get("pages")
    if not isinstance(pages, list) or not pages:
        errors.append("Missing or empty 'pages' array.")
        return {"errors": errors, "warnings": warnings, "normalized": None}

    field_ids = set()
    counts = {"text": 0, "textarea": 0, "checkbox": 0, "dropdown": 0, "radio": 0, "unknown": 0}

    for pi, p in enumerate(pages, start=1):
        if not isinstance(p, dict):
            errors.append(f"Page {pi} is not an object.")
            continue
        elements = p.get("elements")
        if not isinstance(elements, list):
            errors.append(f"Page {pi}: missing/invalid 'elements' array.")
            continue

        for ei, el in enumerate(elements, start=1):
            if not isinstance(el, dict):
                continue
            et = (el.get("type") or "").lower()
            if et not in ("label", "field"):
                warnings.append(f"Page {pi} element {ei}: unknown type '{el.get('type')}'.")
                continue

            if "x" not in el or "y" not in el or not isinstance(el.get("x"), (int, float)) or not isinstance(el.get("y"), (int, float)):
                errors.append(f"Page {pi} element {ei}: missing numeric x/y.")

            if et == "label":
                if not isinstance(el.get("text"), str) or not el.get("text"):
                    warnings.append(f"Page {pi} label {ei}: missing text.")
            else:
                for k in ("w", "h"):
                    if k not in el or not isinstance(el.get(k), (int, float)):
                        errors.append(f"Page {pi} field {ei}: missing numeric {k}.")

                fid = el.get("id")
                if not isinstance(fid, str) or not fid.strip():
                    errors.append(f"Page {pi} field {ei}: missing string id.")
                else:
                    if fid in field_ids:
                        errors.append(f"Duplicate field id '{fid}'.")
                    field_ids.add(fid)

                ftype = (el.get("field_type") or "").lower()
                if ftype in counts:
                    counts[ftype] += 1
                else:
                    counts["unknown"] += 1
                    warnings.append(f"Field '{fid}': unsupported field_type '{ftype}' (fallback).")

                if ftype in ("dropdown", "radio"):
                    opts = el.get("options")
                    if not isinstance(opts, list) or not opts:
                        errors.append(f"Field '{fid}': '{ftype}' requires non-empty options.")

    return {
        "errors": errors,
        "warnings": warnings,
        "normalized": spec_norm,
        "field_stats": {"total": sum(counts.values()), "by_type": counts, "unique_ids": len(field_ids)},
    }


# ----------------------------
# Coordinate + page size helpers
# ----------------------------
def page_dims_mm(page_size: str, orientation: str) -> Tuple[float, float]:
    # returns (width_mm, height_mm) in portrait base, then applies orientation
    if page_size.upper() == "LETTER":
        w_pt, h_pt = LETTER
    else:
        w_pt, h_pt = A4
    w_mm = w_pt / RL_MM
    h_mm = h_pt / RL_MM
    if orientation.lower() == "landscape":
        return h_mm, w_mm
    return w_mm, h_mm


def fpdf_format_orientation(page_size: str, orientation: str) -> Tuple[str, str]:
    fmt = "LETTER" if page_size.upper() == "LETTER" else "A4"
    orient = "L" if orientation.lower() == "landscape" else "P"
    return fmt, orient


def choose_font_family_for_text(text: str, default_family: str, cjk_family: str, available: Dict[str, bool]) -> str:
    if isinstance(text, str) and CJK_RE.search(text):
        if available.get(cjk_family):
            return cjk_family
    if available.get(default_family):
        return default_family
    return "Helvetica"


# ----------------------------
# Engine A: fpdf2 generator (Unicode + AcroForm)
# ----------------------------
def fpdf2_register_fonts(pdf: FPDF, render_log: List[str]) -> Dict[str, bool]:
    reg: Dict[str, bool] = {}
    for family, meta in FONT_REGISTRY.items():
        try:
            path = meta["path"]
            if path.exists():
                pdf.add_font(family, style="", fname=str(path), uni=True)
                reg[family] = True
                render_log.append(f"fpdf2: font registered {family} -> {path}")
            else:
                reg[family] = False
                render_log.append(f"fpdf2: font missing {family}")
        except Exception as e:
            reg[family] = False
            render_log.append(f"fpdf2: font register failed {family} err={e}")
    return reg


def generate_pdf_fpdf2(spec_norm: Dict[str, Any]) -> Tuple[bytes, List[str]]:
    render_log: List[str] = []
    doc = spec_norm.get("document") or {}
    page_size = (doc.get("page_size") or "A4").upper()
    orientation = (doc.get("orientation") or "portrait").lower()

    fmt, orient = fpdf_format_orientation(page_size, orientation)
    pdf = FPDF(orientation=orient, unit="mm", format=fmt)
    pdf.set_auto_page_break(auto=False)

    fonts_cfg = spec_norm.get("fonts") or {}
    default_cfg = (fonts_cfg.get("default") or {}) if isinstance(fonts_cfg, dict) else {}
    cjk_cfg = (fonts_cfg.get("cjk") or {}) if isinstance(fonts_cfg, dict) else {}
    default_family = str(default_cfg.get("family") or "DejaVuSans")
    cjk_family = str(cjk_cfg.get("family") or "NotoSansTC")
    base_size = float(default_cfg.get("size") or 11.0)

    # Ensure fonts downloaded
    fs = st.session_state.get("unicode_fonts_status")
    if fs is None:
        fs = ensure_unicode_fonts()
        st.session_state.unicode_fonts_status = fs

    available = fpdf2_register_fonts(pdf, render_log)

    pages = spec_norm.get("pages") or []
    for p in pages:
        pdf.add_page()
        elements = (p or {}).get("elements") or []
        for el in elements:
            if not isinstance(el, dict):
                continue
            et = (el.get("type") or "").lower()

            if et == "label":
                txt = str(el.get("text") or "")
                family = choose_font_family_for_text(txt, default_family, cjk_family, available)
                if family == "Helvetica" and not available.get(default_family) and not available.get(cjk_family):
                    txt = sanitize_to_latin1(txt)
                    render_log.append("fpdf2: sanitized label text (no unicode fonts available)")

                x = float(el.get("x") or 0)
                y = float(el.get("y") or 0)
                size = float(el.get("size") or base_size)
                style = (el.get("style") or "").upper()
                # Bold with TTF requires separate files; we fall back gracefully.
                try:
                    pdf.set_font(family, style=style, size=size)
                except Exception:
                    pdf.set_font(family, size=size)
                    if style:
                        render_log.append(f"fpdf2: style '{style}' unavailable for {family}; used regular")

                pdf.set_xy(x, y)
                pdf.multi_cell(w=0, h=5, text=txt)

            elif et == "field":
                fid = str(el.get("id") or "")
                ftype = (el.get("field_type") or "text").lower()
                name = el.get("name") or fid
                x = float(el.get("x") or 0)
                y = float(el.get("y") or 0)
                w = float(el.get("w") or 40)
                h = float(el.get("h") or 8)
                value = el.get("value")
                multiline = bool(el.get("multiline") or ftype == "textarea")
                try:
                    if ftype in ("text", "textarea"):
                        kwargs = {}
                        if value is not None:
                            kwargs["value"] = str(value)
                        if multiline:
                            kwargs["multiline"] = True
                        pdf.form_text(name=str(name), x=x, y=y, w=w, h=h, **kwargs)
                    elif ftype in ("dropdown", "combo"):
                        options = el.get("options") or []
                        pdf.form_combo(name=str(name), x=x, y=y, w=w, h=h, options=[str(o) for o in options])
                    elif ftype == "checkbox":
                        pdf.form_checkbox(name=str(name), x=x, y=y, w=w, h=h)
                    else:
                        pdf.form_text(name=str(name), x=x, y=y, w=w, h=h, value=str(value) if value else "")
                        render_log.append(f"fpdf2: fallback field type '{ftype}' -> text for {fid}")
                except Exception as e:
                    # hard fallback placeholder
                    pdf.set_draw_color(120, 120, 120)
                    pdf.rect(x, y, w, h)
                    pdf.set_xy(x + 1.5, y + 1.5)
                    pdf.set_font("Helvetica", size=max(8, int(base_size - 1)))
                    pdf.cell(w=w - 3, h=h - 3, text=sanitize_to_latin1(f"[{ftype}] {name}"), border=0)
                    render_log.append(f"fpdf2: field render failed {fid} err={e}")

    out = pdf.output(dest="S")
    pdf_bytes = bytes(out) if isinstance(out, (bytes, bytearray)) else out.encode("latin-1")
    return pdf_bytes, render_log


# ----------------------------
# Engine B: ReportLab generator (Unicode + AcroForm)
# ----------------------------
def reportlab_register_fonts(render_log: List[str]) -> Dict[str, bool]:
    # Register fonts globally in pdfmetrics (safe to call multiple times)
    reg: Dict[str, bool] = {}
    for family, meta in FONT_REGISTRY.items():
        try:
            p = meta["path"]
            if p.exists():
                # Avoid double-register exceptions by checking name presence
                try:
                    pdfmetrics.getFont(family)
                    reg[family] = True
                    render_log.append(f"reportlab: font already registered {family}")
                except KeyError:
                    pdfmetrics.registerFont(TTFont(family, str(p)))
                    reg[family] = True
                    render_log.append(f"reportlab: font registered {family} -> {p}")
            else:
                reg[family] = False
                render_log.append(f"reportlab: font missing {family}")
        except Exception as e:
            reg[family] = False
            render_log.append(f"reportlab: font register failed {family} err={e}")
    return reg


def rl_font_for_text(text: str, default_family: str, cjk_family: str, available: Dict[str, bool]) -> str:
    if isinstance(text, str) and CJK_RE.search(text) and available.get(cjk_family):
        return cjk_family
    if available.get(default_family):
        return default_family
    return "Helvetica"


def generate_pdf_reportlab(spec_norm: Dict[str, Any]) -> Tuple[bytes, List[str]]:
    render_log: List[str] = []
    doc = spec_norm.get("document") or {}
    page_size = (doc.get("page_size") or "A4").upper()
    orientation = (doc.get("orientation") or "portrait").lower()

    w_mm, h_mm = page_dims_mm(page_size, orientation)
    w_pt, h_pt = w_mm * RL_MM, h_mm * RL_MM

    fonts_cfg = spec_norm.get("fonts") or {}
    default_cfg = (fonts_cfg.get("default") or {}) if isinstance(fonts_cfg, dict) else {}
    cjk_cfg = (fonts_cfg.get("cjk") or {}) if isinstance(fonts_cfg, dict) else {}
    default_family = str(default_cfg.get("family") or "DejaVuSans")
    cjk_family = str(cjk_cfg.get("family") or "NotoSansTC")
    base_size = float(default_cfg.get("size") or 11.0)

    # Ensure fonts downloaded
    fs = st.session_state.get("unicode_fonts_status")
    if fs is None:
        fs = ensure_unicode_fonts()
        st.session_state.unicode_fonts_status = fs

    available = reportlab_register_fonts(render_log)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(w_pt, h_pt))

    # A simple “top-left mm” coordinate conversion:
    # spec y is from top; ReportLab y is from bottom.
    def y_label_top_to_rl(y_mm: float) -> float:
        return h_pt - (y_mm * RL_MM)

    def y_field_top_to_rl(y_mm: float, field_h_mm: float) -> float:
        return h_pt - (y_mm * RL_MM) - (field_h_mm * RL_MM)

    pages = spec_norm.get("pages") or []
    for page_i, p in enumerate(pages, start=1):
        elements = (p or {}).get("elements") or []
        for el in elements:
            if not isinstance(el, dict):
                continue
            et = (el.get("type") or "").lower()

            if et == "label":
                txt = str(el.get("text") or "")
                family = rl_font_for_text(txt, default_family, cjk_family, available)
                if family == "Helvetica" and not available.get(default_family) and not available.get(cjk_family):
                    txt = sanitize_to_latin1(txt)
                    render_log.append("reportlab: sanitized label text (no unicode fonts available)")

                x_mm = float(el.get("x") or 0.0)
                y_mm = float(el.get("y") or 0.0)
                size = float(el.get("size") or base_size)
                # style "B" not handled unless a bold font is registered; ignore (log only)
                style = (el.get("style") or "").upper()
                if style:
                    render_log.append(f"reportlab: label style '{style}' is treated as hint (no bold font mapping)")

                c.setFont(family, size)
                # drawString uses baseline; move a bit down for a nicer alignment vs spec's top coordinate
                c.drawString(x_mm * RL_MM, y_label_top_to_rl(y_mm) - 3, txt)

            elif et == "field":
                fid = str(el.get("id") or "")
                ftype = (el.get("field_type") or "text").lower()
                name = str(el.get("name") or fid)
                x_mm = float(el.get("x") or 0.0)
                y_mm = float(el.get("y") or 0.0)
                w_mm_ = float(el.get("w") or 40.0)
                h_mm_ = float(el.get("h") or 8.0)
                value = el.get("value")
                multiline = bool(el.get("multiline") or ftype == "textarea")

                x = x_mm * RL_MM
                y = y_field_top_to_rl(y_mm, h_mm_)
                w = w_mm_ * RL_MM
                h = h_mm_ * RL_MM

                try:
                    if ftype in ("text", "textarea"):
                        # fieldFlags: 4096 => multiline
                        flags = 4096 if multiline else 0
                        c.acroForm.textfield(
                            name=name,
                            x=x, y=y, width=w, height=h,
                            value=str(value) if value is not None else "",
                            borderStyle="inset",
                            forceBorder=True,
                            fieldFlags=flags,
                            fontName=default_family if available.get(default_family) else "Helvetica",
                            fontSize=max(8, base_size),
                        )
                    elif ftype == "checkbox":
                        c.acroForm.checkbox(
                            name=name,
                            x=x, y=y,
                            size=min(w, h),
                            checked=bool(value) if value is not None else False,
                            buttonStyle="check",
                            borderWidth=1,
                        )
                    elif ftype in ("dropdown", "combo"):
                        options = el.get("options") or []
                        c.acroForm.choice(
                            name=name,
                            x=x, y=y, width=w, height=h,
                            options=[str(o) for o in options],
                            value=str(value) if value is not None else "",
                            fieldFlags=0,
                            borderStyle="inset",
                            forceBorder=True,
                            fontName=default_family if available.get(default_family) else "Helvetica",
                            fontSize=max(8, base_size),
                        )
                    else:
                        c.acroForm.textfield(
                            name=name,
                            x=x, y=y, width=w, height=h,
                            value=str(value) if value is not None else "",
                            borderStyle="inset",
                            forceBorder=True,
                            fontName=default_family if available.get(default_family) else "Helvetica",
                            fontSize=max(8, base_size),
                        )
                        render_log.append(f"reportlab: fallback field type '{ftype}' -> text for {fid}")
                except Exception as e:
                    # fallback: draw a rectangle placeholder
                    c.rect(x, y, w, h, stroke=1, fill=0)
                    c.setFont("Helvetica", max(7, int(base_size - 1)))
                    c.drawString(x + 2, y + h / 2, sanitize_to_latin1(f"[{ftype}] {name}"))
                    render_log.append(f"reportlab: field render failed {fid} err={e}")

        if page_i < len(pages):
            c.showPage()

    c.save()
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes, render_log


# ----------------------------
# Post-process: set NeedAppearances (helps some viewers show/edit fields)
# ----------------------------
def set_need_appearances(pdf_bytes: bytes) -> Tuple[bytes, bool]:
    try:
        r = PdfReader(io.BytesIO(pdf_bytes))
        w = PdfWriter()
        for page in r.pages:
            w.add_page(page)
        root = w._root_object  # pylint: disable=protected-access
        acro = root.get("/AcroForm")
        if acro is None:
            # If no acroform exists, nothing to set
            out = io.BytesIO()
            w.write(out)
            return out.getvalue(), False
        acro.update({"/NeedAppearances": True})
        out = io.BytesIO()
        w.write(out)
        return out.getvalue(), True
    except Exception:
        return pdf_bytes, False


# ----------------------------
# Export scripts (PY / JS) based on spec
# ----------------------------
def safe_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def build_py_script_fpdf2(spec_norm: Dict[str, Any]) -> str:
    # Best-effort standalone script (requires fpdf2 + downloaded fonts alongside script).
    return f"""# Generated by WOW Agentic PDF Studio (fpdf2)
# Requirements: fpdf2
# Fonts: place DejaVuSans.ttf and NotoSansTC-Regular.ttf in ./fonts_cache or adjust paths

import json
from fpdf import FPDF

SPEC = {safe_json(spec_norm)}

FONT_PATHS = {{
  "DejaVuSans": "fonts_cache/DejaVuSans.ttf",
  "NotoSansTC": "fonts_cache/NotoSansTC-Regular.ttf",
}}

def choose_font(text, default_family="DejaVuSans", cjk_family="NotoSansTC"):
    for ch in text:
        if '\\u4e00' <= ch <= '\\u9fff':
            return cjk_family
    return default_family

def main():
    doc = SPEC.get("document", {{}})
    page_size = (doc.get("page_size") or "A4").upper()
    orientation = (doc.get("orientation") or "portrait").lower()
    fmt = "LETTER" if page_size == "LETTER" else "A4"
    orient = "L" if orientation == "landscape" else "P"

    pdf = FPDF(orientation=orient, unit="mm", format=fmt)
    pdf.set_auto_page_break(auto=False)

    # Register fonts
    for fam, path in FONT_PATHS.items():
        try:
            pdf.add_font(fam, style="", fname=path, uni=True)
        except Exception:
            pass

    fonts = SPEC.get("fonts", {{}})
    default_family = (fonts.get("default") or {{}}).get("family", "DejaVuSans")
    cjk_family = (fonts.get("cjk") or {{}}).get("family", "NotoSansTC")
    base_size = float((fonts.get("default") or {{}}).get("size", 11))

    for page in SPEC.get("pages", []):
        pdf.add_page()
        for el in (page or {{}}).get("elements", []):
            if (el.get("type") or "").lower() == "label":
                txt = str(el.get("text") or "")
                fam = choose_font(txt, default_family, cjk_family)
                x = float(el.get("x") or 0)
                y = float(el.get("y") or 0)
                size = float(el.get("size") or base_size)
                pdf.set_font(fam, size=size)
                pdf.set_xy(x, y)
                pdf.multi_cell(w=0, h=5, text=txt)
            elif (el.get("type") or "").lower() == "field":
                fid = str(el.get("id") or "")
                ftype = (el.get("field_type") or "text").lower()
                name = el.get("name") or fid
                x = float(el.get("x") or 0)
                y = float(el.get("y") or 0)
                w = float(el.get("w") or 40)
                h = float(el.get("h") or 8)
                multiline = bool(el.get("multiline") or ftype == "textarea")
                if ftype in ("text", "textarea"):
                    pdf.form_text(name=str(name), x=x, y=y, w=w, h=h, multiline=multiline)
                elif ftype in ("dropdown", "combo"):
                    opts = el.get("options") or []
                    pdf.form_combo(name=str(name), x=x, y=y, w=w, h=h, options=[str(o) for o in opts])
                elif ftype == "checkbox":
                    pdf.form_checkbox(name=str(name), x=x, y=y, w=w, h=h)
                else:
                    pdf.form_text(name=str(name), x=x, y=y, w=w, h=h)

    pdf.output("dynamic_form.pdf")

if __name__ == "__main__":
    main()
"""


def build_py_script_reportlab(spec_norm: Dict[str, Any]) -> str:
    return f"""# Generated by WOW Agentic PDF Studio (ReportLab)
# Requirements: reportlab
# Fonts: place DejaVuSans.ttf and NotoSansTC-Regular.ttf in ./fonts_cache or adjust paths

import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

SPEC = {safe_json(spec_norm)}

FONT_PATHS = {{
  "DejaVuSans": "fonts_cache/DejaVuSans.ttf",
  "NotoSansTC": "fonts_cache/NotoSansTC-Regular.ttf",
}}

def page_dims_mm(page_size, orientation):
    w_pt, h_pt = LETTER if page_size.upper() == "LETTER" else A4
    w_mm, h_mm = w_pt/mm, h_pt/mm
    return (h_mm, w_mm) if orientation.lower() == "landscape" else (w_mm, h_mm)

def has_cjk(text):
    return any('\\u4e00' <= ch <= '\\u9fff' for ch in text)

def main():
    doc = SPEC.get("document", {{}})
    page_size = (doc.get("page_size") or "A4").upper()
    orientation = (doc.get("orientation") or "portrait").lower()

    w_mm, h_mm = page_dims_mm(page_size, orientation)
    w_pt, h_pt = w_mm*mm, h_mm*mm

    # Register fonts
    for fam, path in FONT_PATHS.items():
        try:
            try:
                pdfmetrics.getFont(fam)
            except KeyError:
                pdfmetrics.registerFont(TTFont(fam, path))
        except Exception:
            pass

    fonts = SPEC.get("fonts", {{}})
    default_family = (fonts.get("default") or {{}}).get("family", "DejaVuSans")
    cjk_family = (fonts.get("cjk") or {{}}).get("family", "NotoSansTC")
    base_size = float((fonts.get("default") or {{}}).get("size", 11))

    c = canvas.Canvas("dynamic_form.pdf", pagesize=(w_pt, h_pt))

    def y_label(y_mm):
        return h_pt - y_mm*mm

    def y_field(y_mm, h_mm_):
        return h_pt - y_mm*mm - h_mm_*mm

    pages = SPEC.get("pages", [])
    for pi, p in enumerate(pages, start=1):
        for el in (p or {{}}).get("elements", []):
            if (el.get("type") or "").lower() == "label":
                txt = str(el.get("text") or "")
                fam = cjk_family if has_cjk(txt) else default_family
                x_mm = float(el.get("x") or 0)
                y_mm = float(el.get("y") or 0)
                size = float(el.get("size") or base_size)
                c.setFont(fam, size)
                c.drawString(x_mm*mm, y_label(y_mm)-3, txt)
            elif (el.get("type") or "").lower() == "field":
                fid = str(el.get("id") or "")
                ftype = (el.get("field_type") or "text").lower()
                name = str(el.get("name") or fid)
                x_mm = float(el.get("x") or 0)
                y_mm = float(el.get("y") or 0)
                w_mm_ = float(el.get("w") or 40)
                h_mm_ = float(el.get("h") or 8)
                x, y, w, h = x_mm*mm, y_field(y_mm, h_mm_), w_mm_*mm, h_mm_*mm
                if ftype in ("text", "textarea"):
                    flags = 4096 if bool(el.get("multiline") or ftype=="textarea") else 0
                    c.acroForm.textfield(name=name, x=x, y=y, width=w, height=h, fieldFlags=flags, fontName=default_family, fontSize=max(8, base_size))
                elif ftype == "checkbox":
                    c.acroForm.checkbox(name=name, x=x, y=y, size=min(w, h), buttonStyle="check")
                elif ftype in ("dropdown", "combo"):
                    opts = el.get("options") or []
                    c.acroForm.choice(name=name, x=x, y=y, width=w, height=h, options=[str(o) for o in opts], fontName=default_family, fontSize=max(8, base_size))
                else:
                    c.acroForm.textfield(name=name, x=x, y=y, width=w, height=h, fontName=default_family, fontSize=max(8, base_size))

        if pi < len(pages):
            c.showPage()

    c.save()

if __name__ == "__main__":
    main()
"""


def infer_fields_for_jspdf(spec_norm: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert our PDFSpec to a minimal FormStructure-like object for jsPDF sample.
    Best-effort label association: uses nearest preceding label.
    """
    doc = spec_norm.get("document") or {}
    title = str(doc.get("title") or "Dynamic Form")
    pages = spec_norm.get("pages") or []
    if not pages:
        return {"title": title, "fields": []}

    elements = (pages[0] or {}).get("elements") or []
    labels = [el for el in elements if isinstance(el, dict) and (el.get("type") or "").lower() == "label"]
    fields = [el for el in elements if isinstance(el, dict) and (el.get("type") or "").lower() == "field"]

    def label_for_field(f: Dict[str, Any]) -> str:
        fx = float(f.get("x") or 0)
        fy = float(f.get("y") or 0)
        best = None
        best_score = None
        for lab in labels:
            lx = float(lab.get("x") or 0)
            ly = float(lab.get("y") or 0)
            # heuristic: label above field and to the left-ish
            if ly <= fy + 2 and lx <= fx + 20:
                score = abs(fy - ly) * 2 + abs(fx - lx)
                if best_score is None or score < best_score:
                    best_score = score
                    best = lab
        if best and isinstance(best.get("text"), str):
            return best["text"]
        return str(f.get("name") or f.get("id") or "Field")

    js_fields = []
    for f in fields:
        ftype = (f.get("field_type") or "text").lower()
        # Map to sample FieldType names
        if ftype in ("text", "textarea"):
            jstype = "TEXT"
        elif ftype in ("dropdown", "combo"):
            jstype = "DROPDOWN"
        elif ftype == "checkbox":
            jstype = "CHECKBOX"
        else:
            jstype = "TEXT"
        js_fields.append(
            {
                "label": label_for_field(f),
                "name": str(f.get("name") or f.get("id") or ""),
                "type": jstype,
                "value": f.get("value", ""),
                "options": f.get("options", []),
            }
        )

    return {"title": title, "fields": js_fields}


def build_js_script_jspdf(spec_norm: Dict[str, Any]) -> str:
    structure = infer_fields_for_jspdf(spec_norm)
    structure_json = json.dumps(structure, ensure_ascii=False, indent=2)
    return f"""// Generated by WOW Agentic PDF Studio (jsPDF)
// Requires: jspdf (and a version with AcroForm support enabled)
// This mirrors your provided sample pattern.

import {{ jsPDF }} from "jspdf";

const FieldType = {{
  TEXT: "TEXT",
  DATE: "DATE",
  CHECKBOX: "CHECKBOX",
  DROPDOWN: "DROPDOWN",
}};

const structure = {structure_json};

export const generateClientSidePDF = (structure) => {{
  const doc = new jsPDF({{ unit: "mm", format: "a4" }});

  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text(structure.title, 105, 20, {{ align: "center" }});

  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);

  let currentY = 40;
  const marginX = 20;
  const inputX = 70;
  const lineHeight = 15;

  structure.fields.forEach((field) => {{
    doc.text(String(field.label || field.name || "Field"), marginX, currentY);

    const pdfAny = doc;
    const fieldHeight = 8;
    const fieldWidth = 80;

    if (field.type === FieldType.TEXT || field.type === FieldType.DATE) {{
      const textField = new pdfAny.AcroForm.TextField();
      textField.Rect = [inputX, currentY - 6, fieldWidth, fieldHeight];
      textField.fieldName = field.name;
      textField.value = field.value ? String(field.value) : "";
      pdfAny.addField(textField);
    }} else if (field.type === FieldType.CHECKBOX) {{
      const checkBox = new pdfAny.AcroForm.CheckBox();
      checkBox.Rect = [inputX, currentY - 6, 6, 6];
      checkBox.fieldName = field.name;
      checkBox.appearanceState = field.value ? "On" : "Off";
      pdfAny.addField(checkBox);
    }} else if (field.type === FieldType.DROPDOWN) {{
      const comboBox = new pdfAny.AcroForm.ComboBox();
      comboBox.Rect = [inputX, currentY - 6, fieldWidth, fieldHeight];
      comboBox.fieldName = field.name;
      comboBox.setOptions(field.options || []);
      pdfAny.addField(comboBox);
    }}

    currentY += lineHeight;
  }});

  doc.save("dynamic_form.pdf");
}};

// Example:
// generateClientSidePDF(structure);
"""


# ----------------------------
# PDF preview + field extraction + reconcile
# ----------------------------
def pdf_iframe_view(pdf_bytes: bytes, height: int = 720) -> str:
    b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    return f"""
    <iframe
      src="data:application/pdf;base64,{b64}"
      width="100%"
      height="{height}"
      style="border: 1px solid var(--wow-border); border-radius: 14px; background: var(--wow-card);"
    ></iframe>
    """


def extract_pdf_fields(pdf_bytes: bytes) -> Dict[str, Any]:
    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = reader.get_fields() or {}
    out_fields = {}
    for k, v in fields.items():
        info = {}
        try:
            info["ft"] = str(v.get("/FT", "")) if isinstance(v, dict) else ""
            info["t"] = str(v.get("/T", "")) if isinstance(v, dict) else ""
            info["v"] = str(v.get("/V", "")) if isinstance(v, dict) else ""
        except Exception:
            pass
        out_fields[str(k)] = info
    return {"fields": out_fields, "names": sorted(out_fields.keys()), "raw_count": len(out_fields)}


def spec_field_names(spec_norm: Dict[str, Any]) -> List[str]:
    names = []
    pages = spec_norm.get("pages") or []
    for p in pages:
        elements = (p or {}).get("elements") or []
        for el in elements:
            if not isinstance(el, dict):
                continue
            if (el.get("type") or "").lower() != "field":
                continue
            fid = el.get("id")
            nm = el.get("name") or fid
            if nm:
                names.append(str(nm))
    seen, ordered = set(), []
    for n in names:
        if n not in seen:
            seen.add(n)
            ordered.append(n)
    return ordered


def reconcile_pdf_vs_spec(spec_norm: Dict[str, Any], uploaded_pdf_bytes: bytes) -> Dict[str, Any]:
    pdf_info = extract_pdf_fields(uploaded_pdf_bytes)
    pdf_names = set(pdf_info["names"])
    spec_names_list = spec_field_names(spec_norm)
    spec_names = set(spec_names_list)

    missing_in_pdf = sorted(spec_names - pdf_names)
    extra_in_pdf = sorted(pdf_names - spec_names)

    suggestions = []
    for sname in missing_in_pdf[:40]:
        sslug = re.sub(r"[^a-z0-9]+", "", sname.lower())
        close = None
        for pname in extra_in_pdf:
            pslug = re.sub(r"[^a-z0-9]+", "", pname.lower())
            if sslug and pslug and (sslug in pslug or pslug in sslug):
                close = pname
                break
        if close:
            suggestions.append({"spec": sname, "pdf": close})

    return {
        "spec_field_count": len(spec_names_list),
        "pdf_field_count": pdf_info["raw_count"],
        "missing_in_pdf": missing_in_pdf,
        "extra_in_pdf": extra_in_pdf,
        "rename_suggestions": suggestions,
        "pdf_fields_sample": {k: pdf_info["fields"][k] for k in list(pdf_info["fields"].keys())[:20]},
    }


# ----------------------------
# Minimal pipeline stub (kept)
# ----------------------------
def fake_agent_run(step: Dict[str, Any], input_text: str) -> Tuple[str, int]:
    start = time.time()
    time.sleep(0.2)
    stamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    out = (
        f"## {step['id']} (mock output)\n\n"
        f"- Model: {step['model']}\n"
        f"- Max tokens: {step['max_tokens']}\n"
        f"- Input hash: `{hash_text(input_text)}`\n"
        f"- Generated at: {stamp}\n\n"
        f"### Content\n"
        f"{input_text[:900]}\n"
    )
    return out, int((time.time() - start) * 1000)


def make_default_pipeline() -> List[Dict[str, Any]]:
    return [
        {
            "id": "ingest_normalize",
            "name": {"en": "Ingestion & Normalization", "zh-TW": "匯入與正規化"},
            "model": "gpt-4o-mini",
            "max_tokens": 12000,
            "prompt": "Normalize the application form into clean Markdown (preserve headings, lists, tables).",
            "generated_output": "",
            "final_output": "",
            "status": "not_run",
        },
        {
            "id": "pdf_spec",
            "name": {"en": "PDF Build Specification", "zh-TW": "PDF 建置規格"},
            "model": "gemini-2.5-flash",
            "max_tokens": 12000,
            "prompt": "Generate a PDF build spec (YAML). Ensure Unicode-safe labels.",
            "generated_output": "",
            "final_output": "",
            "status": "not_run",
        },
    ]


# ----------------------------
# App state
# ----------------------------
def init_state():
    st.session_state.setdefault("lang", "en")
    st.session_state.setdefault("theme", "light")
    st.session_state.setdefault("style_key", PAINTER_STYLES[0].key)
    st.session_state.setdefault("app_status", "idle")
    st.session_state.setdefault("last_latency_ms", None)
    st.session_state.setdefault("token_budget", 12000)
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("session_keys", {})

    st.session_state.setdefault("form_source_mode", "default")
    st.session_state.setdefault("form_content", "")

    st.session_state.setdefault("pipeline", make_default_pipeline())

    # Create and load defaultpdfspec.md
    ensure_file("defaultpdfspec.md", DEFAULT_PDFSPEC_MD)
    st.session_state.setdefault("pdfspec_text", load_file_or_default("defaultpdfspec.md", DEFAULT_PDFSPEC_MD))
    st.session_state.setdefault("pdfspec_last_valid_text", "")
    st.session_state.setdefault("pdfspec_last_validation", {"errors": [], "warnings": [], "normalized": None})
    st.session_state.setdefault("pdfspec_strict_mode", False)
    st.session_state.setdefault("pdfspec_page_size_fallback", "A4")
    st.session_state.setdefault("pdfspec_unit_fallback", "mm")

    # Engine + download format
    st.session_state.setdefault("pdf_engine", "fpdf2")  # fpdf2|reportlab
    st.session_state.setdefault("download_format", "pdf")  # pdf|py|js

    # Artifacts
    st.session_state.setdefault("pdf_bytes", None)
    st.session_state.setdefault("pdf_render_log", [])
    st.session_state.setdefault("pdf_generated_at", None)
    st.session_state.setdefault("pdf_generated_from", None)
    st.session_state.setdefault("pdf_last_reconcile", None)
    st.session_state.setdefault("last_spec_norm", None)
    st.session_state.setdefault("artifact_py", "")
    st.session_state.setdefault("artifact_js", "")

    # Fonts status
    st.session_state.setdefault("unicode_fonts_status", None)


def set_status(new_status: str, latency_ms: Optional[int] = None):
    st.session_state.app_status = new_status
    if latency_ms is not None:
        st.session_state.last_latency_ms = latency_ms


def hash_text(s: str) -> str:
    return hashlib.sha256((s or "").encode("utf-8")).hexdigest()[:12]


def provider_env_key(provider: str) -> Optional[str]:
    env_map = {
        "OpenAI": "OPENAI_API_KEY",
        "Gemini": "GEMINI_API_KEY",
        "Anthropic": "ANTHROPIC_API_KEY",
        "Grok": "GROK_API_KEY",
    }
    key_name = env_map.get(provider)
    return os.getenv(key_name) if key_name else None


def provider_effective_key(provider: str) -> Optional[str]:
    env = provider_env_key(provider)
    return env if env else st.session_state.session_keys.get(provider)


def provider_state(provider: str) -> str:
    return "ready" if provider_effective_key(provider) else "missing"


def status_label(status: str) -> str:
    mapping = {
        "idle": t("status_idle"),
        "running": t("status_running"),
        "awaiting": t("status_awaiting"),
        "done": t("status_done"),
        "failed": t("status_failed"),
    }
    return mapping.get(status, status)


def current_style() -> PainterStyle:
    return STYLE_BY_KEY.get(st.session_state.style_key, PAINTER_STYLES[0])


def palette() -> Dict[str, str]:
    s = current_style()
    return s.palette_dark if st.session_state.theme == "dark" else s.palette_light


def style_display_name(style: PainterStyle) -> str:
    return style.name_zh if st.session_state.lang == "zh-TW" else style.name_en


init_state()


# ----------------------------
# CSS (WOW UI)
# ----------------------------
def css_inject():
    pal = palette()
    s = current_style()
    coral = "#FF7F50"
    css = f"""
    <style>
      :root {{
        --wow-bg: {pal['bg']};
        --wow-fg: {pal['fg']};
        --wow-card: {pal['card']};
        --wow-border: {pal['border']};
        --wow-accent: {pal['accent']};
        --wow-accent2: {pal['accent2']};
        --wow-coral: {coral};
        --wow-font: {s.font_family};
      }}
      html, body, [class*="stApp"] {{
        background: var(--wow-bg) !important;
        color: var(--wow-fg) !important;
        font-family: var(--wow-font) !important;
      }}
      section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, var(--wow-card), var(--wow-bg)) !important;
        border-right: 1px solid var(--wow-border);
      }}
      .block-container {{ padding-top: 1.2rem; padding-bottom: 2rem; }}
      .wow-card {{
        background: var(--wow-card);
        border: 1px solid var(--wow-border);
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.06);
      }}
      .wow-subtle {{ opacity: 0.85; }}
      .wow-pill {{
        display:inline-block; padding:6px 10px; border-radius:999px;
        border:1px solid var(--wow-border);
        background: color-mix(in srgb, var(--wow-accent) 10%, var(--wow-card));
        font-size:12px; margin-right:6px; margin-top:4px;
      }}
      .wow-dot {{
        width:10px; height:10px; border-radius:999px; display:inline-block; margin-right:8px;
        background: var(--wow-accent);
        box-shadow:0 0 0 3px color-mix(in srgb, var(--wow-accent) 18%, transparent);
      }}
      .wow-header {{ display:flex; align-items:baseline; justify-content:space-between; gap:12px; }}
      .wow-style-caption {{ font-size:12px; opacity:0.8; }}
      .wow-keyword {{ color: var(--wow-coral); font-weight:700; }}
      .stButton>button {{
        border-radius:12px !important;
        border: 1px solid var(--wow-border) !important;
        background: linear-gradient(180deg,
          color-mix(in srgb, var(--wow-accent) 16%, var(--wow-card)),
          color-mix(in srgb, var(--wow-accent) 8%, var(--wow-card))
        ) !important;
        color: var(--wow-fg) !important;
        font-weight:600;
      }}
      .stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        border-radius:12px !important;
        border:1px solid var(--wow-border) !important;
        background: var(--wow-card) !important;
        color: var(--wow-fg) !important;
      }}
      details {{
        background: var(--wow-card);
        border:1px solid var(--wow-border);
        border-radius:14px;
        padding:4px 10px;
      }}
      div[data-testid="stMetric"] {{
        background: var(--wow-card);
        border:1px solid var(--wow-border);
        border-radius:14px;
        padding:10px 12px;
      }}
      a {{ color: var(--wow-accent) !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def wow_header(title: str, subtitle: Optional[str] = None):
    s = current_style()
    st.markdown(
        f"""
        <div class="wow-card">
          <div class="wow-header">
            <div>
              <h2 style="color: var(--wow-fg); margin:0;">{title}</h2>
              <div class="wow-style-caption">{subtitle or ""}</div>
            </div>
            <div style="text-align:right;">
              <span class="wow-pill"><span class="wow-dot"></span>{style_display_name(s)}</span>
              <span class="wow-pill">{t('ui_theme')}: {t('ui_theme_dark') if st.session_state.theme=='dark' else t('ui_theme_light')}</span>
              <span class="wow-pill">{t('ui_language')}: {"English" if st.session_state.lang=='en' else "繁體中文"}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")


# ----------------------------
# Sidebar
# ----------------------------
def sidebar_ui() -> str:
    with st.sidebar:
        st.markdown(f"### {t('app_title')}")
        st.caption(t("tagline"))

        st.session_state.lang = st.selectbox(
            t("ui_language"),
            options=["en", "zh-TW"],
            format_func=lambda x: "English" if x == "en" else "繁體中文",
            index=0 if st.session_state.lang == "en" else 1,
        )

        st.session_state.theme = st.radio(
            t("ui_theme"),
            options=["light", "dark"],
            format_func=lambda x: t("ui_theme_light") if x == "light" else t("ui_theme_dark"),
            horizontal=True,
            index=0 if st.session_state.theme == "light" else 1,
        )

        style_keys = [s.key for s in PAINTER_STYLES]
        st.session_state.style_key = st.selectbox(
            t("ui_style"),
            options=style_keys,
            index=style_keys.index(st.session_state.style_key) if st.session_state.style_key in style_keys else 0,
            format_func=lambda k: style_display_name(STYLE_BY_KEY[k]),
        )

        c = st.columns(2)
        with c[0]:
            if st.button(t("ui_jackpot"), use_container_width=True):
                st.session_state.style_key = random.choice(style_keys)
                st.rerun()
        with c[1]:
            if st.button(t("ui_reset"), use_container_width=True):
                st.session_state.lang = "en"
                st.session_state.theme = "light"
                st.session_state.style_key = PAINTER_STYLES[0].key
                st.rerun()

        st.divider()

        page = st.radio(
            "Navigation",
            options=["dashboard", "form", "pipeline", "spec", "notes", "settings", "history"],
            format_func=lambda x: {
                "dashboard": t("nav_dashboard"),
                "form": t("nav_form"),
                "pipeline": t("nav_pipeline"),
                "spec": t("nav_spec"),
                "notes": t("nav_notes"),
                "settings": t("nav_settings"),
                "history": t("nav_history"),
            }[x],
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown(f"**{t('ui_status')}:** {status_label(st.session_state.app_status)}")
        if st.session_state.last_latency_ms is not None:
            st.caption(f"{t('dash_latency')}: {st.session_state.last_latency_ms} ms")

        st.markdown(f"**{t('providers')}:**")
        for p in ["OpenAI", "Gemini", "Anthropic", "Grok"]:
            st.caption(f"- {p}: {t('provider_ready') if provider_state(p)=='ready' else t('provider_missing')}")

        st.write("")
        st.markdown(f"**{t('font_status')}:**")
        fs = st.session_state.unicode_fonts_status
        if fs is None:
            st.caption(t("font_downloading"))
            fs = ensure_unicode_fonts()
            st.session_state.unicode_fonts_status = fs
        st.caption(f"- DejaVuSans: {t('font_ready') if fs.get('DejaVuSans') else t('font_failed')}")
        st.caption(f"- NotoSansTC: {t('font_ready') if fs.get('NotoSansTC') else t('font_failed')}")

        return page


# ----------------------------
# Pages
# ----------------------------
def page_dashboard():
    wow_header(t("nav_dashboard"), t("dash_overview"))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(t("ui_status"), status_label(st.session_state.app_status))
    with c2:
        st.metric(t("dash_latency"), f"{st.session_state.last_latency_ms} ms" if st.session_state.last_latency_ms is not None else "—")
    with c3:
        st.metric(t("dash_tokens"), str(st.session_state.token_budget))
    with c4:
        st.metric(t("dash_cost"), t("dash_not_available"))

    st.write("")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown(f"#### {t('dash_recent')}")
        st.markdown(
            f"""
            <div class="wow-card">
              <div class="wow-subtle">
                • Last PDF: <b>{st.session_state.pdf_generated_at or "—"}</b><br/>
                • Source: <b>{st.session_state.pdf_generated_from or "—"}</b><br/>
                • Engine: <b>{st.session_state.pdf_engine}</b><br/>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(f"#### {t('dash_pipeline_health')}")
        ok = sum(1 for s in st.session_state.pipeline if s["status"] in ("done", "accepted"))
        total = len(st.session_state.pipeline)
        pdf_ready = "Yes" if st.session_state.pdf_bytes else "No"
        st.markdown(
            f"""
            <div class="wow-card">
              <div class="wow-subtle">
                Steps completed: <b>{ok}/{total}</b><br/>
                {t('dash_pdf_ready')}: <b>{pdf_ready}</b>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown(f"#### {t('dash_field_stats')}")
    rep = st.session_state.pdfspec_last_validation
    stats = rep.get("field_stats") if isinstance(rep, dict) else None
    if stats:
        by = stats.get("by_type", {})
        st.markdown(
            f"""
            <div class="wow-card">
              <div class="wow-subtle">
                Detected fields: <b>{stats.get('total','—')}</b><br/>
                Text: <b>{by.get('text',0)}</b> &nbsp;
                Textarea: <b>{by.get('textarea',0)}</b> &nbsp;
                Dropdown: <b>{by.get('dropdown',0)}</b> &nbsp;
                Checkbox: <b>{by.get('checkbox',0)}</b><br/>
                Unique IDs: <b>{stats.get('unique_ids','—')}</b>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="wow-card">
              <div class="wow-subtle">
                Validate/generate a PDFSpec to populate stats.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def page_form():
    wow_header(t("nav_form"), t("form_input"))

    mode = st.radio(
        "",
        options=["default", "custom"],
        format_func=lambda x: t("form_use_default") if x == "default" else t("form_use_custom"),
        horizontal=True,
        index=0 if st.session_state.form_source_mode == "default" else 1,
        label_visibility="collapsed",
    )
    st.session_state.form_source_mode = mode

    if mode == "default":
        if not st.session_state.form_content.strip():
            ensure_file("sample.md", DEFAULT_SAMPLE_MD)
            st.session_state.form_content = load_file_or_default("sample.md", DEFAULT_SAMPLE_MD)
        st.info(t("form_use_default"))
    else:
        tab_paste, tab_upload = st.tabs([t("form_paste"), t("form_upload")])
        with tab_paste:
            st.session_state.form_content = st.text_area(t("form_paste"), value=st.session_state.form_content, height=260)
        with tab_upload:
            up = st.file_uploader(t("form_upload"), type=["txt", "md", "docx"])
            if up is not None:
                name = up.name.lower()
                raw = up.read()
                text = ""
                if name.endswith(".txt") or name.endswith(".md"):
                    text = raw.decode("utf-8", errors="replace")
                elif name.endswith(".docx"):
                    try:
                        import docx  # python-docx
                        doc = docx.Document(io.BytesIO(raw))
                        text = "\n".join([p.text for p in doc.paragraphs]).strip()
                    except Exception:
                        st.error("DOCX parsing requires `python-docx`.")
                if text:
                    st.session_state.form_content = text
                    st.success("Uploaded and loaded.")

    st.write("")
    st.markdown(f"#### {t('form_loaded')}")
    with st.expander(t("form_preview"), expanded=True):
        st.text_area("", value=st.session_state.form_content, height=260, label_visibility="collapsed")

    if st.button(t("form_next"), use_container_width=True):
        set_status("awaiting")
        st.rerun()


def page_pipeline():
    wow_header(t("nav_pipeline"), t("pipeline_title"))
    if not st.session_state.form_content.strip():
        st.warning("No form content loaded yet. Go to ‘Form → Dynamic PDF’ first.")
        return

    MODELS = [
        "gpt-4o-mini",
        "gpt-4.1-mini",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-3-flash-preview",
        "anthropic (configured)",
        "grok-4-fast-reasoning",
        "grok-3-mini",
    ]

    for idx, step in enumerate(st.session_state.pipeline):
        step_name = step["name"]["zh-TW"] if st.session_state.lang == "zh-TW" else step["name"]["en"]
        with st.expander(f"{idx+1}. {step_name} — [{step['status']}]", expanded=(idx == 0)):
            cL, cR = st.columns([1, 1])
            with cL:
                step["model"] = st.selectbox(t("pipeline_model"), options=MODELS, key=f"model_{step['id']}")
                step["max_tokens"] = st.number_input(t("pipeline_max_tokens"), min_value=256, max_value=200000, value=int(step.get("max_tokens", 12000)), step=256, key=f"max_{step['id']}")
                step["prompt"] = st.text_area(t("pipeline_prompt"), value=step.get("prompt", ""), height=120, key=f"prompt_{step['id']}")
                b = st.columns(3)
                with b[0]:
                    if st.button(t("pipeline_run_step"), key=f"run_{step['id']}", use_container_width=True):
                        set_status("running")
                        input_text = st.session_state.form_content if idx == 0 else (st.session_state.pipeline[idx - 1]["final_output"] or st.session_state.form_content)
                        out, lat = fake_agent_run(step, input_text)
                        step["generated_output"] = out
                        step["final_output"] = step["final_output"] or out
                        step["status"] = "done"
                        set_status("awaiting", lat)
                        st.rerun()
                with b[1]:
                    if st.button(t("pipeline_reset_output"), key=f"reset_{step['id']}", use_container_width=True):
                        step["final_output"] = step.get("generated_output", "")
                        st.rerun()
                with b[2]:
                    if st.button(t("pipeline_accept"), key=f"accept_{step['id']}", use_container_width=True):
                        step["status"] = "accepted"
                        if step["id"] == "pdf_spec":
                            st.session_state.pdfspec_text = step["final_output"] or st.session_state.pdfspec_text
                        st.rerun()
            with cR:
                view = st.radio("View", options=["text", "md"], horizontal=True, key=f"view_{step['id']}", label_visibility="collapsed",
                                format_func=lambda x: t("pipeline_view_text") if x == "text" else t("pipeline_view_md"))
                step["final_output"] = st.text_area(t("pipeline_output"), value=step.get("final_output", ""), height=280, key=f"out_{step['id']}")
                if view == "md" and step["final_output"].strip():
                    st.markdown("---")
                    st.markdown(step["final_output"])


def page_notes():
    wow_header(t("nav_notes"), t("notes_title"))
    st.info("Note Keeper UI kept minimal in this build; connect to agent models later.")
    left, right = st.columns([1, 1])
    with left:
        st.text_area(t("notes_paste"), value=st.session_state.get("note_content", ""), height=260, key="note_content")
        if st.button(t("notes_transform"), use_container_width=True):
            note = st.session_state.note_content
            st.session_state.note_markdown = f"# Organized Note\n\n{note}"
            st.rerun()
    with right:
        st.text_area("Markdown", value=st.session_state.get("note_markdown", ""), height=340, key="note_markdown")
        st.markdown(st.session_state.get("note_markdown", ""))


def page_settings():
    wow_header(t("nav_settings"), t("nav_settings"))
    st.markdown("#### API Keys")
    for p in ["OpenAI", "Gemini", "Anthropic", "Grok"]:
        env = provider_env_key(p)
        with st.expander(p, expanded=True):
            if env:
                st.success("Key detected from environment (hidden).")
                st.caption("To override, set a session key below.")
            k = st.text_input("Enter key (session only)", type="password", key=f"key_{p}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Save", key=f"save_{p}", use_container_width=True):
                    if k.strip():
                        st.session_state.session_keys[p] = k.strip()
                        st.success("Saved (hidden).")
            with c2:
                if st.button("Clear", key=f"clear_{p}", use_container_width=True):
                    st.session_state.session_keys.pop(p, None)
                    st.rerun()


def page_history():
    wow_header(t("nav_history"), t("history_title"))
    if not st.session_state.history:
        st.markdown(f"<div class='wow-card'><div class='wow-subtle'>{t('history_empty')}</div></div>", unsafe_allow_html=True)
        return
    for i, v in enumerate(st.session_state.history):
        with st.expander(f"Version {i+1} — {v.get('ts','?')} — origin:{v.get('origin','?')}"):
            st.json(v, expanded=False)
            if "artifact_b64" in v:
                try:
                    raw = base64.b64decode(v["artifact_b64"])
                    st.download_button("Download stored artifact", data=raw, file_name=v.get("artifact_name", f"artifact_{i+1}"), use_container_width=True)
                except Exception:
                    st.warning("Could not decode stored artifact.")


def page_spec():
    wow_header(t("spec_title"), t("spec_subtitle"))

    left, right = st.columns([1.1, 1])

    # -------- Left: editor + controls
    with left:
        st.markdown(f"#### {t('spec_source')}")
        source = st.radio(
            "",
            options=["use_last", "paste_new", "load_default"],
            horizontal=True,
            format_func=lambda x: {
                "use_last": t("spec_use_last"),
                "paste_new": t("spec_paste_new"),
                "load_default": t("spec_load_default"),
            }[x],
            label_visibility="collapsed",
        )

        if source == "use_last" and st.session_state.pdfspec_last_valid_text.strip():
            st.session_state.pdfspec_text = st.session_state.pdfspec_last_valid_text
        elif source == "load_default":
            st.session_state.pdfspec_text = load_file_or_default("defaultpdfspec.md", DEFAULT_PDFSPEC_MD)

        # Engine + download format
        c = st.columns([1, 1])
        with c[0]:
            st.session_state.pdf_engine = st.selectbox(
                t("engine"),
                options=["fpdf2", "reportlab"],
                index=0 if st.session_state.pdf_engine == "fpdf2" else 1,
                format_func=lambda x: t("engine_fpdf2") if x == "fpdf2" else t("engine_reportlab"),
            )
        with c[1]:
            st.session_state.download_format = st.selectbox(
                t("download_format"),
                options=["pdf", "py", "js"],
                index=["pdf", "py", "js"].index(st.session_state.download_format),
                format_func=lambda x: {"pdf": t("download_pdf"), "py": t("download_py"), "js": t("download_js")}[x],
            )

        opts = st.columns([1, 1, 1])
        with opts[0]:
            st.session_state.pdfspec_strict_mode = st.checkbox(t("spec_strict"), value=bool(st.session_state.pdfspec_strict_mode))
        with opts[1]:
            st.session_state.pdfspec_unit_fallback = st.selectbox(
                t("spec_units"),
                options=["mm", "pt"],
                index=0 if st.session_state.pdfspec_unit_fallback == "mm" else 1,
                format_func=lambda x: t("spec_unit_mm") if x == "mm" else t("spec_unit_pt"),
            )
        with opts[2]:
            st.session_state.pdfspec_page_size_fallback = st.selectbox(
                t("spec_page_size"),
                options=["A4", "LETTER"],
                index=0 if st.session_state.pdfspec_page_size_fallback.upper() == "A4" else 1,
                format_func=lambda x: t("spec_a4") if x.upper() == "A4" else t("spec_letter"),
            )

        st.markdown(f"#### {t('spec_editor')}")
        st.session_state.pdfspec_text = st.text_area("", value=st.session_state.pdfspec_text, height=520, label_visibility="collapsed")

        btns = st.columns([1, 1, 1])
        with btns[0]:
            if st.button(t("spec_validate"), use_container_width=True):
                set_status("running")
                start = time.time()
                spec_obj, parse_errors = parse_pdfspec(st.session_state.pdfspec_text)
                if parse_errors:
                    report = {"errors": parse_errors, "warnings": [], "normalized": None}
                else:
                    report = validate_pdfspec(
                        spec_obj,
                        unit_fallback=st.session_state.pdfspec_unit_fallback,
                        page_fallback=st.session_state.pdfspec_page_size_fallback,
                    )
                st.session_state.pdfspec_last_validation = report
                if report.get("normalized") is not None and not report.get("errors"):
                    st.session_state.pdfspec_last_valid_text = st.session_state.pdfspec_text
                    st.session_state.last_spec_norm = report.get("normalized")
                set_status("awaiting", int((time.time() - start) * 1000))
                st.rerun()

        with btns[1]:
            if st.button(t("spec_generate"), use_container_width=True):
                set_status("running")
                start = time.time()

                spec_obj, parse_errors = parse_pdfspec(st.session_state.pdfspec_text)
                if parse_errors:
                    st.session_state.pdfspec_last_validation = {"errors": parse_errors, "warnings": [], "normalized": None}
                    set_status("failed", int((time.time() - start) * 1000))
                    st.rerun()

                report = validate_pdfspec(
                    spec_obj,
                    unit_fallback=st.session_state.pdfspec_unit_fallback,
                    page_fallback=st.session_state.pdfspec_page_size_fallback,
                )
                st.session_state.pdfspec_last_validation = report
                errors = report.get("errors") or []
                warnings = report.get("warnings") or []
                if errors or (st.session_state.pdfspec_strict_mode and warnings):
                    set_status("failed", int((time.time() - start) * 1000))
                    st.rerun()

                spec_norm = report["normalized"]
                st.session_state.last_spec_norm = spec_norm

                engine = st.session_state.pdf_engine
                if engine == "reportlab":
                    pdf_bytes, render_log = generate_pdf_reportlab(spec_norm)
                else:
                    pdf_bytes, render_log = generate_pdf_fpdf2(spec_norm)

                # Improve compatibility
                pdf_bytes2, changed = set_need_appearances(pdf_bytes)
                if changed:
                    render_log.append("postprocess: set /NeedAppearances true")

                st.session_state.pdf_bytes = pdf_bytes2
                st.session_state.pdf_render_log = render_log
                st.session_state.pdf_generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                st.session_state.pdf_generated_from = f"spec:{engine}"
                st.session_state.pdf_last_reconcile = None
                st.session_state.pdfspec_last_valid_text = st.session_state.pdfspec_text

                # Build export scripts (always available after a successful validation/generation)
                st.session_state.artifact_py = build_py_script_reportlab(spec_norm) if engine == "reportlab" else build_py_script_fpdf2(spec_norm)
                st.session_state.artifact_js = build_js_script_jspdf(spec_norm)

                set_status("done", int((time.time() - start) * 1000))
                st.rerun()

        with btns[2]:
            if st.button(t("spec_reset_last_valid"), use_container_width=True):
                if st.session_state.pdfspec_last_valid_text.strip():
                    st.session_state.pdfspec_text = st.session_state.pdfspec_last_valid_text
                    st.rerun()

        st.write("")
        st.markdown(f"#### {t('spec_validation')}")
        rep = st.session_state.pdfspec_last_validation or {"errors": [], "warnings": []}
        with st.expander(t("spec_validation"), expanded=True):
            if rep.get("errors"):
                st.error("\n".join([f"- {e}" for e in rep["errors"]]))
            else:
                st.success("No errors.")
            if rep.get("warnings"):
                st.warning("\n".join([f"- {w}" for w in rep["warnings"]]))
            else:
                st.info("No warnings.")

    # -------- Right: preview + download + reconcile
    with right:
        st.markdown(f"#### {t('spec_preview')}")
        if st.session_state.pdf_bytes:
            st.markdown(pdf_iframe_view(st.session_state.pdf_bytes, height=680), unsafe_allow_html=True)

            b64 = base64.b64encode(st.session_state.pdf_bytes).decode("utf-8")
            st.markdown(
                f'<a href="data:application/pdf;base64,{b64}" target="_blank">{t("spec_open_new_tab")}</a>',
                unsafe_allow_html=True,
            )

            # Download artifact based on selection
            fmt = st.session_state.download_format
            if fmt == "pdf":
                st.download_button(
                    label=t("download_artifact"),
                    data=st.session_state.pdf_bytes,
                    file_name="dynamic_form.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            elif fmt == "py":
                py_text = st.session_state.artifact_py or ""
                st.download_button(
                    label=t("download_artifact"),
                    data=py_text.encode("utf-8"),
                    file_name="generate_dynamic_form.py",
                    mime="text/x-python",
                    use_container_width=True,
                )
                with st.expander("PY preview", expanded=False):
                    st.code(py_text, language="python")
            else:
                js_text = st.session_state.artifact_js or ""
                st.download_button(
                    label=t("download_artifact"),
                    data=js_text.encode("utf-8"),
                    file_name="generate_dynamic_form.js",
                    mime="text/javascript",
                    use_container_width=True,
                )
                with st.expander("JS preview", expanded=False):
                    st.code(js_text, language="javascript")

            st.write("")
            with st.expander(t("spec_render_log"), expanded=False):
                st.code("\n".join(st.session_state.pdf_render_log or []) or "—", language="text")

            # Show extracted field count to validate "editable"
            st.write("")
            try:
                info = extract_pdf_fields(st.session_state.pdf_bytes)
                st.caption(f"Detected AcroForm fields in generated PDF: {info.get('raw_count', 0)}")
            except Exception:
                st.caption("Detected AcroForm fields in generated PDF: (unavailable)")

            st.write("")
            st.markdown(f"#### {t('spec_upload_pdf')}")
            up = st.file_uploader(t("spec_upload_pdf"), type=["pdf"], key="upload_modified_pdf")
            if up is not None:
                uploaded_bytes = up.read()
                st.success("Uploaded.")
                if st.button(t("spec_reconcile"), use_container_width=True):
                    spec_norm = st.session_state.last_spec_norm
                    if spec_norm:
                        st.session_state.pdf_last_reconcile = reconcile_pdf_vs_spec(spec_norm, uploaded_bytes)
                        st.rerun()
                    else:
                        st.error("No validated spec available to reconcile against.")

            if st.session_state.pdf_last_reconcile:
                st.write("")
                st.markdown(f"#### {t('spec_reconcile_report')}")
                with st.expander(t("spec_reconcile_report"), expanded=True):
                    st.json(st.session_state.pdf_last_reconcile, expanded=False)

            st.write("")
            if st.button(t("spec_save_version"), use_container_width=True):
                # Save current chosen artifact into history as bytes (base64)
                fmt = st.session_state.download_format
                if fmt == "pdf":
                    artifact = st.session_state.pdf_bytes
                    name = "dynamic_form.pdf"
                elif fmt == "py":
                    artifact = (st.session_state.artifact_py or "").encode("utf-8")
                    name = "generate_dynamic_form.py"
                else:
                    artifact = (st.session_state.artifact_js or "").encode("utf-8")
                    name = "generate_dynamic_form.js"

                snap = {
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "origin": "spec",
                    "engine": st.session_state.pdf_engine,
                    "download_format": fmt,
                    "artifact_name": name,
                    "artifact_b64": base64.b64encode(artifact).decode("utf-8"),
                    "pdf_generated_at": st.session_state.pdf_generated_at,
                }
                st.session_state.history.insert(0, snap)
                st.success("Saved.")
                st.rerun()
        else:
            st.info(t("spec_no_pdf"))


# ----------------------------
# Render app
# ----------------------------
css_inject()
page = sidebar_ui()

st.markdown(
    f"""
    <div class="wow-card">
      <h1 style="margin-bottom: 0.2rem;">{t('app_title')}</h1>
      <div class="wow-subtle">{t('tagline')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

if page == "dashboard":
    page_dashboard()
elif page == "form":
    page_form()
elif page == "pipeline":
    page_pipeline()
elif page == "spec":
    page_spec()
elif page == "notes":
    page_notes()
elif page == "settings":
    page_settings()
elif page == "history":
    page_history()
else:
    page_dashboard()
