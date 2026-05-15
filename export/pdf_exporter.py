from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
import re
from typing import Any, Iterable

from reportlab.lib import colors
from reportlab.lib import styles
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
# TEMA VISUAL
# ============================================================

PAGE_WIDTH, PAGE_HEIGHT = A4

NAVY = colors.HexColor("#0f172a")
NAVY_2 = colors.HexColor("#111827")
BLUE = colors.HexColor("#2563eb")
BLUE_DARK = colors.HexColor("#1d4ed8")
BLUE_LIGHT = colors.HexColor("#dbeafe")
CYAN_LIGHT = colors.HexColor("#e0f2fe")
GREEN = colors.HexColor("#16a34a")
GREEN_LIGHT = colors.HexColor("#dcfce7")
YELLOW = colors.HexColor("#facc15")
YELLOW_LIGHT = colors.HexColor("#fef9c3")
RED = colors.HexColor("#dc2626")
RED_LIGHT = colors.HexColor("#fee2e2")
PURPLE = colors.HexColor("#7c3aed")
PURPLE_LIGHT = colors.HexColor("#ede9fe")
BG = colors.HexColor("#f8fafc")
BG_2 = colors.HexColor("#f1f5f9")
BORDER = colors.HexColor("#cbd5e1")
BORDER_LIGHT = colors.HexColor("#e2e8f0")
TEXT = colors.HexColor("#111827")
MUTED = colors.HexColor("#64748b")
WHITE = colors.white

PROJECT_NAME = "Projeto de Revisão de Crenças"
REPORT_TITLE = "Relatório de Contração de Bases de Crenças"
REPORT_SUBTITLE = "Partial Meet Contraction e Kernel Contraction"


# ============================================================
# FONTES
# ============================================================


def _try_register_unicode_font() -> tuple[str, str, bool]:
    """
    Regista uma fonte Unicode do sistema para evitar quadrados pretos em símbolos
    como α, γ, σ, ⊢, ⊬, ∅, ∩, ∪.

    Não distribui fontes; apenas usa fontes já existentes no sistema.
    """

    candidates_regular = [
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        # macOS
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]

    candidates_bold = [
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        # Windows
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        # macOS
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
# NORMALIZAÇÃO DE TEXTO
# ============================================================

COMMON_REPLACEMENTS = {
    "—": "-",
    "–": "-",
    "“": '"',
    "”": '"',
    "’": "'",
    "´": "'",
}

FALLBACK_REPLACEMENTS = {
    "α": "alpha",
    "β": "beta",
    "γ": "gama",
    "σ": "sigma",
    "⊢": "implica",
    "⊬": "nao implica",
    "⊨": "implica logicamente",
    "⊭": "nao implica logicamente",
    "∅": "vazio",
    "∩": "intersecao",
    "∪": "uniao",
    "⊆": "subconjunto de",
    "⊂": "subconjunto proprio de",
    "¬": "neg",
    "∧": "e",
    "∨": "ou",
    "→": "imp",
    "↔": "eq",
    "✓": "OK",
    "✗": "X",
}


def _safe_text(value: object) -> str:
    text = str(value)

    for old, new in COMMON_REPLACEMENTS.items():
        text = text.replace(old, new)

    if not HAS_UNICODE_FONT:
        for old, new in FALLBACK_REPLACEMENTS.items():
            text = text.replace(old, new)

    return text


def _html(text: object) -> str:
    return escape(_safe_text(text)).replace("\n", "<br/>")


def _p(text: object, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_html(text), style)


def _p_markup(markup: str, style: ParagraphStyle) -> Paragraph:
    """Cria Paragraph com markup controlado internamente."""
    return Paragraph(markup, style)


def _join_formulas(formulas: Iterable[Any]) -> str:
    items = [str(f).strip() for f in formulas if str(f).strip()]
    if not items:
        return "(base vazia)"
    return "\n".join(f"- {item}" for item in items)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


# ============================================================
# NOMES AMIGÁVEIS DO PROJETO
# ============================================================

OPERATOR_LABELS = {
    "partial_meet": "Partial meet contraction",
    "partial meet": "Partial meet contraction",
    "partial meet contraction": "Partial meet contraction",
    "kernel": "Kernel contraction",
    "kernel_contraction": "Kernel contraction",
    "kernel contraction": "Kernel contraction",
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

OPERATOR_DESCRIPTIONS = {
    "partial meet contraction": (
        "Calcula os subconjuntos máximos da base que deixam de implicar a fórmula alvo "
        "e combina os subconjuntos escolhidos pela função de seleção."
    ),
    "kernel contraction": (
        "Identifica subconjuntos mínimos que ainda implicam a fórmula alvo e remove, "
        "por uma função de incisão, pelo menos uma fórmula de cada kernel."
    ),
}

# ============================================================
# POSTULADOS DE CONTRAÇÃO EM BASES DE CRENÇAS
# ============================================================

POSTULATES_INFO = {
    "success": {
        "name": "Sucesso",
        "formula": "Se ⊬ α, então A ÷ α ⊬ α",
        "description": (
            "A base final deixa de implicar a fórmula alvo, desde que a fórmula alvo "
            "não seja uma tautologia."
        ),
    },
    "inclusion": {
        "name": "Inclusão",
        "formula": "A ÷ α ⊆ A",
        "description": (
            "A contração não adiciona fórmulas novas. A base final é subconjunto "
            "da base inicial."
        ),
    },
    "failure": {
        "name": "Failure",
        "formula": "Se ⊢ α, então A ÷ α = A",
        "description": (
            "Se a fórmula alvo é uma tautologia, a contração não deve alterar a base."
        ),
    },
    "vacuity": {
        "name": "Vacuidade",
        "formula": "Se A ⊬ α, então A ÷ α = A",
        "description": (
            "Se a base inicial já não implicava a fórmula alvo, nada precisa de ser removido."
        ),
    },
    "relative_closure": {
        "name": "Fecho relativo",
        "formula": "A ∩ Cn(A ÷ α) ⊆ A ÷ α",
        "description": (
            "As crenças originais que continuam a ser consequência da base final "
            "devem permanecer explicitamente na base."
        ),
    },
    "relevance": {
        "name": "Relevância",
        "formula": "Se β foi removida, então β contribuía para implicar α",
        "description": (
            "Uma fórmula só deve ser removida se tiver algum papel na dedução "
            "da fórmula alvo."
        ),
    },
    "core_retainment": {
        "name": "Core-retainment",
        "formula": "Se β foi removida, β pertence a algum núcleo que implica α",
        "description": (
            "Versão mais fraca da relevância. Garante que cada fórmula removida "
            "participava em alguma dedução mínima da fórmula alvo."
        ),
    },
    "uniformity": {
        "name": "Uniformidade",
        "formula": "Se α e β são implicadas pelos mesmos subconjuntos, então A ÷ α = A ÷ β",
        "description": (
            "Fórmulas que têm o mesmo comportamento relativamente aos subconjuntos "
            "da base devem produzir a mesma contração."
        ),
    },
    "extensionality": {
        "name": "Extensionalidade",
        "formula": "Se ⊢ α ↔ β, então A ÷ α = A ÷ β",
        "description": (
            "Fórmulas logicamente equivalentes devem originar o mesmo resultado."
        ),
    },
}


def _friendly_operator(operator: object) -> str:
    raw = _safe_text(operator).strip()
    return OPERATOR_LABELS.get(raw.lower(), raw or "-")


def _friendly_strategy(strategy: object) -> str:
    raw = _safe_text(strategy).strip()
    return STRATEGY_LABELS.get(raw.lower(), raw or "-")


def _operator_description(operator: object) -> str:
    label = _friendly_operator(operator).lower()
    return OPERATOR_DESCRIPTIONS.get(
        label, "Operação de contração aplicada à base de crenças."
    )


# ============================================================
# LIMPEZA DOS PASSOS GERADOS PELO PROGRAMA
# ============================================================


def _clean_step_line(line: str, target: str = "") -> str:
    line = str(line).strip()

    # Estratégias internas para nomes em português
    line = line.replace("Estratégia γ: full", "Estratégia de seleção: Full meet")
    line = line.replace("Estratégia γ: first", "Estratégia de seleção: Maxichoice")
    line = line.replace(
        "Estratégia γ: max_cardinality",
        "Estratégia de seleção: Maior cardinalidade",
    )
    line = line.replace("Estratégia γ: manual", "Estratégia de seleção: Manual")

    line = line.replace(
        "Estratégia σ: common_first",
        "Estratégia de incisão: Comum se existir",
    )
    line = line.replace(
        "Estratégia σ: first_each",
        "Estratégia de incisão: Primeira por kernel",
    )
    line = line.replace(
        "Estratégia σ: min_hitting",
        "Estratégia de incisão: Incisão mínima",
    )
    line = line.replace("Estratégia σ: manual", "Estratégia de incisão: Manual")

    # Frases com símbolos problemáticos ou demasiado técnicos
    if "A implica α" in line or "A implica a formula alvo" in line:
        return f"A base inicial implica a fórmula alvo {target}."

    if "A não implica α" in line or "A nao implica a formula alvo" in line:
        return f"A base inicial não implica a fórmula alvo {target}."

    line = line.replace("α =", "Fórmula alvo:")
    line = line.replace("α é", "A fórmula alvo é")
    line = line.replace("α não é", "A fórmula alvo não é")
    line = line.replace("Fórmula alvo α:", "Fórmula alvo:")

    return line


def _split_steps(steps: list[str], target: str = "") -> list[str]:
    result: list[str] = []

    for step in steps:
        for line in str(step).splitlines():
            line = line.strip()
            if line:
                result.append(_clean_step_line(line, target))

    return result


def _is_section_step(line: str) -> bool:
    return bool(re.match(r"^\d+\.\s+", line))


def _is_collection_item(line: str) -> bool:
    return bool(re.match(r"^\d+\.\s+\{.*\}$", line))


# ============================================================
# ESTILOS
# ============================================================


def _build_styles() -> dict[str, ParagraphStyle]:
    sample = getSampleStyleSheet()

    return {
        "cover_title": ParagraphStyle(
            "CoverTitle",
            parent=sample["Title"],
            fontName=FONT_BOLD,
            fontSize=26,
            leading=31,
            alignment=TA_CENTER,
            textColor=NAVY,
            spaceAfter=8,
        ),
        "cover_subtitle": ParagraphStyle(
            "CoverSubtitle",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=11.5,
            leading=17,
            alignment=TA_CENTER,
            textColor=MUTED,
        ),
        "eyebrow": ParagraphStyle(
            "Eyebrow",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=11,
            alignment=TA_CENTER,
            textColor=BLUE_DARK,
            uppercase=True,
            spaceAfter=8,
        ),
        "h1": ParagraphStyle(
            "H1Custom",
            parent=sample["Heading1"],
            fontName=FONT_BOLD,
            fontSize=17,
            leading=23,
            textColor=NAVY,
            spaceBefore=6,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "H2Custom",
            parent=sample["Heading2"],
            fontName=FONT_BOLD,
            fontSize=12.5,
            leading=17,
            textColor=BLUE_DARK,
            spaceBefore=8,
            spaceAfter=6,
        ),
        "normal": ParagraphStyle(
            "NormalCustom",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=9.3,
            leading=13,
            textColor=TEXT,
            spaceAfter=3,
        ),
        "normal_bold": ParagraphStyle(
            "NormalBoldCustom",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=9.3,
            leading=13,
            textColor=TEXT,
            spaceAfter=3,
        ),
        "small": ParagraphStyle(
            "SmallCustom",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.3,
            leading=11.5,
            textColor=TEXT,
        ),
        "small_muted": ParagraphStyle(
            "SmallMutedCustom",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.1,
            leading=11.2,
            textColor=MUTED,
        ),
        "muted": ParagraphStyle(
            "MutedCustom",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=9,
            leading=12.5,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "metric_label": ParagraphStyle(
            "MetricLabel",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=7.3,
            leading=9,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "metric_value": ParagraphStyle(
            "MetricValue",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=13.5,
            leading=17,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "metric_caption": ParagraphStyle(
            "MetricCaption",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=7.2,
            leading=9,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "table_label": ParagraphStyle(
            "TableLabel",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=8.5,
            leading=11,
            textColor=NAVY,
        ),
        "formula": ParagraphStyle(
            "Formula",
            parent=sample["Code"],
            fontName=FONT_REGULAR,
            fontSize=8.4,
            leading=12,
            textColor=NAVY,
            leftIndent=0,
        ),
        "formula_blue": ParagraphStyle(
            "FormulaBlue",
            parent=sample["Code"],
            fontName=FONT_BOLD,
            fontSize=9,
            leading=12.5,
            textColor=BLUE_DARK,
        ),
        "step_title": ParagraphStyle(
            "StepTitle",
            parent=sample["Normal"],
            fontName=FONT_BOLD,
            fontSize=10.3,
            leading=14,
            textColor=BLUE_DARK,
            spaceAfter=2,
        ),
        "step_text": ParagraphStyle(
            "StepText",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=8.8,
            leading=12.2,
            textColor=TEXT,
            spaceAfter=1.5,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=sample["Normal"],
            fontName=FONT_REGULAR,
            fontSize=7.3,
            leading=9,
            textColor=MUTED,
        ),
    }


# ============================================================
# COMPONENTES VISUAIS
# ============================================================


def _page_footer(canvas, doc) -> None:
    canvas.saveState()

    # Linha superior do rodapé
    canvas.setStrokeColor(BORDER_LIGHT)
    canvas.setLineWidth(0.6)
    canvas.line(1.8 * cm, 1.55 * cm, PAGE_WIDTH - 1.8 * cm, 1.55 * cm)

    # Marca do relatório
    canvas.setFillColor(MUTED)
    canvas.setFont(FONT_REGULAR, 7.5)
    canvas.drawString(
        1.8 * cm, 1.1 * cm, "Projeto de Bases de Crenças - Relatório de Contração"
    )

    # Número de página
    canvas.drawRightString(PAGE_WIDTH - 1.8 * cm, 1.1 * cm, f"Página {doc.page}")

    canvas.restoreState()


def _section_rule() -> HRFlowable:
    return HRFlowable(
        width="100%", thickness=0.7, color=BORDER_LIGHT, spaceBefore=0, spaceAfter=8
    )


def _metric_card(
    label: str,
    value: object,
    caption: str,
    styles: dict[str, ParagraphStyle],
    width: float | None = None,
) -> Table:
    card_width = width or 3.35 * cm

    table = Table(
        [
            [_p(label.upper(), styles["metric_label"])],
            [_p(value, styles["metric_value"])],
            [_p(caption, styles["metric_caption"])],
        ],
        colWidths=[card_width],
        rowHeights=[0.85 * cm, 1.65 * cm, 0.85 * cm],
        hAlign="CENTER",
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.7, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    return table


def _badge(
    text: object,
    bg: colors.Color,
    fg: colors.Color,
    styles: dict[str, ParagraphStyle],
    width: float | None = None,
    h_align: str = "LEFT",
) -> Table:
    badge_style = ParagraphStyle(
        "Badge",
        parent=styles["small"],
        fontName=FONT_BOLD,
        fontSize=7.7,
        leading=9.5,
        textColor=fg,
        alignment=TA_CENTER,
    )
    table = Table(
        [[_p(text, badge_style)]], colWidths=[width] if width else None, hAlign=h_align
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 0.25, bg),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def _postulate_badge(status: object, styles: dict[str, ParagraphStyle]) -> Table:
    """
    Cria um badge visual para o estado do postulado.
    status pode ser:
        True        -> Cumpre
        False       -> Falha
        None        -> Não verificado
        "expected"  -> Previsto teoricamente
    """

    if status is True:
        label = "Cumpre"
        bg = GREEN_LIGHT
        fg = GREEN
    elif status is False:
        label = "Falha"
        bg = RED_LIGHT
        fg = RED
    elif status == "expected":
        label = "Previsto"
        bg = BLUE_LIGHT
        fg = BLUE_DARK
    else:
        label = "N/verificado"
        bg = BG_2
        fg = MUTED

    return _badge(label, bg, fg, styles, width=2.35 * cm, h_align="CENTER")


def _expected_postulates_for_operator(operator: str) -> list[str]:
    """
    Define quais postulados fazem sentido mostrar de acordo com o operador usado.

    Partial meet:
        Sucesso, Inclusão, Uniformidade, Relevância

    Kernel:
        Sucesso, Inclusão, Uniformidade, Core-retainment
    """

    op = operator.lower().strip()

    if "partial meet" in op:
        return ["success", "inclusion", "uniformity", "relevance"]

    if "kernel" in op:
        return ["success", "inclusion", "uniformity", "core_retainment"]

    return ["success", "inclusion", "vacuity", "failure"]


def _get_postulate_statuses(operation: dict, operator: str) -> list[tuple[str, object]]:
    """
    Lê os resultados dos postulados a partir de operation["postulates"].

    Se operation["postulates"] não existir, os postulados aparecem como "Previsto",
    ou seja, são mostrados como caracterização teórica do operador, não como
    verificação computacional feita pelo programa.
    """

    expected = _expected_postulates_for_operator(operator)

    raw = operation.get("postulates", None)

    # Caso ainda não tenhas implementação automática dos verificadores
    if raw is None:
        return [(key, "expected") for key in expected]

    # Formato recomendado:
    # operation["postulates"] = {
    #     "success": True,
    #     "inclusion": True,
    #     "vacuity": None,
    #     "uniformity": "expected",
    # }
    if isinstance(raw, dict):
        keys = list(dict.fromkeys(expected + list(raw.keys())))
        return [(key, raw.get(key, None)) for key in keys if key in POSTULATES_INFO]

    # Formato alternativo:
    # operation["postulates"] = [
    #     {"key": "success", "status": True},
    #     {"key": "inclusion", "status": True},
    # ]
    if isinstance(raw, list):
        converted = {}
        for item in raw:
            if isinstance(item, dict):
                key = item.get("key")
                status = item.get("status")
                if key:
                    converted[key] = status

        keys = list(dict.fromkeys(expected + list(converted.keys())))
        return [
            (key, converted.get(key, None)) for key in keys if key in POSTULATES_INFO
        ]

    return [(key, "expected") for key in expected]


def _postulates_table(
    operation: dict,
    operator: str,
    styles: dict[str, ParagraphStyle],
    content_width: float,
) -> Table:
    rows = _get_postulate_statuses(operation, operator)

    header_style = ParagraphStyle(
        "PostulateHeader",
        parent=styles["small"],
        fontName=FONT_BOLD,
        fontSize=8,
        leading=10,
        textColor=WHITE,
        alignment=TA_CENTER,
    )

    data = [
        [
            _p("Postulado", header_style),
            _p("Formulação", header_style),
            _p("Estado", header_style),
            _p("Interpretação", header_style),
        ]
    ]

    for key, status in rows:
        info = POSTULATES_INFO[key]

        data.append(
            [
                _p(info["name"], styles["table_label"]),
                _p(info["formula"], styles["small"]),
                _postulate_badge(status, styles),
                _p(info["description"], styles["small_muted"]),
            ]
        )

    table = Table(
        data,
        colWidths=[
            3.0 * cm,
            4.5 * cm,
            2.7 * cm,
            content_width - 10.2 * cm,
        ],
        hAlign="LEFT",
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("BACKGROUND", (0, 1), (-1, -1), WHITE),
                ("GRID", (0, 0), (-1, -1), 0.45, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    return table


def _render_postulates_section(
    story: list[Any],
    operation: dict,
    operator: str,
    styles: dict[str, ParagraphStyle],
    content_width: float,
) -> None:
    story.append(_p("3. Verificação dos postulados", styles["h1"]))
    story.append(_section_rule())

    story.append(
        _p(
            "Esta secção apresenta os postulados associados ao operador de contração usado. "
            "Quando o estado aparece como “Previsto”, significa que o postulado faz parte "
            "da caracterização teórica do operador escolhido. Quando aparece como “Cumpre” "
            "ou “Falha”, significa que o programa recebeu ou calculou esse resultado.",
            styles["muted"],
        )
    )

    story.append(Spacer(1, 0.25 * cm))
    story.append(_postulates_table(operation, operator, styles, content_width))
    story.append(Spacer(1, 0.4 * cm))

    op = operator.lower()

    if "partial meet" in op:
        note = (
            "Para partial meet contraction em bases de crenças, os postulados característicos "
            "são Sucesso, Inclusão, Uniformidade e Relevância."
        )
    elif "kernel" in op:
        note = (
            "Para kernel contraction em bases de crenças, os postulados característicos "
            "são Sucesso, Inclusão, Uniformidade e Core-retainment."
        )
    else:
        note = (
            "Para este operador, são apresentados os postulados básicos de contração "
            "em bases de crenças."
        )

    note_table = Table(
        [[_p(note, styles["small"])]],
        colWidths=[content_width],
        hAlign="LEFT",
    )

    note_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), BG),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER_LIGHT),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(note_table)


def _info_table(
    rows: list[tuple[str, object]], styles: dict[str, ParagraphStyle], width: float
) -> Table:
    data = [
        [_p(label, styles["table_label"]), _p(value, styles["normal"])]
        for label, value in rows
    ]
    table = Table(data, colWidths=[3.7 * cm, width - 3.7 * cm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), BG_2),
                ("BACKGROUND", (1, 0), (1, -1), WHITE),
                ("GRID", (0, 0), (-1, -1), 0.45, BORDER_LIGHT),
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
    formulas: list[Any],
    styles: dict[str, ParagraphStyle],
    accent: colors.Color,
) -> Table:
    items = _as_list(formulas)

    if not items:
        body = [_p("(base vazia)", styles["small_muted"])]
    else:
        body = [
            _p(f"{idx}. {formula}", styles["formula"])
            for idx, formula in enumerate(items, start=1)
        ]

    header_style = ParagraphStyle(
        f"Header_{title}",
        parent=styles["normal_bold"],
        fontName=FONT_BOLD,
        fontSize=9.2,
        leading=12,
        textColor=WHITE,
    )

    rows = [[_p(title, header_style)], [body]]
    table = Table(rows, colWidths=[7.05 * cm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), accent),
                ("BACKGROUND", (0, 1), (-1, 1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.8, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    return table


def _formula_comparison(
    before: list[Any], after: list[Any], styles: dict[str, ParagraphStyle]
) -> Table:
    left = _formula_box("Base inicial", before, styles, NAVY)
    right = _formula_box("Base final", after, styles, GREEN)

    table = Table([[left, right]], colWidths=[7.25 * cm, 7.25 * cm], hAlign="LEFT")
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


def _colon_markup_line(
    text: object,
    styles: dict[str, ParagraphStyle],
    value_color: str = "#1d4ed8",
    bold_value: bool = False,
) -> Paragraph:
    safe_text = _safe_text(text)

    if ":" not in safe_text:
        return _p(safe_text, styles["step_text"])

    label, value = safe_text.split(":", 1)
    label_html = escape(label)
    value_html = escape(value.strip())

    if bold_value:
        value_part = f'<b><font color="{value_color}">{value_html}</font></b>'
    else:
        value_part = f'<font color="{value_color}">{value_html}</font>'

    return _p_markup(f"<b>{label_html}:</b> {value_part}", styles["step_text"])


def _step_block(
    paragraphs: list[Paragraph],
    styles: dict[str, ParagraphStyle],
    accent: colors.Color = BLUE,
) -> Table:
    rows = [["", paragraph] for paragraph in paragraphs]

    table = Table(rows, colWidths=[0.16 * cm, 14.35 * cm], hAlign="LEFT", splitByRow=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), accent),
                ("BACKGROUND", (1, 0), (1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), 0),
                ("TOPPADDING", (0, 0), (0, -1), 0),
                ("BOTTOMPADDING", (0, 0), (0, -1), 0),
                ("LEFTPADDING", (1, 0), (1, -1), 8),
                ("RIGHTPADDING", (1, 0), (1, -1), 9),
                ("TOPPADDING", (1, 0), (1, -1), 4.5),
                ("BOTTOMPADDING", (1, 0), (1, -1), 4.5),
            ]
        )
    )
    return table


def _render_steps(
    story: list[Any], steps: list[str], target: str, styles: dict[str, ParagraphStyle]
) -> None:
    flat_steps = _split_steps(steps, target)

    if not flat_steps:
        empty = Table(
            [[_p("Sem passos registados para esta operação.", styles["muted"])]],
            colWidths=[14.55 * cm],
            hAlign="LEFT",
        )
        empty.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), BG),
                    ("BOX", (0, 0), (-1, -1), 0.6, BORDER_LIGHT),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(empty)
        return

    current_block: list[Paragraph] = []

    def flush_block() -> None:
        nonlocal current_block
        if not current_block:
            return
        story.append(_step_block(current_block, styles))
        story.append(Spacer(1, 0.22 * cm))
        current_block = []

    for line in flat_steps:
        if line.startswith("==="):
            flush_block()
            cleaned = line.replace("=", "").strip()
            story.append(_p(cleaned, styles["h2"]))
            continue

        if _is_section_step(line) and not _is_collection_item(line):
            flush_block()
            current_block.append(_p(line, styles["step_title"]))
            continue

        if _is_collection_item(line):
            current_block.append(_p(line, styles["formula"]))
            continue

        if line.startswith("Base final:") or line.startswith(
            "Resultado da interseção:"
        ):
            current_block.append(
                _colon_markup_line(line, styles, value_color="#111827", bold_value=True)
            )
        elif ":" in line:
            current_block.append(
                _colon_markup_line(
                    line, styles, value_color="#1d4ed8", bold_value=False
                )
            )
        else:
            current_block.append(_p(line, styles["step_text"]))

    flush_block()


# ============================================================
# EXPORTADOR
# ============================================================


def export_operation_pdf(path: str | Path, operation: dict) -> None:
    """
    Exporta um relatório PDF estilizado de uma operação de contração de crenças.

    Espera um dicionário operation com, pelo menos, as chaves:
        - operator: str
        - strategy: str
        - target: str
        - before: list[str]
        - after: list[str]
        - steps: list[str]

    A função mantém compatibilidade com a tua versão original.
    """

    path = Path(path)
    styles = _build_styles()

    margin_x = 1.8 * cm
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=margin_x,
        leftMargin=margin_x,
        topMargin=1.7 * cm,
        bottomMargin=1.85 * cm,
        title=REPORT_TITLE,
        author=PROJECT_NAME,
        subject="Contração de bases de crenças em lógica proposicional",
    )

    content_width = PAGE_WIDTH - doc.leftMargin - doc.rightMargin

    operator_raw = operation.get("operator", "-")
    strategy_raw = operation.get("strategy", "-")
    target = operation.get("target", "-")
    before = _as_list(operation.get("before", []))
    after = _as_list(operation.get("after", []))
    steps = _as_list(operation.get("steps", []))

    operator = _friendly_operator(operator_raw)
    strategy = _friendly_strategy(strategy_raw)
    now = datetime.now().strftime("%d/%m/%Y %H:%M")

    removed_count = max(0, len(before) - len(after))
    kept_count = len(after)

    story: list[Any] = []

    # ========================================================
    # CAPA
    # ========================================================

    story.append(Spacer(1, 1.25 * cm))

    cover_inner = [
        _p("RELATÓRIO AUTOMÁTICO", styles["eyebrow"]),
        _p(REPORT_TITLE, styles["cover_title"]),
        _p(
            "Execução detalhada de uma operação de contração numa base de crenças."
            "O relatório mostra a fórmula removida, a estratégia usada e a base resultante.",
            styles["cover_subtitle"],
        ),
        Spacer(1, 0.28 * cm),
        Table(
            [
                [
                    _badge(
                        operator,
                        BLUE_LIGHT,
                        BLUE_DARK,
                        styles,
                        width=6.2 * cm,
                        h_align="CENTER",
                    )
                ]
            ],
            colWidths=[content_width - 24],
            hAlign="CENTER",
        ),
    ]

    cover = Table([[cover_inner]], colWidths=[content_width], hAlign="LEFT")
    cover.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0, WHITE),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )
    story.append(cover)
    story.append(Spacer(1, 0.55 * cm))
    story.append(_section_rule())
    story.append(Spacer(1, 0.25 * cm))
    card_width = content_width / 4

    cover_cards = Table(
        [
            [
                _metric_card(
                    "Operador", operator, "modelo aplicado", styles, card_width
                ),
                _metric_card(
                    "Estratégia", strategy, "critério escolhido", styles, card_width
                ),
                _metric_card(
                    "Fórmula alvo", target, "crença a remover", styles, card_width
                ),
                _metric_card(
                    "Removidas", removed_count, "fórmulas retiradas", styles, card_width
                ),
            ]
        ],
        colWidths=[card_width, card_width, card_width, card_width],
        hAlign="CENTER",
    )

    cover_cards.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(cover_cards)
    story.append(Spacer(1, 0.55 * cm))

    intro = Table(
        [
            [
                _p(
                    "Este documento resume a execução de uma operação de contração sobre uma base de crenças. "
                    "Inclui a base inicial, a fórmula alvo, a estratégia aplicada, os passos intermédios e a base final.",
                    styles["muted"],
                )
            ]
        ],
        colWidths=[content_width],
        hAlign="LEFT",
    )
    intro.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), BG),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER_LIGHT),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
            ]
        )
    )
    story.append(intro)
    story.append(Spacer(1, 0.55 * cm))

    story.append(
        _info_table(
            [
                ("Projeto", PROJECT_NAME),
                ("Operador", operator),
                ("Estratégia", strategy),
                ("Fórmula alvo", target),
                ("Data", now),
            ],
            styles,
            content_width,
        )
    )

    story.append(PageBreak())

    # ========================================================
    # RESUMO
    # ========================================================

    story.append(_p("1. Resumo da operação", styles["h1"]))
    story.append(_section_rule())

    story.append(
        _info_table(
            [
                ("Operador", operator),
                ("Estratégia", strategy),
                ("Fórmula alvo", target),
                ("Descrição", _operator_description(operator)),
                ("Base inicial", f"{len(before)} fórmula(s)"),
                ("Base final", f"{len(after)} fórmula(s)"),
            ],
            styles,
            content_width,
        )
    )

    story.append(Spacer(1, 0.45 * cm))

    summary_cards = Table(
        [
            [
                _metric_card(
                    "Antes",
                    len(before),
                    "fórmulas na base",
                    styles,
                ),
                _metric_card("Depois", kept_count, "fórmulas mantidas", styles),
                _metric_card("Remoção", removed_count, "alteração mínima", styles),
                _metric_card(
                    "Passos",
                    len(_split_steps(steps, str(target))),
                    "linhas registadas",
                    styles,
                ),
            ]
        ],
        colWidths=[3.45 * cm, 3.45 * cm, 3.45 * cm, 3.45 * cm],
        hAlign="CENTER",
    )
    summary_cards.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.append(summary_cards)

    story.append(Spacer(1, 0.5 * cm))
    story.append(_p("Bases de crenças", styles["h2"]))
    story.append(_formula_comparison(before, after, styles))

    story.append(Spacer(1, 0.55 * cm))
    story.append(_p("Resultado final", styles["h2"]))

    result_body = [
        _p(
            f"Após contrair a base pela fórmula alvo <b>{escape(_safe_text(target))}</b>, "
            f"a base resultante contém <b>{len(after)}</b> fórmula(s):",
            styles["normal"],
        ),
        Spacer(1, 0.12 * cm),
        _p(_join_formulas(after), styles["formula_blue"]),
    ]

    result_table = Table(
        [["", result_body]],
        colWidths=[0.16 * cm, content_width - 0.16 * cm],
        hAlign="LEFT",
    )
    result_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), GREEN),
                ("BACKGROUND", (1, 0), (1, -1), GREEN_LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.8, GREEN),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
                ("RIGHTPADDING", (0, 0), (0, -1), 0),
                ("TOPPADDING", (0, 0), (0, -1), 0),
                ("BOTTOMPADDING", (0, 0), (0, -1), 0),
                ("LEFTPADDING", (1, 0), (1, -1), 10),
                ("RIGHTPADDING", (1, 0), (1, -1), 10),
                ("TOPPADDING", (1, 0), (1, -1), 9),
                ("BOTTOMPADDING", (1, 0), (1, -1), 9),
            ]
        )
    )
    story.append(result_table)

    story.append(PageBreak())

    # ========================================================
    # PASSOS
    # ========================================================

    story.append(_p("2. Passos da contração", styles["h1"]))
    story.append(_section_rule())

    story.append(
        _p(
            "A sequência abaixo mostra a execução interna do operador. Os blocos destacam verificações, "
            "cálculo de subconjuntos relevantes, aplicação da estratégia e construção da base final.",
            styles["muted"],
        )
    )
    story.append(Spacer(1, 0.25 * cm))

    _render_steps(story, steps, str(target), styles)

    story.append(PageBreak())

    # ========================================================
    # POSTULADOS
    # ========================================================

    _render_postulates_section(
        story=story,
        operation=operation,
        operator=operator,
        styles=styles,
        content_width=content_width,
    )

    story.append(Spacer(1, 0.4 * cm))

    # ========================================================
    # NOTAS FINAIS
    # ========================================================

    story.append(_p("4. Nota de leitura", styles["h1"]))
    story.append(_section_rule())

    notes = Table(
        [
            [
                _badge("Lógica proposicional", CYAN_LIGHT, BLUE_DARK, styles),
                _p(
                    "As fórmulas da base são tratadas como sentenças proposicionais.",
                    styles["small"],
                ),
            ],
            [
                _badge("Contração", YELLOW_LIGHT, NAVY, styles),
                _p(
                    "O objetivo é remover informação suficiente para que a base deixe de implicar a fórmula alvo.",
                    styles["small"],
                ),
            ],
            [
                _badge("Mudança mínima", GREEN_LIGHT, GREEN, styles),
                _p(
                    "A estratégia escolhida tenta preservar o máximo possível da base original.",
                    styles["small"],
                ),
            ],
        ],
        colWidths=[4.0 * cm, content_width - 4.0 * cm],
        hAlign="LEFT",
    )
    notes.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER_LIGHT),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(notes)

    doc.build(story, onFirstPage=_page_footer, onLaterPages=_page_footer)
