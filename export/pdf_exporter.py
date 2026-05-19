from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
import re
from typing import Any, Iterable, Sequence

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4
PROJECT_NAME = "Projeto de Revisão de Crenças"
REPORT_TITLE = "Relatório de Contração de Bases de Crenças"
REPORT_SUBTITLE = "Partial Meet Contraction e Kernel Contraction"

# Cores base
WHITE = colors.white
BLACK = colors.black
TEXT = colors.HexColor("#111827")
MUTED = colors.HexColor("#64748b")
BG = colors.HexColor("#f8fafc")
BG_2 = colors.HexColor("#f1f5f9")
BORDER = colors.HexColor("#cbd5e1")
BORDER_LIGHT = colors.HexColor("#e2e8f0")
RED = colors.HexColor("#dc2626")
RED_DARK = colors.HexColor("#991b1b")
RED_LIGHT = colors.HexColor("#fee2e2")
GREEN = colors.HexColor("#16a34a")
GREEN_DARK = colors.HexColor("#166534")
GREEN_LIGHT = colors.HexColor("#dcfce7")
YELLOW = colors.HexColor("#ca8a04")
YELLOW_LIGHT = colors.HexColor("#fef9c3")
NAVY = colors.HexColor("#0f172a")
BLUE = colors.HexColor("#2563eb")
BLUE_DARK = colors.HexColor("#1d4ed8")
BLUE_LIGHT = colors.HexColor("#dbeafe")
PURPLE = colors.HexColor("#7c3aed")
PURPLE_DARK = colors.HexColor("#5b21b6")
PURPLE_LIGHT = colors.HexColor("#ede9fe")
TEAL = colors.HexColor("#0d9488")
TEAL_DARK = colors.HexColor("#0f766e")
TEAL_LIGHT = colors.HexColor("#ccfbf1")
ORANGE = colors.HexColor("#f97316")
ORANGE_DARK = colors.HexColor("#c2410c")
ORANGE_LIGHT = colors.HexColor("#ffedd5")
ROSE = colors.HexColor("#e11d48")
ROSE_DARK = colors.HexColor("#9f1239")
ROSE_LIGHT = colors.HexColor("#ffe4e6")

# Paletas por tipo de contração.
# Pedido: manter cores diferentes para cada uma das contrações.
PALETTES: dict[str, dict[str, Any]] = {
    "partial meet": {
        "name": "Partial Meet",
        "accent": colors.HexColor("#dc2626"),
        "accent_dark": colors.HexColor("#991b1b"),
        "secondary": colors.HexColor("#dc2626"),
        "secondary_dark": colors.HexColor("#991b1b"),
        "tertiary": colors.HexColor("#334155"),
        "tertiary_dark": colors.HexColor("#0f172a"),
        "info": colors.HexColor("#334155"),
        "info_dark": colors.HexColor("#0f172a"),
        "success": colors.HexColor("#16a34a"),
        "success_dark": colors.HexColor("#166534"),
        "warning": colors.HexColor("#334155"),
        "warning_dark": colors.HexColor("#0f172a"),
        "danger": colors.HexColor("#dc2626"),
        "danger_dark": colors.HexColor("#991b1b"),
        "pale": colors.HexColor("#fff1f2"),
        "pale_2": colors.HexColor("#f8fafc"),
        "pale_3": colors.HexColor("#f1f5f9"),
        "pale_info": colors.HexColor("#f8fafc"),
        "pale_success": colors.HexColor("#f0fdf4"),
        "pale_warning": colors.HexColor("#f8fafc"),
        "dark": colors.HexColor("#450a0a"),
        "hex": "#dc2626",
        "dark_hex": "#450a0a",
        "pale_hex": "#fff1f2",
    },
    "kernel": {
        "name": "Kernel",
        "accent": colors.HexColor("#059669"),
        "accent_dark": colors.HexColor("#065f46"),
        "secondary": colors.HexColor("#059669"),
        "secondary_dark": colors.HexColor("#065f46"),
        "tertiary": colors.HexColor("#334155"),
        "tertiary_dark": colors.HexColor("#0f172a"),
        "info": colors.HexColor("#334155"),
        "info_dark": colors.HexColor("#0f172a"),
        "success": colors.HexColor("#16a34a"),
        "success_dark": colors.HexColor("#166534"),
        "warning": colors.HexColor("#334155"),
        "warning_dark": colors.HexColor("#0f172a"),
        "danger": colors.HexColor("#dc2626"),
        "danger_dark": colors.HexColor("#991b1b"),
        "pale": colors.HexColor("#ecfdf5"),
        "pale_2": colors.HexColor("#f8fafc"),
        "pale_3": colors.HexColor("#f1f5f9"),
        "pale_info": colors.HexColor("#f8fafc"),
        "pale_success": colors.HexColor("#f0fdf4"),
        "pale_warning": colors.HexColor("#f8fafc"),
        "dark": colors.HexColor("#052e16"),
        "hex": "#059669",
        "dark_hex": "#052e16",
        "pale_hex": "#ecfdf5",
    },
    "default": {
        "name": "Contração",
        "accent": colors.HexColor("#334155"),
        "accent_dark": colors.HexColor("#0f172a"),
        "secondary": colors.HexColor("#334155"),
        "secondary_dark": colors.HexColor("#0f172a"),
        "tertiary": colors.HexColor("#334155"),
        "tertiary_dark": colors.HexColor("#0f172a"),
        "info": colors.HexColor("#334155"),
        "info_dark": colors.HexColor("#0f172a"),
        "success": colors.HexColor("#16a34a"),
        "success_dark": colors.HexColor("#166534"),
        "warning": colors.HexColor("#334155"),
        "warning_dark": colors.HexColor("#0f172a"),
        "danger": colors.HexColor("#dc2626"),
        "danger_dark": colors.HexColor("#991b1b"),
        "pale": colors.HexColor("#f1f5f9"),
        "pale_2": colors.HexColor("#f8fafc"),
        "pale_3": colors.HexColor("#f1f5f9"),
        "pale_info": colors.HexColor("#f8fafc"),
        "pale_success": colors.HexColor("#f0fdf4"),
        "pale_warning": colors.HexColor("#f8fafc"),
        "dark": colors.HexColor("#0f172a"),
        "hex": "#334155",
        "dark_hex": "#0f172a",
        "pale_hex": "#f1f5f9",
    },
}

OPERATOR_LABELS = {
    "partial_meet": "Partial Meet Contraction",
    "partial meet": "Partial Meet Contraction",
    "partial meet contraction": "Partial Meet Contraction",
    "partial-meet": "Partial Meet Contraction",
    "kernel": "Kernel Contraction",
    "kernel_contraction": "Kernel Contraction",
    "kernel contraction": "Kernel Contraction",
}

STRATEGY_LABELS = {
    "full": "Full meet",
    "first": "Maxichoice",
    "max_cardinality": "Maior cardinalidade",
    "manual": "Manual",
    "common_first": "Comum se existir",
    "first_each": "Primeira por kernel",
    "min_hitting": "Incisão mínima",
}

# ============================================================
# FONTES
# ============================================================


def _try_register_unicode_font() -> tuple[str, str, bool]:
    """
    Usa uma fonte Unicode já instalada no sistema, se existir.
    Isto evita problemas com símbolos como ¬, ∧, ∨, →, ↔, γ e σ.
    Não distribui nem copia fontes: apenas regista fontes locais.
    """
    candidates_regular = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    candidates_bold = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]

    regular = next((p for p in candidates_regular if Path(p).exists()), None)
    bold = next((p for p in candidates_bold if Path(p).exists()), None)

    if regular:
        try:
            pdfmetrics.registerFont(TTFont("AppUnicode", regular))
            if bold:
                pdfmetrics.registerFont(TTFont("AppUnicode-Bold", bold))
                return "AppUnicode", "AppUnicode-Bold", True
            return "AppUnicode", "AppUnicode", True
        except Exception:
            pass

    return "Helvetica", "Helvetica-Bold", False


FONT_REGULAR, FONT_BOLD, HAS_UNICODE_FONT = _try_register_unicode_font()

# ============================================================
# TEXTO E FÓRMULAS
# ============================================================

COMMON_REPLACEMENTS = {
    "—": "-",
    "–": "-",
    "“": '"',
    "”": '"',
    "’": "'",
    "´": "'",
    "⊢": " implica ",
    "⊬": " não implica ",
    "⊨": " implica logicamente ",
    "⊭": " não implica logicamente ",
}

UNICODE_FALLBACKS = {
    "¬": "neg",
    "∧": "e",
    "∨": "ou",
    "→": "imp",
    "↔": "eq",
    "⊢": "implica",
    "⊬": "nao implica",
    "⊨": "implica logicamente",
    "⊭": "nao implica logicamente",
    "∅": "vazio",
    "∩": "intersecao",
    "∪": "uniao",
    "⊆": "subconjunto de",
    "⊂": "subconjunto proprio de",
    "γ": "gama",
    "σ": "sigma",
    "α": "alpha",
    "β": "beta",
    "✓": "OK",
    "✗": "X",
}


def _safe_text(value: object) -> str:
    text = "" if value is None else str(value)
    for old, new in COMMON_REPLACEMENTS.items():
        text = text.replace(old, new)
    if not HAS_UNICODE_FONT:
        for old, new in UNICODE_FALLBACKS.items():
            text = text.replace(old, new)
    return text


def _html(value: object) -> str:
    return escape(_safe_text(value)).replace("\n", "<br/>")


def _p(value: object, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_html(value), style)


def _p_markup(markup: str, style: ParagraphStyle) -> Paragraph:
    """Cria Paragraph com markup controlado internamente."""
    if not HAS_UNICODE_FONT:
        for old, new in UNICODE_FALLBACKS.items():
            markup = markup.replace(old, new)
    return Paragraph(markup, style)


def _normalize_formula(value: object) -> str:
    """Transforma a sintaxe textual do projeto em símbolos mais bonitos no PDF."""
    text = _safe_text(value).strip()
    if not text:
        return ""

    if HAS_UNICODE_FONT:
        replacements = [
            (r"\bneg\b", "¬"),
            (r"\be\b", "∧"),
            (r"\bou\b", "∨"),
            (r"\bimp\b", "→"),
            (r"\beq\b", "↔"),
        ]
        for pattern, repl in replacements:
            text = re.sub(pattern, repl, text)

    # Limpeza visual de espaços.
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("( ", "(").replace(" )", ")")
    return text


def _normalize_text_line(value: object) -> str:
    text = _safe_text(value).strip()
    if not text:
        return ""

    # Tradução de símbolos internos/estratégias para nomes legíveis.
    replacements = {
        "Estratégia γ: full": "Estratégia de seleção: Full meet",
        "Estratégia γ: first": "Estratégia de seleção: Maxichoice",
        "Estratégia γ: max_cardinality": "Estratégia de seleção: Maior cardinalidade",
        "Estratégia γ: manual": "Estratégia de seleção: Manual",
        "Estratégia σ: common_first": "Estratégia de incisão: Comum se existir",
        "Estratégia σ: first_each": "Estratégia de incisão: Primeira por kernel",
        "Estratégia σ: min_hitting": "Estratégia de incisão: Incisão mínima",
        "Estratégia σ: manual": "Estratégia de incisão: Manual",
        "α =": "Fórmula alvo:",
        "Fórmula alvo α:": "Fórmula alvo:",
        "A implica α": "A base inicial implica a fórmula alvo.",
        "A não implica α": "A base inicial não implica a fórmula alvo.",
        "A nao implica α": "A base inicial não implica a fórmula alvo.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    return [value]


def _clean_list(value: Any) -> list[str]:
    items = []
    for item in _as_list(value):
        if isinstance(item, (list, tuple, set)):
            inner = [_normalize_formula(x) for x in item if str(x).strip()]
            text = "{" + ", ".join(inner) + "}"
        else:
            text = _normalize_formula(item)
        if text:
            items.append(text)
    return items


def _dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _limit_items_for_cell(items: Sequence[str], max_items: int = 24) -> list[str]:
    """Evita células gigantes em tabelas do ReportLab.

    Tabelas do ReportLab não conseguem dividir uma linha muito alta por várias páginas.
    Por isso, nas tabelas de resumo mostramos uma lista compacta; os passos detalhados
    continuam a ser divididos em blocos menores mais abaixo.
    """
    if len(items) <= max_items:
        return list(items)
    hidden = len(items) - max_items
    return list(items[:max_items]) + [f"... e mais {hidden} elemento(s)"]


def _set_text(items: Sequence[str], empty: str = "Nenhuma", max_items: int = 24) -> str:
    if not items:
        return empty
    return ", ".join(_limit_items_for_cell(items, max_items=max_items))


def _numbered_list(
    items: Sequence[Any], empty: str = "Nenhum elemento", max_items: int = 24
) -> str:
    cleaned = _clean_list(items)
    if not cleaned:
        return empty
    limited = _limit_items_for_cell(cleaned, max_items=max_items)
    return "\n".join(f"{i}. {item}" for i, item in enumerate(limited, start=1))


def _join_inline(
    items: Sequence[Any], empty: str = "não indicado", max_items: int = 24
) -> str:
    cleaned = _clean_list(items)
    if not cleaned:
        return empty
    return ", ".join(_limit_items_for_cell(cleaned, max_items=max_items))


def _friendly_operator(value: object) -> str:
    raw = _safe_text(value).strip()
    return OPERATOR_LABELS.get(raw.lower(), raw or "Não indicado")


def _friendly_strategy(value: object) -> str:
    raw = _safe_text(value).strip()
    return STRATEGY_LABELS.get(raw.lower(), raw or "Não indicada")


def _operator_key(operation: dict[str, Any]) -> str:
    op = _safe_text(operation.get("operator", "")).lower().strip()
    if "partial" in op or "meet" in op:
        return "partial meet"
    if "kernel" in op:
        return "kernel"
    return "default"


def _palette(operation: dict[str, Any]) -> dict[str, Any]:
    return PALETTES.get(_operator_key(operation), PALETTES["default"])


def _mode_label(operation: dict[str, Any]) -> str:
    if _options(operation):
        return "Exploração de todas as opções"
    return "Última contração executada"


def _steps(operation: dict[str, Any]) -> list[str]:
    raw = operation.get("steps", [])
    result: list[str] = []
    for step in _as_list(raw):
        for line in str(step).splitlines():
            line = _normalize_text_line(line)
            if line:
                result.append(line)
    return result


def _options(operation: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("options", "all_options", "possibilities", "alternatives"):
        value = operation.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _removed_formulas(before: Sequence[str], after: Sequence[str]) -> list[str]:
    after_set = set(after)
    return [formula for formula in before if formula not in after_set]


def _kept_formulas(before: Sequence[str], after: Sequence[str]) -> list[str]:
    after_set = set(after)
    return [formula for formula in before if formula in after_set]


def _added_formulas(before: Sequence[str], after: Sequence[str]) -> list[str]:
    before_set = set(before)
    return [formula for formula in after if formula not in before_set]


# ============================================================
# ESTILOS
# ============================================================


def _build_styles(palette: dict[str, Any]) -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCustom",
            parent=sample["Title"],
            fontName=FONT_BOLD,
            fontSize=26,
            leading=32,
            alignment=TA_CENTER,
            textColor=palette["dark"],
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCustom",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=11.2,
            leading=16,
            alignment=TA_CENTER,
            textColor=MUTED,
            spaceAfter=8,
        ),
        "section": ParagraphStyle(
            "SectionCustom",
            parent=sample["Heading1"],
            fontName=FONT_BOLD,
            fontSize=17,
            leading=23,
            textColor=palette["accent_dark"],
            spaceBefore=4,
            spaceAfter=6,
        ),
        "subsection": ParagraphStyle(
            "SubsectionCustom",
            parent=sample["Heading2"],
            fontName=FONT_BOLD,
            fontSize=12.6,
            leading=16,
            textColor=palette["secondary_dark"],
            spaceBefore=5,
            spaceAfter=4,
        ),
        "subsection_soft": ParagraphStyle(
            "SubsectionSoft",
            parent=sample["Heading2"],
            fontName=FONT_BOLD,
            fontSize=10.5,
            leading=13.5,
            textColor=palette["accent_dark"],
            spaceBefore=4,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "BodyCustom",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=9.4,
            leading=13.6,
            textColor=TEXT,
            spaceAfter=3,
        ),
        "body_bold": ParagraphStyle(
            "BodyBoldCustom",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=9.4,
            leading=13.6,
            textColor=TEXT,
            spaceAfter=3,
        ),
        "muted": ParagraphStyle(
            "MutedCustom",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.9,
            leading=12.8,
            textColor=MUTED,
            spaceAfter=3,
        ),
        "small": ParagraphStyle(
            "SmallCustom",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.35,
            leading=11.8,
            textColor=TEXT,
        ),
        "small_bold": ParagraphStyle(
            "SmallBoldCustom",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=8.25,
            leading=11.6,
            textColor=TEXT,
        ),
        "small_muted": ParagraphStyle(
            "SmallMutedCustom",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.05,
            leading=11.2,
            textColor=MUTED,
        ),
        "table_label": ParagraphStyle(
            "TableLabel",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=8.55,
            leading=11.2,
            textColor=palette["dark"],
        ),
        "formula": ParagraphStyle(
            "FormulaCustom",
            parent=sample["Code"],
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=12.2,
            textColor=palette["dark"],
        ),
        "formula_kept": ParagraphStyle(
            "FormulaKept",
            parent=sample["Code"],
            fontName=FONT_REGULAR,
            fontSize=8.45,
            leading=12,
            textColor=GREEN_DARK,
        ),
        "formula_removed": ParagraphStyle(
            "FormulaRemoved",
            parent=sample["Code"],
            fontName=FONT_BOLD,
            fontSize=8.45,
            leading=12,
            textColor=RED_DARK,
        ),
        "metric_label": ParagraphStyle(
            "MetricLabel",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=7.1,
            leading=9.0,
            alignment=TA_CENTER,
            textColor=MUTED,
        ),
        "metric_label_light": ParagraphStyle(
            "MetricLabelLight",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=7.1,
            leading=9.0,
            alignment=TA_CENTER,
            textColor=WHITE,
        ),
        "metric_value": ParagraphStyle(
            "MetricValue",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=13.8,
            leading=17,
            alignment=TA_CENTER,
            textColor=palette["dark"],
        ),
        "metric_value_light": ParagraphStyle(
            "MetricValueLight",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=13.8,
            leading=17,
            alignment=TA_CENTER,
            textColor=WHITE,
        ),
        "metric_caption": ParagraphStyle(
            "MetricCaption",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=7.1,
            leading=9.0,
            alignment=TA_CENTER,
            textColor=MUTED,
        ),
        "metric_caption_light": ParagraphStyle(
            "MetricCaptionLight",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=7.1,
            leading=9.0,
            alignment=TA_CENTER,
            textColor=WHITE,
        ),
        "footer": ParagraphStyle(
            "FooterCustom",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=7.2,
            leading=9,
            textColor=MUTED,
        ),
    }


# ============================================================
# COMPONENTES VISUAIS
# ============================================================


def _page_footer(palette: dict[str, Any]):
    def draw(canvas, doc) -> None:
        canvas.saveState()
        canvas.setStrokeColor(BORDER_LIGHT)
        canvas.setLineWidth(0.7)
        canvas.line(1.6 * cm, 1.45 * cm, PAGE_WIDTH - 1.6 * cm, 1.45 * cm)

        canvas.setFillColor(palette["accent"])
        canvas.rect(1.6 * cm, 1.1 * cm, 0.22 * cm, 0.22 * cm, fill=1, stroke=0)

        canvas.setFillColor(MUTED)
        canvas.setFont(FONT_REGULAR, 7.4)
        canvas.drawString(
            1.95 * cm,
            1.08 * cm,
            f"{PROJECT_NAME} - {palette['name']} - Relatório de Contração",
        )
        canvas.drawRightString(PAGE_WIDTH - 1.6 * cm, 1.08 * cm, f"Página {doc.page}")
        canvas.restoreState()

    return draw


def _rule(color: colors.Color = BORDER_LIGHT, thickness: float = 0.7) -> HRFlowable:
    return HRFlowable(
        width="100%", thickness=thickness, color=color, spaceBefore=2, spaceAfter=8
    )


def _badge(
    text: object,
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
    *,
    width: float | None = None,
    secondary: bool = False,
) -> Table:
    bg = palette["pale_2"] if secondary else palette["pale"]
    fg = palette["secondary_dark"] if secondary else palette["accent_dark"]
    badge_style = ParagraphStyle(
        "BadgeStyle",
        parent=styles["small"],
        fontName=FONT_BOLD,
        fontSize=7.8,
        leading=9.8,
        alignment=TA_CENTER,
        textColor=fg,
    )
    table = Table(
        [[Paragraph(_html(text), badge_style)]],
        colWidths=[width] if width else None,
        hAlign="CENTER",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 0.35, bg),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _metric_card(
    label: str,
    value: object,
    caption: str,
    styles: dict[str, ParagraphStyle],
    width: float,
    *,
    band_color: colors.Color | None = None,
    body_color: colors.Color = WHITE,
    border_color: colors.Color = BORDER_LIGHT,
    light_text: bool = False,
) -> Table:
    """Cartão de métrica discreto: barra superior colorida e texto escuro.

    Quando o valor é uma frase longa, usa uma fonte menor e uma célula
    mais alta. Isto evita o bug visual em cartões como "Todas as incisões válidas".
    """
    value_text = _safe_text(value).strip()
    long_value = len(value_text) > 13 or " " in value_text

    value_style = styles["metric_value"]
    value_row_height = 0.86 * cm
    if long_value:
        value_style = ParagraphStyle(
            f"MetricValueLong_{abs(hash(value_text))}",
            parent=styles["metric_value"],
            fontName=FONT_BOLD,
            fontSize=9.8,
            leading=11.6,
            alignment=TA_CENTER,
            textColor=palette_dark_from_style(styles, fallback=TEXT),
        )
        value_row_height = 1.25 * cm

    table = Table(
        [
            [""],
            [_p(label.upper(), styles["metric_label"])],
            [_p(value_text, value_style)],
            [_p(caption, styles["metric_caption"])],
        ],
        colWidths=[width],
        rowHeights=[0.12 * cm, 0.48 * cm, value_row_height, 0.50 * cm],
        hAlign="CENTER",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), band_color or border_color),
                ("BACKGROUND", (0, 1), (-1, -1), body_color),
                ("BOX", (0, 0), (-1, -1), 0.55, border_color),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def palette_dark_from_style(
    styles: dict[str, ParagraphStyle], fallback: colors.Color = TEXT
) -> colors.Color:
    """Obtém uma cor escura consistente a partir do estilo das métricas."""
    try:
        color = getattr(styles.get("metric_value"), "textColor", None)
        return color or fallback
    except Exception:
        return fallback


def _metric_cards_grid(
    cards: Sequence[Table],
    *,
    columns: int = 4,
    col_width: float = 4.0 * cm,
) -> Table:
    rows: list[list[Any]] = []
    current: list[Any] = []
    for card in cards:
        current.append(card)
        if len(current) == columns:
            rows.append(current)
            current = []
    if current:
        while len(current) < columns:
            current.append(Spacer(1, 0.1 * cm))
        rows.append(current)
    table = Table(rows, colWidths=[col_width] * columns, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _summary_grid(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    before = _clean_list(operation.get("before", []))
    after = _clean_list(operation.get("after", []))
    removed = _removed_formulas(before, after)
    kept = _kept_formulas(before, after)
    width = 3.55 * cm
    cards = [
        _metric_card(
            "Base inicial",
            len(before),
            "fórmulas antes",
            styles,
            width,
            band_color=palette["accent_dark"],
            body_color=WHITE,
            border_color=BORDER_LIGHT,
        ),
        _metric_card(
            "Base final",
            len(after),
            "fórmulas depois",
            styles,
            width,
            band_color=palette["accent"],
            body_color=WHITE,
            border_color=BORDER_LIGHT,
        ),
        _metric_card(
            "Removidas",
            len(removed),
            f"{len(kept)} preservadas",
            styles,
            width,
            band_color=RED_DARK,
            body_color=WHITE,
            border_color=RED_LIGHT,
        ),
        _metric_card(
            "Estratégia",
            _friendly_strategy(operation.get("strategy", "-")),
            "seleção/incisão",
            styles,
            width,
            band_color=colors.HexColor("#334155"),
            body_color=WHITE,
            border_color=BORDER_LIGHT,
        ),
    ]
    return _metric_cards_grid(cards, columns=4, col_width=width + 0.25 * cm)


def _section_title(
    title: str, styles: dict[str, ParagraphStyle], palette: dict[str, Any]
) -> list[Any]:
    table = Table(
        [[_p(title, styles["section"])]], colWidths=[16.0 * cm], hAlign="CENTER"
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("LINEBELOW", (0, 0), (-1, 0), 1.0, palette["accent"]),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return [table, Spacer(1, 0.08 * cm)]


def _callout(
    title: str,
    body: str,
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
    *,
    tone: str = "info",
) -> Table:
    if tone == "warning":
        bg = YELLOW_LIGHT
        accent = YELLOW
        title_color = colors.HexColor("#854d0e")
    elif tone == "danger":
        bg = RED_LIGHT
        accent = RED
        title_color = RED_DARK
    elif tone == "success":
        bg = GREEN_LIGHT
        accent = GREEN
        title_color = GREEN_DARK
    else:
        bg = palette["pale"]
        accent = palette["accent"]
        title_color = palette["accent_dark"]

    title_style = ParagraphStyle(
        "CalloutTitle",
        parent=styles["body_bold"],
        fontName=FONT_BOLD,
        fontSize=9.1,
        leading=12.5,
        textColor=title_color,
    )
    rows = [[_p(title, title_style)], [_p(body, styles["small"])]]
    table = Table(rows, colWidths=[16.0 * cm], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
                ("BOX", (0, 0), (-1, -1), 0.35, bg),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _info_table(
    rows: Sequence[tuple[str, object]],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
    *,
    width: float = 16.0 * cm,
) -> Table:
    data = [
        [_p(label, styles["table_label"]), _p(value, styles["small"])]
        for label, value in rows
    ]
    table = Table(data, colWidths=[4.1 * cm, width - 4.1 * cm], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), BG_2),
                ("BACKGROUND", (1, 0), (1, -1), WHITE),
                ("GRID", (0, 0), (-1, -1), 0.35, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _formula_box(
    title: str,
    formulas: Sequence[str],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
    *,
    kind: str = "normal",
    width: float = 7.75 * cm,
) -> Table:
    if kind == "removed":
        header_bg = RED_DARK
        body_bg = RED_LIGHT
        border = RED
        formula_style = styles["formula_removed"]
    elif kind in {"kept", "final"}:
        header_bg = GREEN_DARK
        body_bg = GREEN_LIGHT
        border = GREEN
        formula_style = styles["formula_kept"] if kind == "kept" else styles["formula"]
    else:
        header_bg = colors.HexColor("#334155")
        body_bg = BG_2
        border = BORDER_LIGHT
        formula_style = styles["formula"]

    header_style = ParagraphStyle(
        f"Header_{title}",
        parent=styles["body_bold"],
        fontName=FONT_BOLD,
        fontSize=9.0,
        leading=12,
        textColor=WHITE,
    )
    cleaned = list(formulas)
    if not cleaned:
        body = [_p("(base vazia)", styles["small_muted"])]
    else:
        body = [
            _p(f"{idx}. {formula}", formula_style)
            for idx, formula in enumerate(cleaned, start=1)
        ]

    table = Table(
        [[_p(title, header_style)], [body]], colWidths=[width], hAlign="CENTER"
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("BACKGROUND", (0, 1), (-1, 1), body_bg),
                ("BOX", (0, 0), (-1, -1), 0.6, border),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _comparison_table(
    before: Sequence[str],
    after: Sequence[str],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    left = _formula_box("Base inicial", before, palette, styles, kind="normal")
    right = _formula_box("Base final", after, palette, styles, kind="final")
    table = Table([[left, right]], colWidths=[8.0 * cm, 8.0 * cm], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


def _status_chip(
    text: str,
    bg: colors.Color,
    fg: colors.Color,
    styles: dict[str, ParagraphStyle],
    *,
    width: float = 2.45 * cm,
) -> Table:
    """Pequena etiqueta visual usada em tabelas de estado."""
    chip_style = ParagraphStyle(
        "StatusChip",
        parent=styles["small"],
        fontName=FONT_BOLD,
        fontSize=7.2,
        leading=9.0,
        alignment=TA_CENTER,
        textColor=fg,
    )
    table = Table(
        [[Paragraph(_html(text), chip_style)]], colWidths=[width], hAlign="LEFT"
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 0.25, bg),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def _formula_status_table(
    before: Sequence[str],
    after: Sequence[str],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
    *,
    max_rows: int = 30,
) -> Table:
    """Mostra, fórmula a fórmula, o que aconteceu na contração."""
    after_set = set(after)
    rows: list[list[Any]] = [
        [
            _p("Fórmula da base inicial", styles["table_label"]),
            _p("Estado após a contração", styles["table_label"]),
            _p("Leitura", styles["table_label"]),
        ]
    ]

    limited = list(before[:max_rows])
    for formula in limited:
        if formula in after_set:
            status = _status_chip("MANTIDA", GREEN_LIGHT, GREEN_DARK, styles)
            reading = "Foi preservada porque não precisou de ser retirada para obter o resultado final."
        else:
            status = _status_chip("REMOVIDA", RED_LIGHT, RED_DARK, styles)
            reading = "Foi retirada por participar no conflito com a fórmula alvo segundo a estratégia aplicada."
        rows.append(
            [_p(formula, styles["formula"]), status, _p(reading, styles["small_muted"])]
        )

    hidden = len(before) - len(limited)
    if hidden > 0:
        rows.append(
            [
                _p(f"... e mais {hidden} fórmula(s)", styles["small_muted"]),
                _p("", styles["small_muted"]),
                _p(
                    "A lista foi resumida para manter o relatório legível.",
                    styles["small_muted"],
                ),
            ]
        )

    table = Table(
        rows, colWidths=[6.35 * cm, 3.0 * cm, 6.65 * cm], hAlign="CENTER", repeatRows=1
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), BG_2),
                ("GRID", (0, 0), (-1, -1), 0.35, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _process_timeline(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    """Resumo visual discreto do processo lógico usado pelo operador."""
    key = _operator_key(operation)
    if key == "partial meet":
        steps = [
            (
                "1",
                "Fórmula alvo",
                "Identificar α e o que deve deixar de ser implicado.",
            ),
            ("2", "Remainders", "Subconjuntos máximos que já não implicam α."),
            ("3", "Seleção γ", "Escolha das alternativas conforme a estratégia."),
            ("4", "Interseção", "Intersetar seleções para obter a base final."),
        ]
    elif key == "kernel":
        steps = [
            (
                "1",
                "Fórmula alvo",
                "Identificar α e confirmar se a contração é necessária.",
            ),
            ("2", "Kernels", "Subconjuntos mínimos que ainda implicam α."),
            ("3", "Incisão σ", "Escolher fórmulas que cortam todos os kernels."),
            ("4", "Remoção", "Remover a incisão e apresentar a base final."),
        ]
    else:
        steps = [
            ("1", "Entrada", "Ler a base e a fórmula alvo."),
            ("2", "Análise", "Determinar estruturas que sustentam α."),
            ("3", "Escolha", "Aplicar a estratégia de contração."),
            ("4", "Resultado", "Apresentar a base contraída."),
        ]

    number_style = ParagraphStyle(
        "TimelineNumber",
        parent=styles["metric_value"],
        fontName=FONT_BOLD,
        fontSize=12,
        leading=14,
        alignment=TA_CENTER,
        textColor=WHITE,
    )
    title_style = ParagraphStyle(
        "TimelineTitle",
        parent=styles["body_bold"],
        fontName=FONT_BOLD,
        fontSize=8.6,
        leading=11,
        alignment=TA_CENTER,
        textColor=palette["dark"],
    )
    desc_style = ParagraphStyle(
        "TimelineDesc",
        parent=styles["small_muted"],
        fontName=FONT_REGULAR,
        fontSize=7.3,
        leading=9.5,
        alignment=TA_CENTER,
        textColor=MUTED,
    )

    cards: list[Any] = []
    for number, title, desc in steps:
        card = Table(
            [
                [Paragraph(number, number_style)],
                [Paragraph(_html(title), title_style)],
                [Paragraph(_html(desc), desc_style)],
            ],
            colWidths=[3.75 * cm],
            rowHeights=[0.55 * cm, 0.50 * cm, 1.05 * cm],
        )
        card.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), palette["accent_dark"]),
                    ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                    ("BOX", (0, 0), (-1, -1), 0.45, BORDER_LIGHT),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        cards.append(card)

    table = Table([cards], colWidths=[4.0 * cm] * 4, hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return table


# ============================================================
# EXPLICAÇÕES E CONCLUSÕES
# ============================================================


def _first_int_from_patterns(
    lines: Sequence[str], patterns: Sequence[tuple[str, str]]
) -> dict[str, int]:
    found: dict[str, int] = {}
    for line in lines:
        low = line.lower()
        for pattern, label in patterns:
            if label in found:
                continue
            match = re.search(pattern, low)
            if match:
                found[label] = int(match.group(1))
    return found


def _extract_execution_metrics(operation: dict[str, Any]) -> list[tuple[str, object]]:
    key = _operator_key(operation)
    steps = _steps(operation)
    before = _clean_list(operation.get("before", []))
    after = _clean_list(operation.get("after", []))
    metrics: list[tuple[str, object]] = [
        ("Base inicial", len(before)),
        ("Base final", len(after)),
    ]

    if key == "partial meet":
        remainders = len(_clean_list(operation.get("remainders", [])))
        if remainders:
            metrics.append(("Remainders", remainders))
    elif key == "kernel":
        kernels = len(_clean_list(operation.get("kernels", [])))
        if kernels:
            metrics.append(("Kernels", kernels))

    options_count = len(_options(operation))
    if options_count:
        metrics.append(("Opções", options_count))

    patterns = [
        (r"foram encontrados\s+(\d+)\s+remainders?", "Remainders"),
        (r"foram encontrados\s+(\d+)\s+kernels?", "Kernels"),
        (r"n[uú]mero de sele[cç][oõ]es poss[ií]veis\s*:\s*(\d+)", "Seleções possíveis"),
        (r"n[uú]mero de incis[õo]es poss[ií]veis\s*:\s*(\d+)", "Incisões possíveis"),
        (r"foram geradas\s+(\d+)\s+op[cç][oõ]es", "Opções geradas"),
        (r"(\d+)\s+subconjuntos?.*n[aã]o implicam", "Subconjuntos que não implicam α"),
        (r"(\d+)\s+subconjuntos?.*implicam", "Subconjuntos que implicam α"),
        (r"(\d+)\s+elementos?.*n[aã]o implicam", "Elementos que não implicam α"),
        (r"(\d+)\s+elementos?.*implicam", "Elementos que implicam α"),
    ]
    found = _first_int_from_patterns(steps, patterns)
    known = {label for label, _ in metrics}
    for label, value in found.items():
        if label not in known:
            metrics.append((label, value))
    return metrics


def _overview_metrics_table(
    metrics: Sequence[tuple[str, object]],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    cards: list[Table] = []
    width = 3.55 * cm
    for label, value in metrics:
        low = str(label).lower()
        if "remov" in low:
            band = RED_DARK
            border = RED_LIGHT
        elif "base final" in low or "mant" in low:
            band = GREEN_DARK
            border = GREEN_LIGHT
        elif (
            "kernel" in low
            or "remainder" in low
            or "op" in low
            or "sele" in low
            or "incis" in low
        ):
            band = palette["accent_dark"]
            border = palette["pale"]
        else:
            band = colors.HexColor("#334155")
            border = BORDER_LIGHT
        cards.append(
            _metric_card(
                label,
                value,
                "indicador",
                styles,
                width,
                band_color=band,
                body_color=WHITE,
                border_color=border,
            )
        )
    return _metric_cards_grid(cards, columns=4, col_width=width + 0.25 * cm)


def _operator_explanation(operation: dict[str, Any]) -> str:
    key = _operator_key(operation)
    strategy = _friendly_strategy(operation.get("strategy", "Não indicada"))
    target = _normalize_formula(operation.get("target", "")) or "a fórmula alvo"

    if key == "partial meet":
        return (
            f"Foi aplicada uma contração por Partial Meet sobre a fórmula {target}. "
            "Este método procura subconjuntos máximos da base que já não implicam a fórmula alvo, "
            "chamados remainders. Depois, a função de seleção γ escolhe alguns desses remainders "
            f"segundo a estratégia {strategy}. A base final é obtida pela interseção dos remainders selecionados."
        )

    if key == "kernel":
        return (
            f"Foi aplicada uma contração por Kernel sobre a fórmula {target}. "
            "Este método identifica subconjuntos mínimos da base que ainda implicam a fórmula alvo, "
            "chamados kernels. Depois, a função de incisão σ escolhe fórmulas a remover, tocando pelo menos "
            f"um elemento de cada kernel, segundo a estratégia {strategy}."
        )

    return (
        f"Foi aplicada uma operação de contração sobre a fórmula {target}. "
        "O objetivo da contração é obter uma base resultante que deixe de sustentar a fórmula alvo, "
        "preservando o máximo possível da base inicial."
    )


def _warnings(
    operation: dict[str, Any],
    before: Sequence[str],
    after: Sequence[str],
    removed: Sequence[str],
    added: Sequence[str],
) -> list[tuple[str, str, str]]:
    warnings: list[tuple[str, str, str]] = []
    steps_text = "\n".join(_steps(operation)).lower()

    if not operation.get("target"):
        warnings.append(
            (
                "Fórmula alvo em falta",
                "Não foi encontrada uma fórmula alvo estruturada na operação.",
                "warning",
            )
        )

    if not before:
        warnings.append(
            (
                "Base inicial vazia",
                "A base inicial não contém fórmulas. A contração pode não ter efeito visível.",
                "warning",
            )
        )

    if not removed:
        warnings.append(
            (
                "Sem remoções",
                "A base final coincide com a base inicial ou nenhuma fórmula precisou de ser removida.",
                "info",
            )
        )

    if added:
        warnings.append(
            (
                "Fórmulas novas detetadas",
                "A base final contém fórmulas que não estavam na base inicial. Numa contração pura isto merece verificação.",
                "danger",
            )
        )

    if operation.get("target_is_tautology") is True or "tautologia" in steps_text:
        warnings.append(
            (
                "Fórmula alvo tautológica",
                "Se a fórmula alvo for uma tautologia, a contração não deve remover informação da base.",
                "warning",
            )
        )

    if "não implica" in steps_text or "nao implica" in steps_text:
        warnings.append(
            (
                "Contração possivelmente desnecessária",
                "Os passos indicam que a base inicial já podia não implicar a fórmula alvo.",
                "info",
            )
        )

    return warnings


def _automatic_conclusion(
    operation: dict[str, Any],
    before: Sequence[str],
    after: Sequence[str],
    removed: Sequence[str],
    kept: Sequence[str],
    added: Sequence[str],
) -> tuple[str, str]:
    target = _normalize_formula(operation.get("target", "")) or "a fórmula alvo"
    key = _operator_key(operation)
    op_name = (
        "Partial Meet"
        if key == "partial meet"
        else "Kernel" if key == "kernel" else "contração"
    )

    explicit_success = operation.get(
        "success", operation.get("contraction_success", None)
    )
    after_entails = operation.get(
        "after_entails_target", operation.get("final_entails_target", None)
    )

    if explicit_success is True or after_entails is False:
        title = "Contração concluída com sucesso"
        body = f"A base final foi obtida por {op_name} e já não implica {target}. Foram removidas {len(removed)} fórmula(s) e preservadas {len(kept)}."
        return title, body

    if explicit_success is False or after_entails is True:
        title = "Contração a rever"
        body = f"A informação recebida indica que a base final ainda pode implicar {target}. Confirma os passos e a estratégia usada."
        return title, body

    if added:
        title = "Resultado gerado, mas com aviso"
        body = "A base final foi gerada, mas contém fórmulas que não estavam na base inicial. Para uma contração pura, confirma se isto era intencional."
        return title, body

    if not removed:
        title = "Resultado sem alterações"
        body = f"A operação por {op_name} não removeu fórmulas. Isto é esperado quando a base inicial já não implica {target}, quando a fórmula alvo é tautológica ou quando a estratégia escolhida preserva toda a base possível."
        return title, body

    title = "Contração aplicada"
    body = f"A operação por {op_name} removeu {len(removed)} fórmula(s) e manteve {len(kept)}. A base final apresentada é o resultado da estratégia escolhida para contrair {target}."
    return title, body


# ============================================================
# SECÇÕES DO RELATÓRIO NORMAL
# ============================================================


def _cover_section(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    target = (
        _normalize_formula(operation.get("target", "Não indicada")) or "Não indicada"
    )
    operator = _friendly_operator(operation.get("operator", "Não indicado"))
    strategy = _friendly_strategy(operation.get("strategy", "Não indicada"))

    story: list[Any] = [Spacer(1, 0.4 * cm)]
    story.append(_p(REPORT_TITLE, styles["title"]))
    story.append(_p(REPORT_SUBTITLE, styles["subtitle"]))
    story.append(Spacer(1, 0.25 * cm))

    badges = Table(
        [
            [
                _badge(palette["name"], palette, styles, width=4.5 * cm),
                _badge(
                    _mode_label(operation),
                    palette,
                    styles,
                    width=7.0 * cm,
                    secondary=True,
                ),
            ]
        ],
        colWidths=[5.0 * cm, 7.5 * cm],
        hAlign="CENTER",
    )
    badges.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(badges)
    story.append(Spacer(1, 0.75 * cm))

    story.append(_summary_grid(operation, palette, styles))
    story.append(Spacer(1, 0.5 * cm))

    intro_rows = [
        ("Operador", operator),
        ("Estratégia", strategy),
        ("Fórmula alvo", target),
        ("Gerado em", datetime.now().strftime("%d/%m/%Y %H:%M")),
    ]
    story.append(_info_table(intro_rows, palette, styles))
    story.append(Spacer(1, 0.35 * cm))

    story.append(
        _callout("Como interpretar", _operator_explanation(operation), palette, styles)
    )
    story.append(PageBreak())
    return story


def _result_section(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    before = _clean_list(operation.get("before", []))
    after = _clean_list(operation.get("after", []))
    removed = _removed_formulas(before, after)
    kept = _kept_formulas(before, after)
    added = _added_formulas(before, after)

    story: list[Any] = []
    story.extend(_section_title("1. Resumo da operação", styles, palette))
    story.append(
        _p(
            "Esta secção mostra o efeito direto da contração: o estado da base antes da operação, "
            "o estado final e a diferença entre ambas.",
            styles["muted"],
        )
    )
    story.append(Spacer(1, 0.15 * cm))
    story.append(_comparison_table(before, after, palette, styles))
    story.append(Spacer(1, 0.28 * cm))

    if before:
        story.append(_p("Mapa fórmula a fórmula", styles["subsection"]))
        story.append(
            _p(
                "Esta leitura torna claro o que foi preservado e o que foi removido durante a contração.",
                styles["muted"],
            )
        )
        story.append(Spacer(1, 0.08 * cm))
        story.append(_formula_status_table(before, after, palette, styles))
        story.append(Spacer(1, 0.32 * cm))

    diff_table = Table(
        [
            [
                _formula_box(
                    "Fórmulas removidas",
                    removed,
                    palette,
                    styles,
                    kind="removed",
                    width=7.75 * cm,
                ),
                _formula_box(
                    "Fórmulas mantidas",
                    kept,
                    palette,
                    styles,
                    kind="kept",
                    width=7.75 * cm,
                ),
            ]
        ],
        colWidths=[8.0 * cm, 8.0 * cm],
        hAlign="CENTER",
    )
    diff_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(diff_table)
    story.append(Spacer(1, 0.35 * cm))

    for title, body, tone in _warnings(operation, before, after, removed, added):
        story.append(_callout(title, body, palette, styles, tone=tone))
        story.append(Spacer(1, 0.15 * cm))

    conclusion_title, conclusion_body = _automatic_conclusion(
        operation, before, after, removed, kept, added
    )
    story.append(
        _callout(
            conclusion_title,
            conclusion_body,
            palette,
            styles,
            tone="success" if "sucesso" in conclusion_title.lower() else "info",
        )
    )
    story.append(Spacer(1, 0.35 * cm))
    return story


def _diagnostic_section(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    key = _operator_key(operation)
    before = _clean_list(operation.get("before", []))
    after = _clean_list(operation.get("after", []))
    removed = _removed_formulas(before, after)
    kept = _kept_formulas(before, after)

    story: list[Any] = []
    story.extend(_section_title("2. Leitura do método aplicado", styles, palette))
    story.append(
        _p(
            "O relatório passa a explicitar o raciocínio do operador antes de mostrar os dados técnicos. "
            "Assim, o leitor percebe a ligação entre fórmula alvo, estruturas calculadas, escolha da estratégia e base final.",
            styles["muted"],
        )
    )
    story.append(Spacer(1, 0.12 * cm))
    story.append(_process_timeline(operation, palette, styles))
    story.append(Spacer(1, 0.28 * cm))

    if key == "partial meet":
        remainders = _clean_list(operation.get("remainders", []))
        selected = _clean_list(
            operation.get("selected_remainders", operation.get("selection", []))
        )
        rows = [
            ("Tipo de contração", "Partial Meet"),
            (
                "Ideia central",
                "Selecionar remainders através da função γ e intersetá-los para obter a base contraída.",
            ),
            (
                "Função de seleção γ",
                _friendly_strategy(operation.get("strategy", "Não indicada")),
            ),
            (
                "Remainders calculados",
                _numbered_list(
                    remainders,
                    "Não foram recebidos de forma estruturada; consulta os passos.",
                ),
            ),
            (
                "Remainders selecionados",
                _numbered_list(
                    selected, "Não indicados de forma estruturada; consulta os passos."
                ),
            ),
            ("Fórmulas removidas", _set_text(removed)),
            ("Fórmulas preservadas", _set_text(kept)),
        ]
    elif key == "kernel":
        kernels = _clean_list(operation.get("kernels", []))
        incision = _clean_list(
            operation.get("incision", operation.get("removed_formulas", removed))
        )
        rows = [
            ("Tipo de contração", "Kernel"),
            (
                "Ideia central",
                "Encontrar kernels e aplicar uma incisão σ que toque todos os subconjuntos críticos.",
            ),
            (
                "Função de incisão σ",
                _friendly_strategy(operation.get("strategy", "Não indicada")),
            ),
            (
                "Kernels calculados",
                _numbered_list(
                    kernels,
                    "Não foram recebidos de forma estruturada; consulta os passos.",
                ),
            ),
            ("Incisão / remoções", _set_text(incision)),
            ("Fórmulas preservadas", _set_text(kept)),
            (
                "Leitura final",
                "A base final é obtida removendo da base inicial as fórmulas escolhidas pela incisão.",
            ),
        ]
    else:
        rows = [
            (
                "Tipo de contração",
                _friendly_operator(operation.get("operator", "Não indicado")),
            ),
            (
                "Estratégia",
                _friendly_strategy(operation.get("strategy", "Não indicada")),
            ),
            ("Fórmulas removidas", _set_text(removed)),
            ("Fórmulas preservadas", _set_text(kept)),
        ]

    story.append(_info_table(rows, palette, styles))
    story.append(Spacer(1, 0.25 * cm))
    story.append(
        _callout(
            "Nota",
            "Esta secção substitui qualquer tabela de postulados. O foco do relatório fica no que foi calculado, no que foi selecionado/incidido e no efeito final sobre a base.",
            palette,
            styles,
        )
    )
    story.append(Spacer(1, 0.35 * cm))
    return story


def _split_steps_into_blocks(steps: Sequence[str]) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    current_title = "Execução"
    current_lines: list[str] = []

    for raw in steps:
        line = _normalize_text_line(raw)
        if not line:
            continue

        cleaned = line.strip("= ").strip()
        is_heading = line.startswith("===") or bool(re.match(r"^\d+\.\s+[^{}]+$", line))

        if is_heading:
            if current_lines or current_title != "Execução":
                blocks.append((current_title, current_lines))
            current_title = cleaned
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines or current_title != "Execução":
        blocks.append((current_title, current_lines))
    return blocks


def _split_long_display_line(line: str, max_chars: int = 150) -> list[str]:
    """Divide linhas longas em pedaços legíveis, preferindo ; e ,.

    Isto evita o erro: "Flowable ... too large on page", que acontece quando
    uma tabela recebe um parágrafo demasiado alto para caber numa página.
    """
    line = line.strip()
    if len(line) <= max_chars:
        return [line]

    parts = re.split(r"(;\s*|,\s*)", line)
    chunks: list[str] = []
    current = ""

    for idx in range(0, len(parts), 2):
        token = parts[idx]
        sep = parts[idx + 1] if idx + 1 < len(parts) else ""
        piece = token + sep

        if len(current) + len(piece) <= max_chars:
            current += piece
        else:
            if current.strip():
                chunks.append(current.strip())
            current = piece

    if current.strip():
        chunks.append(current.strip())

    final: list[str] = []
    for chunk in chunks or [line]:
        if len(chunk) <= max_chars:
            final.append(chunk)
        else:
            final.extend(
                chunk[i : i + max_chars] for i in range(0, len(chunk), max_chars)
            )
    return final


def _chunk_display_lines(
    lines: Sequence[str], *, max_lines: int = 10, max_chars: int = 1050
) -> list[list[str]]:
    expanded: list[str] = []
    for line in lines:
        expanded.extend(_split_long_display_line(line))

    chunks: list[list[str]] = []
    current: list[str] = []
    current_chars = 0

    for line in expanded:
        extra = len(line) + 1
        if current and (len(current) >= max_lines or current_chars + extra > max_chars):
            chunks.append(current)
            current = []
            current_chars = 0
        current.append(line)
        current_chars += extra

    if current:
        chunks.append(current)
    return chunks


def _simple_text_panel(
    text: str,
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
    *,
    width: float = 16.0 * cm,
    line_color: colors.Color | None = None,
    bg_color: colors.Color = WHITE,
    text_style: ParagraphStyle | None = None,
) -> Table:
    table = Table(
        [[Paragraph(_html(text), text_style or styles["small"])]],
        colWidths=[width],
        hAlign="CENTER",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg_color),
                ("LINEBEFORE", (0, 0), (0, -1), 3, line_color or palette["accent"]),
                ("BOX", (0, 0), (-1, -1), 0.35, BORDER_LIGHT),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def _format_log_line_markup(line: str) -> str:
    match = re.match(r"^([A-Za-zÀ-ÿ0-9#γσαβ\- ]{1,38})(:|\s*=)\s*(.+)$", line)
    if match:
        left, sep, right = match.groups()
        return f"<b>{_html(left)}{sep}</b> {_html(right)}"
    return _html(line)


def _classify_step_line(
    line: str, palette: dict[str, Any]
) -> tuple[colors.Color, colors.Color, str]:
    low = line.lower()
    if any(k in low for k in ["erro", "inválid", "invalid", "falhou", "falha"]):
        return RED_DARK, RED_LIGHT, "bold"
    if any(
        k in low
        for k in ["fórmulas removidas", "formulas removidas", "removidas", "removida"]
    ):
        return RED_DARK, RED_LIGHT, "bold"
    if any(
        k in low
        for k in [
            "base resultante",
            "base final",
            "mantidas",
            "preservadas",
            "conclu",
            "sucesso",
        ]
    ):
        return GREEN_DARK, GREEN_LIGHT, "bold"
    if any(
        k in low
        for k in [
            "foram encontrados",
            "número de",
            "numero de",
            "foram geradas",
            "subconjuntos",
            "remainders",
            "kernels",
        ]
    ):
        return palette["accent_dark"], palette["pale"], "bold"
    if any(
        k in low for k in ["opção", "opcao", "seleção", "selecao", "incisão", "incisao"]
    ):
        return colors.HexColor("#334155"), BG_2, "bold"
    return BORDER, WHITE, "normal"


def _log_line_panel(
    line: str,
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    marker, bg, weight = _classify_step_line(line, palette)
    style = styles["small_bold"] if weight == "bold" else styles["small"]
    para = Paragraph(_format_log_line_markup(line), style)
    table = Table([["", para]], colWidths=[0.23 * cm, 15.55 * cm], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), marker),
                ("BACKGROUND", (1, 0), (1, 0), bg),
                ("BOX", (0, 0), (-1, -1), 0.35, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, 0), 0),
                ("RIGHTPADDING", (0, 0), (0, 0), 0),
                ("LEFTPADDING", (1, 0), (1, 0), 8),
                ("RIGHTPADDING", (1, 0), (1, 0), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def _steps_section(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    # Quando o relatório é de "todas as opções", os passos completos repetem
    # muita informação e aumentam demasiado o PDF. A exploração já tem a sua
    # própria secção de detalhes, por isso ocultamos o "Registo da execução".
    if _options(operation):
        return []

    steps = _steps(operation)
    story: list[Any] = []
    story.extend(_section_title("3. Registo da execução", styles, palette))

    if not steps:
        story.append(
            _callout(
                "Sem passos registados",
                "Não foram recebidos passos técnicos para esta operação.",
                palette,
                styles,
                tone="warning",
            )
        )
        story.append(Spacer(1, 0.35 * cm))
        return story

    metrics = _extract_execution_metrics(operation)
    if metrics:
        story.append(
            KeepTogether(
                [
                    _p("Indicadores extraídos dos logs", styles["subsection_soft"]),
                    _overview_metrics_table(metrics[:8], palette, styles),
                ]
            )
        )
        story.append(Spacer(1, 0.18 * cm))

    for title, lines in _split_steps_into_blocks(steps):
        title_table = Table(
            [[Paragraph(f"<b>{_html(title)}</b>", styles["subsection"])]],
            colWidths=[16.0 * cm],
            hAlign="CENTER",
        )
        title_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), BG_2),
                    ("LINEBEFORE", (0, 0), (0, -1), 4, palette["accent"]),
                    ("BOX", (0, 0), (-1, -1), 0.35, BORDER_LIGHT),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )

        if not lines:
            story.append(
                KeepTogether(
                    [
                        title_table,
                        Spacer(1, 0.08 * cm),
                        _simple_text_panel(
                            "Sem detalhes adicionais.",
                            palette,
                            styles,
                            bg_color=WHITE,
                            line_color=palette["accent"],
                        ),
                    ]
                )
            )
            story.append(Spacer(1, 0.12 * cm))
            continue

        first_panel = _log_line_panel(
            _split_long_display_line(lines[0], max_chars=135)[0], palette, styles
        )
        story.append(KeepTogether([title_table, Spacer(1, 0.08 * cm), first_panel]))
        story.append(Spacer(1, 0.08 * cm))

        for line in lines[1:]:
            for split_line in _split_long_display_line(line, max_chars=135):
                story.append(_log_line_panel(split_line, palette, styles))
                story.append(Spacer(1, 0.07 * cm))
        # Se a primeira linha foi dividida, adiciona as restantes divisões.
        for split_line in _split_long_display_line(lines[0], max_chars=135)[1:]:
            story.append(_log_line_panel(split_line, palette, styles))
            story.append(Spacer(1, 0.07 * cm))
        story.append(Spacer(1, 0.10 * cm))

    story.append(Spacer(1, 0.35 * cm))
    return story


# ============================================================
# SECÇÕES PARA "VER TODAS AS OPÇÕES"
# ============================================================


def _option_id(option: dict[str, Any], fallback: int) -> str:
    return _safe_text(option.get("option_id") or option.get("id") or fallback)


def _option_result_base(option: dict[str, Any]) -> list[str]:
    return _clean_list(option.get("result_base", option.get("after", [])))


def _option_removed_formulas(
    option: dict[str, Any], before: Sequence[str]
) -> list[str]:
    explicit = _clean_list(option.get("removed_formulas", []))
    if explicit:
        return explicit
    result = _option_result_base(option)
    if result:
        return _removed_formulas(before, result)
    return []


def _option_choice_text(option: dict[str, Any], key: str) -> str:
    if key == "partial meet":
        indices = _as_list(option.get("selected_indices", []))
        selected = _clean_list(option.get("selected_remainders", []))
        if indices:
            return "γ escolhe " + _join_inline(indices, "não indicado", max_items=10)
        if selected:
            return f"γ seleciona {len(selected)} remainder(s)"
        return "Seleção γ não indicada"

    incision = _clean_list(option.get("incision", []))
    if incision:
        return "σ = {" + _set_text(incision, max_items=8) + "}"
    return "Incisão σ não indicada"


def _option_kind_text(option: dict[str, Any], key: str) -> str:
    if key == "partial meet":
        return "Seleção de remainders"
    is_minimal = option.get("is_minimal", None)
    if is_minimal is True:
        return "Incisão mínima"
    if is_minimal is False:
        return "Incisão válida"
    return "Incisão"


def _option_reading(
    option: dict[str, Any],
    key: str,
    before: Sequence[str],
) -> str:
    result = _option_result_base(option)
    removed = _option_removed_formulas(option, before)
    final_size = len(result)

    if key == "partial meet":
        chosen = _clean_list(option.get("selected_remainders", []))
        if chosen:
            return (
                f"Esta possibilidade escolhe {len(chosen)} remainder(s). "
                f"Ao intersetar essa seleção, preserva {final_size} fórmula(s) "
                f"e remove {len(removed)}."
            )
        return (
            f"Esta possibilidade representa uma seleção γ alternativa. "
            f"O resultado preserva {final_size} fórmula(s) e remove {len(removed)}."
        )

    incision = _clean_list(option.get("incision", []))
    if incision:
        return (
            f"Esta possibilidade corta os kernels através da incisão σ com {len(incision)} fórmula(s). "
            f"Depois da remoção, a base resultante fica com {final_size} fórmula(s)."
        )
    return (
        f"Esta possibilidade representa uma incisão alternativa. "
        f"A base resultante fica com {final_size} fórmula(s) e remove {len(removed)}."
    )


def _all_options_intro_text(operation: dict[str, Any]) -> tuple[str, str]:
    key = _operator_key(operation)
    options_count = len(_options(operation))
    target = _normalize_formula(operation.get("target", "")) or "a fórmula alvo"

    if key == "partial meet":
        return (
            "Leitura da exploração por Partial Meet",
            f"Foram geradas {options_count} possibilidade(s) de seleção γ para contrair {target}. "
            "Cada possibilidade corresponde a uma forma admissível de escolher remainders; "
            "a base final de cada uma resulta da interseção dos remainders escolhidos. "
            "Em seguida é apresentada uma síntese e depois o detalhe de cada possibilidade.",
        )

    return (
        "Leitura da exploração por Kernel",
        f"Foram geradas {options_count} possibilidade(s) de incisão σ para contrair {target}. "
        "Cada possibilidade remove pelo menos uma fórmula de cada kernel relevante. "
        "A síntese inicial identifica quais incisões são mais conservadoras e quais retiram mais informação.",
    )


def _all_options_summary_table(
    options: Sequence[dict[str, Any]],
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    key = _operator_key(operation)
    before = _clean_list(operation.get("before", []))

    header_style = ParagraphStyle(
        "AllOptionsHeader",
        parent=styles["table_label"],
        fontName=FONT_BOLD,
        fontSize=8.2,
        leading=10.5,
        textColor=WHITE,
        alignment=TA_CENTER,
    )

    header = [
        Paragraph("Opção", header_style),
        Paragraph("Escolha", header_style),
        Paragraph("Tipo", header_style),
        Paragraph("Removidas", header_style),
        Paragraph("Tamanho final", header_style),
        Paragraph("Leitura rápida", header_style),
    ]
    rows: list[list[Any]] = [header]
    row_tones: list[tuple[int, colors.Color, colors.Color]] = []

    for idx, option in enumerate(options, start=1):
        result = _option_result_base(option)
        removed = _option_removed_formulas(option, before)
        option_label = f"#{_option_id(option, idx)}"
        is_selected = (
            option.get("selected") is True or option.get("is_selected") is True
        )
        if is_selected:
            option_label += "\nSelecionada"

        removed_text = _set_text(removed, max_items=6) if removed else "Nenhuma"
        tone = (
            palette["accent"]
            if is_selected
            else (
                palette["success"]
                if not removed
                else (
                    palette["danger"]
                    if len(removed) >= max(1, len(before) // 2)
                    else palette["secondary"]
                )
            )
        )
        bg = (
            palette["pale"]
            if is_selected
            else (
                palette["pale_success"]
                if not removed
                else (
                    RED_LIGHT
                    if len(removed) >= max(1, len(before) // 2)
                    else palette["pale_2"]
                )
            )
        )
        row_tones.append((idx, tone, bg))

        rows.append(
            [
                _p(option_label, styles["body_bold"]),
                _p(_option_choice_text(option, key), styles["small"]),
                _p(_option_kind_text(option, key), styles["small"]),
                _p(removed_text, styles["small"]),
                _p(str(len(result)), styles["body_bold"]),
                _p(_option_reading(option, key, before), styles["small_muted"]),
            ]
        )

    table = Table(
        rows,
        colWidths=[1.45 * cm, 3.05 * cm, 2.3 * cm, 3.05 * cm, 1.65 * cm, 4.15 * cm],
        hAlign="CENTER",
        repeatRows=1,
    )
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    for row, tone, bg in row_tones:
        style_cmds.extend(
            [
                ("BACKGROUND", (0, row), (-1, row), bg),
                ("LINEBEFORE", (0, row), (0, row), 4, tone),
            ]
        )
    table.setStyle(TableStyle(style_cmds))
    return table


def _option_table(
    option: dict[str, Any],
    key: str,
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
    *,
    before: Sequence[str] = (),
) -> Table:
    result = _option_result_base(option)
    removed = _option_removed_formulas(option, before)

    if key == "partial meet":
        rows = [
            ("Seleção γ aplicada", _option_choice_text(option, key)),
            (
                "Remainders escolhidos",
                _numbered_list(
                    option.get("selected_remainders", []), "não indicados", max_items=16
                ),
            ),
            ("Interpretação", _option_reading(option, key, before)),
        ]
    else:
        rows = [
            ("Incisão σ aplicada", _option_choice_text(option, key)),
            ("Classificação", _option_kind_text(option, key)),
            ("Interpretação", _option_reading(option, key, before)),
        ]

    left = _info_table(rows, palette, styles, width=7.65 * cm)
    right = Table(
        [
            [
                _formula_box(
                    "Fórmulas removidas",
                    removed,
                    palette,
                    styles,
                    kind="removed",
                    width=7.95 * cm,
                )
            ],
            [Spacer(1, 0.10 * cm)],
            [
                _formula_box(
                    "Base resultante",
                    result,
                    palette,
                    styles,
                    kind="final",
                    width=7.95 * cm,
                )
            ],
        ],
        colWidths=[8.05 * cm],
        hAlign="CENTER",
    )
    right.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))

    panel = Table([[left, right]], colWidths=[7.85 * cm, 8.15 * cm], hAlign="CENTER")
    panel.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    return panel


def _option_metrics_row(
    option: dict[str, Any],
    before: Sequence[str],
    styles: dict[str, ParagraphStyle],
    palette: dict[str, Any],
) -> Table:
    result = _option_result_base(option)
    removed = _option_removed_formulas(option, before)
    kept = _kept_formulas(before, result)
    width = 3.55 * cm
    cards = [
        _metric_card(
            "Resultado",
            len(result),
            "fórmulas finais",
            styles,
            width,
            band_color=GREEN_DARK,
            body_color=WHITE,
            border_color=GREEN_LIGHT,
        ),
        _metric_card(
            "Removidas",
            len(removed),
            "fórmulas",
            styles,
            width,
            band_color=RED_DARK,
            body_color=WHITE,
            border_color=RED_LIGHT,
        ),
        _metric_card(
            "Mantidas",
            len(kept),
            "fórmulas",
            styles,
            width,
            band_color=GREEN,
            body_color=WHITE,
            border_color=GREEN_LIGHT,
        ),
        _metric_card(
            "Impacto",
            f"{len(removed)}/{len(before)}",
            "remoções/base",
            styles,
            width,
            band_color=colors.HexColor("#334155"),
            body_color=WHITE,
            border_color=BORDER_LIGHT,
        ),
    ]
    return _metric_cards_grid(cards, columns=4, col_width=width + 0.25 * cm)


def _all_options_final_synthesis(
    options: Sequence[dict[str, Any]],
    operation: dict[str, Any],
) -> tuple[str, str]:
    before = _clean_list(operation.get("before", []))
    key = _operator_key(operation)
    stats: list[tuple[int, int, str]] = []
    for idx, option in enumerate(options, start=1):
        result = _option_result_base(option)
        removed = _option_removed_formulas(option, before)
        stats.append((len(removed), len(result), _option_id(option, idx)))

    if not stats:
        return "Síntese", "Não foram encontradas possibilidades para comparar."

    min_removed = min(x[0] for x in stats)
    max_removed = max(x[0] for x in stats)
    conservative = [
        option_id for removed, _, option_id in stats if removed == min_removed
    ]
    aggressive = [
        option_id for removed, _, option_id in stats if removed == max_removed
    ]

    if key == "partial meet":
        title = "Síntese da exploração por Partial Meet"
        body = (
            f"As opções mais conservadoras são {', '.join('#' + x for x in conservative)} "
            f"com {min_removed} remoção(ões). As opções com maior alteração são "
            f"{', '.join('#' + x for x in aggressive)} com {max_removed} remoção(ões). "
            "Isto ajuda a justificar a escolha de uma seleção γ: quanto menos fórmulas forem removidas, "
            "mais próxima a base final fica da base inicial."
        )
    else:
        title = "Síntese da exploração por Kernel"
        body = (
            f"As incisões mais conservadoras são {', '.join('#' + x for x in conservative)} "
            f"com {min_removed} remoção(ões). As incisões com maior impacto são "
            f"{', '.join('#' + x for x in aggressive)} com {max_removed} remoção(ões). "
            "Esta leitura permite comparar rapidamente o custo informacional de cada incisão σ."
        )
    return title, body


def _all_options_section(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    options = _options(operation)
    if not options:
        return []

    key = _operator_key(operation)
    before = _clean_list(operation.get("before", []))
    story: list[Any] = [PageBreak()]
    story.extend(_section_title("4. Exploração de todas as opções", styles, palette))

    intro_title, intro_body = _all_options_intro_text(operation)
    story.append(_callout(intro_title, intro_body, palette, styles))
    story.append(Spacer(1, 0.18 * cm))

    # Para "todas as opções" mantemos a leitura curta e passamos logo
    # para a síntese e para o detalhe. Removemos a tabela "Comparação rápida"
    # e os indicadores extraídos dos logs para evitar repetição visual.
    story.append(_process_timeline(operation, palette, styles))
    story.append(Spacer(1, 0.22 * cm))

    title, body = _all_options_final_synthesis(options, operation)
    story.append(_callout(title, body, palette, styles, tone="success"))
    story.append(PageBreak())

    story.append(_p("Detalhe das possibilidades", styles["section"]))
    story.append(_rule(palette["tertiary"], 1.2))
    story.append(
        _p(
            "Cada possibilidade é apresentada com a mesma estrutura: cabeçalho discreto, métricas, interpretação e blocos separados para fórmulas removidas e base resultante.",
            styles["muted"],
        )
    )
    story.append(Spacer(1, 0.12 * cm))

    for idx, option in enumerate(options, start=1):
        title_text = f"Possibilidade #{_option_id(option, idx)}"
        is_selected = (
            option.get("selected") is True or option.get("is_selected") is True
        )
        if is_selected:
            title_text += " · selecionada"

        header_bg = (
            palette["accent_dark"] if is_selected else colors.HexColor("#334155")
        )
        title_style = ParagraphStyle(
            f"OptionHeader{idx}",
            parent=styles["subsection"],
            fontName=FONT_BOLD,
            fontSize=12.0,
            leading=14.8,
            textColor=WHITE,
        )
        subtitle_style = ParagraphStyle(
            f"OptionSubHeader{idx}",
            parent=styles["small"],
            fontName=FONT_REGULAR,
            fontSize=8.0,
            leading=10.2,
            textColor=WHITE,
        )
        subtitle = _option_kind_text(option, key)
        if is_selected:
            subtitle += " · destaque da execução"

        title_table = Table(
            [
                [Paragraph(_html(title_text), title_style)],
                [Paragraph(_html(subtitle), subtitle_style)],
            ],
            colWidths=[16.0 * cm],
            hAlign="CENTER",
        )
        title_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), header_bg),
                    ("BOX", (0, 0), (-1, -1), 0.45, header_bg),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(
            KeepTogether(
                [
                    title_table,
                    Spacer(1, 0.10 * cm),
                    _option_metrics_row(option, before, styles, palette),
                ]
            )
        )
        story.append(Spacer(1, 0.10 * cm))
        story.append(_option_table(option, key, palette, styles, before=before))
        story.append(Spacer(1, 0.28 * cm))

    return story


# ============================================================
# EXPORTADOR PRINCIPAL
# ============================================================


def export_operation_pdf(path: str | Path, operation: dict[str, Any]) -> None:
    """
    Exporta um PDF profissional e legível para uma operação de contração.

    Chaves esperadas em operation:
      - operator: str
      - strategy: str
      - target: str
      - before: list[str]
      - after: list[str]
      - steps: list[str]

    Chaves opcionais suportadas:
      - remainders, selected_remainders
      - kernels, incision
      - options / all_options / possibilities / alternatives
      - success / contraction_success
      - after_entails_target / final_entails_target
      - target_is_tautology

    Não inclui postulados, por pedido: o foco fica no aspeto visual,
    explicação clara, diferença entre bases e conclusão automática.
    """
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    palette = _palette(operation)
    styles = _build_styles(palette)

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=1.7 * cm,
        leftMargin=1.7 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.9 * cm,
        title=REPORT_TITLE,
        author=PROJECT_NAME,
    )

    story: list[Any] = []
    story.extend(_cover_section(operation, palette, styles))
    story.extend(_result_section(operation, palette, styles))
    story.extend(_diagnostic_section(operation, palette, styles))
    story.extend(_steps_section(operation, palette, styles))
    story.extend(_all_options_section(operation, palette, styles))

    doc.build(
        story, onFirstPage=_page_footer(palette), onLaterPages=_page_footer(palette)
    )


# Aliases de compatibilidade, caso alguma parte da interface use nomes alternativos.
def export_pdf(path: str | Path, operation: dict[str, Any]) -> None:
    export_operation_pdf(path, operation)


def export_contraction_pdf(path: str | Path, operation: dict[str, Any]) -> None:
    export_operation_pdf(path, operation)
