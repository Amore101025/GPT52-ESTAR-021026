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
from typing import Dict, Any, List, Optional, Tuple

import streamlit as st

# Optional deps in requirements.txt
import yaml  # PyYAML
from fpdf import FPDF  # fpdf2
from pypdf import PdfReader  # pypdf


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
        "provider_error": "Error",
        "settings_api_keys": "API Keys",
        "settings_env_key_detected": "Key detected from environment (hidden).",
        "settings_enter_key": "Enter API key (stored in session only).",
        "settings_use_different_key": "Use a different key",
        "settings_never_shown": "Keys are never shown after submission.",
        "settings_save": "Save",
        "settings_clear": "Clear session keys",
        "settings_privacy": "Privacy",
        "settings_privacy_text": "Your content may be sent to the model provider(s) you select. Avoid uploading sensitive data unless necessary.",
        "dash_overview": "Overview",
        "dash_recent": "Recent Activity",
        "dash_metrics": "Metrics",
        "dash_field_stats": "Field Stats",
        "dash_pipeline_health": "Pipeline Health",
        "dash_latency": "Latency (last run)",
        "dash_tokens": "Token Budget",
        "dash_cost": "Cost Estimate",
        "dash_not_available": "Not available",
        "dash_pdf_ready": "PDF Ready",
        "dash_last_pdf": "Last PDF",
        "form_input": "Form Input",
        "form_use_default": "Use default sample (sample.md)",
        "form_use_custom": "Provide new application form",
        "form_paste": "Paste text / Markdown",
        "form_upload": "Upload file (.txt, .md, .docx)",
        "form_loaded": "Loaded content",
        "form_preview": "Preview",
        "form_next": "Proceed to pipeline",
        "pipeline_title": "Agent Pipeline (Step-by-step, editable)",
        "pipeline_controls": "Controls",
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
        # NEW: Spec tab strings
        "spec_title": "PDF Build Spec → Dynamic PDF",
        "spec_subtitle": "Paste YAML/JSON spec (or Markdown-wrapped) to generate a fillable PDF.",
        "spec_source": "Spec source",
        "spec_use_last": "Use last generated spec",
        "spec_paste_new": "Paste new spec",
        "spec_load_example": "Load example spec",
        "spec_editor": "Spec editor (YAML/JSON or Markdown-wrapped)",
        "spec_validate": "Validate spec",
        "spec_generate": "Generate dynamic PDF",
        "spec_reset_last_valid": "Reset to last valid spec",
        "spec_strict": "Strict mode (fail on warnings)",
        "spec_units": "Units",
        "spec_unit_mm": "mm",
        "spec_unit_pt": "pt",
        "spec_page_size": "Page size",
        "spec_a4": "A4",
        "spec_letter": "Letter",
        "spec_preview": "PDF preview",
        "spec_download": "Download PDF",
        "spec_upload_pdf": "Upload modified PDF",
        "spec_reconcile": "Reconcile uploaded PDF vs spec",
        "spec_render_log": "Render log",
        "spec_validation": "Validation report",
        "spec_reconcile_report": "Reconciliation report",
        "spec_last_valid": "Last valid spec",
        "spec_no_last_spec": "No last spec available yet.",
        "spec_no_pdf": "No PDF generated yet.",
        "spec_save_version": "Save version (spec + PDF)",
        "spec_open_new_tab": "Open PDF in a new tab",
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
        "provider_error": "錯誤",
        "settings_api_keys": "API 金鑰",
        "settings_env_key_detected": "已從環境變數偵測到金鑰（已隱藏）。",
        "settings_enter_key": "輸入 API 金鑰（僅保存在本次 session）。",
        "settings_use_different_key": "使用不同金鑰",
        "settings_never_shown": "提交後不會顯示金鑰內容。",
        "settings_save": "儲存",
        "settings_clear": "清除 session 金鑰",
        "settings_privacy": "隱私",
        "settings_privacy_text": "你的內容可能會送到你選擇的模型供應商。除非必要，請避免上傳敏感資料。",
        "dash_overview": "總覽",
        "dash_recent": "近期活動",
        "dash_metrics": "指標",
        "dash_field_stats": "欄位統計",
        "dash_pipeline_health": "流程健康度",
        "dash_latency": "延遲（上次執行）",
        "dash_tokens": "Token 預算",
        "dash_cost": "費用估算",
        "dash_not_available": "不可用",
        "dash_pdf_ready": "PDF 就緒",
        "dash_last_pdf": "最新 PDF",
        "form_input": "表單輸入",
        "form_use_default": "使用預設範例（sample.md）",
        "form_use_custom": "提供新的申請表",
        "form_paste": "貼上文字 / Markdown",
        "form_upload": "上傳檔案（.txt, .md, .docx）",
        "form_loaded": "已載入內容",
        "form_preview": "預覽",
        "form_next": "前往代理流程",
        "pipeline_title": "代理流程（逐步執行、可編輯）",
        "pipeline_controls": "控制項",
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
        # NEW: Spec tab strings
        "spec_title": "PDF 建置規格 → 動態 PDF",
        "spec_subtitle": "貼上 YAML/JSON 規格（可用 Markdown 包住）以生成可填寫 PDF。",
        "spec_source": "規格來源",
        "spec_use_last": "使用上次生成的規格",
        "spec_paste_new": "貼上新規格",
        "spec_load_example": "載入範例規格",
        "spec_editor": "規格編輯器（YAML/JSON 或 Markdown 包裝）",
        "spec_validate": "驗證規格",
        "spec_generate": "生成動態 PDF",
        "spec_reset_last_valid": "重置為上次有效規格",
        "spec_strict": "嚴格模式（有警告就失敗）",
        "spec_units": "單位",
        "spec_unit_mm": "mm",
        "spec_unit_pt": "pt",
        "spec_page_size": "紙張大小",
        "spec_a4": "A4",
        "spec_letter": "Letter",
        "spec_preview": "PDF 預覽",
        "spec_download": "下載 PDF",
        "spec_upload_pdf": "上傳已修改的 PDF",
        "spec_reconcile": "比對：上傳 PDF vs 規格",
        "spec_render_log": "渲染記錄",
        "spec_validation": "驗證報告",
        "spec_reconcile_report": "比對報告",
        "spec_last_valid": "上次有效規格",
        "spec_no_last_spec": "目前尚無上次規格可用。",
        "spec_no_pdf": "尚未生成 PDF。",
        "spec_save_version": "儲存版本（規格 + PDF）",
        "spec_open_new_tab": "在新分頁開啟 PDF",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return I18N.get(lang, I18N["en"]).get(key, key)


# ----------------------------
# Painter styles
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
    PainterStyle(
        key="vangogh",
        name_en="Vincent van Gogh",
        name_zh="梵谷",
        description="Bold strokes, starry accents, high-contrast warmth.",
        palette_light={"bg": "#FBF6EA", "fg": "#1A1A1A", "card": "#FFFFFF", "border": "#E8DCC2", "accent": "#2A6F97", "accent2": "#FCA311"},
        palette_dark={"bg": "#0B1320", "fg": "#EDEDED", "card": "#121B2B", "border": "#1E2A44", "accent": "#2A9D8F", "accent2": "#F4D35E"},
    ),
    PainterStyle(
        key="monet",
        name_en="Claude Monet",
        name_zh="莫內",
        description="Soft gradients, airy spacing, gentle water-lily calm.",
        palette_light={"bg": "#F4FAFB", "fg": "#14213D", "card": "#FFFFFF", "border": "#D7EEF2", "accent": "#277DA1", "accent2": "#90BE6D"},
        palette_dark={"bg": "#09151A", "fg": "#EAF6F7", "card": "#0F222A", "border": "#183642", "accent": "#4D96FF", "accent2": "#6BCB77"},
    ),
    PainterStyle(
        key="picasso",
        name_en="Pablo Picasso",
        name_zh="畢卡索",
        description="Geometric rhythm, sharp edges, confident blocks.",
        palette_light={"bg": "#FAFAFA", "fg": "#111827", "card": "#FFFFFF", "border": "#E5E7EB", "accent": "#2563EB", "accent2": "#F59E0B"},
        palette_dark={"bg": "#0B0F19", "fg": "#F3F4F6", "card": "#101827", "border": "#1F2937", "accent": "#60A5FA", "accent2": "#FBBF24"},
    ),
    PainterStyle(
        key="dali",
        name_en="Salvador Dalí",
        name_zh="達利",
        description="Surreal shimmer, dramatic highlights, dreamlike contrast.",
        palette_light={"bg": "#FFF7ED", "fg": "#1F2937", "card": "#FFFFFF", "border": "#FED7AA", "accent": "#7C3AED", "accent2": "#EF4444"},
        palette_dark={"bg": "#120B1C", "fg": "#F5F3FF", "card": "#1A1028", "border": "#2B1B3E", "accent": "#A78BFA", "accent2": "#FB7185"},
    ),
    PainterStyle(
        key="davinci",
        name_en="Leonardo da Vinci",
        name_zh="達文西",
        description="Renaissance restraint, parchment warmth, precise lines.",
        palette_light={"bg": "#FBF3E4", "fg": "#2B2B2B", "card": "#FFFFFF", "border": "#E7D2B1", "accent": "#6B4F2A", "accent2": "#2F6F6D"},
        palette_dark={"bg": "#17120A", "fg": "#F3E9D7", "card": "#1E170D", "border": "#2D2214", "accent": "#D4A373", "accent2": "#4D908E"},
    ),
    PainterStyle(
        key="michelangelo",
        name_en="Michelangelo",
        name_zh="米開朗基羅",
        description="Sculptural clarity, marble neutrals, bold shadows.",
        palette_light={"bg": "#F7F7F7", "fg": "#111111", "card": "#FFFFFF", "border": "#E2E2E2", "accent": "#374151", "accent2": "#B91C1C"},
        palette_dark={"bg": "#0D0F12", "fg": "#F5F5F5", "card": "#141820", "border": "#222833", "accent": "#9CA3AF", "accent2": "#F87171"},
    ),
    PainterStyle(
        key="rembrandt",
        name_en="Rembrandt",
        name_zh="林布蘭",
        description="Chiaroscuro depth, golden highlights, intimate focus.",
        palette_light={"bg": "#FFF8E7", "fg": "#1C1917", "card": "#FFFFFF", "border": "#E7D6B7", "accent": "#92400E", "accent2": "#0F766E"},
        palette_dark={"bg": "#0E0B07", "fg": "#F5EBDD", "card": "#15100B", "border": "#2A1D12", "accent": "#F59E0B", "accent2": "#2DD4BF"},
    ),
    PainterStyle(
        key="vermeer",
        name_en="Johannes Vermeer",
        name_zh="維梅爾",
        description="Quiet luminosity, Delft blues, crisp composure.",
        palette_light={"bg": "#F2F6FF", "fg": "#0F172A", "card": "#FFFFFF", "border": "#DDE6F7", "accent": "#1D4ED8", "accent2": "#EAB308"},
        palette_dark={"bg": "#0A1022", "fg": "#E8EEFF", "card": "#0F1935", "border": "#1A2A57", "accent": "#60A5FA", "accent2": "#FDE047"},
    ),
    PainterStyle(
        key="klimt",
        name_en="Gustav Klimt",
        name_zh="克林姆",
        description="Gold ornament, luxurious contrasts, art-nouveau glow.",
        palette_light={"bg": "#FFFBEB", "fg": "#1F2937", "card": "#FFFFFF", "border": "#FDE68A", "accent": "#B45309", "accent2": "#7C3AED"},
        palette_dark={"bg": "#130F07", "fg": "#FFF7D6", "card": "#1B150B", "border": "#3B2F16", "accent": "#FBBF24", "accent2": "#C4B5FD"},
    ),
    PainterStyle(
        key="kandinsky",
        name_en="Wassily Kandinsky",
        name_zh="康丁斯基",
        description="Abstract energy, vibrant accents, playful structure.",
        palette_light={"bg": "#F8FAFC", "fg": "#0F172A", "card": "#FFFFFF", "border": "#E2E8F0", "accent": "#EF4444", "accent2": "#3B82F6"},
        palette_dark={"bg": "#070B12", "fg": "#E2E8F0", "card": "#0C1220", "border": "#1C2A44", "accent": "#FB7185", "accent2": "#60A5FA"},
    ),
    PainterStyle(
        key="pollock",
        name_en="Jackson Pollock",
        name_zh="波洛克",
        description="Splatter dynamism, high contrast, bold UI punch.",
        palette_light={"bg": "#FFFFFF", "fg": "#111827", "card": "#FAFAFA", "border": "#E5E7EB", "accent": "#111827", "accent2": "#10B981"},
        palette_dark={"bg": "#050505", "fg": "#FAFAFA", "card": "#0E0E0E", "border": "#222222", "accent": "#F97316", "accent2": "#34D399"},
    ),
    PainterStyle(
        key="matisse",
        name_en="Henri Matisse",
        name_zh="馬諦斯",
        description="Fauvist color blocks, friendly warmth, clean space.",
        palette_light={"bg": "#FFF5F5", "fg": "#1F2937", "card": "#FFFFFF", "border": "#FED7D7", "accent": "#E11D48", "accent2": "#2563EB"},
        palette_dark={"bg": "#1A0B0F", "fg": "#FFE4EA", "card": "#241017", "border": "#3B1723", "accent": "#FB7185", "accent2": "#93C5FD"},
    ),
    PainterStyle(
        key="munch",
        name_en="Edvard Munch",
        name_zh="孟克",
        description="Expressionist intensity, moody tones, striking alerts.",
        palette_light={"bg": "#FDF2F8", "fg": "#111827", "card": "#FFFFFF", "border": "#FBCFE8", "accent": "#7F1D1D", "accent2": "#0EA5E9"},
        palette_dark={"bg": "#12060C", "fg": "#FCE7F3", "card": "#1C0B12", "border": "#3A1226", "accent": "#F87171", "accent2": "#38BDF8"},
    ),
    PainterStyle(
        key="kahlo",
        name_en="Frida Kahlo",
        name_zh="芙烈達·卡蘿",
        description="Vivid botanicals, bold identity, confident accent colors.",
        palette_light={"bg": "#F0FDF4", "fg": "#052E16", "card": "#FFFFFF", "border": "#BBF7D0", "accent": "#16A34A", "accent2": "#DC2626"},
        palette_dark={"bg": "#05140B", "fg": "#DCFCE7", "card": "#0A1E11", "border": "#12351F", "accent": "#4ADE80", "accent2": "#FB7185"},
    ),
    PainterStyle(
        key="warhol",
        name_en="Andy Warhol",
        name_zh="安迪·沃荷",
        description="Pop Art punch, neon accents, crisp modular layout.",
        palette_light={"bg": "#FDF4FF", "fg": "#111827", "card": "#FFFFFF", "border": "#F5D0FE", "accent": "#A21CAF", "accent2": "#2563EB"},
        palette_dark={"bg": "#130414", "fg": "#FAE8FF", "card": "#1F0820", "border": "#3B0F3D", "accent": "#E879F9", "accent2": "#93C5FD"},
    ),
    PainterStyle(
        key="hokusai",
        name_en="Hokusai",
        name_zh="北齋",
        description="Ukiyo-e calm, wave blues, disciplined typography.",
        palette_light={"bg": "#F0F9FF", "fg": "#0F172A", "card": "#FFFFFF", "border": "#BAE6FD", "accent": "#0369A1", "accent2": "#F97316"},
        palette_dark={"bg": "#04131C", "fg": "#E0F2FE", "card": "#071E2B", "border": "#0C3144", "accent": "#38BDF8", "accent2": "#FDBA74"},
    ),
    PainterStyle(
        key="qibaishi",
        name_en="Qi Baishi",
        name_zh="齊白石",
        description="Ink simplicity, vermilion seal accents, airy margins.",
        palette_light={"bg": "#FFFEF7", "fg": "#111111", "card": "#FFFFFF", "border": "#EEE6D9", "accent": "#C1121F", "accent2": "#1D3557"},
        palette_dark={"bg": "#0B0A08", "fg": "#F5F1E8", "card": "#141210", "border": "#292420", "accent": "#F87171", "accent2": "#93C5FD"},
    ),
    PainterStyle(
        key="zhangdaqian",
        name_en="Zhang Daqian",
        name_zh="張大千",
        description="Splash-ink elegance, mineral blues/greens, refined contrast.",
        palette_light={"bg": "#F6FFFE", "fg": "#0F172A", "card": "#FFFFFF", "border": "#D1FAE5", "accent": "#065F46", "accent2": "#1D4ED8"},
        palette_dark={"bg": "#041310", "fg": "#D1FAE5", "card": "#07241D", "border": "#0E3A2F", "accent": "#34D399", "accent2": "#93C5FD"},
    ),
    PainterStyle(
        key="okeeffe",
        name_en="Georgia O’Keeffe",
        name_zh="喬治亞·歐姬芙",
        description="Modern calm, spacious composition, floral accent warmth.",
        palette_light={"bg": "#FFF7ED", "fg": "#111827", "card": "#FFFFFF", "border": "#FFEDD5", "accent": "#EA580C", "accent2": "#0F766E"},
        palette_dark={"bg": "#160C05", "fg": "#FFEDD5", "card": "#1E1208", "border": "#3A210F", "accent": "#FDBA74", "accent2": "#2DD4BF"},
    ),
    PainterStyle(
        key="turner",
        name_en="J.M.W. Turner",
        name_zh="透納",
        description="Luminous haze, sunset gradients, gentle emphasis cues.",
        palette_light={"bg": "#FFFAF0", "fg": "#1F2937", "card": "#FFFFFF", "border": "#FDE2C5", "accent": "#F59E0B", "accent2": "#3B82F6"},
        palette_dark={"bg": "#100B06", "fg": "#FFF3D6", "card": "#191108", "border": "#2D1E10", "accent": "#FBBF24", "accent2": "#93C5FD"},
    ),
    PainterStyle(
        key="studio_minimal",
        name_en="Studio Minimal (Bonus)",
        name_zh="工作室極簡（加碼）",
        description="Ultra-clean layout, strong readability, subtle borders.",
        palette_light={"bg": "#F9FAFB", "fg": "#111827", "card": "#FFFFFF", "border": "#E5E7EB", "accent": "#2563EB", "accent2": "#10B981"},
        palette_dark={"bg": "#0B1220", "fg": "#E5E7EB", "card": "#0F1A2E", "border": "#1C2B4A", "accent": "#60A5FA", "accent2": "#34D399"},
    ),
]

STYLE_BY_KEY = {s.key: s for s in PAINTER_STYLES}


# ----------------------------
# Default sample.md content
# ----------------------------
DEFAULT_SAMPLE_MD = """# Application Form (Mock Sample)

## Section A — Applicant Information
1. Full Name *Required*
2. Date of Birth (MM/DD/YYYY)
3. Email Address *Required*
4. Phone Number
5. Address (Street, City, State/Province, Postal Code)

## Section B — Submission Details
1. Submission Type (choose one): 510(k), PMA, De Novo
2. Device Name *Required*
3. Submission Date (default: today)

## Section C — Declarations
- [ ] I confirm the information provided is accurate. *Required*
- [ ] I agree to the terms and conditions.

## Section D — Additional Notes
Provide any supporting details (multi-line).

## Section E — Signature
Signature Name (typed)
Date
"""


def ensure_sample_file():
    try:
        if not os.path.exists("sample.md"):
            with open("sample.md", "w", encoding="utf-8") as f:
                f.write(DEFAULT_SAMPLE_MD)
    except Exception:
        pass


def load_sample() -> str:
    ensure_sample_file()
    try:
        with open("sample.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return DEFAULT_SAMPLE_MD


# ----------------------------
# Spec example template
# ----------------------------
DEFAULT_PDFSPEC_MD = """# Example PDF Build Spec (YAML)

```yaml
document:
  title: "Mock Application — Fillable PDF"
  page_size: "A4"          # A4 | LETTER
  orientation: "portrait"  # portrait | landscape
  unit: "mm"               # mm | pt
  margin:
    left: 12
    top: 12
    right: 12
    bottom: 12
fonts:
  default:
    family: "Helvetica"
    size: 11
pages:
  - number: 1
    elements:
      - type: "label"
        text: "Mock Application — Fillable PDF"
        x: 12
        y: 14
        size: 14
        style: "B"

      - type: "label"
        text: "Applicant Information"
        x: 12
        y: 26
        size: 12
        style: "B"

      - type: "label"
        text: "Full Name:"
        x: 12
        y: 34
      - type: "field"
        field_type: "text"
        id: "full_name"
        name: "Full_Name"
        x: 50
        y: 31.5
        w: 140
        h: 8
        required: true

      - type: "label"
        text: "Submission Type:"
        x: 12
        y: 46
      - type: "field"
        field_type: "dropdown"
        id: "submission_type"
        name: "Submission_Type"
        x: 50
        y: 43.5
        w: 60
        h: 8
        options: ["510(k)", "PMA", "De Novo"]

      - type: "label"
        text: "Confirm Accuracy:"
        x: 12
        y: 58
      - type: "field"
        field_type: "checkbox"
        id: "confirm"
        name: "Confirm"
        x: 50
        y: 56
        w: 5
        h: 5

      - type: "label"
        text: "Additional Notes:"
        x: 12
        y: 70
      - type: "field"
        field_type: "textarea"
        id: "notes"
        name: "Notes"
        x: 12
        y: 74
        w: 178
        h: 40
        multiline: true
```
"""


# ----------------------------
# UI state initialization
# ----------------------------
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
            "id": "extract_fields",
            "name": {"en": "Field & Section Extraction", "zh-TW": "欄位與段落擷取"},
            "model": "gpt-4o-mini",
            "max_tokens": 12000,
            "prompt": "Extract fields/sections into a structured schema: ids, labels, types, required flags, options.",
            "generated_output": "",
            "final_output": "",
            "status": "not_run",
        },
        {
            "id": "layout_plan",
            "name": {"en": "Layout Planning", "zh-TW": "版面規劃"},
            "model": "gpt-4.1-mini",
            "max_tokens": 12000,
            "prompt": "Create a layout plan: pages, margins, coordinates, spacing. Avoid overlaps and page splits.",
            "generated_output": "",
            "final_output": "",
            "status": "not_run",
        },
        {
            "id": "pdf_spec",
            "name": {"en": "PDF Build Specification", "zh-TW": "PDF 建置規格"},
            "model": "gemini-2.5-flash",
            "max_tokens": 12000,
            "prompt": "Generate a PDF build spec with interactive fields (text/combo/checkbox) and styling directives (YAML preferred).",
            "generated_output": "",
            "final_output": "",
            "status": "not_run",
        },
        {
            "id": "qa_repair",
            "name": {"en": "QA & Repair Suggestions", "zh-TW": "品質檢查與修復建議"},
            "model": "grok-4-fast-reasoning",
            "max_tokens": 12000,
            "prompt": "Review artifacts, detect missing/overlapping fields, and propose targeted fixes.",
            "generated_output": "",
            "final_output": "",
            "status": "not_run",
        },
    ]


def init_state():
    st.session_state.setdefault("lang", "en")
    st.session_state.setdefault("theme", "light")  # light|dark
    st.session_state.setdefault("style_key", PAINTER_STYLES[0].key)
    st.session_state.setdefault("app_status", "idle")  # idle|running|awaiting|done|failed
    st.session_state.setdefault("last_latency_ms", None)
    st.session_state.setdefault("token_budget", 12000)

    st.session_state.setdefault("history", [])
    st.session_state.setdefault("session_keys", {})  # provider -> key (session only)

    st.session_state.setdefault("form_source_mode", "default")  # default|custom
    st.session_state.setdefault("form_content", "")

    st.session_state.setdefault("note_content", "")
    st.session_state.setdefault("note_markdown", "")
    st.session_state.setdefault("note_persistent_prompt", "")
    st.session_state.setdefault("note_keyword_rules", [])  # {kw,color}

    st.session_state.setdefault("pipeline", make_default_pipeline())

    # NEW: spec tab state
    st.session_state.setdefault("pdfspec_text", DEFAULT_PDFSPEC_MD)
    st.session_state.setdefault("pdfspec_last_valid_text", "")
    st.session_state.setdefault("pdfspec_last_validation", {"errors": [], "warnings": [], "normalized": None})
    st.session_state.setdefault("pdfspec_strict_mode", False)
    st.session_state.setdefault("pdfspec_page_size_fallback", "A4")
    st.session_state.setdefault("pdfspec_unit_fallback", "mm")

    # NEW: generated PDF artifacts
    st.session_state.setdefault("pdf_bytes", None)  # latest generated PDF bytes
    st.session_state.setdefault("pdf_render_log", [])
    st.session_state.setdefault("pdf_generated_at", None)
    st.session_state.setdefault("pdf_generated_from", None)  # "spec" or "pipeline"
    st.session_state.setdefault("pdf_last_reconcile", None)


init_state()


# ----------------------------
# Helpers
# ----------------------------
def set_status(new_status: str, latency_ms: Optional[int] = None):
    st.session_state.app_status = new_status
    if latency_ms is not None:
        st.session_state.last_latency_ms = latency_ms


def current_style() -> PainterStyle:
    return STYLE_BY_KEY.get(st.session_state.style_key, PAINTER_STYLES[0])


def palette() -> Dict[str, str]:
    s = current_style()
    return s.palette_dark if st.session_state.theme == "dark" else s.palette_light


def style_display_name(style: PainterStyle) -> str:
    return style.name_zh if st.session_state.lang == "zh-TW" else style.name_en


def status_label(status: str) -> str:
    mapping = {
        "idle": t("status_idle"),
        "running": t("status_running"),
        "awaiting": t("status_awaiting"),
        "done": t("status_done"),
        "failed": t("status_failed"),
    }
    return mapping.get(status, status)


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
    if env:
        return env
    return st.session_state.session_keys.get(provider)


def provider_state(provider: str) -> str:
    return "ready" if provider_effective_key(provider) else "missing"


def hash_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]


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

      .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2.0rem;
      }}

      .wow-card {{
        background: var(--wow-card);
        border: 1px solid var(--wow-border);
        border-radius: 16px;
        padding: 16px 16px 14px 16px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.06);
      }}
      .wow-subtle {{ opacity: 0.85; }}

      .wow-pill {{
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        border: 1px solid var(--wow-border);
        background: color-mix(in srgb, var(--wow-accent) 10%, var(--wow-card));
        color: var(--wow-fg);
        font-size: 12px;
        margin-right: 6px;
        margin-top: 4px;
      }}
      .wow-dot {{
        width: 10px; height: 10px; border-radius: 999px;
        display: inline-block; margin-right: 8px;
        background: var(--wow-accent);
        box-shadow: 0 0 0 3px color-mix(in srgb, var(--wow-accent) 18%, transparent);
      }}

      .stButton>button {{
        border-radius: 12px !important;
        border: 1px solid var(--wow-border) !important;
        background: linear-gradient(180deg,
          color-mix(in srgb, var(--wow-accent) 16%, var(--wow-card)),
          color-mix(in srgb, var(--wow-accent) 8%, var(--wow-card))
        ) !important;
        color: var(--wow-fg) !important;
        font-weight: 600;
      }}
      .stButton>button:hover {{
        border-color: color-mix(in srgb, var(--wow-accent) 55%, var(--wow-border)) !important;
      }}

      .stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {{
        border-radius: 12px !important;
        border: 1px solid var(--wow-border) !important;
        background: var(--wow-card) !important;
        color: var(--wow-fg) !important;
      }}

      details {{
        background: var(--wow-card);
        border: 1px solid var(--wow-border);
        border-radius: 14px;
        padding: 4px 10px;
      }}

      .wow-keyword {{
        color: var(--wow-coral);
        font-weight: 700;
      }}

      .wow-header {{
        display:flex;
        align-items:baseline;
        justify-content:space-between;
        gap: 12px;
      }}
      .wow-style-caption {{
        font-size: 12px;
        opacity: 0.8;
      }}

      div[data-testid="stMetric"] {{
        background: var(--wow-card);
        border: 1px solid var(--wow-border);
        border-radius: 14px;
        padding: 10px 12px;
      }}

      a {{ color: var(--wow-accent) !important; }}
      code {{ font-size: 0.92em; }}
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
# Sidebar UI
# ----------------------------
def sidebar_ui() -> str:
    with st.sidebar:
        st.markdown(f"### {t('app_title')}")
        st.caption(t("tagline"))

        lang = st.selectbox(
            t("ui_language"),
            options=["en", "zh-TW"],
            format_func=lambda x: "English" if x == "en" else "繁體中文",
            index=0 if st.session_state.lang == "en" else 1,
        )
        st.session_state.lang = lang

        theme = st.radio(
            t("ui_theme"),
            options=["light", "dark"],
            format_func=lambda x: t("ui_theme_light") if x == "light" else t("ui_theme_dark"),
            horizontal=True,
            index=0 if st.session_state.theme == "light" else 1,
        )
        st.session_state.theme = theme

        style_keys = [s.key for s in PAINTER_STYLES]
        st.session_state.style_key = st.selectbox(
            t("ui_style"),
            options=style_keys,
            index=style_keys.index(st.session_state.style_key) if st.session_state.style_key in style_keys else 0,
            format_func=lambda k: style_display_name(STYLE_BY_KEY[k]),
        )

        cols = st.columns([1, 1])
        with cols[0]:
            if st.button(t("ui_jackpot"), use_container_width=True):
                st.session_state.style_key = random.choice(style_keys)
                st.rerun()
        with cols[1]:
            if st.button(t("ui_reset"), use_container_width=True):
                st.session_state.lang = "en"
                st.session_state.theme = "light"
                st.session_state.style_key = PAINTER_STYLES[0].key
                st.rerun()

        s = current_style()
        st.caption(f"**{style_display_name(s)}** — {s.description}")

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
            state = provider_state(p)
            label = t("provider_ready") if state == "ready" else t("provider_missing")
            st.caption(f"- {p}: {label}")

        return page


# ----------------------------
# Pipeline (mock runner + hook to capture PDFSpec)
# ----------------------------
def fake_agent_run(step: Dict[str, Any], input_text: str) -> Tuple[str, int]:
    start = time.time()
    time.sleep(0.25)

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
    latency_ms = int((time.time() - start) * 1000)
    return out, latency_ms


# ----------------------------
# Note Keeper helper
# ----------------------------
def highlight_keywords_html(md_text: str, keyword_rules: List[Dict[str, str]]) -> str:
    if not md_text:
        return ""
    html = md_text
    rules = sorted(keyword_rules, key=lambda r: len(r.get("kw", "")), reverse=True)
    for r in rules:
        kw = (r.get("kw") or "").strip()
        color = (r.get("color") or "#FF7F50").strip()
        if not kw:
            continue
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        html = pattern.sub(lambda m: f'<span style="color:{color}; font-weight:700;">{m.group(0)}</span>', html)
    return html


def organize_note_stub(note: str) -> str:
    note = note.strip()
    if not note:
        return ""
    kws = sorted(set(re.findall(r"\b[A-Z][a-zA-Z]{3,}\b", note)))[:12]
    md = []
    md.append("# Organized Note")
    md.append("")
    md.append("## Key Points")
    md.append("- " + ("\n- ".join([line.strip() for line in note.splitlines() if line.strip()][:5]) if note else "—"))
    md.append("")
    md.append("## Details")
    md.append(note)
    md.append("")
    md.append("## Keywords")
    if kws:
        md.append(", ".join([f'<span class="wow-keyword">{k}</span>' for k in kws]))
    else:
        md.append("—")
    return "\n".join(md)


# ----------------------------
# PDFSpec parsing/validation/generation
# ----------------------------
MM_PER_PT = 0.3527777778


def extract_structured_block(text: str) -> Tuple[str, str]:
    """
    Returns (kind, payload) where kind in {"yaml","json","raw"}.
    If markdown fenced block exists, extract it.
    """
    # Prefer fenced YAML/JSON blocks
    m = re.search(r"```(?:yaml|yml)\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return "yaml", m.group(1).strip()
    m = re.search(r"```json\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        return "json", m.group(1).strip()
    return "raw", text.strip()


def parse_pdfspec(text: str) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Parse text into dict. Tries YAML then JSON.
    Returns (spec_dict, errors)
    """
    kind, payload = extract_structured_block(text)
    errors = []
    if not payload:
        return None, ["Spec is empty."]
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
    if not errors:
        errors = ["Parsed content is not a dictionary/object."]
    return None, errors


def normalize_units_in_place(spec: Dict[str, Any], target_unit: str) -> Tuple[List[str], List[str]]:
    """
    Normalize all x/y/w/h and margins into target_unit (mm recommended for fpdf2 here).
    Returns (warnings, errors)
    """
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

    # Convert margins
    margin = doc.get("margin") or {}
    if isinstance(margin, dict):
        for k in ("left", "top", "right", "bottom"):
            if k in margin:
                margin[k] = convert(margin[k])

    # Convert element geometry
    pages = spec.get("pages")
    if not isinstance(pages, list):
        return warnings, errors
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

    # Write normalized unit
    doc["unit"] = target_unit
    spec["document"] = doc
    return warnings, errors


def validate_pdfspec(spec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns report dict:
      { errors:[], warnings:[], normalized: spec_norm, field_stats:{...} }
    """
    errors: List[str] = []
    warnings: List[str] = []

    if not isinstance(spec, dict):
        return {"errors": ["Spec is not an object."], "warnings": [], "normalized": None}

    doc = spec.get("document")
    if not isinstance(doc, dict):
        errors.append("Missing or invalid 'document' object.")
        doc = {}

    page_size = (doc.get("page_size") or st.session_state.pdfspec_page_size_fallback or "A4").upper()
    if page_size not in ("A4", "LETTER"):
        warnings.append(f"Unsupported page_size '{page_size}', falling back to A4.")
        page_size = "A4"
    doc["page_size"] = page_size

    orientation = (doc.get("orientation") or "portrait").lower()
    if orientation not in ("portrait", "landscape"):
        warnings.append(f"Unsupported orientation '{orientation}', using portrait.")
        orientation = "portrait"
    doc["orientation"] = orientation

    # Normalize to mm for generation
    norm_unit = (st.session_state.pdfspec_unit_fallback or "mm").lower()
    if norm_unit not in ("mm", "pt"):
        norm_unit = "mm"

    spec_norm = json.loads(json.dumps(spec))  # deep copy
    spec_norm.setdefault("document", {})
    spec_norm["document"].update(doc)

    unit_warnings, unit_errors = normalize_units_in_place(spec_norm, target_unit=norm_unit)
    warnings.extend(unit_warnings)
    errors.extend(unit_errors)

    fonts = spec_norm.get("fonts") or {}
    if not isinstance(fonts, dict):
        warnings.append("Invalid 'fonts' object; using defaults.")
        fonts = {}
        spec_norm["fonts"] = fonts

    pages = spec_norm.get("pages")
    if not isinstance(pages, list) or not pages:
        errors.append("Missing or empty 'pages' array.")
        return {"errors": errors, "warnings": warnings, "normalized": None}

    # Validate elements + fields
    field_ids = set()
    field_count = {"text": 0, "textarea": 0, "checkbox": 0, "dropdown": 0, "radio": 0, "unknown": 0}
    min_field_w, min_field_h = 6.0, 4.0

    for pi, p in enumerate(pages, start=1):
        if not isinstance(p, dict):
            errors.append(f"Page {pi} is not an object.")
            continue
        elements = p.get("elements")
        if not isinstance(elements, list):
            errors.append(f"Page {pi}: missing or invalid 'elements' array.")
            continue
        for ei, el in enumerate(elements, start=1):
            if not isinstance(el, dict):
                warnings.append(f"Page {pi} element {ei}: not an object; skipped.")
                continue
            et = (el.get("type") or "").lower()
            if et not in ("label", "field"):
                warnings.append(f"Page {pi} element {ei}: unknown type '{el.get('type')}'.")
                continue

            # Geometry checks
            for k in ("x", "y"):
                if k not in el or not isinstance(el[k], (int, float)):
                    errors.append(f"Page {pi} element {ei}: missing numeric '{k}'.")
            if et == "field":
                for k in ("w", "h"):
                    if k not in el or not isinstance(el[k], (int, float)):
                        errors.append(f"Page {pi} field element {ei}: missing numeric '{k}'.")
                if all(isinstance(el.get(k), (int, float)) for k in ("w", "h")):
                    if el["w"] < min_field_w or el["h"] < min_field_h:
                        warnings.append(f"Page {pi} field '{el.get('id','?')}' too small (w/h).")

                fid = el.get("id")
                if not fid or not isinstance(fid, str):
                    errors.append(f"Page {pi} field element {ei}: missing string 'id'.")
                else:
                    if fid in field_ids:
                        errors.append(f"Duplicate field id '{fid}'.")
                    field_ids.add(fid)

                ftype = (el.get("field_type") or "").lower()
                if ftype in ("text", "textarea", "checkbox", "dropdown", "radio"):
                    field_count[ftype] += 1
                else:
                    field_count["unknown"] += 1
                    warnings.append(f"Field '{fid}': unsupported field_type '{ftype}' (will attempt fallback).")

                if ftype in ("dropdown", "radio"):
                    opts = el.get("options")
                    if not isinstance(opts, list) or not opts:
                        errors.append(f"Field '{fid}': '{ftype}' requires non-empty 'options' array.")

                # Name is recommended (AcroForm field name); fallback allowed
                nm = el.get("name")
                if nm is not None and not isinstance(nm, str):
                    warnings.append(f"Field '{fid}': 'name' should be a string.")

            if et == "label":
                if not isinstance(el.get("text"), str) or not el.get("text"):
                    warnings.append(f"Page {pi} label element {ei}: missing 'text'.")

    # Optional overlap sanity check (very lightweight)
    # Only checks fields vs fields on same page
    for pi, p in enumerate(pages, start=1):
        elements = p.get("elements") if isinstance(p, dict) else None
        if not isinstance(elements, list):
            continue
        fields = [el for el in elements if isinstance(el, dict) and (el.get("type") or "").lower() == "field"]
        for i in range(len(fields)):
            a = fields[i]
            if not all(isinstance(a.get(k), (int, float)) for k in ("x", "y", "w", "h")):
                continue
            ax1, ay1, ax2, ay2 = a["x"], a["y"], a["x"] + a["w"], a["y"] + a["h"]
            for j in range(i + 1, len(fields)):
                b = fields[j]
                if not all(isinstance(b.get(k), (int, float)) for k in ("x", "y", "w", "h")):
                    continue
                bx1, by1, bx2, by2 = b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]
                overlap = not (ax2 <= bx1 or bx2 <= ax1 or ay2 <= by1 or by2 <= ay1)
                if overlap:
                    warnings.append(f"Page {pi}: fields '{a.get('id','?')}' and '{b.get('id','?')}' overlap.")

    return {
        "errors": errors,
        "warnings": warnings,
        "normalized": spec_norm,
        "field_stats": {
            "total": sum(field_count.values()) - field_count["unknown"] + field_count["unknown"],
            "by_type": field_count,
            "unique_ids": len(field_ids),
        },
    }


def page_format_for_fpdf(page_size: str, orientation: str) -> Tuple[str, str]:
    fmt = "A4" if page_size.upper() == "A4" else "LETTER"
    orient = "P" if orientation.lower() == "portrait" else "L"
    return fmt, orient


def pdfspec_to_pdf_bytes(spec_norm: Dict[str, Any]) -> Tuple[bytes, List[str]]:
    """
    Generate fillable PDF via fpdf2 from normalized spec (assumed mm unit).
    Returns (pdf_bytes, render_log)
    """
    log: List[str] = []
    doc = spec_norm.get("document") or {}
    page_size = (doc.get("page_size") or "A4").upper()
    orientation = (doc.get("orientation") or "portrait").lower()

    fmt, orient = page_format_for_fpdf(page_size, orientation)

    fonts = (spec_norm.get("fonts") or {}).get("default") or {}
    family = fonts.get("family") or "Helvetica"
    base_size = float(fonts.get("size") or 11)

    pdf = FPDF(orientation=orient, unit="mm", format=fmt)
    pdf.set_auto_page_break(auto=False)

    pages = spec_norm.get("pages") or []
    for p in pages:
        pdf.add_page()
        pdf.set_font(family, size=base_size)
        elements = (p or {}).get("elements") or []
        for el in elements:
            if not isinstance(el, dict):
                continue
            et = (el.get("type") or "").lower()
            if et == "label":
                txt = str(el.get("text") or "")
                x = float(el.get("x") or 0)
                y = float(el.get("y") or 0)
                size = float(el.get("size") or base_size)
                style = (el.get("style") or "").upper()  # "B", "I", "BI", etc.
                try:
                    pdf.set_font(family, style=style, size=size)
                except Exception:
                    pdf.set_font(family, size=size)
                pdf.set_xy(x, y)
                # Using multi_cell for long labels
                pdf.multi_cell(w=0, h=5, text=txt)
                pdf.set_font(family, size=base_size)
                log.append(f"Label: '{txt[:40]}' @ ({x},{y})")
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

                # fpdf2 form helpers (may vary by version; keep fallbacks)
                try:
                    if ftype in ("text", "textarea"):
                        kwargs = {}
                        if value is not None:
                            kwargs["value"] = str(value)
                        if multiline:
                            kwargs["multiline"] = True
                        pdf.form_text(name=str(name), x=x, y=y, w=w, h=h, **kwargs)
                        log.append(f"Field(text): {fid} name={name} @ ({x},{y}) {w}x{h} multiline={multiline}")
                    elif ftype in ("dropdown", "combo"):
                        options = el.get("options") or []
                        pdf.form_combo(name=str(name), x=x, y=y, w=w, h=h, options=[str(o) for o in options])
                        log.append(f"Field(dropdown): {fid} opts={len(options)} @ ({x},{y}) {w}x{h}")
                    elif ftype == "checkbox":
                        pdf.form_checkbox(name=str(name), x=x, y=y, w=w, h=h)
                        log.append(f"Field(checkbox): {fid} @ ({x},{y}) {w}x{h}")
                    else:
                        # Fallback: render as text field
                        pdf.form_text(name=str(name), x=x, y=y, w=w, h=h, value=str(value) if value else "")
                        log.append(f"Field(fallback->text): {fid} unsupported type '{ftype}'")
                except Exception as e:
                    # Hard fallback: draw a rectangle placeholder (non-interactive) but keep log
                    pdf.set_draw_color(120, 120, 120)
                    pdf.rect(x, y, w, h)
                    pdf.set_xy(x + 1.5, y + 1.5)
                    pdf.set_font(family, size=base_size - 1)
                    pdf.cell(w=w - 3, h=h - 3, text=f"[{ftype}] {name}", border=0)
                    pdf.set_font(family, size=base_size)
                    log.append(f"Field(render-failed): {fid} type={ftype} err={e}")

    # Return bytes
    out = pdf.output(dest="S")
    if isinstance(out, (bytes, bytearray)):
        return bytes(out), log
    return out.encode("latin-1"), log


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
    """
    Best-effort extraction of AcroForm fields from an uploaded PDF using pypdf.
    Returns { fields: {name:{...}}, names:[...], raw_count:n }
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    fields = reader.get_fields() or {}
    out_fields = {}
    for k, v in fields.items():
        info = {}
        try:
            # common keys: /FT (field type), /T (name), /V (value)
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
    # preserve order but dedupe
    seen = set()
    ordered = []
    for n in names:
        if n in seen:
            continue
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

    # Heuristic rename suggestions (very simple)
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
# Pages
# ----------------------------
def page_dashboard():
    wow_header(t("nav_dashboard"), t("dash_overview"))

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(t("ui_status"), status_label(st.session_state.app_status))
    with c2:
        latency = st.session_state.last_latency_ms
        st.metric(t("dash_latency"), f"{latency} ms" if latency is not None else "—")
    with c3:
        st.metric(t("dash_tokens"), str(st.session_state.token_budget))
    with c4:
        st.metric(t("dash_cost"), t("dash_not_available"))

    st.write("")

    providers = ["OpenAI", "Gemini", "Anthropic", "Grok"]
    st.markdown(f"#### {t('providers')}")
    cols = st.columns(4)
    for i, p in enumerate(providers):
        with cols[i]:
            state = provider_state(p)
            if state == "ready":
                st.success(f"{p}: {t('provider_ready')}")
            else:
                st.warning(f"{p}: {t('provider_missing')}")

    st.write("")

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown(f"#### {t('dash_recent')}")
        last_pdf = st.session_state.pdf_generated_at
        last_src = st.session_state.pdf_generated_from
        st.markdown(
            f"""
            <div class="wow-card">
              <div class="wow-subtle">
                • Input hash: <code>{hash_text(st.session_state.form_content or '')}</code><br/>
                • Last PDF: <b>{last_pdf or '—'}</b><br/>
                • Source: <b>{last_src or '—'}</b><br/>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(f"#### {t('dash_pipeline_health')}")
        ok = sum(1 for s in st.session_state.pipeline if s["status"] in ("done", "accepted"))
        total = len(st.session_state.pipeline)
        readiness = min(100, 40 + ok * 12)
        pdf_ready = "Yes" if st.session_state.pdf_bytes else "No"
        st.markdown(
            f"""
            <div class="wow-card">
              <div class="wow-subtle">
                Steps completed: <b>{ok}/{total}</b><br/>
                {t('dash_pdf_ready')}: <b>{pdf_ready}</b><br/>
                Readiness score: <b>{readiness}%</b>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown(f"#### {t('dash_field_stats')}")
    stats = st.session_state.pdfspec_last_validation.get("field_stats") if isinstance(st.session_state.pdfspec_last_validation, dict) else None
    if stats:
        by = stats.get("by_type", {})
        st.markdown(
            f"""
            <div class="wow-card">
              <div class="wow-subtle">
                Detected fields: <b>{stats.get('total','—')}</b><br/>
                Text: <b>{by.get('text',0)}</b> &nbsp;&nbsp;
                Textarea: <b>{by.get('textarea',0)}</b> &nbsp;&nbsp;
                Dropdown: <b>{by.get('dropdown',0)}</b> &nbsp;&nbsp;
                Checkbox: <b>{by.get('checkbox',0)}</b><br/>
                Unique IDs: <b>{stats.get('unique_ids','—')}</b>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="wow-card">
              <div class="wow-subtle">
                Detected fields: —<br/>
                (Generate/validate a PDFSpec to populate stats.)
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
        if st.session_state.form_content.strip() == "":
            st.session_state.form_content = load_sample()
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
                    try:
                        text = raw.decode("utf-8", errors="replace")
                    except Exception:
                        text = raw.decode(errors="replace")
                elif name.endswith(".docx"):
                    try:
                        import docx  # python-docx
                        doc = docx.Document(io.BytesIO(raw))
                        parts = [para.text for para in doc.paragraphs]
                        text = "\n".join(parts).strip()
                    except Exception:
                        st.error("DOCX parsing requires `python-docx`. Upload .md/.txt or add dependency.")
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

    top = st.columns([1.2, 1, 1, 1])
    with top[0]:
        st.markdown(
            f"""
            <div class="wow-card">
              <div class="wow-subtle">
                <b>Input</b>: {('sample.md' if st.session_state.form_source_mode=='default' else 'custom form')}<br/>
                <b>Content hash</b>: <code>{hash_text(st.session_state.form_content)}</code>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top[1]:
        st.session_state.token_budget = st.number_input(
            t("pipeline_max_tokens"), min_value=256, max_value=200000, value=int(st.session_state.token_budget), step=256
        )
    with top[2]:
        if st.button("Mark Running", use_container_width=True):
            set_status("running")
            st.rerun()
    with top[3]:
        if st.button("Mark Idle", use_container_width=True):
            set_status("idle")
            st.rerun()

    st.write("")

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
                step["model"] = st.selectbox(
                    t("pipeline_model"),
                    options=MODELS,
                    index=MODELS.index(step["model"]) if step["model"] in MODELS else 0,
                    key=f"model_{step['id']}",
                )
                step["max_tokens"] = st.number_input(
                    t("pipeline_max_tokens"),
                    min_value=256,
                    max_value=200000,
                    value=int(step.get("max_tokens", 12000)),
                    step=256,
                    key=f"max_tokens_{step['id']}",
                )
                step["prompt"] = st.text_area(
                    t("pipeline_prompt"),
                    value=step.get("prompt", ""),
                    height=140,
                    key=f"prompt_{step['id']}",
                )

                btns = st.columns([1, 1, 1])
                with btns[0]:
                    if st.button(t("pipeline_run_step"), key=f"run_{step['id']}", use_container_width=True):
                        set_status("running")
                        if idx == 0:
                            input_text = st.session_state.form_content
                        else:
                            prev = st.session_state.pipeline[idx - 1]
                            input_text = prev["final_output"] or prev["generated_output"] or st.session_state.form_content

                        out, latency_ms = fake_agent_run(step, input_text)
                        step["generated_output"] = out
                        step["final_output"] = step["final_output"] or out
                        step["status"] = "done"
                        set_status("awaiting", latency_ms=latency_ms)
                        st.rerun()

                with btns[1]:
                    if st.button(t("pipeline_run_from_here"), key=f"run_from_{step['id']}", use_container_width=True):
                        set_status("running")
                        input_text = st.session_state.form_content if idx == 0 else (
                            st.session_state.pipeline[idx - 1]["final_output"]
                            or st.session_state.pipeline[idx - 1]["generated_output"]
                            or st.session_state.form_content
                        )
                        total_latency = 0
                        for j in range(idx, len(st.session_state.pipeline)):
                            stp = st.session_state.pipeline[j]
                            out, lat = fake_agent_run(stp, input_text)
                            stp["generated_output"] = out
                            stp["final_output"] = stp["final_output"] or out
                            stp["status"] = "done"
                            input_text = stp["final_output"]
                            total_latency += lat
                        set_status("awaiting", latency_ms=total_latency)
                        st.rerun()

                with btns[2]:
                    if st.button(t("pipeline_reset_output"), key=f"reset_{step['id']}", use_container_width=True):
                        step["final_output"] = step.get("generated_output", "")
                        st.rerun()

            with cR:
                view = st.radio(
                    "View",
                    options=["text", "md"],
                    horizontal=True,
                    format_func=lambda x: t("pipeline_view_text") if x == "text" else t("pipeline_view_md"),
                    key=f"view_{step['id']}",
                    label_visibility="collapsed",
                )

                step["final_output"] = st.text_area(
                    t("pipeline_output"),
                    value=step.get("final_output", ""),
                    height=280,
                    key=f"output_{step['id']}",
                )

                if st.button(t("pipeline_accept"), key=f"accept_{step['id']}", use_container_width=True):
                    step["status"] = "accepted"

                    # Hook: if this is the PDFSpec step, capture it for the Spec tab.
                    if step["id"] == "pdf_spec":
                        st.session_state.pdfspec_text = step["final_output"] or st.session_state.pdfspec_text

                    set_status("awaiting")
                    st.rerun()

                if view == "md" and step["final_output"].strip():
                    st.markdown("---")
                    st.markdown("**Rendered Markdown Preview**")
                    st.markdown(step["final_output"])


def page_spec_to_pdf():
    wow_header(t("nav_spec"), t("spec_subtitle"))

    left, right = st.columns([1.1, 1])

    with left:
        st.markdown(f"#### {t('spec_source')}")
        source = st.radio(
            "",
            options=["use_last", "paste_new", "load_example"],
            horizontal=True,
            format_func=lambda x: {
                "use_last": t("spec_use_last"),
                "paste_new": t("spec_paste_new"),
                "load_example": t("spec_load_example"),
            }[x],
            label_visibility="collapsed",
        )

        if source == "use_last":
            if st.session_state.pdfspec_last_valid_text.strip():
                st.session_state.pdfspec_text = st.session_state.pdfspec_last_valid_text
            else:
                st.info(t("spec_no_last_spec"))
        elif source == "load_example":
            st.session_state.pdfspec_text = DEFAULT_PDFSPEC_MD

        # Controls
        opts = st.columns([1, 1, 1])
        with opts[0]:
            st.session_state.pdfspec_strict_mode = st.checkbox(
                t("spec_strict"),
                value=bool(st.session_state.pdfspec_strict_mode),
            )
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
        st.session_state.pdfspec_text = st.text_area(
            "",
            value=st.session_state.pdfspec_text,
            height=520,
            label_visibility="collapsed",
        )

        btns = st.columns([1, 1, 1])
        with btns[0]:
            if st.button(t("spec_validate"), use_container_width=True):
                set_status("running")
                start = time.time()
                spec_obj, parse_errors = parse_pdfspec(st.session_state.pdfspec_text)
                if parse_errors:
                    report = {"errors": parse_errors, "warnings": [], "normalized": None}
                else:
                    report = validate_pdfspec(spec_obj)
                st.session_state.pdfspec_last_validation = report
                if report.get("normalized") is not None and not report.get("errors"):
                    st.session_state.pdfspec_last_valid_text = st.session_state.pdfspec_text
                latency = int((time.time() - start) * 1000)
                set_status("awaiting", latency_ms=latency)
                st.rerun()

        with btns[1]:
            if st.button(t("spec_generate"), use_container_width=True):
                set_status("running")
                start = time.time()

                spec_obj, parse_errors = parse_pdfspec(st.session_state.pdfspec_text)
                if parse_errors:
                    st.session_state.pdfspec_last_validation = {"errors": parse_errors, "warnings": [], "normalized": None}
                    set_status("failed", latency_ms=int((time.time() - start) * 1000))
                    st.rerun()

                report = validate_pdfspec(spec_obj)
                st.session_state.pdfspec_last_validation = report

                errors = report.get("errors") or []
                warnings = report.get("warnings") or []
                if errors or (st.session_state.pdfspec_strict_mode and warnings):
                    set_status("failed", latency_ms=int((time.time() - start) * 1000))
                    st.rerun()

                spec_norm = report["normalized"]
                pdf_bytes, render_log = pdfspec_to_pdf_bytes(spec_norm)

                st.session_state.pdf_bytes = pdf_bytes
                st.session_state.pdf_render_log = render_log
                st.session_state.pdf_generated_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
                st.session_state.pdf_generated_from = "spec"
                st.session_state.pdf_last_reconcile = None

                # Save last valid spec text on successful generation
                st.session_state.pdfspec_last_valid_text = st.session_state.pdfspec_text

                latency = int((time.time() - start) * 1000)
                set_status("done", latency_ms=latency)
                st.rerun()

        with btns[2]:
            if st.button(t("spec_reset_last_valid"), use_container_width=True):
                if st.session_state.pdfspec_last_valid_text.strip():
                    st.session_state.pdfspec_text = st.session_state.pdfspec_last_valid_text
                    st.rerun()
                else:
                    st.info(t("spec_no_last_spec"))

        # Reports
        st.write("")
        st.markdown(f"#### {t('spec_validation')}")
        rep = st.session_state.pdfspec_last_validation or {"errors": [], "warnings": []}
        errs = rep.get("errors") or []
        warns = rep.get("warnings") or []
        with st.expander(t("spec_validation"), expanded=True):
            if errs:
                st.error("\n".join([f"- {e}" for e in errs]))
            else:
                st.success("No errors.")
            if warns:
                st.warning("\n".join([f"- {w}" for w in warns]))
            else:
                st.info("No warnings.")

    with right:
        st.markdown(f"#### {t('spec_preview')}")
        if st.session_state.pdf_bytes:
            st.markdown(pdf_iframe_view(st.session_state.pdf_bytes, height=720), unsafe_allow_html=True)

            # Provide open in new tab link
            b64 = base64.b64encode(st.session_state.pdf_bytes).decode("utf-8")
            st.markdown(f"[{t('spec_open_new_tab')}]({{'data:application/pdf;base64,' + b64}})")

            st.download_button(
                label=t("spec_download"),
                data=st.session_state.pdf_bytes,
                file_name="dynamic_form.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

            st.write("")
            with st.expander(t("spec_render_log"), expanded=False):
                log = st.session_state.pdf_render_log or []
                st.code("\n".join(log) if log else "—", language="text")

            st.write("")
            st.markdown(f"#### {t('spec_upload_pdf')}")
            up = st.file_uploader(t("spec_upload_pdf"), type=["pdf"], key="upload_modified_pdf")
            if up is not None:
                uploaded_bytes = up.read()
                st.success("Uploaded.")

                if st.button(t("spec_reconcile"), use_container_width=True):
                    rep = st.session_state.pdfspec_last_validation
                    spec_norm = rep.get("normalized") if isinstance(rep, dict) else None

                    # If no validated spec, try to validate current editor content
                    if not spec_norm:
                        spec_obj, parse_errors = parse_pdfspec(st.session_state.pdfspec_text)
                        if parse_errors:
                            st.error("Spec parse failed; cannot reconcile.")
                        else:
                            vrep = validate_pdfspec(spec_obj)
                            if vrep.get("errors"):
                                st.error("Spec validation failed; cannot reconcile.")
                            else:
                                spec_norm = vrep.get("normalized")

                    if spec_norm:
                        st.session_state.pdf_last_reconcile = reconcile_pdf_vs_spec(spec_norm, uploaded_bytes)
                        st.rerun()

            if st.session_state.pdf_last_reconcile:
                st.write("")
                st.markdown(f"#### {t('spec_reconcile_report')}")
                with st.expander(t("spec_reconcile_report"), expanded=True):
                    st.json(st.session_state.pdf_last_reconcile, expanded=False)

            st.write("")
            if st.button(t("spec_save_version"), use_container_width=True):
                snap = {
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "lang": st.session_state.lang,
                    "theme": st.session_state.theme,
                    "style_key": st.session_state.style_key,
                    "origin": "spec",
                    "pdf_generated_at": st.session_state.pdf_generated_at,
                    "pdf_b64": base64.b64encode(st.session_state.pdf_bytes).decode("utf-8"),
                    "pdfspec_text": st.session_state.pdfspec_text,
                    "validation": st.session_state.pdfspec_last_validation,
                }
                st.session_state.history.insert(0, snap)
                st.success("Saved.")
                st.rerun()
        else:
            st.info(t("spec_no_pdf"))


def page_notes():
    wow_header(t("nav_notes"), t("notes_title"))

    left, right = st.columns([1, 1])
    with left:
        st.markdown(f"#### {t('notes_paste')}")
        st.session_state.note_content = st.text_area(
            "", value=st.session_state.note_content, height=260, label_visibility="collapsed"
        )

        st.markdown("#### Persistent Prompt")
        st.session_state.note_persistent_prompt = st.text_area(
            "", value=st.session_state.note_persistent_prompt, height=100, label_visibility="collapsed"
        )

        if st.button(t("notes_transform"), use_container_width=True):
            st.session_state.note_markdown = organize_note_stub(st.session_state.note_content)
            set_status("awaiting")
            st.rerun()

        st.markdown(f"#### {t('notes_keywords')}")
        st.caption("Default coral highlight is applied in auto-organized output. Use AI Keywords for custom rules.")

        st.markdown(f"#### {t('notes_magics')}")
        magic = st.selectbox(
            "",
            options=["ai_keywords", "outline", "actions", "minutes", "simplify", "qa"],
            format_func=lambda x: {
                "ai_keywords": t("notes_magic_keywords"),
                "outline": t("notes_magic_outline"),
                "actions": t("notes_magic_actions"),
                "minutes": t("notes_magic_minutes"),
                "simplify": t("notes_magic_simplify"),
                "qa": t("notes_magic_qa"),
            }[x],
            label_visibility="collapsed",
        )

        if magic == "ai_keywords":
            kw = st.text_input("Keyword")
            color = st.color_picker("Color", value="#FF7F50")
            if st.button("Add rule", use_container_width=True):
                if kw.strip():
                    st.session_state.note_keyword_rules.append({"kw": kw.strip(), "color": color})
                    st.rerun()
            if st.session_state.note_keyword_rules:
                st.markdown("**Rules**")
                for r in st.session_state.note_keyword_rules:
                    st.markdown(f"- `{r['kw']}` → `{r['color']}`")
                if st.button("Clear rules", use_container_width=True):
                    st.session_state.note_keyword_rules = []
                    st.rerun()
        else:
            st.info("This WOW UI includes placeholders. Connect these Magics to your agent pipeline later.")
            st.button("Run selected Magic (placeholder)", use_container_width=True)

    with right:
        st.markdown("#### Output (editable Markdown)")
        st.session_state.note_markdown = st.text_area(
            "", value=st.session_state.note_markdown, height=420, label_visibility="collapsed"
        )

        st.markdown("#### Rendered Preview")
        preview = highlight_keywords_html(st.session_state.note_markdown, st.session_state.note_keyword_rules)
        st.markdown(preview, unsafe_allow_html=True)


def page_settings():
    wow_header(t("nav_settings"), t("settings_api_keys"))

    st.markdown(f"#### {t('settings_api_keys')}")
    for p in ["OpenAI", "Gemini", "Anthropic", "Grok"]:
        env = provider_env_key(p)
        effective = provider_effective_key(p)
        with st.expander(p, expanded=True):
            if env:
                st.success(t("settings_env_key_detected"))
                use_diff = st.checkbox(t("settings_use_different_key"), key=f"use_diff_{p}")
                if use_diff:
                    k = st.text_input(t("settings_enter_key"), type="password", key=f"key_{p}")
                    if st.button(t("settings_save"), key=f"save_{p}"):
                        if k.strip():
                            st.session_state.session_keys[p] = k.strip()
                            st.success(t("settings_never_shown"))
            else:
                if effective:
                    st.success(f"{t('provider_ready')} (session)")
                else:
                    st.warning(t("provider_missing"))
                k = st.text_input(t("settings_enter_key"), type="password", key=f"key_{p}")
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button(t("settings_save"), key=f"save_{p}"):
                        if k.strip():
                            st.session_state.session_keys[p] = k.strip()
                            st.success(t("settings_never_shown"))
                with c2:
                    if st.button("Clear", key=f"clear_{p}"):
                        st.session_state.session_keys.pop(p, None)
                        st.rerun()

    st.write("")
    st.markdown(f"#### {t('settings_privacy')}")
    st.info(t("settings_privacy_text"))

    if st.button(t("settings_clear"), use_container_width=True):
        st.session_state.session_keys = {}
        st.success("Cleared.")
        st.rerun()


def page_history():
    wow_header(t("nav_history"), t("history_title"))

    if not st.session_state.history:
        st.markdown(
            f"""
            <div class="wow-card">
              <div class="wow-subtle">{t('history_empty')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button(t("btn_save_version"), use_container_width=True):
            snap = {
                "ts": datetime.utcnow().isoformat() + "Z",
                "lang": st.session_state.lang,
                "theme": st.session_state.theme,
                "style_key": st.session_state.style_key,
                "origin": "ui_snapshot",
                "form_hash": hash_text(st.session_state.form_content or ""),
                "form_source_mode": st.session_state.form_source_mode,
                "pipeline": json.loads(json.dumps(st.session_state.pipeline)),
                "note_md_hash": hash_text(st.session_state.note_markdown or ""),
                "pdf_generated_at": st.session_state.pdf_generated_at,
                "pdf_generated_from": st.session_state.pdf_generated_from,
            }
            st.session_state.history.insert(0, snap)
            st.success("Saved.")
            st.rerun()

    with c2:
        st.caption("Versions are stored in session (ephemeral). Export/import can be added later.")

    if st.session_state.history:
        st.write("")
        for i, v in enumerate(st.session_state.history):
            title = f"Version {i+1} — {v.get('ts','?')} — origin:{v.get('origin','?')}"
            with st.expander(title):
                st.json(v, expanded=False)

                # If this version includes a pdf, offer download
                if "pdf_b64" in v:
                    try:
                        pdf_bytes = base64.b64decode(v["pdf_b64"])
                        st.download_button(
                            label="Download PDF from this version",
                            data=pdf_bytes,
                            file_name=f"dynamic_form_{i+1}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except Exception:
                        st.warning("PDF artifact in this version could not be decoded.")

                b1, b2 = st.columns([1, 1])
                with b1:
                    if st.button(t("btn_restore"), key=f"restore_{i}", use_container_width=True):
                        st.session_state.lang = v.get("lang", st.session_state.lang)
                        st.session_state.theme = v.get("theme", st.session_state.theme)
                        st.session_state.style_key = v.get("style_key", st.session_state.style_key)

                        if "pipeline" in v:
                            st.session_state.pipeline = v["pipeline"]

                        # Restore spec + pdf if present
                        if "pdfspec_text" in v:
                            st.session_state.pdfspec_text = v["pdfspec_text"]
                        if "validation" in v:
                            st.session_state.pdfspec_last_validation = v["validation"]
                        if "pdf_b64" in v:
                            try:
                                st.session_state.pdf_bytes = base64.b64decode(v["pdf_b64"])
                                st.session_state.pdf_generated_at = v.get("pdf_generated_at")
                                st.session_state.pdf_generated_from = v.get("origin")
                            except Exception:
                                pass

                        st.success("Restored.")
                        st.rerun()
                with b2:
                    if st.button(t("btn_delete"), key=f"delete_{i}", use_container_width=True):
                        st.session_state.history.pop(i)
                        st.rerun()


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
    page_spec_to_pdf()
elif page == "notes":
    page_notes()
elif page == "settings":
    page_settings()
elif page == "history":
    page_history()
else:
    page_dashboard()
