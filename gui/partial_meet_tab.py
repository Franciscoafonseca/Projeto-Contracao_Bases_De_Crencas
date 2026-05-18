# gui/partial_meet_tab.py

import customtkinter as ctk

from .theme import COLORS
from .widgets import (
    make_card,
    make_log_card,
    section_title,
    secondary_button,
    danger_button,
    pm_button,
    pm_outline_button,
    export_button,
)


class _SelectedFormulaDisplay:
    """Pequeno adaptador para permitir 'Selecionada #n:' em destaque.

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
            if str(text).startswith("Selecionada #") and ":" in str(text):
                prefix, value = str(text).split(":", 1)
                self.prefix_label.configure(text=prefix + ": ")
                self.value_label.configure(text=value.strip())
            elif str(text).startswith("Nenhuma fórmula"):
                self.prefix_label.configure(text="")
                self.value_label.configure(text=text)
            else:
                # Se o prefixo já foi configurado por actions.py novo,
                # preserva-o e muda apenas o valor.
                self.value_label.configure(text=text)

        if text_color is not None:
            self.value_label.configure(text_color=text_color)

        extra_kwargs = {k: v for k, v in kwargs.items() if k != "text_color"}
        if extra_kwargs:
            self.value_label.configure(**extra_kwargs)


def build_tab_partial_meet(app, parent: ctk.CTkFrame) -> None:
    # Fontes locais para esta aba. Se a fonte não existir, o Tk faz fallback.
    font_section = ctk.CTkFont(
        family="Segoe UI Variable Display",
        size=16,
        weight="bold",
    )
    font_label = ctk.CTkFont(
        family="Segoe UI Variable Text",
        size=12,
        weight="bold",
    )
    font_selected_bold = ctk.CTkFont(
        family="Segoe UI Variable Text",
        size=12,
        weight="bold",
    )

    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=2, minsize=360)
    parent.grid_columnconfigure(1, weight=2, minsize=370)
    parent.grid_columnconfigure(2, weight=3, minsize=460)

    # ============================================================
    # BASE PARTIAL MEET
    # ============================================================

    base_card = make_card(parent)
    base_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
    base_card.grid_rowconfigure(5, weight=1)
    base_card.grid_columnconfigure(0, weight=1)

    header = ctk.CTkFrame(base_card, fg_color="transparent", height=36)
    header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
    header.grid_propagate(False)
    header.grid_columnconfigure(0, weight=1)

    section_title(
        header,
        "Base Partial Meet",
        font_section,
        color_key="pm",
    ).grid(row=0, column=0, sticky="w")

    app.pm_label_count = ctk.CTkLabel(
        header,
        text="0 fórmulas",
        font=app.font_small,
        text_color=COLORS["muted"],
    )
    app.pm_label_count.grid(row=0, column=1, sticky="e")

    app.entry_pm_formula = ctk.CTkEntry(
        base_card,
        placeholder_text="Adicionar fórmula. Ex: p; p imp q",
        height=36,
        fg_color=COLORS["input"],
        border_color=COLORS["border"],
        text_color=COLORS["text"],
        font=app.font_body,
    )
    app.entry_pm_formula.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))
    app.entry_pm_formula.bind(
        "<Return>",
        lambda event: app._add_formula_to("pm"),
    )

    pm_button(
        base_card,
        "Adicionar fórmula à base",
        lambda: app._add_formula_to("pm"),
        app.font_small,
    ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

    file_buttons = ctk.CTkFrame(base_card, fg_color="transparent", height=40)
    file_buttons.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 8))
    file_buttons.grid_propagate(False)
    file_buttons.grid_columnconfigure((0, 1), weight=1)

    secondary_button(
        file_buttons,
        "Guardar base",
        lambda: app._save_base_to_file("pm"),
        app.font_small,
        variant="pm",
    ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

    secondary_button(
        file_buttons,
        "Carregar base",
        lambda: app._load_base_from_file("pm"),
        app.font_small,
        variant="pm",
    ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    app.pm_text_base = ctk.CTkTextbox(
        base_card,
        font=app.font_mono,
        fg_color=COLORS["input"],
        text_color=COLORS["text"],
        border_width=1,
        border_color=COLORS["border"],
        corner_radius=12,
        activate_scrollbars=True,
    )
    app.pm_text_base.grid(row=5, column=0, sticky="nsew", padx=16, pady=(0, 8))
    app.pm_text_base.tag_config(
        "selected_line",
        background=COLORS.get("pm_panel_strong", COLORS["pm_soft"]),
        foreground=COLORS["text"],
    )

    def _handle_pm_base_click(event):
        app._on_operator_base_click("pm", event)
        return "break"

    app.pm_text_base.bind("<Button-1>", _handle_pm_base_click)
    app.pm_text_base.bind("<Key>", lambda event: "break")

    bottom = ctk.CTkFrame(base_card, fg_color="transparent", height=78)
    bottom.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 12))
    bottom.grid_propagate(False)
    bottom.grid_columnconfigure((0, 1), weight=1)

    selected_row = ctk.CTkFrame(bottom, fg_color="transparent")
    selected_row.grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="ew",
        pady=(0, 6),
    )
    selected_row.grid_columnconfigure(1, weight=1)

    app.pm_label_selected_prefix = ctk.CTkLabel(
        selected_row,
        text="",
        font=font_selected_bold,
        text_color=COLORS.get("pm_dark", COLORS["pm"]),
        anchor="w",
    )
    app.pm_label_selected_prefix.grid(row=0, column=0, sticky="w")

    pm_label_selected_value = ctk.CTkLabel(
        selected_row,
        text="Nenhuma fórmula selecionada",
        font=app.font_small,
        text_color=COLORS["muted"],
        anchor="w",
    )
    pm_label_selected_value.grid(row=0, column=1, sticky="ew")

    app.pm_label_selected = _SelectedFormulaDisplay(
        app.pm_label_selected_prefix,
        pm_label_selected_value,
    )

    app.pm_btn_remove = secondary_button(
        bottom,
        "Remover selecionada",
        lambda: app._remove_selected_from("pm"),
        app.font_small,
        variant="pm",
    )
    app.pm_btn_remove.grid(row=1, column=0, sticky="ew", padx=(0, 5))
    app.pm_btn_remove.configure(state="disabled")

    danger_button(
        bottom,
        "Limpar",
        lambda: app._clear_base_for("pm"),
        app.font_small,
    ).grid(row=1, column=1, sticky="ew", padx=(5, 0))

    # ============================================================
    # OPERAÇÃO PARTIAL MEET
    # ============================================================

    operation_card = make_card(parent, alt=True)
    operation_card.configure(
        fg_color=COLORS.get("pm_panel", COLORS["pm_soft"]),
        border_color=COLORS.get("pm_border", COLORS["border"]),
    )
    operation_card.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    operation_card.grid_columnconfigure(0, weight=1)

    section_title(
        operation_card,
        "Operação Partial Meet",
        font_section,
        color_key="pm",
    ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 8))

    ctk.CTkLabel(
        operation_card,
        text="1. Fórmula a contrair α",
        font=font_label,
        text_color=COLORS.get("pm_dark", COLORS["pm"]),
    ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 4))

    app.entry_pm_target = ctk.CTkEntry(
        operation_card,
        placeholder_text="Ex: r",
        height=36,
        fg_color=COLORS["input"],
        border_color=COLORS["border"],
        text_color=COLORS["text"],
        font=app.font_body,
    )
    app.entry_pm_target.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
    app.entry_pm_target.bind(
        "<Return>",
        lambda event: app._run_partial_meet_selected_mode(),
    )

    ctk.CTkLabel(
        operation_card,
        text="2. Função de seleção γ",
        font=font_label,
        text_color=COLORS.get("pm_dark", COLORS["pm"]),
    ).grid(row=3, column=0, sticky="w", padx=16, pady=(0, 4))

    app.combo_pm_strategy = ctk.CTkOptionMenu(
        operation_card,
        values=[
            "Full meet",
            "Maxichoice",
            "Maior cardinalidade",
            "Manual",
            "Todas as seleções possíveis",
        ],
        variable=app.pm_strategy,
        height=36,
        font=app.font_small,
        fg_color=COLORS["pm"],
        button_color=COLORS.get("pm_dark", COLORS["pm"]),
        button_hover_color=COLORS["pm_hover"],
        dropdown_fg_color="#ffffff",
        dropdown_hover_color=COLORS["pm_soft"],
        text_color="white",
    )
    app.combo_pm_strategy.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 14))

    pm_outline_button(
        operation_card,
        "Ver remainders antes de contrair",
        app._show_remainders,
        app.font_small,
    ).grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 8))

    pm_button(
        operation_card,
        "Executar opção selecionada",
        app._run_partial_meet_selected_mode,
        app.font_small,
    ).grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 14))

    explanation = ctk.CTkFrame(
        operation_card,
        fg_color=COLORS.get("pm_panel_strong", COLORS["pm_soft"]),
        corner_radius=14,
    )
    explanation.grid(row=7, column=0, sticky="ew", padx=16, pady=(0, 14))
    explanation.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        explanation,
        text="Como ler esta aba",
        font=font_section,
        text_color=COLORS.get("pm_dark", COLORS["pm"]),
        anchor="w",
    ).grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))

    ctk.CTkLabel(
        explanation,
        text=(
            "Partial Meet calcula os remainders de A por α.\n"
            "Depois escolhe alguns remainders com γ e interseta-os.\n\n"
            "Escolhe a opção no menu acima e carrega em "
            "Executar opção selecionada. A opção de exploração não altera a base."
        ),
        font=app.font_small,
        text_color=COLORS["text"],
        justify="left",
        wraplength=330,
    ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))

    # ============================================================
    # RESULTADOS PARTIAL MEET
    # ============================================================

    result_card = make_log_card(parent)
    result_card.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=10)
    result_card.grid_rowconfigure(1, weight=1)
    result_card.grid_columnconfigure(0, weight=1)

    result_header = ctk.CTkFrame(
        result_card,
        fg_color=COLORS["log_header"],
        corner_radius=14,
    )
    result_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 8))
    result_header.grid_columnconfigure(0, weight=1)

    section_title(
        result_header,
        "Resultados Partial Meet",
        font_section,
        color_key="pm",
    ).grid(row=0, column=0, sticky="w", padx=12, pady=8)

    secondary_button(
        result_header,
        "Limpar",
        app._clear_pm_log,
        app.font_small,
        variant="pm",
    ).grid(row=0, column=1, sticky="e", padx=8, pady=6)

    app.text_pm_log = ctk.CTkTextbox(
        result_card,
        font=app.font_body,
        fg_color=COLORS["log"],
        text_color=COLORS["text"],
        border_width=0,
        corner_radius=12,
        activate_scrollbars=True,
    )
    app.text_pm_log.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))
    app.text_pm_log.bind("<Key>", lambda event: "break")
    app._configure_log_tags(app.text_pm_log)

    result_footer = ctk.CTkFrame(result_card, fg_color="transparent", height=44)
    result_footer.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))
    result_footer.grid_propagate(False)
    result_footer.grid_columnconfigure(0, weight=1)

    export_button(
        result_footer,
        "Guardar último relatório em PDF",
        lambda: app._export_last_operation_pdf("Partial Meet"),
        app.font_small,
    ).grid(row=0, column=0, sticky="ew")

    app._pm_log("Partial Meet pronto.")
    app._pm_log("Cria uma base nesta aba, escolhe α e executa a opção.")
