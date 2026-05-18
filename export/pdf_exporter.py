from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any, Iterable, Sequence
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
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

PAGE_WIDTH, PAGE_HEIGHT = A4
PROJECT_NAME = "Projeto de Contração de Bases de Crenças"
REPORT_TITLE = "Relatório de Contração"

NAVY = colors.HexColor("#0f172a")
SLATE = colors.HexColor("#1f2937")
BG = colors.HexColor("#f8fafc")
BORDER = colors.HexColor("#cbd5e1")
BORDER_LIGHT = colors.HexColor("#e2e8f0")
TEXT = colors.HexColor("#111827")
MUTED = colors.HexColor("#64748b")
WHITE = colors.white

PALETTES = {
    "partial meet": {
        "name": "Partial Meet",
        "accent": colors.HexColor("#dc2626"),
        "dark": colors.HexColor("#991b1b"),
        "soft": colors.HexColor("#fee2e2"),
        "pale": colors.HexColor("#fff1f2"),
        "badge": colors.HexColor("#fee2e2"),
        "label": colors.HexColor("#7f1d1d"),
    },
    "kernel": {
        "name": "Kernel",
        "accent": colors.HexColor("#16a34a"),
        "dark": colors.HexColor("#14532d"),
        "soft": colors.HexColor("#dcfce7"),
        "pale": colors.HexColor("#f0fdf4"),
        "badge": colors.HexColor("#dcfce7"),
        "label": colors.HexColor("#14532d"),
    },
}

MODE_LABELS = {
    "single": "Execução única",
    "all_selections": "Exploração de todas as seleções",
    "all_incisions": "Exploração de todas as incisões",
    "all_minimal_incisions": "Exploração de incisões mínimas",
}

STRATEGY_LABELS = {
    "full": "Full meet",
    "first": "Maxichoice",
    "max_cardinality": "Maior cardinalidade",
    "manual": "Manual",
    "common_first": "Comum se existir",
    "first_each": "Primeira por kernel",
    "min_hitting": "Incisão mínima",
    "all_selections": "Todas as seleções possíveis",
    "all_incisions": "Todas as incisões válidas",
    "all_minimal_incisions": "Todas as incisões mínimas",
    "todas as seleções possíveis": "Todas as seleções possíveis",
    "todas as incisões válidas": "Todas as incisões válidas",
    "todas as incisões mínimas": "Todas as incisões mínimas",
}


def _try_register_unicode_font() -> tuple[str, str, bool]:
    regular_candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    bold_candidates = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]

    regular = next((p for p in regular_candidates if Path(p).exists()), None)
    bold = next((p for p in bold_candidates if Path(p).exists()), None)

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
    "∅": "vazio",
    "∩": "intersecao",
    "∪": "uniao",
    "⊆": "subconjunto de",
    "¬": "neg",
    "∧": "e",
    "∨": "ou",
    "→": "imp",
    "↔": "eq",
    "✓": "OK",
    "✗": "X",
}


def _safe_text(value: object) -> str:
    text = "" if value is None else str(value)
    for old, new in COMMON_REPLACEMENTS.items():
        text = text.replace(old, new)

    if not HAS_UNICODE_FONT:
        for old, new in FALLBACK_REPLACEMENTS.items():
            text = text.replace(old, new)

    return text


def _html(value: object) -> str:
    return escape(_safe_text(value)).replace("\n", "<br/>")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _clean_list(items: Iterable[Any]) -> list[str]:
    return [_safe_text(x).strip() for x in _as_list(items) if _safe_text(x).strip()]


def _join_inline(items: Iterable[Any], empty: str = "(vazio)") -> str:
    values = _clean_list(items)
    return "; ".join(values) if values else empty


def _numbered_list(items: Iterable[Any], empty: str = "(vazio)") -> str:
    values = _clean_list(items)
    if not values:
        return empty
    return "\n".join(f"{i}. {x}" for i, x in enumerate(values, start=1))


def _set_text(items: Iterable[Any], empty: str = "∅") -> str:
    values = _clean_list(items)
    return "{ " + "; ".join(values) + " }" if values else empty


def _removed_formulas(before: Iterable[Any], after: Iterable[Any]) -> list[str]:
    after_set = set(_clean_list(after))
    return [x for x in _clean_list(before) if x not in after_set]


def _kept_formulas(before: Iterable[Any], after: Iterable[Any]) -> list[str]:
    after_set = set(_clean_list(after))
    return [x for x in _clean_list(before) if x in after_set]


def _dedupe_preserve_order(items: Iterable[Any]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []

    for item in _clean_list(items):
        if item in seen:
            continue
        seen.add(item)
        out.append(item)

    return out


def _friendly_strategy(value: object) -> str:
    raw = _safe_text(value).strip()
    return STRATEGY_LABELS.get(raw.lower(), raw or "Não indicada")


def _operator_key(operation: dict[str, Any]) -> str:
    raw = _safe_text(operation.get("operator", "")).lower().replace("_", " ")
    if "kernel" in raw:
        return "kernel"
    return "partial meet"


def _mode(operation: dict[str, Any]) -> str:
    return _safe_text(operation.get("mode", "single")).strip() or "single"


def _is_all_mode(operation: dict[str, Any]) -> bool:
    return _mode(operation).startswith("all_")


def _mode_label(operation: dict[str, Any]) -> str:
    mode = _mode(operation)
    return MODE_LABELS.get(mode, mode.replace("_", " ").title())


def _options(operation: dict[str, Any]) -> list[dict[str, Any]]:
    options = operation.get("all_options") or operation.get("options") or []
    return [o for o in _as_list(options) if isinstance(o, dict)]


def _clean_step_line(line: str) -> str:
    line = _safe_text(line).strip()

    if not line:
        return ""

    line = re.sub(
        r"^(F[oó]rmula alvo)\s+F[oó]rmula alvo\s*:\s*",
        r"\1: ",
        line,
        flags=re.IGNORECASE,
    )

    line = line.strip("▶►• ").strip()
    return line


def _steps(operation: dict[str, Any]) -> list[str]:
    raw_steps = _clean_list(operation.get("steps", []))
    cleaned: list[str] = []

    for raw in raw_steps:
        for line in str(raw).splitlines():
            line = _clean_step_line(line)
            if not line:
                continue
            if set(line) <= {"━", "─", "-", "="}:
                continue
            cleaned.append(line)

    return cleaned


def _split_steps_into_blocks(steps: Sequence[str]) -> list[tuple[str, list[str]]]:
    blocks: list[tuple[str, list[str]]] = []
    current_title = "Registo inicial"
    current_lines: list[str] = []

    for line in steps:
        is_numbered = re.match(r"^\d+\.\s+", line) is not None
        is_major_title = line.lower() in {
            "partial meet contraction",
            "kernel contraction",
            "resultado da contração partial meet",
            "resultado da contração kernel",
        }

        if is_numbered or is_major_title:
            if current_lines:
                blocks.append((current_title, current_lines))
            current_title = line.rstrip(":")
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        blocks.append((current_title, current_lines))
    elif not blocks and current_title:
        blocks.append((current_title, []))

    return blocks


def _build_styles(palette: dict[str, Any]) -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "TitleCustom",
            parent=base["Title"],
            fontName=FONT_BOLD,
            fontSize=28,
            leading=34,
            alignment=TA_CENTER,
            textColor=NAVY,
            spaceAfter=12,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCustom",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=11,
            leading=16,
            alignment=TA_CENTER,
            textColor=MUTED,
        ),
        "section": ParagraphStyle(
            "SectionCustom",
            parent=base["Heading1"],
            fontName=FONT_BOLD,
            fontSize=18,
            leading=23,
            textColor=NAVY,
            spaceBefore=14,
            spaceAfter=8,
        ),
        "subsection": ParagraphStyle(
            "SubsectionCustom",
            parent=base["Heading2"],
            fontName=FONT_BOLD,
            fontSize=13,
            leading=17,
            textColor=palette["dark"],
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "BodyCustom",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=9.2,
            leading=13.2,
            textColor=TEXT,
            spaceAfter=5,
        ),
        "muted": ParagraphStyle(
            "MutedCustom",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=8.5,
            leading=12,
            textColor=MUTED,
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "SmallCustom",
            parent=base["BodyText"],
            fontName=FONT_REGULAR,
            fontSize=7.7,
            leading=10.5,
            textColor=TEXT,
        ),
        "small_bold": ParagraphStyle(
            "SmallBoldCustom",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=7.8,
            leading=10.5,
            textColor=TEXT,
        ),
        "center_bold": ParagraphStyle(
            "CenterBoldCustom",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            textColor=NAVY,
        ),
        "badge": ParagraphStyle(
            "BadgeCustom",
            parent=base["BodyText"],
            fontName=FONT_BOLD,
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=palette["label"],
        ),
    }


def _p(text: object, style: ParagraphStyle) -> Paragraph:
    return Paragraph(_html(text), style)


def _rule(color: colors.Color = BORDER_LIGHT, thickness: float = 0.7) -> HRFlowable:
    return HRFlowable(
        width="100%",
        thickness=thickness,
        color=color,
        spaceBefore=4,
        spaceAfter=10,
    )


def _badge(
    text: str,
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
    width: float = 6.2 * cm,
) -> Table:
    table = Table(
        [[Paragraph(_html(text), styles["badge"])]],
        colWidths=[width],
        hAlign="CENTER",
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), palette["badge"]),
                ("BOX", (0, 0), (-1, -1), 0.4, palette["soft"]),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ]
        )
    )
    return table


def _info_table(
    rows: list[tuple[str, object]],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    data = []

    for label, value in rows:
        data.append(
            [
                Paragraph(_html(label), styles["small_bold"]),
                Paragraph(_html(value), styles["small"]),
            ]
        )

    table = Table(data, colWidths=[4.0 * cm, 11.4 * cm], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER_LIGHT),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("BACKGROUND", (0, 0), (0, -1), palette["pale"]),
            ]
        )
    )
    return table


def _summary_grid(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    operator = palette["name"]
    target = _safe_text(operation.get("target", "Não indicada")) or "Não indicada"
    strategy = _friendly_strategy(operation.get("strategy", "Não indicada"))
    before = _clean_list(operation.get("before", []))
    after = _clean_list(operation.get("after", []))
    options_count = len(_options(operation))

    if _is_all_mode(operation):
        cards = [
            ("OPERADOR", operator, "modelo aplicado"),
            ("ESTRATÉGIA", strategy, "critério escolhido"),
            ("FÓRMULA ALVO", target, "crença a remover"),
            ("OPÇÕES", str(options_count), "possibilidades"),
        ]
    else:
        removed = _removed_formulas(before, after)
        cards = [
            ("OPERADOR", operator, "modelo aplicado"),
            ("ESTRATÉGIA", strategy, "critério escolhido"),
            ("ANTES", str(len(before)), "fórmulas"),
            ("REMOVIDAS", str(len(removed)), "fórmulas"),
        ]

    row = []

    for title, value, footer in cards:
        cell = [
            Paragraph(
                f'<font color="{palette["label"].hexval()}"><b>{_html(title)}</b></font>',
                styles["center_bold"],
            ),
            Spacer(1, 4),
            Paragraph(
                f'<font size="15"><b>{_html(value)}</b></font>', styles["center_bold"]
            ),
            Spacer(1, 3),
            Paragraph(_html(footer), styles["muted"]),
        ]
        row.append(cell)

    table = Table([row], colWidths=[4.0 * cm] * 4, hAlign="CENTER")
    style = [
        ("BOX", (0, 0), (-1, -1), 0.45, BORDER_LIGHT),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ]

    for col in range(4):
        style.append(
            (
                "BACKGROUND",
                (col, 0),
                (col, 0),
                palette["pale"] if col in (0, 3) else WHITE,
            )
        )

    table.setStyle(TableStyle(style))
    return table


def _callout(
    title: str,
    body: str,
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    content = [
        [Paragraph(f"<b>{_html(title)}</b>", styles["body"])],
        [Paragraph(_html(body), styles["small"])],
    ]

    table = Table(content, colWidths=[16.0 * cm], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), palette["pale"]),
                ("LINEBEFORE", (0, 0), (0, -1), 3, palette["accent"]),
                ("BOX", (0, 0), (-1, -1), 0.45, BORDER_LIGHT),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _section_title(
    text: str,
    styles: dict[str, ParagraphStyle],
    palette: dict[str, Any],
) -> list[Any]:
    return [
        Paragraph(_html(text), styles["section"]),
        _rule(palette["soft"], 0.8),
    ]


def _cover(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    is_all = _is_all_mode(operation)

    title = "Exploração de Possibilidades" if is_all else REPORT_TITLE
    subtitle = (
        "Comparação organizada das seleções/incisões calculadas, sem alterar a base original."
        if is_all
        else "Relatório gerado a partir da última contração executada na aplicação."
    )

    story: list[Any] = [Spacer(1, 0.5 * cm)]
    story.append(Paragraph(_html(title), styles["title"]))
    story.append(Paragraph(_html(subtitle), styles["subtitle"]))
    story.append(Spacer(1, 0.35 * cm))

    badges = Table(
        [
            [
                _badge(palette["name"], palette, styles, width=4.8 * cm),
                _badge(_mode_label(operation), palette, styles, width=6.8 * cm),
            ]
        ],
        colWidths=[5.2 * cm, 7.2 * cm],
        hAlign="CENTER",
    )
    badges.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(badges)
    story.append(Spacer(1, 0.9 * cm))
    story.append(_rule(BORDER_LIGHT, 0.8))
    story.append(Spacer(1, 0.25 * cm))
    story.append(_summary_grid(operation, palette, styles))
    story.append(Spacer(1, 0.55 * cm))

    if is_all:
        body = (
            "Este relatório mostra cada possibilidade calculada pelo operador. "
            "Nesta modalidade, a aplicação apenas explora alternativas: nenhuma opção é aplicada automaticamente à base. "
            "A leitura principal deve ser feita na secção 'Detalhe de cada possibilidade'."
        )
    elif _operator_key(operation) == "partial meet":
        body = (
            "Partial Meet contrai a base calculando remainders e escolhendo alguns deles através da função de seleção γ. "
            "A base final resulta da interseção dos remainders selecionados."
        )
    else:
        body = (
            "Kernel contrai a base calculando kernels e escolhendo uma incisão σ. "
            "A incisão deve tocar todos os kernels, removendo pelo menos uma fórmula de cada kernel."
        )

    story.append(_callout("Como interpretar", body, palette, styles))
    story.append(Spacer(1, 0.35 * cm))
    story.append(
        Paragraph(
            _html(f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"),
            styles["muted"],
        )
    )
    story.append(PageBreak())
    return story


def _normal_result_section(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    before = _clean_list(operation.get("before", []))
    after = _clean_list(operation.get("after", []))
    removed = _removed_formulas(before, after)
    kept = _kept_formulas(before, after)

    story: list[Any] = []
    story.extend(_section_title("1. Resultado final", styles, palette))
    story.append(
        _info_table(
            [
                ("Base inicial", _numbered_list(before, "(base vazia)")),
                ("Base final", _numbered_list(after, "(base vazia)")),
                ("Fórmulas mantidas", _set_text(kept)),
                ("Fórmulas removidas", _set_text(removed)),
            ],
            palette,
            styles,
        )
    )
    story.append(Spacer(1, 0.35 * cm))
    return story


def _normal_steps_section(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    steps = _steps(operation)
    story: list[Any] = []
    story.extend(_section_title("2. Passos da contração", styles, palette))

    if not steps:
        story.append(
            _p(
                "Não foram registados passos técnicos para esta operação.",
                styles["body"],
            )
        )
        return story

    story.append(
        _p(
            "A sequência abaixo mostra a execução interna do operador: verificações iniciais, cálculo dos conjuntos relevantes, escolha da estratégia e construção da base final.",
            styles["muted"],
        )
    )
    story.append(Spacer(1, 0.1 * cm))

    for title, lines in _split_steps_into_blocks(steps):
        rows = [[Paragraph(f"<b>{_html(title)}</b>", styles["subsection"])]]

        if lines:
            rows.append([Paragraph(_html("\n".join(lines)), styles["small"])])

        table = Table(rows, colWidths=[16.0 * cm], hAlign="CENTER")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), WHITE),
                    ("LINEBEFORE", (0, 0), (0, -1), 3, palette["accent"]),
                    ("BOX", (0, 0), (-1, -1), 0.35, BORDER_LIGHT),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(KeepTogether([table, Spacer(1, 0.15 * cm)]))

    return story


def _extract_numbered_sets_from_steps(
    steps: Sequence[str],
    keywords: Sequence[str],
) -> list[str]:
    out: list[str] = []
    active = False

    for line in steps:
        lower = line.lower()

        if any(k.lower() in lower for k in keywords):
            active = True
            continue

        if active:
            if re.match(r"^\d+\.", line) or line.startswith("{"):
                out.append(line)
            elif line.endswith(":"):
                active = False

    return _dedupe_preserve_order(out)


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
    steps = _steps(operation)

    story: list[Any] = []
    story.extend(_section_title("3. Diagnóstico", styles, palette))

    if key == "partial meet":
        remainders = _clean_list(operation.get("remainders", []))

        if not remainders:
            remainders = _extract_numbered_sets_from_steps(
                steps,
                ["remainders encontrados", "remainders"],
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
                "Remainders considerados",
                _numbered_list(
                    remainders,
                    "Não foram recebidos de forma estruturada; consulta os passos técnicos.",
                ),
            ),
            ("Fórmulas removidas", _set_text(removed)),
            ("Fórmulas preservadas", _set_text(kept)),
            (
                "Leitura final",
                "A contração preserva as fórmulas que permanecem na interseção dos remainders selecionados.",
            ),
        ]

        note = (
            "Este diagnóstico substitui a antiga tabela de postulados. "
            "Aqui o foco está em remainders, função γ, fórmulas removidas e base final."
        )

    else:
        kernels = _clean_list(operation.get("kernels", []))

        if not kernels:
            kernels = _extract_numbered_sets_from_steps(
                steps,
                ["kernels encontrados", "kernels"],
            )

        incision = (
            operation.get("incision") or operation.get("removed_formulas") or removed
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
                "Kernels considerados",
                _numbered_list(
                    kernels,
                    "Não foram recebidos de forma estruturada; consulta os passos técnicos.",
                ),
            ),
            ("Incisão / remoções", _set_text(incision)),
            ("Fórmulas preservadas", _set_text(kept)),
            (
                "Leitura final",
                "A base final é obtida removendo da base inicial as fórmulas escolhidas pela incisão.",
            ),
        ]

        note = (
            "Este diagnóstico substitui a antiga tabela de postulados. "
            "Aqui o foco está em kernels, incisão σ, cobertura dos kernels e base final."
        )

    story.append(_info_table(rows, palette, styles))
    story.append(Spacer(1, 0.25 * cm))
    story.append(_callout("Nota", note, palette, styles))
    return story


def _computed_sets_section(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    key = _operator_key(operation)
    story: list[Any] = []
    story.extend(_section_title("1. Conjuntos calculados", styles, palette))

    if key == "partial meet":
        sets = _clean_list(operation.get("remainders", []))
        label = "Remainders"
        explanation = "Cada remainder é uma sub-base maximal que deixa de implicar a fórmula alvo."
    else:
        sets = _clean_list(operation.get("kernels", []))
        label = "Kernels"
        explanation = "Cada kernel é um subconjunto mínimo da base que ainda implica a fórmula alvo."

    story.append(_p(explanation, styles["muted"]))
    story.append(Spacer(1, 0.1 * cm))
    story.append(
        _info_table(
            [
                (
                    label,
                    _numbered_list(
                        sets, "Nenhum conjunto recebido de forma estruturada."
                    ),
                )
            ],
            palette,
            styles,
        )
    )
    story.append(PageBreak())
    return story


def _option_id(option: dict[str, Any], fallback: int) -> str:
    return _safe_text(option.get("option_id") or option.get("id") or fallback)


def _partial_option_table(
    option: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    selected_indices = option.get("selected_indices", [])
    selected_remainders = option.get("selected_remainders", [])
    removed = option.get("removed_formulas", [])
    result = option.get("result_base", [])

    rows = [
        (
            "Seleção γ",
            "Índices escolhidos: " + _join_inline(selected_indices, "não indicados"),
        ),
        ("Remainders escolhidos", _numbered_list(selected_remainders, "não indicados")),
        ("Fórmulas removidas", _set_text(removed)),
        ("Base resultante", _numbered_list(result, "(base vazia)")),
    ]

    return _info_table(rows, palette, styles)


def _kernel_option_table(
    option: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> Table:
    incision = option.get("incision", [])
    removed = option.get("removed_formulas", [])
    result = option.get("result_base", [])
    is_minimal = option.get("is_minimal", None)

    if is_minimal is True:
        kind = "Incisão minimal"
    elif is_minimal is False:
        kind = "Incisão válida"
    else:
        kind = "Não indicado"

    rows = [
        ("Incisão σ", _set_text(incision)),
        ("Tipo", kind),
        ("Fórmulas removidas", _set_text(removed)),
        ("Base resultante", _numbered_list(result, "(base vazia)")),
    ]

    return _info_table(rows, palette, styles)


def _all_options_detail_section(
    operation: dict[str, Any],
    palette: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> list[Any]:
    key = _operator_key(operation)
    options = _options(operation)

    story: list[Any] = []
    story.extend(_section_title("2. Detalhe de cada possibilidade", styles, palette))

    if not options:
        story.append(
            _p(
                "Não foram recebidas possibilidades estruturadas para exportação.",
                styles["body"],
            )
        )
        return story

    intro = (
        "Cada bloco abaixo representa uma seleção γ diferente."
        if key == "partial meet"
        else "Cada bloco abaixo representa uma incisão σ diferente."
    )

    story.append(_p(intro, styles["muted"]))
    story.append(Spacer(1, 0.15 * cm))

    for idx, option in enumerate(options, start=1):
        title = f"Possibilidade #{_option_id(option, idx)}"

        title_table = Table(
            [[Paragraph(f"<b>{_html(title)}</b>", styles["subsection"])]],
            colWidths=[16.0 * cm],
            hAlign="CENTER",
        )
        title_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), palette["pale"]),
                    ("LINEBEFORE", (0, 0), (0, -1), 4, palette["accent"]),
                    ("BOX", (0, 0), (-1, -1), 0.4, BORDER_LIGHT),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ]
            )
        )

        if key == "partial meet":
            detail = _partial_option_table(option, palette, styles)
        else:
            detail = _kernel_option_table(option, palette, styles)

        story.append(KeepTogether([title_table, detail, Spacer(1, 0.25 * cm)]))

    return story


def _draw_page_frame(canvas, doc, palette: dict[str, Any]) -> None:
    canvas.saveState()
    width, height = A4

    canvas.setFillColor(palette["accent"])
    canvas.rect(0, height - 0.32 * cm, width, 0.32 * cm, fill=1, stroke=0)

    canvas.setFont(FONT_REGULAR, 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(1.6 * cm, 0.75 * cm, PROJECT_NAME)
    canvas.drawRightString(width - 1.6 * cm, 0.75 * cm, f"Página {doc.page}")

    canvas.restoreState()


def export_operation_pdf(path: str | Path, operation: dict[str, Any]) -> None:
    if not isinstance(operation, dict):
        raise TypeError("operation deve ser um dicionário.")

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    key = _operator_key(operation)
    palette = PALETTES[key]
    styles = _build_styles(palette)

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=1.45 * cm,
        leftMargin=1.45 * cm,
        topMargin=1.25 * cm,
        bottomMargin=1.35 * cm,
        title=REPORT_TITLE,
        author=PROJECT_NAME,
    )

    story: list[Any] = []
    story.extend(_cover(operation, palette, styles))

    if _is_all_mode(operation):
        story.extend(_computed_sets_section(operation, palette, styles))
        story.extend(_all_options_detail_section(operation, palette, styles))
    else:
        story.extend(_normal_result_section(operation, palette, styles))
        story.extend(_normal_steps_section(operation, palette, styles))
        story.append(PageBreak())
        story.extend(_diagnostic_section(operation, palette, styles))

    def on_page(canvas, doc_obj):
        _draw_page_frame(canvas, doc_obj, palette)

    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)


def export_pdf(path: str | Path, operation: dict[str, Any]) -> None:
    export_operation_pdf(path, operation)
