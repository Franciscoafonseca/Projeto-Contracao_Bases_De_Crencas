from turtle import left, right

import customtkinter as ctk

from .theme import COLORS
from .widgets import (
    make_card,
    section_title,
    primary_button,
    secondary_button,
    danger_button,
)


def build_tab_base(app, parent: ctk.CTkFrame) -> None:
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=3)
    parent.grid_columnconfigure(1, weight=2)

    left = make_card(parent)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=8)
    left.grid_rowconfigure(1, weight=1)
    left.grid_columnconfigure(0, weight=1)

    header = ctk.CTkFrame(left, fg_color="transparent", height=34)
    header.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 4))
    header.grid_propagate(False)
    header.grid_columnconfigure(0, weight=1)

    section_title(header, "Base de Crenças", app.font_section).grid(
        row=0, column=0, sticky="w"
    )

    app.label_count = ctk.CTkLabel(
        header,
        text="0 fórmulas",
        font=app.font_small,
        text_color=COLORS["muted"],
    )
    app.label_count.grid(row=0, column=1, sticky="e")

    app.text_base = ctk.CTkTextbox(
        left,
        font=app.font_mono,
        fg_color=COLORS["input"],
        text_color=COLORS["text"],
        border_width=1,
        border_color="#e5e7eb",
        corner_radius=10,
        activate_scrollbars=True,
    )
    app.text_base.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))
    app.text_base.tag_config("selected_line", background=COLORS["selected"])
    app.text_base.bind("<ButtonRelease-1>", app._on_base_click)
    app.text_base.bind("<Key>", lambda event: "break")

    bottom = ctk.CTkFrame(left, fg_color="transparent", height=40)
    bottom.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))
    bottom.grid_propagate(False)
    bottom.grid_columnconfigure(0, weight=1)

    app.label_selected = ctk.CTkLabel(
        bottom,
        text="Nenhuma fórmula selecionada",
        font=app.font_small,
        text_color=COLORS["muted"],
        anchor="w",
        width=360,
    )
    app.label_selected.grid(row=0, column=0, sticky="ew", padx=(0, 8))

    app.btn_remove = secondary_button(
        bottom,
        "Remover",
        app._remove_selected,
        app.font_small,
    )
    app.btn_remove.grid(row=0, column=1, sticky="e", padx=(0, 8))
    app.btn_remove.configure(state="disabled")

    danger_button(
        bottom,
        "Limpar base",
        app._clear_base,
        app.font_small,
    ).grid(row=0, column=2, sticky="e")

    file_buttons = ctk.CTkFrame(left, fg_color="transparent", height=40)
    file_buttons.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 10))
    file_buttons.grid_propagate(False)
    file_buttons.grid_columnconfigure((0, 1), weight=1)

    secondary_button(
        file_buttons,
        "Guardar base",
        app._save_base_to_file,
        app.font_small,
    ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

    secondary_button(
        file_buttons,
        "Carregar base",
        app._load_base_from_file,
        app.font_small,
    ).grid(row=0, column=1, sticky="ew", padx=(5, 0))
    right = make_card(parent, alt=True)
    right.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=8)
    right.grid_columnconfigure(0, weight=1)
    right.grid_rowconfigure(9, weight=1)

    section_title(right, "Nova fórmula", app.font_section).grid(
        row=0, column=0, sticky="w", padx=14, pady=(10, 4)
    )

    app.entry_formula = ctk.CTkEntry(
        right,
        placeholder_text="ex: p; p imp q; neg r",
        height=32,
        fg_color=COLORS["input"],
        border_color=COLORS["border"],
        text_color=COLORS["text"],
        font=app.font_body,
    )
    app.entry_formula.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 6))
    app.entry_formula.bind("<Return>", lambda event: app._add_formula())

    primary_button(
        right,
        "Adicionar à base",
        app._add_formula,
        app.font_small,
    ).grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))

    section_title(right, "Fórmula a contrair", app.font_section).grid(
        row=3, column=0, sticky="w", padx=14, pady=(0, 4)
    )

    app.entry_target = ctk.CTkEntry(
        right,
        placeholder_text="fórmula a contrair  ex: q",
        height=32,
        fg_color=COLORS["input"],
        border_color=COLORS["border"],
        text_color=COLORS["text"],
        font=app.font_body,
    )
    app.entry_target.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 6))
    app.entry_target.bind("<Return>", lambda event: app._contract_partial_meet())

    strategy_frame = ctk.CTkFrame(right, fg_color="transparent")
    strategy_frame.grid(row=5, column=0, sticky="ew", padx=14, pady=(0, 8))
    strategy_frame.grid_columnconfigure((0, 1), weight=1)

    pm_box = ctk.CTkFrame(strategy_frame, fg_color="transparent")
    pm_box.grid(row=0, column=0, sticky="ew", padx=(0, 5))
    pm_box.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        pm_box,
        text="Seleção γ",
        font=app.font_small,
        text_color=COLORS["muted"],
    ).grid(row=0, column=0, sticky="w", pady=(0, 2))

    app.combo_pm_strategy = ctk.CTkOptionMenu(
        pm_box,
        values=["Full meet", "Maxichoice", "Maior cardinalidade", "Manual"],
        variable=app.pm_strategy,
        height=30,
        font=app.font_small,
        fg_color=COLORS["primary"],
        button_color=COLORS["primary"],
        button_hover_color=COLORS["primary_light"],
    )
    app.combo_pm_strategy.grid(row=1, column=0, sticky="ew")

    kernel_box = ctk.CTkFrame(strategy_frame, fg_color="transparent")
    kernel_box.grid(row=0, column=1, sticky="ew", padx=(5, 0))
    kernel_box.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        kernel_box,
        text="Incisão σ",
        font=app.font_small,
        text_color=COLORS["muted"],
    ).grid(row=0, column=0, sticky="w", pady=(0, 2))

    app.combo_kernel_strategy = ctk.CTkOptionMenu(
        kernel_box,
        values=[
            "Comum se existir",
            "Primeira por kernel",
            "Incisão mínima",
            "Manual",
        ],
        variable=app.kernel_strategy,
        height=30,
        font=app.font_small,
        fg_color=COLORS["primary"],
        button_color=COLORS["primary"],
        button_hover_color=COLORS["primary_light"],
    )
    app.combo_kernel_strategy.grid(row=1, column=0, sticky="ew")

    preview_buttons = ctk.CTkFrame(right, fg_color="transparent")
    preview_buttons.grid(row=6, column=0, sticky="ew", padx=14, pady=(0, 6))
    preview_buttons.grid_columnconfigure((0, 1), weight=1)

    secondary_button(
        preview_buttons,
        "Ver Remainders",
        app._show_remainders,
        app.font_small,
    ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

    secondary_button(
        preview_buttons,
        "Ver Kernels",
        app._show_kernels,
        app.font_small,
    ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    action_buttons = ctk.CTkFrame(right, fg_color="transparent")
    action_buttons.grid(row=7, column=0, sticky="ew", padx=14, pady=(0, 6))
    action_buttons.grid_columnconfigure((0, 1), weight=1)

    primary_button(
        action_buttons,
        "Partial Meet",
        app._contract_partial_meet,
        app.font_small,
    ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

    primary_button(
        action_buttons,
        "Kernel",
        app._contract_kernel,
        app.font_small,
    ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

    hint = ctk.CTkLabel(
        right,
        text="Sintaxe: neg, e, ou, imp, iff. Também podes usar ->.",
        font=app.font_small,
        text_color=COLORS["muted"],
        wraplength=360,
        justify="center",
    )
    hint.grid(row=8, column=0, sticky="ew", padx=14, pady=(0, 8))

    log_card = ctk.CTkFrame(
        right,
        fg_color=COLORS["log"],
        corner_radius=12,
    )
    log_card.grid(row=9, column=0, sticky="nsew", padx=14, pady=(0, 10))
    log_card.grid_rowconfigure(1, weight=1)
    log_card.grid_columnconfigure(0, weight=1)

    log_header = ctk.CTkFrame(log_card, fg_color="transparent", height=38)
    log_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 0))
    log_header.grid_propagate(False)
    log_header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        log_header,
        text="Centro de Informações",
        font=app.font_section,
        text_color=COLORS["primary"],
    ).grid(row=0, column=0, sticky="w")

    secondary_button(
        log_header,
        "Limpar",
        app._clear_log,
        app.font_small,
    ).grid(row=0, column=1, sticky="e")
    secondary_button(
        right,
        "Exportar PDF",
        app._export_last_operation_pdf,
        app.font_small,
    ).grid(row=10, column=0, sticky="ew", padx=14, pady=(0, 10))
    app.text_log = ctk.CTkTextbox(
        log_card,
        height=170,
        font=app.font_small,
        fg_color=COLORS["log"],
        text_color=COLORS["text"],
        border_width=0,
        activate_scrollbars=True,
    )
    app.text_log.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    app.text_log.bind("<Key>", lambda event: "break")

    app._log("Bem-vindo.")
    app._log("Adiciona uma base, escolhe uma fórmula alvo e testa os operadores.")
