# gui/kernel_tab.py

import customtkinter as ctk

from .theme import COLORS
from .widgets import (
    make_card,
    make_log_card,
    section_title,
    secondary_button,
    danger_button,
    success_button,
    kernel_button,
    explore_button,
    export_button,
)


def build_tab_kernel(app, parent: ctk.CTkFrame) -> None:
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=2)
    parent.grid_columnconfigure(1, weight=2)
    parent.grid_columnconfigure(2, weight=3)

    # ============================================================
    # BASE KERNEL
    # ============================================================

    base_card = make_card(parent)
    base_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
    base_card.grid_rowconfigure(5, weight=1)
    base_card.grid_columnconfigure(0, weight=1)

    header = ctk.CTkFrame(base_card, fg_color="transparent", height=34)
    header.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 6))
    header.grid_propagate(False)
    header.grid_columnconfigure(0, weight=1)

    section_title(
        header,
        "Base Kernel",
        app.font_section,
        color_key="kernel",
    ).grid(row=0, column=0, sticky="w")

    app.kernel_label_count = ctk.CTkLabel(
        header,
        text="0 fórmulas",
        font=app.font_small,
        text_color=COLORS["muted"],
    )
    app.kernel_label_count.grid(row=0, column=1, sticky="e")

    app.entry_kernel_formula = ctk.CTkEntry(
        base_card,
        placeholder_text="Adicionar fórmula. Ex: p; p imp q",
        height=34,
        fg_color=COLORS["input"],
        border_color=COLORS["border"],
        text_color=COLORS["text"],
        font=app.font_body,
    )
    app.entry_kernel_formula.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))
    app.entry_kernel_formula.bind(
        "<Return>",
        lambda event: app._add_formula_to("kernel"),
    )

    success_button(
        base_card,
        "Adicionar fórmula à base",
        lambda: app._add_formula_to("kernel"),
        app.font_small,
    ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

    file_buttons = ctk.CTkFrame(base_card, fg_color="transparent", height=38)
    file_buttons.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 8))
    file_buttons.grid_propagate(False)
    file_buttons.grid_columnconfigure((0, 1), weight=1)

    secondary_button(
        file_buttons,
        "Guardar base",
        lambda: app._save_base_to_file("kernel"),
        app.font_small,
    ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

    secondary_button(
        file_buttons,
        "Carregar base",
        lambda: app._load_base_from_file("kernel"),
        app.font_small,
    ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    app.kernel_text_base = ctk.CTkTextbox(
        base_card,
        font=app.font_mono,
        fg_color=COLORS["input"],
        text_color=COLORS["text"],
        border_width=1,
        border_color=COLORS["border"],
        corner_radius=12,
        activate_scrollbars=True,
    )
    app.kernel_text_base.grid(row=5, column=0, sticky="nsew", padx=16, pady=(0, 8))
    app.kernel_text_base.tag_config(
        "selected_line",
        background=COLORS["kernel_soft"],
    )
    app.kernel_text_base.bind(
        "<Button-1>",
        lambda event: app._on_operator_base_click("kernel", event),
    )
    app.kernel_text_base.bind("<Key>", lambda event: "break")

    bottom = ctk.CTkFrame(base_card, fg_color="transparent", height=40)
    bottom.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 12))
    bottom.grid_propagate(False)
    bottom.grid_columnconfigure(0, weight=1)

    app.kernel_label_selected = ctk.CTkLabel(
        bottom,
        text="Nenhuma fórmula selecionada",
        font=app.font_small,
        text_color=COLORS["muted"],
        anchor="w",
    )
    app.kernel_label_selected.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    app.kernel_btn_remove = secondary_button(
        bottom,
        "Remover selecionada",
        lambda: app._remove_selected_from("kernel"),
        app.font_small,
    )
    app.kernel_btn_remove.grid(row=0, column=1, sticky="e", padx=(0, 8))
    app.kernel_btn_remove.configure(state="disabled")

    danger_button(
        bottom,
        "Limpar",
        lambda: app._clear_base_for("kernel"),
        app.font_small,
    ).grid(row=0, column=2, sticky="e")

    # ============================================================
    # OPERAÇÃO KERNEL
    # ============================================================

    operation_card = make_card(parent, alt=True)
    operation_card.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    operation_card.grid_columnconfigure(0, weight=1)

    section_title(
        operation_card,
        "Operação Kernel",
        app.font_section,
        color_key="kernel",
    ).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 8))

    ctk.CTkLabel(
        operation_card,
        text="1. Fórmula a contrair α",
        font=app.font_small,
        text_color=COLORS["muted_dark"],
    ).grid(row=1, column=0, sticky="w", padx=16, pady=(0, 4))

    app.entry_kernel_target = ctk.CTkEntry(
        operation_card,
        placeholder_text="Ex: r",
        height=34,
        fg_color=COLORS["input"],
        border_color=COLORS["border"],
        text_color=COLORS["text"],
        font=app.font_body,
    )
    app.entry_kernel_target.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 10))
    app.entry_kernel_target.bind(
        "<Return>",
        lambda event: app._run_kernel_selected_mode(),
    )

    ctk.CTkLabel(
        operation_card,
        text="2. Função de incisão σ",
        font=app.font_small,
        text_color=COLORS["muted_dark"],
    ).grid(row=3, column=0, sticky="w", padx=16, pady=(0, 4))

    app.combo_kernel_strategy = ctk.CTkOptionMenu(
        operation_card,
        values=[
            "Comum se existir",
            "Primeira por kernel",
            "Incisão mínima",
            "Manual",
            "Todas as incisões válidas",
            "Todas as incisões mínimas",
        ],
        variable=app.kernel_strategy,
        height=34,
        font=app.font_small,
        fg_color=COLORS["kernel"],
        button_color=COLORS["kernel"],
        button_hover_color=COLORS["kernel_light"],
        dropdown_fg_color="#ffffff",
        dropdown_hover_color=COLORS["kernel_soft"],
        text_color="white",
    )
    app.combo_kernel_strategy.grid(
        row=4,
        column=0,
        sticky="ew",
        padx=16,
        pady=(0, 14),
    )

    secondary_button(
        operation_card,
        "Ver kernels antes de contrair",
        app._show_kernels,
        app.font_small,
    ).grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 8))

    kernel_button(
        operation_card,
        "Aplicar Kernel à base",
        app._run_kernel_selected_mode,
        app.font_small,
    ).grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 8))

    explore_button(
        operation_card,
        "Explorar todas as incisões válidas",
        lambda: app._show_all_kernel_incision_options(minimal_only=False),
        app.font_small,
    ).grid(row=7, column=0, sticky="ew", padx=16, pady=(0, 8))

    explore_button(
        operation_card,
        "Explorar apenas incisões mínimas",
        lambda: app._show_all_kernel_incision_options(minimal_only=True),
        app.font_small,
    ).grid(row=8, column=0, sticky="ew", padx=16, pady=(0, 8))

    export_button(
        operation_card,
        "Exportar último relatório PDF",
        lambda: app._export_last_operation_pdf("Kernel"),
        app.font_small,
    ).grid(row=9, column=0, sticky="ew", padx=16, pady=(0, 14))

    explanation = ctk.CTkFrame(
        operation_card,
        fg_color=COLORS["kernel_soft"],
        corner_radius=14,
    )
    explanation.grid(row=10, column=0, sticky="ew", padx=16, pady=(0, 14))
    explanation.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        explanation,
        text="Como ler esta aba",
        font=app.font_section,
        text_color=COLORS["kernel"],
        anchor="w",
    ).grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))

    ctk.CTkLabel(
        explanation,
        text=(
            "Kernel calcula os subconjuntos mínimos que implicam α.\n"
            "Depois escolhe uma incisão σ que toca em todos os kernels.\n\n"
            "Mesmo que não exista uma fórmula comum a todos os kernels, "
            "podem existir incisões válidas com várias fórmulas."
        ),
        font=app.font_small,
        text_color=COLORS["text"],
        justify="left",
        wraplength=330,
    ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 12))

    # ============================================================
    # RESULTADOS KERNEL
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

    ctk.CTkLabel(
        result_header,
        text="Resultados Kernel",
        font=app.font_section,
        text_color=COLORS["kernel"],
    ).grid(row=0, column=0, sticky="w", padx=12, pady=8)

    secondary_button(
        result_header,
        "Limpar",
        app._clear_kernel_log,
        app.font_small,
    ).grid(row=0, column=1, sticky="e", padx=8, pady=6)

    app.text_kernel_log = ctk.CTkTextbox(
        result_card,
        font=app.font_body,
        fg_color=COLORS["log"],
        text_color=COLORS["text"],
        border_width=0,
        corner_radius=12,
        activate_scrollbars=True,
    )
    app.text_kernel_log.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
    app.text_kernel_log.bind("<Key>", lambda event: "break")

    app._kernel_log("Kernel pronto.")
    app._kernel_log("Cria uma base nesta aba, escolhe α e aplica uma incisão.")
