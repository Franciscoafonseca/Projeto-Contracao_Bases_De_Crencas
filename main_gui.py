# main_gui.py
#
# Aplicação gráfica com dois separadores:
#   1. "Base de Crenças"
#   2. "Cálculo Proposicional"
#
# Estilo claro com azul, branco e amarelo.
# - Títulos mais discretos.
# - Remoção de fórmulas por clique na linha.
# - Fonte moderna (Segoe UI).
# - Log com aspeto de "centro de informações".
#
# Compatível com PyInstaller (ProjetoCrencas.exe).

import customtkinter as ctk
from tkinter import messagebox
from pathlib import Path
import sys

from logica import (
    BeliefBase,
    partial_meet_contraction,
    kernel_contraction,
    ParseError,
    parse_formula,
    is_cp_formula,
    is_tautology,
    conseqlog_strings,
)

# ---------- CONFIGURAÇÃO GLOBAL DO TEMA ----------

ctk.set_appearance_mode("light")  # agora tema claro
ctk.set_default_color_theme("blue")  # base azul

# Paleta de cores clara
COLORS = {
    "bg_main": "#e5e7eb",  # cinzento muito claro (fundo da janela)
    "card": "#ffffff",  # branco (painéis)
    "card_alt": "#f3f4f6",  # cinzento claro (painel alternativo)
    "primary": "#1d4ed8",  # azul forte
    "primary_light": "#2563eb",  # azul ligeiramente mais claro
    "accent_yellow": "#eab308",  # amarelo
    "text_main": "#111827",  # quase preto
    "text_muted": "#6b7280",  # cinzento para texto secundário
    "border": "#d1d5db",  # borda clara
    "highlight": "#dbeafe",  # azul clarinho para linha selecionada
    "log_bg": "#eff6ff",  # fundo da área de log
}


def resource_path(relative: str) -> str:
    """
    Devolve o caminho correto para ficheiros tanto em modo normal
    como dentro do .exe gerado pelo PyInstaller.
    """
    base_path = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str(base_path / relative)


# ---------- Helpers de estilo ----------


def make_card(parent, alt: bool = False) -> ctk.CTkFrame:
    """Cria um painel tipo 'card'."""
    return ctk.CTkFrame(
        parent,
        corner_radius=14,
        fg_color=COLORS["card_alt" if alt else "card"],
        border_width=1,
        border_color=COLORS["border"],
    )


def title_label(parent, text: str, font) -> ctk.CTkLabel:
    """Título da aplicação (mais discreto)."""
    return ctk.CTkLabel(
        parent,
        text=text,
        font=font,
        text_color=COLORS["text_main"],
    )


def section_label(parent, text: str, font) -> ctk.CTkFrame:
    """Título de secção com barra amarela à esquerda."""
    frame = ctk.CTkFrame(
        parent,
        fg_color="transparent",
    )
    bar = ctk.CTkFrame(
        frame,
        fg_color=COLORS["accent_yellow"],
        width=3,
        corner_radius=999,
    )
    bar.pack(side="left", fill="y", padx=(0, 6), pady=2)
    label = ctk.CTkLabel(
        frame,
        text=text,
        font=font,
        text_color=COLORS["text_main"],
    )
    label.pack(side="left")
    return frame


def primary_button(parent, text: str, command, font) -> ctk.CTkButton:
    """Botão principal azul."""
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=32,
        corner_radius=10,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_light"],
        font=font,
        text_color="white",
    )


def secondary_button(parent, text: str, command, font) -> ctk.CTkButton:
    """Botão secundário contornado."""
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=32,
        corner_radius=10,
        fg_color="transparent",
        border_width=1,
        border_color=COLORS["primary"],
        text_color=COLORS["primary"],
        hover_color="#e0f2fe",
        font=font,
    )


# ---------- Classe principal ----------


class BeliefApp(ctk.CTk):
    """Janela principal da aplicação."""

    def __init__(self):
        super().__init__()

        # Ícone da janela
        try:
            icon_path = resource_path("favicon.ico")
            self.iconbitmap(icon_path)
        except Exception as e:
            print("Não foi possível carregar o ícone:", e)

        # Janela
        self.title("Projeto Crenças – Operadores de Contração em Bases de Crenças")
        # Janela fixa (sem resize)
        W, H = 1080, 740
        self.geometry(f"{W}x{H}")
        self.minsize(W, H)
        self.maxsize(W, H)
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_main"])

        # -----------Configurar TIPO DE LETRAS
        # Fontes modernas (Segoe UI)
        self.font_title = ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        self.font_section = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.font_body = ctk.CTkFont(family="Segoe UI", size=11)
        self.font_mono = ctk.CTkFont(family="Cascadia Code", size=11)

        # Base de crenças
        self.base = BeliefBase()
        self.selected_index: int | None = None  # índice da fórmula selecionada

        self._build_ui()
        self._refresh_base_view()

    # ---------- Construção da UI ----------

    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=14, pady=(8, 0))
        header.grid_columnconfigure(0, weight=1)

        title = title_label(header, "Projeto Crenças", self.font_title)
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Operadores de Contração em Bases de Crenças",
            font=self.font_body,
            text_color=COLORS["text_muted"],
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 4))

        sep = ctk.CTkFrame(header, fg_color=COLORS["accent_yellow"], height=2)
        sep.grid(row=2, column=0, sticky="ew", pady=(4, 0))

        # Tabs
        tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_main"],
            segmented_button_fg_color=COLORS["card"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_light"],
            segmented_button_unselected_color=COLORS["card_alt"],
            segmented_button_unselected_hover_color="#e5e7eb",
            text_color=COLORS["text_main"],
        )
        tabview.grid(row=1, column=0, sticky="nsew", padx=14, pady=10)

        tab_base = tabview.add("Base de Crenças")
        tab_cp = tabview.add("Cálculo Proposicional")

        self._build_tab_base(tab_base)
        self._build_tab_cp(tab_cp)

    # ---------- Tab 1: Base de Crenças ----------

    def _build_tab_base(self, parent: ctk.CTkFrame) -> None:
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=2)
        parent.grid_columnconfigure(1, weight=1)

        # Painel da base
        left_card = make_card(parent)
        left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        left_card.grid_rowconfigure(1, weight=1)
        left_card.grid_columnconfigure(0, weight=1)

        section_label(left_card, "Base de Crenças", self.font_section).grid(
            row=0, column=0, sticky="w", padx=15, pady=(10, 4)
        )

        # Caixa com as fórmulas
        self.text_base = ctk.CTkTextbox(
            left_card,
            height=400,
            activate_scrollbars=True,
            font=self.font_mono,
            fg_color="#f9fafb",
            text_color=COLORS["text_main"],
            border_width=0,
        )
        self.text_base.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 8))

        # Tag para destacar linha selecionada
        self.text_base.tag_config("selected_line", background=COLORS["highlight"])

        # Clique numa linha seleciona a fórmula
        self.text_base.bind("<ButtonRelease-1>", self._on_base_click)

        # Barra inferior com botão remover (agora dependente da seleção)
        bottom_frame = ctk.CTkFrame(left_card, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.label_selected = ctk.CTkLabel(
            bottom_frame,
            text="Nenhuma fórmula selecionada",
            font=self.font_body,
            text_color=COLORS["text_muted"],
        )
        self.label_selected.grid(row=0, column=0, sticky="w")

        self.btn_remove = secondary_button(
            bottom_frame,
            "Remover seleção",
            self._remove_selected,
            self.font_body,
        )
        self.btn_remove.grid(row=0, column=1, sticky="e")
        self.btn_remove.configure(state="disabled")  # começa desativado

        # Painel direito (comandos)
        right_card = make_card(parent, alt=True)
        right_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)
        right_card.grid_columnconfigure(0, weight=1)
        right_card.grid_rowconfigure(7, weight=1)

        section_label(right_card, "Nova fórmula", self.font_section).grid(
            row=0, column=0, sticky="w", padx=15, pady=(10, 4)
        )

        self.entry_formula = ctk.CTkEntry(
            right_card,
            placeholder_text="ex: p -> q",
            fg_color="#f9fafb",
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_main"],
            font=self.font_body,
        )
        self.entry_formula.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 6))

        primary_button(
            right_card,
            "Adicionar à base",
            self._add_formula,
            self.font_body,
        ).grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))

        section_label(right_card, "Operadores de contração", self.font_section).grid(
            row=3, column=0, sticky="w", padx=15, pady=(4, 4)
        )

        self.entry_target = ctk.CTkEntry(
            right_card,
            placeholder_text="fórmula a contrair (ex: p)",
            fg_color="#f9fafb",
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_main"],
            font=self.font_body,
        )
        self.entry_target.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 6))

        btn_row = ctk.CTkFrame(right_card, fg_color="transparent")
        btn_row.grid(row=5, column=0, sticky="ew", padx=15, pady=(0, 8))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        primary_button(
            btn_row,
            "Contração Partial Meet",
            self._contract_partial_meet,
            self.font_body,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        primary_button(
            btn_row,
            "Contração Kernel",
            self._contract_kernel,
            self.font_body,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Centro de informações (log)
        info_card = ctk.CTkFrame(
            right_card,
            fg_color=COLORS["log_bg"],
            corner_radius=10,
            border_width=0,
        )
        info_card.grid(row=6, column=0, sticky="nsew", padx=15, pady=(4, 10))
        info_card.grid_rowconfigure(1, weight=1)
        info_card.grid_columnconfigure(0, weight=1)

        header_log = ctk.CTkLabel(
            info_card,
            text="Centro de Informações",
            font=self.font_section,
            text_color=COLORS["primary"],
        )
        header_log.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

        self.text_log = ctk.CTkTextbox(
            info_card,
            height=200,
            activate_scrollbars=True,
            font=self.font_body,
            fg_color=COLORS["log_bg"],
            text_color=COLORS["text_main"],
            border_width=0,
        )
        self.text_log.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))

        self._log("Bem-vindo ao sistema de bases de crenças.")
        self._log("Use esta aba para adicionar fórmulas e aplicar contrações.")

    # ---------- Tab 2: Cálculo Proposicional ----------

    def _build_tab_cp(self, parent: ctk.CTkFrame) -> None:
        # parent.grid_rowconfigure(0, weight=1)
        # parent.grid_columnconfigure(0, weight=1)

        # card = make_card(parent)
        # card.grid(row=0, column=0, sticky="nsew", padx=0, pady=5)
        # card.grid_columnconfigure(0, weight=1)
        # card.grid_rowconfigure(7, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # ✅ Scroll container
        scroll = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        scroll.grid_columnconfigure(0, weight=1)

        # ✅ O teu card agora vai dentro do scroll
        card = make_card(scroll)
        card.grid(row=0, column=0, sticky="nsew", padx=0, pady=5)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(7, weight=1)

        section_label(card, "Testes de fórmula CP", self.font_section).grid(
            row=0, column=0, sticky="w", padx=15, pady=(10, 4)
        )

        self.entry_cp_formula = ctk.CTkEntry(
            card,
            placeholder_text="ex: (p imp q), (p e (q ou r)), neg p",
            fg_color="#f9fafb",
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_main"],
            font=self.font_body,
        )
        self.entry_cp_formula.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 6))

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 8))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        primary_button(
            btn_row,
            "É fórmula CP?",
            self._test_cp_formula,
            self.font_body,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        secondary_button(
            btn_row,
            "É tautologia?",
            self._test_tautology,
            self.font_body,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        section_label(
            card, "Teste de consequência lógica  Γ ⊨ φ", self.font_section
        ).grid(row=3, column=0, sticky="w", padx=15, pady=(4, 4))

        self.entry_cp_premises = ctk.CTkEntry(
            card,
            placeholder_text="premissas separadas por ';'  ex:  p imp q; p",
            fg_color="#f9fafb",
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_main"],
            font=self.font_body,
        )
        self.entry_cp_premises.grid(row=4, column=0, sticky="ew", padx=15, pady=(0, 6))

        self.entry_cp_conclusion = ctk.CTkEntry(
            card,
            placeholder_text="conclusão  ex:  q",
            fg_color="#f9fafb",
            border_color=COLORS["border"],
            border_width=1,
            text_color=COLORS["text_main"],
            font=self.font_body,
        )
        self.entry_cp_conclusion.grid(
            row=5, column=0, sticky="ew", padx=15, pady=(0, 6)
        )

        primary_button(
            card,
            "Testar consequência  (Γ ⊨ φ)",
            self._test_consequence,
            self.font_body,
        ).grid(row=6, column=0, sticky="ew", padx=15, pady=(0, 8))

        # Log CP também estilizado como centro de informação
        cp_info = ctk.CTkFrame(
            card,
            fg_color=COLORS["log_bg"],
            corner_radius=10,
            border_width=0,
        )
        cp_info.grid(row=7, column=0, sticky="nsew", padx=15, pady=(0, 10))
        cp_info.grid_rowconfigure(1, weight=1)
        cp_info.grid_columnconfigure(0, weight=1)

        header_cp_log = ctk.CTkLabel(
            cp_info,
            text="Resultados de CP",
            font=self.font_section,
            text_color=COLORS["primary"],
        )
        header_cp_log.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 2))

        self.text_cp_log = ctk.CTkTextbox(
            cp_info,
            height=150,
            activate_scrollbars=True,
            font=self.font_body,
            fg_color=COLORS["log_bg"],
            text_color=COLORS["text_main"],
            border_width=0,
        )
        self.text_cp_log.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 8))

        self._cp_log(
            "Use esta aba para testar fórmulas de CP, tautologias e consequências lógicas."
        )

    # ---------- Lógica de seleção na base ----------

    def _clear_selection(self) -> None:
        """Limpa destaque e desativa botão remover."""
        self.text_base.tag_remove("selected_line", "1.0", "end")
        self.selected_index = None
        self.btn_remove.configure(state="disabled")
        self.label_selected.configure(
            text="Nenhuma fórmula selecionada",
            text_color=COLORS["text_muted"],
        )

    def _on_base_click(self, event) -> None:
        """
        Quando o utilizador clica na base de crenças, selecionamos a linha
        correspondente (se existir uma fórmula nessa linha).
        """
        # índice Tk: linha.coluna (ex: '3.5')
        index = self.text_base.index(f"@{event.x},{event.y}")
        line_str = index.split(".")[0]
        line = int(line_str)
        idx = line - 1  # 0-based

        if 0 <= idx < len(self.base.formulas):
            # limpar seleção anterior
            self.text_base.tag_remove("selected_line", "1.0", "end")
            # aplicar destaque na linha clicada
            self.text_base.tag_add(
                "selected_line",
                f"{line}.0",
                f"{line}.end",
            )
            self.selected_index = idx
            self.btn_remove.configure(state="normal")
            self.label_selected.configure(
                text=f"Selecionada fórmula #{line}",
                text_color=COLORS["text_main"],
            )
        else:
            # clicou numa zona vazia
            self._clear_selection()

    # ---------- Logs / refresh ----------

    def _log(self, msg: str) -> None:
        self.text_log.insert("end", "• " + msg + "\n")
        self.text_log.see("end")

    def _cp_log(self, msg: str) -> None:
        self.text_cp_log.insert("end", "• " + msg + "\n")
        self.text_cp_log.see("end")

    def _refresh_base_view(self) -> None:
        """Atualiza a lista de fórmulas na base."""
        self.text_base.configure(state="normal")
        self.text_base.delete("1.0", "end")
        if self.base.is_empty():
            self.text_base.insert("end", "(base vazia)\n")
        else:
            for i, f in enumerate(self.base.formulas, start=1):
                self.text_base.insert("end", f"{i}. {f}\n")
        self.text_base.configure(state="disabled")
        self._clear_selection()

    # ---------- Callbacks Tab Base ----------

    def _add_formula(self) -> None:
        formula = self.entry_formula.get().strip()
        if not formula:
            messagebox.showwarning("Aviso", "Introduza uma fórmula.")
            return
        self.base.add(formula)
        self.entry_formula.delete(0, "end")
        self._refresh_base_view()
        self._log(f"Adicionada fórmula: {formula}")

    def _remove_selected(self) -> None:
        """Remove a fórmula atualmente selecionada (se existir)."""
        if self.selected_index is None:
            return
        if self.base.remove_index(self.selected_index):
            self._log(f"Removida fórmula #{self.selected_index + 1}")
            self._refresh_base_view()
        else:
            messagebox.showwarning("Aviso", "Não foi possível remover a fórmula.")
            self._refresh_base_view()

    def _get_target_formula(self) -> str:
        alvo = self.entry_target.get().strip()
        if not alvo:
            messagebox.showwarning("Aviso", "Introduza a fórmula a contrair.")
            return ""
        return alvo

    def _contract_partial_meet(self) -> None:
        alvo = self._get_target_formula()
        if not alvo:
            return
        self.base = partial_meet_contraction(self.base, alvo)
        self._refresh_base_view()
        self._log(f"Contração Partial Meet aplicada a: {alvo}")

    def _contract_kernel(self) -> None:
        alvo = self._get_target_formula()
        if not alvo:
            return
        self.base = kernel_contraction(self.base, alvo)
        self._refresh_base_view()
        self._log(f"Contração Kernel aplicada a: {alvo}")

    # ---------- Callbacks Tab CP ----------

    def _test_cp_formula(self) -> None:
        s = self.entry_cp_formula.get().strip()
        if not s:
            messagebox.showwarning("Aviso", "Introduza uma fórmula CP.")
            return
        if is_cp_formula(s):
            self._cp_log(f"'{s}' é uma fórmula bem formada de CP.")
        else:
            self._cp_log(f"'{s}' NÃO é uma fórmula bem formada de CP.")

    def _test_tautology(self) -> None:
        s = self.entry_cp_formula.get().strip()
        if not s:
            messagebox.showwarning("Aviso", "Introduza uma fórmula CP.")
            return
        try:
            f = parse_formula(s)
        except ParseError as e:
            self._cp_log(f"Erro de sintaxe em '{s}': {e}")
            return
        if is_tautology(f):
            self._cp_log(f"'{s}' é uma tautologia.")
        else:
            self._cp_log(f"'{s}' NÃO é uma tautologia.")

    def _test_consequence(self) -> None:
        prem_str = self.entry_cp_premises.get().strip()
        concl_str = self.entry_cp_conclusion.get().strip()

        if not prem_str or not concl_str:
            messagebox.showwarning("Aviso", "Preencha premissas e conclusão.")
            return

        premises_list = [p.strip() for p in prem_str.split(";") if p.strip()]
        try:
            res = conseqlog_strings(premises_list, concl_str)
        except ParseError as e:
            self._cp_log(f"Erro de sintaxe: {e}")
            return

        if res:
            self._cp_log(f"{premises_list} ⊨ {concl_str}")
        else:
            self._cp_log(f"{premises_list} ⊭ {concl_str}")


if __name__ == "__main__":
    app = BeliefApp()
    app.mainloop()
