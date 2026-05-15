import customtkinter as ctk

from .theme import COLORS
from .widgets import make_card, section_title, primary_button, secondary_button


def build_tab_cp(app, parent: ctk.CTkFrame) -> None:
    parent.grid_rowconfigure(1, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_columnconfigure(1, weight=1)

    formula_card = make_card(parent)
    formula_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=8)
    formula_card.grid_columnconfigure(0, weight=1)

    section_title(formula_card, "Testes de fórmula CP", app.font_section).grid(
        row=0, column=0, sticky="w", padx=16, pady=(14, 8)
    )

    app.entry_cp_formula = ctk.CTkEntry(
        formula_card,
        placeholder_text="ex: (p imp q), (p e (q ou r)), neg p",
        height=34,
        fg_color=COLORS["input"],
        border_color=COLORS["border"],
        font=app.font_body,
    )
    app.entry_cp_formula.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

    row_formula_buttons = ctk.CTkFrame(formula_card, fg_color="transparent")
    row_formula_buttons.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))
    row_formula_buttons.grid_columnconfigure((0, 1), weight=1)

    primary_button(
        row_formula_buttons,
        "É fórmula CP?",
        app._test_cp_formula,
        app.font_small,
    ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

    secondary_button(
        row_formula_buttons,
        "É tautologia?",
        app._test_tautology,
        app.font_small,
    ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

    consequence_card = make_card(parent)
    consequence_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=8)
    consequence_card.grid_columnconfigure(0, weight=1)

    section_title(
        consequence_card,
        "Consequência lógica  Γ ⊨ φ",
        app.font_section,
    ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

    app.entry_cp_premises = ctk.CTkEntry(
        consequence_card,
        placeholder_text="premissas separadas por ';'  ex: p imp q; p",
        height=34,
        fg_color=COLORS["input"],
        border_color=COLORS["border"],
        font=app.font_body,
    )
    app.entry_cp_premises.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

    app.entry_cp_conclusion = ctk.CTkEntry(
        consequence_card,
        placeholder_text="conclusão  ex: q",
        height=34,
        fg_color=COLORS["input"],
        border_color=COLORS["border"],
        font=app.font_body,
    )
    app.entry_cp_conclusion.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

    primary_button(
        consequence_card,
        "Testar consequência",
        app._test_consequence,
        app.font_small,
    ).grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 14))

    cp_log_card = ctk.CTkFrame(
        parent,
        fg_color=COLORS["log"],
        corner_radius=14,
    )
    cp_log_card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=0, pady=(8, 8))
    cp_log_card.grid_rowconfigure(1, weight=1)
    cp_log_card.grid_columnconfigure(0, weight=1)

    cp_header = ctk.CTkFrame(cp_log_card, fg_color="transparent")
    cp_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
    cp_header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        cp_header,
        text="Resultados de CP",
        font=app.font_section,
        text_color=COLORS["primary"],
    ).grid(row=0, column=0, sticky="w")

    secondary_button(
        cp_header,
        "Limpar",
        app._clear_cp_log,
        app.font_small,
    ).grid(row=0, column=1, sticky="e")

    app.text_cp_log = ctk.CTkTextbox(
        cp_log_card,
        font=app.font_small,
        fg_color=COLORS["log"],
        text_color=COLORS["text"],
        border_width=0,
        activate_scrollbars=True,
    )
    app.text_cp_log.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
    app.text_cp_log.bind("<Key>", lambda event: "break")

    app._cp_log("Usa esta aba para testar fórmulas, tautologias e consequências.")
