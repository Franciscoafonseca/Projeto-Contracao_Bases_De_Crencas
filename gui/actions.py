from tkinter import messagebox

from logica import (
    partial_meet_contraction_with_steps,
    partial_meet_contraction_manual_with_steps,
    kernel_contraction_with_steps,
    kernel_contraction_manual_with_steps,
    remainders,
    kernels,
    ParseError,
    parse_formula,
    is_cp_formula,
    is_tautology,
    conseqlog_strings,
    selecionar_remainders,
)

from .theme import COLORS, MAX_SAFE_FORMULAS
from .utils import normalize_formula_text, split_formulas
from .dialogs import choose_remainders_manual, choose_kernel_incision_manual
from tkinter import filedialog
from storage import save_base, load_base
from export import export_operation_pdf


class AppActions:
    def _format_base(self, formulas: list[str] | None = None) -> str:
        formulas = self.base.formulas if formulas is None else formulas
        return "; ".join(formulas) if formulas else "(base vazia)"

    def _format_set_of_sets(self, sets: list[list[str]]) -> str:
        if not sets:
            return "∅"

        lines = []
        for i, conjunto in enumerate(sets, start=1):
            content = "; ".join(conjunto) if conjunto else "∅"
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

            if estrategia == "manual":
                selected = self._choose_remainders_manual(rs)
                if selected is None:
                    self._log("Seleção manual cancelada.")
                    return
            else:
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

        estrategia = self._kernel_strategy_value()

        try:
            ks = kernels(self.base.formulas, target)

            selected = None
            if estrategia == "manual":
                selected = self._choose_kernel_incision_manual(ks)
                if selected is None:
                    self._log("Incisão manual cancelada.")
                    return

        except Exception as e:
            self._log(f"Erro ao calcular kernels: {e}")
            return

        self._log("")
        self._log(f"Kernels de A por {target}:")
        self._log(self._format_set_of_sets(ks))

        if estrategia == "manual":
            self._log("Fórmulas escolhidas para remover:")
            self._log(self._format_base(selected))

    def _choose_remainders_manual(
        self,
        rems: list[list[str]],
    ) -> list[list[str]] | None:
        return choose_remainders_manual(
            self,
            rems,
            self.font_section,
            self.font_small,
        )

    def _choose_kernel_incision_manual(
        self,
        kerns: list[list[str]],
    ) -> list[str] | None:
        return choose_kernel_incision_manual(
            self,
            kerns,
            self.base.formulas,
            self.font_section,
            self.font_small,
        )

    def _contract_partial_meet(self) -> None:
        target = self._get_target_formula()

        if not target:
            return

        if not self._warn_if_large_base():
            return

        estrategia = self._pm_strategy_value()
        before = list(self.base.formulas)

        try:
            if estrategia == "manual":
                rs = remainders(self.base.formulas, target)

                selected = self._choose_remainders_manual(rs)
                if selected is None:
                    self._log("Contração Partial Meet manual cancelada.")
                    return

                self.base, steps = partial_meet_contraction_manual_with_steps(
                    self.base,
                    target,
                    selected,
                )
            else:
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
        self.last_operation = {
            "operator": "Partial Meet",
            "strategy": self.pm_strategy.get(),
            "target": target,
            "before": before,
            "after": after,
            "steps": steps,
        }

    def _contract_kernel(self) -> None:
        target = self._get_target_formula()

        if not target:
            return

        if not self._warn_if_large_base():
            return

        estrategia = self._kernel_strategy_value()
        before = list(self.base.formulas)

        try:
            if estrategia == "manual":
                ks = kernels(self.base.formulas, target)

                selected = self._choose_kernel_incision_manual(ks)
                if selected is None:
                    self._log("Contração Kernel manual cancelada.")
                    return

                self.base, steps = kernel_contraction_manual_with_steps(
                    self.base,
                    target,
                    selected,
                )
            else:
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
        self.last_operation = {
            "operator": "Kernel",
            "strategy": self.kernel_strategy.get(),
            "target": target,
            "before": before,
            "after": after,
            "steps": steps,
        }

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
            "Manual": "manual",
        }
        return mapping.get(self.pm_strategy.get(), "full")

    def _kernel_strategy_value(self) -> str:
        mapping = {
            "Comum se existir": "common_first",
            "Primeira por kernel": "first_each",
            "Incisão mínima": "min_hitting",
            "Manual": "manual",
        }
        return mapping.get(self.kernel_strategy.get(), "common_first")

    def _save_base_to_file(self) -> None:
        if self.base.is_empty():
            messagebox.showwarning("Guardar base", "A base está vazia.")
            return

        path = filedialog.asksaveasfilename(
            title="Guardar base de crenças",
            defaultextension=".json",
            filetypes=[
                ("Base de crenças JSON", "*.json"),
                ("Base de crenças TXT", "*.txt"),
                ("Todos os ficheiros", "*.*"),
            ],
        )

        if not path:
            return

        try:
            save_base(path, self.base.formulas)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível guardar a base:\n\n{e}")
            return

        self._log(f"Base guardada em: {path}")

    def _load_base_from_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Carregar base de crenças",
            filetypes=[
                ("Bases de crenças", "*.json *.txt"),
                ("Base de crenças JSON", "*.json"),
                ("Base de crenças TXT", "*.txt"),
                ("Todos os ficheiros", "*.*"),
            ],
        )

        if not path:
            return

        try:
            formulas = load_base(path)

            for formula in formulas:
                if not self._validate_formula(formula):
                    return

            self.base.clear()

            for formula in formulas:
                if formula not in self.base.formulas:
                    self.base.add(formula)

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a base:\n\n{e}")
            return

        self._refresh_base_view()
        self._log(f"Base carregada de: {path}")
        self._log(f"Base atual: {self._format_base()}")

    def _export_last_operation_pdf(self) -> None:
        if not self.last_operation:
            messagebox.showwarning(
                "Exportar PDF",
                "Ainda não existe nenhuma operação para exportar.",
            )
            return

        path = filedialog.asksaveasfilename(
            title="Exportar relatório PDF",
            defaultextension=".pdf",
            filetypes=[
                ("PDF", "*.pdf"),
                ("Todos os ficheiros", "*.*"),
            ],
        )

        if not path:
            return

        try:
            export_operation_pdf(path, self.last_operation)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível exportar o PDF:\n\n{e}")
            return

        self._log(f"Relatório PDF exportado para: {path}")
