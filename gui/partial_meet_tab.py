# gui/partial_meet_tab.py
# Versão SEM QUADRADOS/CARTÕES de opções - nome novo para evitar confusão nas transferências

import customtkinter as ctk

from .theme import COLORS, TITLE_FONT, APP_FONT, MONO_FONT
from .widgets import (
    make_card,
    make_log_card,
    section_title,
    secondary_button,
    danger_button,
    pm_button,
    pm_outline_button,
    export_button,
    style_choice_menu,
    style_neutral_button,
    style_soft_button,
)


# Paleta local: não obriga a mexer no theme.py, mas aproveita as cores se existirem.
def _c(key: str, fallback: str) -> str:
    return COLORS.get(key, fallback)


PM_UI = {
    "accent": _c("pm", "#dc2626"),
    "accent_dark": _c("pm_dark", "#450a0a"),
    "accent_mid": _c("pm_hover", "#991b1b"),
    "secondary": _c("pm_secondary", "#f97316"),
    "secondary_dark": _c("pm_secondary_dark", "#c2410c"),
    "tertiary": _c("pm_tertiary", "#7c3aed"),
    "tertiary_dark": _c("pm_tertiary_dark", "#4c1d95"),
    "info": _c("pm_info", "#2563eb"),
    "success": _c("success", "#16a34a"),
    "danger": _c("danger", "#dc2626"),
    "soft": _c("pm_soft", "#fee2e2"),
    "soft_2": _c("pm_panel", "#fff7ed"),
    "soft_3": _c("pm_panel_strong", "#ffedd5"),
    "purple_soft": _c("pm_purple_soft", "#f3e8ff"),
    "blue_soft": _c("pm_blue_soft", "#dbeafe"),
    "green_soft": _c("pm_green_soft", "#dcfce7"),
    "ink": _c("text", "#111827"),
    "muted": _c("muted", "#64748b"),
    "border": _c("border", "#cbd5e1"),
    "input": _c("input", "#ffffff"),
    "white": "#ffffff",
}


class _SelectedFormulaDisplay:
    """Adaptador para permitir 'Selecionada #n:' em destaque.

    Mantém compatibilidade com actions.py antigo, que faz:
        app.pm_label_selected.configure(text="Selecionada #2: ...")

    E também com actions.py novo, que pode configurar separadamente:
        app.pm_label_selected_prefix.configure(text="Selecionada #2: ")
        app.pm_label_selected.configure(text="p imp q")
    """

    def __init__(self, prefix_label: ctk.CTkLabel, value_label: ctk.CTkLabel):
        self.prefix_label = prefix_label
        self.value_label = value_label

    def configure(self, **kwargs) -> None:
        text = kwargs.pop("text", None)
        text_color = kwargs.get("text_color", None)

        if text is not None:
            text = str(text)
            if text.startswith("Selecionada #") and ":" in text:
                prefix, value = text.split(":", 1)
                self.prefix_label.configure(text=prefix + ": ")
                self.value_label.configure(text=value.strip())
            elif text.startswith("Nenhuma fórmula"):
                self.prefix_label.configure(text="")
                self.value_label.configure(text=text)
            else:
                self.value_label.configure(text=text)

        if text_color is not None:
            self.value_label.configure(text_color=text_color)

        extra_kwargs = {k: v for k, v in kwargs.items() if k != "text_color"}
        if extra_kwargs:
            self.value_label.configure(**extra_kwargs)


def _pill(parent, text: str, fg: str, bg: str, font) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=font,
        text_color=fg,
        fg_color=bg,
        corner_radius=999,
        padx=10,
        pady=4,
    )


def _step_label(parent, text: str, font, color: str) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=font,
        text_color=color,
        anchor="w",
    )


def build_tab_partial_meet(app, parent: ctk.CTkFrame) -> None:
    # Fontes locais para esta aba. Se a fonte não existir, o Tk faz fallback.
    font_section = ctk.CTkFont(family=TITLE_FONT, size=18, weight="bold")
    font_panel_title = ctk.CTkFont(family=TITLE_FONT, size=14, weight="bold")
    font_label = ctk.CTkFont(family=APP_FONT, size=12, weight="bold")
    font_body = ctk.CTkFont(family=APP_FONT, size=13)
    font_small = ctk.CTkFont(family=APP_FONT, size=12)
    font_mono = ctk.CTkFont(family=MONO_FONT, size=12)
    font_selected_bold = ctk.CTkFont(family=APP_FONT, size=12, weight="bold")

    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=2, minsize=320)
    parent.grid_columnconfigure(1, weight=2, minsize=350)
    parent.grid_columnconfigure(2, weight=3, minsize=420)

    # ============================================================
    # BASE PARTIAL MEET
    # ============================================================

    base_card = make_card(parent)
    base_card.configure(border_color=PM_UI["soft_3"], border_width=1)
    base_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
    base_card.grid_rowconfigure(5, weight=1)
    base_card.grid_columnconfigure(0, weight=1)

    header = ctk.CTkFrame(base_card, fg_color="transparent", height=42)
    header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 8))
    header.grid_propagate(False)
    header.grid_columnconfigure(0, weight=1)

    section_title(header, "Base Partial Meet", font_section, color_key="pm").grid(
        row=0, column=0, sticky="w"
    )

    app.pm_label_count = _pill(
        header,
        "0 fórmulas",
        PM_UI["accent_dark"],
        PM_UI["soft"],
        font_small,
    )
    app.pm_label_count.grid(row=0, column=1, sticky="e")

    app.entry_pm_formula = ctk.CTkEntry(
        base_card,
        placeholder_text="Adicionar fórmula. Ex: p; p imp q",
        height=38,
        fg_color=PM_UI["input"],
        border_color=PM_UI["soft_3"],
        text_color=PM_UI["ink"],
        font=font_body,
    )
    app.entry_pm_formula.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))
    app.entry_pm_formula.bind("<Return>", lambda event: app._add_formula_to("pm"))

    pm_button(
        base_card,
        "Adicionar fórmula à base",
        lambda: app._add_formula_to("pm"),
        font_small,
    ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

    file_buttons = ctk.CTkFrame(base_card, fg_color="transparent", height=40)
    file_buttons.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 8))
    file_buttons.grid_propagate(False)
    file_buttons.grid_columnconfigure((0, 1), weight=1)

    app.pm_btn_save = secondary_button(
        file_buttons,
        "Guardar base",
        lambda: app._save_base_to_file("pm"),
        font_small,
        variant="pm",
    )
    style_neutral_button(app.pm_btn_save)
    app.pm_btn_save.grid(row=0, column=0, sticky="ew", padx=(0, 5))

    app.pm_btn_load = secondary_button(
        file_buttons,
        "Carregar base",
        lambda: app._load_base_from_file("pm"),
        font_small,
        variant="pm",
    )
    style_neutral_button(app.pm_btn_load)
    app.pm_btn_load.grid(row=0, column=1, sticky="ew", padx=(5, 0))

    ctk.CTkLabel(
        base_card,
        text="Clica numa linha para a selecionar. A fórmula selecionada fica destacada abaixo.",
        font=font_small,
        text_color=PM_UI["muted"],
        anchor="w",
        justify="left",
        wraplength=315,
    ).grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 7))

    app.pm_text_base = ctk.CTkTextbox(
        base_card,
        font=font_mono,
        fg_color=PM_UI["input"],
        text_color=PM_UI["ink"],
        border_width=1,
        border_color=PM_UI["soft_3"],
        corner_radius=14,
        activate_scrollbars=True,
    )
    app.pm_text_base.grid(row=5, column=0, sticky="nsew", padx=16, pady=(0, 8))
    app.pm_text_base.tag_config(
        "selected_line",
        background=PM_UI["soft_3"],
        foreground=PM_UI["accent_dark"],
    )

    def _handle_pm_base_click(event):
        app._on_operator_base_click("pm", event)
        return "break"

    app.pm_text_base.bind("<Button-1>", _handle_pm_base_click)
    app.pm_text_base.bind("<Key>", lambda event: "break")

    bottom = ctk.CTkFrame(
        base_card, fg_color=PM_UI["soft_2"], corner_radius=14, height=86
    )
    bottom.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 12))
    bottom.grid_propagate(False)
    bottom.grid_columnconfigure((0, 1), weight=1)

    selected_row = ctk.CTkFrame(bottom, fg_color="transparent")
    selected_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(8, 6))
    selected_row.grid_columnconfigure(1, weight=1)

    app.pm_label_selected_prefix = ctk.CTkLabel(
        selected_row,
        text="",
        font=font_selected_bold,
        text_color=PM_UI["accent_dark"],
        anchor="w",
    )
    app.pm_label_selected_prefix.grid(row=0, column=0, sticky="w")

    pm_label_selected_value = ctk.CTkLabel(
        selected_row,
        text="Nenhuma fórmula selecionada",
        font=font_small,
        text_color=PM_UI["muted"],
        anchor="w",
    )
    pm_label_selected_value.grid(row=0, column=1, sticky="ew")

    app.pm_label_selected = _SelectedFormulaDisplay(
        app.pm_label_selected_prefix, pm_label_selected_value
    )

    app.pm_btn_remove = secondary_button(
        bottom,
        "Remover selecionada",
        lambda: app._remove_selected_from("pm"),
        font_small,
        variant="pm",
    )
    style_neutral_button(app.pm_btn_remove)
    app.pm_btn_remove.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=(0, 8))
    app.pm_btn_remove.configure(state="disabled")

    app.pm_btn_clear_base = danger_button(
        bottom,
        "Limpar base",
        lambda: app._clear_base_for("pm"),
        font_small,
    )
    style_neutral_button(app.pm_btn_clear_base)
    app.pm_btn_clear_base.grid(row=1, column=1, sticky="ew", padx=(5, 10), pady=(0, 8))

    # ============================================================
    # OPERAÇÃO PARTIAL MEET
    # ============================================================

    operation_card = make_card(parent, alt=True)
    operation_card.configure(
        fg_color=PM_UI["soft_2"],
        border_color=PM_UI["soft_3"],
        border_width=1,
    )
    operation_card.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=10,
        pady=10,
    )
    operation_card.grid_columnconfigure(0, weight=1)

    # ---------------------------------------------------------
    # Cabeçalho da operação
    # ---------------------------------------------------------

    op_header = ctk.CTkFrame(
        operation_card,
        fg_color="transparent",
    )

    op_header.grid(
        row=0,
        column=0,
        sticky="ew",
        padx=16,
        pady=(12, 8),
    )

    op_header.grid_columnconfigure(
        0,
        weight=1,
        minsize=225,
    )

    op_header.grid_columnconfigure(
        1,
        weight=0,
    )

    op_title = section_title(
        op_header,
        "Operação Partial Meet",
        font_section,
        color_key="pm",
    )

    op_title.grid(
        row=0,
        column=0,
        sticky="w",
        padx=(0, 8),
    )

    selection_pill = _pill(
        op_header,
        "γ seleção",
        PM_UI["secondary_dark"],
        PM_UI["soft_3"],
        font_small,
    )

    selection_pill.grid(
        row=0,
        column=1,
        sticky="e",
    )

    # ---------------------------------------------------------
    # Painel da fórmula α
    # ---------------------------------------------------------

    alpha_panel = ctk.CTkFrame(
        operation_card,
        fg_color=PM_UI["white"],
        corner_radius=16,
        border_width=1,
        border_color=PM_UI["soft_3"],
    )

    alpha_panel.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=16,
        pady=(0, 10),
    )

    alpha_panel.grid_columnconfigure(
        0,
        weight=1,
    )

    # A partir daqui já podes usar alpha_panel
    _step_label(
        alpha_panel,
        "1. Fórmula a contrair α",
        font_label,
        PM_UI["accent_dark"],
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=12,
        pady=(10, 5),
    )
    app.entry_pm_target = ctk.CTkEntry(
        alpha_panel,
        placeholder_text="Ex: r",
        height=38,
        fg_color=PM_UI["input"],
        border_color=PM_UI["border"],
        text_color=PM_UI["ink"],
        font=font_body,
    )
    app.entry_pm_target.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))
    app.entry_pm_target.bind(
        "<Return>", lambda event: app._run_partial_meet_selected_mode()
    )

    strategy_panel = ctk.CTkFrame(
        operation_card,
        fg_color=PM_UI["white"],
        corner_radius=16,
        border_width=1,
        border_color=PM_UI["soft_3"],
    )
    strategy_panel.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
    strategy_panel.grid_columnconfigure(0, weight=1)

    _step_label(
        strategy_panel,
        "2. Escolher função de seleção γ",
        font_label,
        PM_UI["accent_dark"],
    ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

    app.combo_pm_strategy = ctk.CTkOptionMenu(
        strategy_panel,
        values=[
            "Full meet",
            "Maxichoice",
            "Maior cardinalidade",
            "Manual",
            "Todas as seleções possíveis",
        ],
        variable=app.pm_strategy,
        height=38,
        font=font_small,
        fg_color=PM_UI["accent"],
        button_color=PM_UI["accent_dark"],
        button_hover_color=PM_UI["accent_mid"],
        dropdown_fg_color="#ffffff",
        dropdown_hover_color=PM_UI["soft"],
        dropdown_text_color=PM_UI["ink"],
        text_color="white",
    )
    style_choice_menu(app.combo_pm_strategy, "pm")
    app.combo_pm_strategy.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))

    actions_panel = ctk.CTkFrame(operation_card, fg_color="transparent")
    actions_panel.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 12))
    actions_panel.grid_columnconfigure(0, weight=1)

    pm_outline_button(
        actions_panel,
        "Ver remainders antes",
        app._show_remainders,
        font_small,
    ).grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 8))

    pm_button(
        actions_panel,
        "Executar selecionada",
        app._run_partial_meet_selected_mode,
        font_small,
    ).grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 0))

    # Bloco explicativo removido: sem quadrados/cartões de opções nesta página.

    # ============================================================
    # RESULTADOS PARTIAL MEET
    # ============================================================

    result_card = make_log_card(parent)
    result_card.configure(border_color=PM_UI["soft_3"], border_width=1)
    result_card.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=10)
    result_card.grid_rowconfigure(1, weight=1)
    result_card.grid_columnconfigure(0, weight=1)

    result_header = ctk.CTkFrame(
        result_card, fg_color=PM_UI["accent_dark"], corner_radius=16
    )
    result_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
    result_header.grid_columnconfigure(0, weight=1)
    result_header.grid_columnconfigure(1, weight=0)

    # Título do cabeçalho
    ctk.CTkLabel(
        result_header,
        text="Resultados Partial Meet",
        font=font_section,
        text_color="#ffffff",
        anchor="w",
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=12,
        pady=(8, 0),
    )

    # Subtítulo do cabeçalho
    result_subtitle = ctk.CTkLabel(
        result_header,
        text="contagens, remainders, seleções, remoções e base resultante",
        font=font_small,
        text_color="#ffedd5",
        anchor="w",
        justify="left",
        wraplength=390,
    )

    result_subtitle.grid(
        row=1,
        column=0,
        columnspan=2,
        sticky="ew",
        padx=12,
        pady=(0, 8),
    )

    # Botão Limpar
    app.pm_btn_clear_log = secondary_button(
        result_header,
        "Limpar",
        app._clear_pm_log,
        font_small,
        variant="pm",
    )

    style_soft_button(app.pm_btn_clear_log)

    app.pm_btn_clear_log.grid(
        row=0,
        column=1,
        sticky="e",
        padx=8,
        pady=8,
    )

    app.text_pm_log = ctk.CTkTextbox(
        result_card,
        font=font_body,
        fg_color=_c("pm_log", "#fffafa"),
        text_color=PM_UI["ink"],
        border_width=1,
        border_color=PM_UI["soft_3"],
        corner_radius=14,
        activate_scrollbars=True,
    )
    app.text_pm_log.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))
    app.text_pm_log.bind("<Key>", lambda event: "break")
    app._configure_log_tags(app.text_pm_log)

    result_footer = ctk.CTkFrame(result_card, fg_color="transparent", height=44)
    result_footer.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))
    result_footer.grid_propagate(False)
    result_footer.grid_columnconfigure(0, weight=1)

    app.pm_btn_export_pdf = export_button(
        result_footer,
        "Guardar último relatório em PDF",
        lambda: app._export_last_operation_pdf("Partial Meet"),
        font_small,
    )
    style_soft_button(app.pm_btn_export_pdf)
    app.pm_btn_export_pdf.grid(row=0, column=0, sticky="ew")

    app._pm_log("Partial Meet pronto.")
    app._pm_log("Cria uma base nesta aba, escolhe α e executa a opção.")
