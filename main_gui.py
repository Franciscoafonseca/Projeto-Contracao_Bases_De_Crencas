# main_gui.py

from __future__ import annotations

import sys
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from logica import (
    BeliefBase,
    partial_meet_contraction,
    kernel_contraction,
    partial_meet_contraction_with_steps,
    kernel_contraction_with_steps,
    remainders,
    kernels,
    ParseError,
    parse_formula,
    is_cp_formula,
    is_tautology,
    conseqlog_strings,
    selecionar_remainders,
)

# ============================================================
# TEMA
# ============================================================

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_main": "#edf1f5",
    "card": "#ffffff",
    "card_alt": "#f8fafc",
    "primary": "#1d4ed8",
    "primary_light": "#2563eb",
    "accent": "#eab308",
    "danger": "#dc2626",
    "success": "#16a34a",
    "text": "#111827",
    "muted": "#64748b",
    "border": "#d1d5db",
    "input": "#f9fafb",
    "log": "#eff6ff",
    "selected": "#dbeafe",
}

MAX_SAFE_FORMULAS = 12


# ============================================================
# HELPERS
# ============================================================


def resource_path(relative: str) -> str:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return str(base_path / relative)


def normalize_formula_text(text: str) -> str:
    s = text.strip()
    s = s.replace("->", " imp ")
    s = s.replace("→", " imp ")
    s = s.replace("¬", " neg ")
    s = s.replace("~", " neg ")
    s = " ".join(s.split())
    return s


def split_formulas(text: str) -> list[str]:
    return [
        normalize_formula_text(part)
        for part in text.split(";")
        if normalize_formula_text(part)
    ]


def make_card(parent, alt: bool = False) -> ctk.CTkFrame:
    return ctk.CTkFrame(
        parent,
        fg_color=COLORS["card_alt" if alt else "card"],
        corner_radius=16,
        border_width=1,
        border_color=COLORS["border"],
    )


def section_title(parent, text: str, font) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(
        parent,
        fg_color="transparent",
        height=24,
    )
    frame.grid_propagate(False)
    frame.pack_propagate(False)

    bar = ctk.CTkFrame(
        frame,
        width=4,
        height=18,
        fg_color=COLORS["accent"],
        corner_radius=99,
    )
    bar.grid(row=0, column=0, sticky="w", padx=(0, 8))

    label = ctk.CTkLabel(
        frame,
        text=text,
        font=font,
        text_color=COLORS["text"],
        height=22,
    )
    label.grid(row=0, column=1, sticky="w")

    return frame


def primary_button(parent, text: str, command, font) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=34,
        corner_radius=10,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_light"],
        text_color="white",
        font=font,
    )


def secondary_button(parent, text: str, command, font) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=34,
        corner_radius=10,
        fg_color="transparent",
        hover_color="#e0f2fe",
        border_width=1,
        border_color=COLORS["primary"],
        text_color=COLORS["primary"],
        font=font,
    )


def danger_button(parent, text: str, command, font) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=34,
        corner_radius=10,
        fg_color="transparent",
        hover_color="#fee2e2",
        border_width=1,
        border_color=COLORS["danger"],
        text_color=COLORS["danger"],
        font=font,
    )


# ============================================================
# APP
# ============================================================


class BeliefApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            self.iconbitmap(resource_path("favicon.ico"))
        except Exception:
            pass

        self.title("Projeto Crenças – Operadores de Contração em Bases de Crenças")
        self.geometry("1180x700")
        self.minsize(980, 620)
        self.resizable(True, True)
        self.configure(fg_color=COLORS["bg_main"])

        self.font_title = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        self.font_section = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.font_body = ctk.CTkFont(family="Segoe UI", size=12)
        self.font_small = ctk.CTkFont(family="Segoe UI", size=11)
        self.font_mono = ctk.CTkFont(family="Cascadia Code", size=12)

        self.base = BeliefBase()
        self.selected_index: int | None = None

        self.pm_strategy = ctk.StringVar(value="Full meet")
        self.kernel_strategy = ctk.StringVar(value="Comum se existir")

        self._build_ui()
        self._refresh_base_view()

    # ========================================================
    # UI PRINCIPAL
    # ========================================================

    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(8, 2))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Projeto Crenças",
            font=self.font_title,
            text_color=COLORS["text"],
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Operadores de Contração em Bases de Crenças — Partial Meet e Kernel",
            font=self.font_small,
            text_color=COLORS["muted"],
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 6))

        sep = ctk.CTkFrame(header, height=2, fg_color=COLORS["accent"])
        sep.grid(row=2, column=0, sticky="ew")

        tabs = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_main"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_light"],
            segmented_button_unselected_color="#ffffff",
            segmented_button_unselected_hover_color="#e5e7eb",
            text_color=COLORS["text"],
        )
        tabs.grid(row=1, column=0, sticky="nsew", padx=18, pady=(2, 12))

        tab_base = tabs.add("Base de Crenças")
        tab_cp = tabs.add("Cálculo Proposicional")

        tab_base.grid_rowconfigure(0, weight=1)
        tab_base.grid_columnconfigure(0, weight=1)
        tab_cp.grid_rowconfigure(0, weight=1)
        tab_cp.grid_columnconfigure(0, weight=1)

        base_scroll = ctk.CTkScrollableFrame(
            tab_base,
            fg_color="transparent",
            corner_radius=0,
        )
        base_scroll.grid(row=0, column=0, sticky="nsew")
        base_scroll.grid_columnconfigure(0, weight=1)
        base_scroll.grid_rowconfigure(0, weight=1)

        cp_scroll = ctk.CTkScrollableFrame(
            tab_cp,
            fg_color="transparent",
            corner_radius=0,
        )
        cp_scroll.grid(row=0, column=0, sticky="nsew")
        cp_scroll.grid_columnconfigure(0, weight=1)
        cp_scroll.grid_rowconfigure(0, weight=1)

        self._build_tab_base(base_scroll)
        self._build_tab_cp(cp_scroll)

    # ========================================================
    # TAB BASE
    # ========================================================

    def _build_tab_base(self, parent: ctk.CTkFrame) -> None:
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=3)
        parent.grid_columnconfigure(1, weight=2)

        # =====================================================
        # LADO ESQUERDO — BASE
        # =====================================================

        left = make_card(parent)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=8)
        left.grid_rowconfigure(1, weight=1)
        left.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(left, fg_color="transparent", height=34)
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 4))
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)

        section_title(header, "Base de Crenças", self.font_section).grid(
            row=0, column=0, sticky="w"
        )

        self.label_count = ctk.CTkLabel(
            header,
            text="0 fórmulas",
            font=self.font_small,
            text_color=COLORS["muted"],
        )
        self.label_count.grid(row=0, column=1, sticky="e")

        self.text_base = ctk.CTkTextbox(
            left,
            font=self.font_mono,
            fg_color=COLORS["input"],
            text_color=COLORS["text"],
            border_width=1,
            border_color="#e5e7eb",
            corner_radius=10,
            activate_scrollbars=True,
        )
        self.text_base.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))
        self.text_base.tag_config("selected_line", background=COLORS["selected"])
        self.text_base.bind("<ButtonRelease-1>", self._on_base_click)
        self.text_base.bind("<Key>", lambda event: "break")

        bottom = ctk.CTkFrame(left, fg_color="transparent", height=40)
        bottom.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))
        bottom.grid_propagate(False)
        bottom.grid_columnconfigure(0, weight=1)

        self.label_selected = ctk.CTkLabel(
            bottom,
            text="Nenhuma fórmula selecionada",
            font=self.font_small,
            text_color=COLORS["muted"],
            anchor="w",
            width=360,
        )
        self.label_selected.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.btn_remove = secondary_button(
            bottom,
            "Remover",
            self._remove_selected,
            self.font_small,
        )
        self.btn_remove.grid(row=0, column=1, sticky="e", padx=(0, 8))
        self.btn_remove.configure(state="disabled")

        danger_button(
            bottom,
            "Limpar base",
            self._clear_base,
            self.font_small,
        ).grid(row=0, column=2, sticky="e")

        # =====================================================
        # LADO DIREITO — OPERAÇÕES
        # =====================================================

        right = make_card(parent, alt=True)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=8)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(9, weight=1)

        section_title(right, "Nova fórmula", self.font_section).grid(
            row=0, column=0, sticky="w", padx=14, pady=(10, 4)
        )

        self.entry_formula = ctk.CTkEntry(
            right,
            placeholder_text="ex: p; p imp q; neg r",
            height=32,
            fg_color=COLORS["input"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=self.font_body,
        )
        self.entry_formula.grid(row=1, column=0, sticky="ew", padx=14, pady=(0, 6))
        self.entry_formula.bind("<Return>", lambda event: self._add_formula())

        primary_button(
            right,
            "Adicionar à base",
            self._add_formula,
            self.font_small,
        ).grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 10))

        section_title(right, "Contração", self.font_section).grid(
            row=3, column=0, sticky="w", padx=14, pady=(0, 4)
        )

        self.entry_target = ctk.CTkEntry(
            right,
            placeholder_text="fórmula a contrair  ex: q",
            height=32,
            fg_color=COLORS["input"],
            border_color=COLORS["border"],
            text_color=COLORS["text"],
            font=self.font_body,
        )
        self.entry_target.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 6))
        self.entry_target.bind("<Return>", lambda event: self._contract_partial_meet())
        strategy_frame = ctk.CTkFrame(right, fg_color="transparent")
        strategy_frame.grid(row=5, column=0, sticky="ew", padx=14, pady=(0, 8))
        strategy_frame.grid_columnconfigure((0, 1), weight=1)

        pm_box = ctk.CTkFrame(strategy_frame, fg_color="transparent")
        pm_box.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        pm_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            pm_box,
            text="Seleção γ",
            font=self.font_small,
            text_color=COLORS["muted"],
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.combo_pm_strategy = ctk.CTkOptionMenu(
            pm_box,
            values=["Full meet", "Maxichoice", "Maior cardinalidade"],
            variable=self.pm_strategy,
            height=30,
            font=self.font_small,
            fg_color=COLORS["primary"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_light"],
        )
        self.combo_pm_strategy.grid(row=1, column=0, sticky="ew")

        kernel_box = ctk.CTkFrame(strategy_frame, fg_color="transparent")
        kernel_box.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        kernel_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            kernel_box,
            text="Incisão σ",
            font=self.font_small,
            text_color=COLORS["muted"],
        ).grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.combo_kernel_strategy = ctk.CTkOptionMenu(
            kernel_box,
            values=["Comum se existir", "Primeira por kernel", "Incisão mínima"],
            variable=self.kernel_strategy,
            height=30,
            font=self.font_small,
            fg_color=COLORS["primary"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_light"],
        )
        self.combo_kernel_strategy.grid(row=1, column=0, sticky="ew")

        buttons1 = ctk.CTkFrame(right, fg_color="transparent")
        buttons1.grid(row=6, column=0, sticky="ew", padx=14, pady=(0, 6))
        buttons1.grid_columnconfigure((0, 1), weight=1)

        primary_button(
            buttons1,
            "Partial Meet",
            self._contract_partial_meet,
            self.font_small,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        primary_button(
            buttons1,
            "Kernel",
            self._contract_kernel,
            self.font_small,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        buttons2 = ctk.CTkFrame(right, fg_color="transparent")
        buttons2.grid(row=7, column=0, sticky="ew", padx=14, pady=(0, 6))
        buttons2.grid_columnconfigure((0, 1), weight=1)

        secondary_button(
            buttons2,
            "Ver Remainders",
            self._show_remainders,
            self.font_small,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        secondary_button(
            buttons2,
            "Ver Kernels",
            self._show_kernels,
            self.font_small,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        hint = ctk.CTkLabel(
            right,
            text="Sintaxe: neg, e, ou, imp, iff. Também podes usar ->.",
            font=self.font_small,
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
            font=self.font_section,
            text_color=COLORS["primary"],
        ).grid(row=0, column=0, sticky="w")

        secondary_button(
            log_header,
            "Limpar",
            self._clear_log,
            self.font_small,
        ).grid(row=0, column=1, sticky="e")

        self.text_log = ctk.CTkTextbox(
            log_card,
            height=170,
            font=self.font_small,
            fg_color=COLORS["log"],
            text_color=COLORS["text"],
            border_width=0,
            activate_scrollbars=True,
        )
        self.text_log.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.text_log.bind("<Key>", lambda event: "break")

        self._log("Bem-vindo.")
        self._log("Adiciona uma base, escolhe uma fórmula alvo e testa os operadores.")

    # ========================================================
    # TAB CP
    # ========================================================

    def _build_tab_cp(self, parent: ctk.CTkFrame) -> None:
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)

        # Fórmulas
        formula_card = make_card(parent)
        formula_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=8)
        formula_card.grid_columnconfigure(0, weight=1)

        section_title(formula_card, "Testes de fórmula CP", self.font_section).grid(
            row=0, column=0, sticky="w", padx=16, pady=(14, 8)
        )

        self.entry_cp_formula = ctk.CTkEntry(
            formula_card,
            placeholder_text="ex: (p imp q), (p e (q ou r)), neg p",
            height=34,
            fg_color=COLORS["input"],
            border_color=COLORS["border"],
            font=self.font_body,
        )
        self.entry_cp_formula.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        row_formula_buttons = ctk.CTkFrame(formula_card, fg_color="transparent")
        row_formula_buttons.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 14))
        row_formula_buttons.grid_columnconfigure((0, 1), weight=1)

        primary_button(
            row_formula_buttons,
            "É fórmula CP?",
            self._test_cp_formula,
            self.font_small,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 5))

        secondary_button(
            row_formula_buttons,
            "É tautologia?",
            self._test_tautology,
            self.font_small,
        ).grid(row=0, column=1, sticky="ew", padx=(5, 0))

        # Consequência
        consequence_card = make_card(parent)
        consequence_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=8)
        consequence_card.grid_columnconfigure(0, weight=1)

        section_title(
            consequence_card,
            "Consequência lógica  Γ ⊨ φ",
            self.font_section,
        ).grid(row=0, column=0, sticky="w", padx=16, pady=(14, 8))

        self.entry_cp_premises = ctk.CTkEntry(
            consequence_card,
            placeholder_text="premissas separadas por ';'  ex: p imp q; p",
            height=34,
            fg_color=COLORS["input"],
            border_color=COLORS["border"],
            font=self.font_body,
        )
        self.entry_cp_premises.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        self.entry_cp_conclusion = ctk.CTkEntry(
            consequence_card,
            placeholder_text="conclusão  ex: q",
            height=34,
            fg_color=COLORS["input"],
            border_color=COLORS["border"],
            font=self.font_body,
        )
        self.entry_cp_conclusion.grid(
            row=2, column=0, sticky="ew", padx=16, pady=(0, 8)
        )

        primary_button(
            consequence_card,
            "Testar consequência",
            self._test_consequence,
            self.font_small,
        ).grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 14))

        # Log CP
        cp_log_card = ctk.CTkFrame(
            parent,
            fg_color=COLORS["log"],
            corner_radius=14,
        )
        cp_log_card.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=0, pady=(8, 8)
        )
        cp_log_card.grid_rowconfigure(1, weight=1)
        cp_log_card.grid_columnconfigure(0, weight=1)

        cp_header = ctk.CTkFrame(cp_log_card, fg_color="transparent")
        cp_header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 4))
        cp_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            cp_header,
            text="Resultados de CP",
            font=self.font_section,
            text_color=COLORS["primary"],
        ).grid(row=0, column=0, sticky="w")

        secondary_button(
            cp_header,
            "Limpar",
            self._clear_cp_log,
            self.font_small,
        ).grid(row=0, column=1, sticky="e")

        self.text_cp_log = ctk.CTkTextbox(
            cp_log_card,
            font=self.font_small,
            fg_color=COLORS["log"],
            text_color=COLORS["text"],
            border_width=0,
            activate_scrollbars=True,
        )
        self.text_cp_log.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        self.text_cp_log.bind("<Key>", lambda event: "break")

        self._cp_log("Usa esta aba para testar fórmulas, tautologias e consequências.")

    # ========================================================
    # FORMATAÇÃO / VALIDAÇÃO
    # ========================================================

    def _format_base(self, formulas: list[str] | None = None) -> str:
        formulas = self.base.formulas if formulas is None else formulas
        return "; ".join(formulas) if formulas else "(base vazia)"

    def _format_set_of_sets(self, sets: list[list[str]]) -> str:
        if not sets:
            return "∅"

        lines = []
        for i, conjunto in enumerate(sets, start=1):
            content = "; ".join(conjunto)
            lines.append(f"{i}. {{ {content} }}")

        return "\n".join(lines)

    def _validate_formula(self, formula: str) -> bool:
        try:
            parse_formula(formula)
            return True
        except ParseError as e:
            messagebox.showerror(
                "Erro de sintaxe",
                f"Fórmula inválida:\n\n{formula}\n\n{e}",
            )
            return False

    def _warn_if_large_base(self) -> bool:
        n = len(self.base.formulas)

        if n <= MAX_SAFE_FORMULAS:
            return True

        return messagebox.askyesno(
            "Base grande",
            f"A base tem {n} fórmulas.\n\n"
            "Os algoritmos de remainders/kernels geram subconjuntos da base "
            "e podem demorar.\n\n"
            "Queres continuar?",
        )

    # ========================================================
    # SELEÇÃO
    # ========================================================
    def _ellipsis(self, text: str, max_chars: int = 48) -> str:
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 3] + "..."

    def _clear_selection(self) -> None:
        self.text_base.tag_remove("selected_line", "1.0", "end")
        self.selected_index = None
        self.btn_remove.configure(state="disabled")
        self.label_selected.configure(
            text="Nenhuma fórmula selecionada",
            text_color=COLORS["muted"],
        )

    def _on_base_click(self, event) -> None:
        index = self.text_base.index(f"@{event.x},{event.y}")
        line = int(index.split(".")[0])
        idx = line - 1

        if 0 <= idx < len(self.base.formulas):
            self.text_base.tag_remove("selected_line", "1.0", "end")
            self.text_base.tag_add("selected_line", f"{line}.0", f"{line}.end")

            self.selected_index = idx
            self.btn_remove.configure(state="normal")

            formula = self.base.formulas[idx]
            shown = self._ellipsis(f"Selecionada #{line}: {formula}", 48)

            self.label_selected.configure(
                text=shown,
                text_color=COLORS["text"],
            )
        else:
            self._clear_selection()

    # ========================================================
    # LOGS
    # ========================================================

    def _log(self, msg: str) -> None:
        for line in str(msg).splitlines():
            self.text_log.insert("end", "• " + line + "\n")
        self.text_log.see("end")

    def _cp_log(self, msg: str) -> None:
        for line in str(msg).splitlines():
            self.text_cp_log.insert("end", "• " + line + "\n")
        self.text_cp_log.see("end")

    def _clear_log(self) -> None:
        self.text_log.delete("1.0", "end")
        self._log("Log limpo.")

    def _clear_cp_log(self) -> None:
        self.text_cp_log.delete("1.0", "end")
        self._cp_log("Log limpo.")

    def _refresh_base_view(self) -> None:
        self.text_base.delete("1.0", "end")

        if self.base.is_empty():
            self.text_base.insert("end", "(base vazia)\n")
        else:
            for i, formula in enumerate(self.base.formulas, start=1):
                self.text_base.insert("end", f"{i}. {formula}\n")

        count = len(self.base.formulas)
        self.label_count.configure(
            text=f"{count} fórmula" if count == 1 else f"{count} fórmulas"
        )

        self._clear_selection()

    # ========================================================
    # CALLBACKS BASE
    # ========================================================

    def _add_formula(self) -> None:
        text = self.entry_formula.get().strip()

        if not text:
            messagebox.showwarning("Aviso", "Introduz uma fórmula.")
            return

        formulas = split_formulas(text)

        for formula in formulas:
            if not self._validate_formula(formula):
                return

        for formula in formulas:
            if formula not in self.base.formulas:
                self.base.add(formula)
                self._log(f"Adicionada: {formula}")
            else:
                self._log(f"Já existia: {formula}")

        self.entry_formula.delete(0, "end")
        self._refresh_base_view()
        self._log(f"Base atual: {self._format_base()}")

    def _remove_selected(self) -> None:
        if self.selected_index is None:
            return

        formula = self.base.formulas[self.selected_index]

        if self.base.remove_index(self.selected_index):
            self._log(f"Removida: {formula}")
            self._refresh_base_view()

    def _clear_base(self) -> None:
        if self.base.is_empty():
            return

        if not messagebox.askyesno("Limpar base", "Queres mesmo limpar a base?"):
            return

        self.base.clear()
        self._refresh_base_view()
        self._log("Base limpa.")

    def _get_target_formula(self) -> str:
        target = normalize_formula_text(self.entry_target.get())

        if not target:
            messagebox.showwarning("Aviso", "Introduz a fórmula a contrair.")
            return ""

        if not self._validate_formula(target):
            return ""

        return target

    def _show_remainders(self) -> None:
        target = self._get_target_formula()

        if not target:
            return

        if not self._warn_if_large_base():
            return

        estrategia = self._pm_strategy_value()

        try:
            rs = remainders(self.base.formulas, target)
            selected = selecionar_remainders(rs, estrategia=estrategia)
        except Exception as e:
            self._log(f"Erro ao calcular remainders: {e}")
            return

        self._log("")
        self._log(f"Remainders de A por {target}:")
        self._log(self._format_set_of_sets(rs))
        self._log(f"Estratégia γ atual: {estrategia}")
        self._log("Remainders selecionados:")
        self._log(self._format_set_of_sets(selected))

    def _show_kernels(self) -> None:
        target = self._get_target_formula()

        if not target:
            return

        if not self._warn_if_large_base():
            return

        try:
            ks = kernels(self.base.formulas, target)
        except Exception as e:
            self._log(f"Erro ao calcular kernels: {e}")
            return

        self._log(f"Kernels de A por {target}:")
        self._log(self._format_set_of_sets(ks))

    def _contract_partial_meet(self) -> None:
        target = self._get_target_formula()

        if not target:
            return

        if not self._warn_if_large_base():
            return

        estrategia = self._pm_strategy_value()
        before = list(self.base.formulas)

        try:
            self.base, steps = partial_meet_contraction_with_steps(
                self.base,
                target,
                estrategia=estrategia,
            )
        except Exception as e:
            self._log(f"Erro na contração Partial Meet: {e}")
            return

        after = list(self.base.formulas)

        self._refresh_base_view()

        self._log("")
        self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for step in steps:
            self._log(step)
        self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._log(f"Antes: {self._format_base(before)}")
        self._log(f"Depois: {self._format_base(after)}")

    def _contract_kernel(self) -> None:
        target = self._get_target_formula()

        if not target:
            return

        if not self._warn_if_large_base():
            return

        estrategia = self._kernel_strategy_value()
        before = list(self.base.formulas)

        try:
            self.base, steps = kernel_contraction_with_steps(
                self.base,
                target,
                estrategia=estrategia,
            )
        except Exception as e:
            self._log(f"Erro na contração Kernel: {e}")
            return

        after = list(self.base.formulas)

        self._refresh_base_view()

        self._log("")
        self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        for step in steps:
            self._log(step)
        self._log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._log(f"Antes: {self._format_base(before)}")
        self._log(f"Depois: {self._format_base(after)}")

    # ========================================================
    # CALLBACKS CP
    # ========================================================

    def _test_cp_formula(self) -> None:
        formula = normalize_formula_text(self.entry_cp_formula.get())

        if not formula:
            messagebox.showwarning("Aviso", "Introduz uma fórmula.")
            return

        if is_cp_formula(formula):
            self._cp_log(f"'{formula}' é uma fórmula bem formada.")
        else:
            self._cp_log(f"'{formula}' NÃO é uma fórmula bem formada.")

    def _test_tautology(self) -> None:
        formula = normalize_formula_text(self.entry_cp_formula.get())

        if not formula:
            messagebox.showwarning("Aviso", "Introduz uma fórmula.")
            return

        try:
            parsed = parse_formula(formula)
        except ParseError as e:
            self._cp_log(f"Erro de sintaxe: {e}")
            return

        if is_tautology(parsed):
            self._cp_log(f"'{formula}' é uma tautologia.")
        else:
            self._cp_log(f"'{formula}' NÃO é uma tautologia.")

    def _test_consequence(self) -> None:
        premises_text = self.entry_cp_premises.get().strip()
        conclusion = normalize_formula_text(self.entry_cp_conclusion.get())

        if not premises_text or not conclusion:
            messagebox.showwarning("Aviso", "Preenche premissas e conclusão.")
            return

        premises = split_formulas(premises_text)

        try:
            for p in premises:
                parse_formula(p)
            parse_formula(conclusion)

            result = conseqlog_strings(premises, conclusion)
        except ParseError as e:
            self._cp_log(f"Erro de sintaxe: {e}")
            return
        except Exception as e:
            self._cp_log(f"Erro: {e}")
            return

        if result:
            self._cp_log(f"{premises} ⊨ {conclusion}")
        else:
            self._cp_log(f"{premises} ⊭ {conclusion}")

    def _pm_strategy_value(self) -> str:
        mapping = {
            "Full meet": "full",
            "Maxichoice": "first",
            "Maior cardinalidade": "max_cardinality",
        }
        return mapping.get(self.pm_strategy.get(), "full")

    def _kernel_strategy_value(self) -> str:
        mapping = {
            "Comum se existir": "common_first",
            "Primeira por kernel": "first_each",
            "Incisão mínima": "min_hitting",
        }
        return mapping.get(self.kernel_strategy.get(), "common_first")


if __name__ == "__main__":
    app = BeliefApp()
    app.mainloop()
