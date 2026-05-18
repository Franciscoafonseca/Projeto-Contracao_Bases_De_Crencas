# gui/actions.py

from __future__ import annotations

from tkinter import filedialog, messagebox

from logica import (
    BeliefBase,
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

from logica.contractions.exhaustive import (
    partial_meet_all_selection_options,
    kernel_all_incision_options,
)

from .theme import COLORS, MAX_SAFE_FORMULAS
from .utils import normalize_formula_text, split_formulas
from .dialogs import choose_remainders_manual, choose_kernel_incision_manual

from storage import save_base, load_base
from export import export_operation_pdf


class AppActions:
    # ============================================================
    # HELPERS GERAIS
    # ============================================================

    def _base_for_kind(self, kind: str) -> BeliefBase:
        if kind == "pm":
            return self.pm_base

        if kind == "kernel":
            return self.kernel_base

        raise ValueError(f"Tipo de base desconhecido: {kind}")

    def _set_base_for_kind(self, kind: str, base: BeliefBase) -> None:
        if kind == "pm":
            self.pm_base = base
            return

        if kind == "kernel":
            self.kernel_base = base
            return

        raise ValueError(f"Tipo de base desconhecido: {kind}")

    def _operator_name(self, kind: str) -> str:
        if kind == "pm":
            return "Partial Meet"

        if kind == "kernel":
            return "Kernel"

        return kind

    def _format_base(self, formulas: list[str] | None = None) -> str:
        if formulas is None:
            formulas = []

        return "; ".join(formulas) if formulas else "(base vazia)"

    def _format_set_of_sets(self, sets: list[list[str]]) -> str:
        if not sets:
            return "∅"

        lines = []

        for i, conjunto in enumerate(sets, start=1):
            content = "; ".join(conjunto) if conjunto else "∅"
            lines.append(f"{i}. {{ {content} }}")

        return "\n".join(lines)

    def _format_numbered_sets(self, sets: list[list[str]], prefix: str) -> list[str]:
        if not sets:
            return [f"{prefix}: ∅"]

        lines: list[str] = []

        for i, conjunto in enumerate(sets, start=1):
            content = "; ".join(conjunto) if conjunto else "∅"
            lines.append(f"{prefix}{i} = {{ {content} }}")

        return lines

    def _ellipsis(self, text: str, max_chars: int = 58) -> str:
        if len(text) <= max_chars:
            return text

        return text[: max_chars - 3] + "..."

    # ============================================================
    # VALIDAÇÃO
    # ============================================================

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

    def _warn_if_large_base(self, base: BeliefBase) -> bool:
        n = len(base.formulas)

        if n <= MAX_SAFE_FORMULAS:
            return True

        return messagebox.askyesno(
            "Base grande",
            f"A base tem {n} fórmulas.\n\n"
            "Os algoritmos geram subconjuntos da base e podem demorar.\n\n"
            "Queres continuar?",
        )

    def _get_target_formula_from(self, entry) -> str:
        target = normalize_formula_text(entry.get())

        if not target:
            messagebox.showwarning("Aviso", "Introduz a fórmula a contrair.")
            return ""

        if not self._validate_formula(target):
            return ""

        return target

    def _get_pm_target_formula(self) -> str:
        return self._get_target_formula_from(self.entry_pm_target)

    def _get_kernel_target_formula(self) -> str:
        return self._get_target_formula_from(self.entry_kernel_target)

    # ============================================================
    # LOGS
    # ============================================================

    def _write_to_log(self, attr_name: str, msg: str) -> None:
        textbox = getattr(self, attr_name, None)

        if textbox is None:
            return

        text = str(msg)

        if text == "":
            textbox.insert("end", "\n")
            textbox.see("end")
            return

        for line in text.splitlines():
            textbox.insert("end", line + "\n")

        textbox.see("end")

    def _pm_log(self, msg: str) -> None:
        self._write_to_log("text_pm_log", msg)

    def _kernel_log(self, msg: str) -> None:
        self._write_to_log("text_kernel_log", msg)

    def _cp_log(self, msg: str) -> None:
        self._write_to_log("text_cp_log", msg)

    def _log_for_kind(self, kind: str, msg: str) -> None:
        if kind == "pm":
            self._pm_log(msg)
            return

        if kind == "kernel":
            self._kernel_log(msg)
            return

    def _clear_pm_log(self) -> None:
        self.text_pm_log.delete("1.0", "end")
        self._pm_log("Resultados limpos.")

    def _clear_kernel_log(self) -> None:
        self.text_kernel_log.delete("1.0", "end")
        self._kernel_log("Resultados limpos.")

    def _clear_cp_log(self) -> None:
        self.text_cp_log.delete("1.0", "end")
        self._cp_log("Resultados limpos.")

    # ============================================================
    # BASES DOS OPERADORES
    # ============================================================

    def _clear_operator_selection(self, kind: str) -> None:
        text_base = getattr(self, f"{kind}_text_base")
        label_selected = getattr(self, f"{kind}_label_selected")
        btn_remove = getattr(self, f"{kind}_btn_remove")

        text_base.tag_remove("selected_line", "1.0", "end")
        setattr(self, f"{kind}_selected_index", None)

        btn_remove.configure(state="disabled")
        label_selected.configure(
            text="Nenhuma fórmula selecionada",
            text_color=COLORS["muted"],
        )

    def _on_operator_base_click(self, kind: str, event) -> None:
        base = self._base_for_kind(kind)
        text_base = getattr(self, f"{kind}_text_base")
        label_selected = getattr(self, f"{kind}_label_selected")
        btn_remove = getattr(self, f"{kind}_btn_remove")

        index = text_base.index(f"@{event.x},{event.y}")
        line = int(index.split(".")[0])
        idx = line - 1

        if 0 <= idx < len(base.formulas):
            text_base.tag_remove("selected_line", "1.0", "end")
            text_base.tag_add("selected_line", f"{line}.0", f"{line}.end")

            setattr(self, f"{kind}_selected_index", idx)
            btn_remove.configure(state="normal")

            formula = base.formulas[idx]
            shown = self._ellipsis(f"Selecionada #{line}: {formula}")

            label_selected.configure(
                text=shown,
                text_color=COLORS["text"],
            )
        else:
            self._clear_operator_selection(kind)

    def _refresh_operator_base_view(self, kind: str) -> None:
        base = self._base_for_kind(kind)
        text_base = getattr(self, f"{kind}_text_base")
        label_count = getattr(self, f"{kind}_label_count")

        text_base.delete("1.0", "end")

        if base.is_empty():
            text_base.insert("end", "A base está vazia.\n")
            text_base.insert("end", "Adiciona fórmulas no campo acima.\n")
        else:
            for i, formula in enumerate(base.formulas, start=1):
                text_base.insert("end", f"{i}. {formula}\n")

        count = len(base.formulas)

        label_count.configure(
            text=f"{count} fórmula" if count == 1 else f"{count} fórmulas"
        )

        self._clear_operator_selection(kind)

    def _add_formula_to(self, kind: str) -> None:
        base = self._base_for_kind(kind)
        entry = getattr(self, f"entry_{kind}_formula")

        text = entry.get().strip()

        if not text:
            messagebox.showwarning("Aviso", "Introduz uma fórmula.")
            return

        formulas = split_formulas(text)

        for formula in formulas:
            if not self._validate_formula(formula):
                return

        added_any = False

        for formula in formulas:
            if formula not in base.formulas:
                base.add(formula)
                self._log_for_kind(
                    kind,
                    f"✓ Adicionada à base {self._operator_name(kind)}: {formula}",
                )
                added_any = True
            else:
                self._log_for_kind(
                    kind,
                    f"• Já existia na base {self._operator_name(kind)}: {formula}",
                )

        entry.delete(0, "end")
        self._refresh_operator_base_view(kind)

        if added_any:
            self._log_for_kind(kind, f"Base atual: {self._format_base(base.formulas)}")

    def _remove_selected_from(self, kind: str) -> None:
        base = self._base_for_kind(kind)
        selected_index = getattr(self, f"{kind}_selected_index")

        if selected_index is None:
            return

        if not (0 <= selected_index < len(base.formulas)):
            self._clear_operator_selection(kind)
            return

        formula = base.formulas[selected_index]

        if base.remove_index(selected_index):
            self._log_for_kind(
                kind,
                f"− Removida da base {self._operator_name(kind)}: {formula}",
            )
            self._refresh_operator_base_view(kind)

    def _clear_base_for(self, kind: str) -> None:
        base = self._base_for_kind(kind)

        if base.is_empty():
            return

        if not messagebox.askyesno(
            "Limpar base",
            f"Queres limpar a base {self._operator_name(kind)}?",
        ):
            return

        base.clear()
        self._refresh_operator_base_view(kind)
        self._log_for_kind(kind, f"Base {self._operator_name(kind)} limpa.")

    def _save_base_to_file(self, kind: str) -> None:
        base = self._base_for_kind(kind)

        if base.is_empty():
            messagebox.showwarning("Guardar base", "A base está vazia.")
            return

        operator_name = self._operator_name(kind)

        path = filedialog.asksaveasfilename(
            title=f"Guardar base {operator_name}",
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
            save_base(path, base.formulas)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível guardar a base:\n\n{e}")
            return

        self._log_for_kind(kind, f"Base guardada em: {path}")

    def _load_base_from_file(self, kind: str) -> None:
        path = filedialog.askopenfilename(
            title=f"Carregar base {self._operator_name(kind)}",
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

            new_base = BeliefBase()

            for formula in formulas:
                if formula not in new_base.formulas:
                    new_base.add(formula)

            self._set_base_for_kind(kind, new_base)

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar a base:\n\n{e}")
            return

        self._refresh_operator_base_view(kind)
        self._log_for_kind(kind, f"Base carregada de: {path}")
        self._log_for_kind(
            kind,
            f"Base atual: {self._format_base(self._base_for_kind(kind).formulas)}",
        )

    # ============================================================
    # PARTIAL MEET
    # ============================================================

    def _pm_strategy_value(self) -> str:
        mapping = {
            "Full meet": "full",
            "Maxichoice": "first",
            "Maior cardinalidade": "max_cardinality",
            "Manual": "manual",
            "Todas as seleções possíveis": "all_selections",
        }

        return mapping.get(self.pm_strategy.get(), "full")

    def _run_partial_meet_selected_mode(self) -> None:
        if self._pm_strategy_value() == "all_selections":
            self._show_all_partial_meet_options()
            return

        self._contract_partial_meet()

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

    def _show_remainders(self) -> None:
        target = self._get_pm_target_formula()

        if not target:
            return

        if not self._warn_if_large_base(self.pm_base):
            return

        estrategia = self._pm_strategy_value()

        try:
            rs = remainders(self.pm_base.formulas, target)

            if estrategia == "manual":
                selected = self._choose_remainders_manual(rs)

                if selected is None:
                    self._pm_log("Seleção manual cancelada.")
                    return
            elif estrategia == "all_selections":
                selected = []
            else:
                selected = selecionar_remainders(rs, estrategia=estrategia)

        except Exception as e:
            self._pm_log(f"Erro ao calcular remainders: {e}")
            return

        self._pm_log("")
        self._pm_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._pm_log(f"Remainders de A por α = {target}")
        self._pm_log("")

        for line in self._format_numbered_sets(rs, "R"):
            self._pm_log(line)

        self._pm_log("")
        self._pm_log(f"Estratégia atual: {self.pm_strategy.get()}")

        if estrategia != "all_selections":
            self._pm_log("Remainders selecionados:")

            for line in self._format_numbered_sets(selected, "S"):
                self._pm_log(line)
        else:
            total = (2 ** len(rs)) - 1 if rs else 0
            self._pm_log(f"Esta opção irá gerar {total} seleções possíveis.")

        self._pm_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def _contract_partial_meet(self) -> None:
        target = self._get_pm_target_formula()

        if not target:
            return

        if not self._warn_if_large_base(self.pm_base):
            return

        estrategia = self._pm_strategy_value()
        before = list(self.pm_base.formulas)

        try:
            if estrategia == "manual":
                rs = remainders(self.pm_base.formulas, target)
                selected = self._choose_remainders_manual(rs)

                if selected is None:
                    self._pm_log("Contração Partial Meet manual cancelada.")
                    return

                new_base, steps = partial_meet_contraction_manual_with_steps(
                    self.pm_base,
                    target,
                    selected,
                )
            else:
                new_base, steps = partial_meet_contraction_with_steps(
                    self.pm_base,
                    target,
                    estrategia=estrategia,
                )

            self.pm_base = new_base

        except Exception as e:
            self._pm_log(f"Erro na contração Partial Meet: {e}")
            return

        after = list(self.pm_base.formulas)

        self._refresh_operator_base_view("pm")

        self._pm_log("")
        self._pm_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._pm_log("Resultado da contração Partial Meet")
        self._pm_log("")

        for step in steps:
            self._pm_log(step)

        self._pm_log("")
        self._pm_log(f"Antes:  {self._format_base(before)}")
        self._pm_log(f"Depois: {self._format_base(after)}")
        self._pm_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.last_operation = {
            "operator": "Partial Meet",
            "mode": "single",
            "strategy": self.pm_strategy.get(),
            "target": target,
            "before": before,
            "after": after,
            "steps": steps,
        }

    def _show_all_partial_meet_options(self) -> None:
        target = self._get_pm_target_formula()

        if not target:
            return

        if not self._warn_if_large_base(self.pm_base):
            return

        before = list(self.pm_base.formulas)

        try:
            rems, options, steps = partial_meet_all_selection_options(
                self.pm_base,
                target,
                max_options=512,
            )
        except Exception as e:
            self._pm_log(f"Erro ao calcular todas as seleções Partial Meet: {e}")
            return

        display_steps: list[str] = []
        display_steps.extend(steps)
        display_steps.append("")
        display_steps.append("Remainders encontrados:")

        for line in self._format_numbered_sets(rems, "R"):
            display_steps.append(line)

        display_steps.append("")
        display_steps.append("Seleções possíveis:")

        if not options:
            display_steps.append("Nenhuma seleção gerada.")
        else:
            for option in options:
                selected = ", ".join(f"R{i}" for i in option.selected_indices)

                removed = (
                    "; ".join(option.removed_formulas)
                    if option.removed_formulas
                    else "(nada)"
                )

                result = (
                    "; ".join(option.result_base)
                    if option.result_base
                    else "(base vazia)"
                )

                display_steps.append(f"Opção {option.option_id}: γ = {{ {selected} }}")
                display_steps.append(f"  Fórmulas removidas: {removed}")
                display_steps.append(f"  Base resultante: {result}")

        self._pm_log("")
        self._pm_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._pm_log("Exploração de todas as seleções Partial Meet")
        self._pm_log("")

        for step in display_steps:
            self._pm_log(step)

        self._pm_log("")
        self._pm_log("A base não foi alterada.")
        self._pm_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.last_operation = {
            "operator": "Partial Meet",
            "mode": "all_selections",
            "strategy": "Todas as seleções possíveis",
            "target": target,
            "before": before,
            "after": before,
            "steps": display_steps,
        }

    # ============================================================
    # KERNEL
    # ============================================================

    def _kernel_strategy_value(self) -> str:
        mapping = {
            "Comum se existir": "common_first",
            "Primeira por kernel": "first_each",
            "Incisão mínima": "min_hitting",
            "Manual": "manual",
            "Todas as incisões válidas": "all_incisions",
            "Todas as incisões mínimas": "all_minimal_incisions",
        }

        return mapping.get(self.kernel_strategy.get(), "common_first")

    def _run_kernel_selected_mode(self) -> None:
        estrategia = self._kernel_strategy_value()

        if estrategia == "all_incisions":
            self._show_all_kernel_incision_options(minimal_only=False)
            return

        if estrategia == "all_minimal_incisions":
            self._show_all_kernel_incision_options(minimal_only=True)
            return

        self._contract_kernel()

    def _choose_kernel_incision_manual(
        self,
        kerns: list[list[str]],
    ) -> list[str] | None:
        return choose_kernel_incision_manual(
            self,
            kerns,
            self.kernel_base.formulas,
            self.font_section,
            self.font_small,
        )

    def _show_kernels(self) -> None:
        target = self._get_kernel_target_formula()

        if not target:
            return

        if not self._warn_if_large_base(self.kernel_base):
            return

        estrategia = self._kernel_strategy_value()

        try:
            ks = kernels(self.kernel_base.formulas, target)
            selected = None

            if estrategia == "manual":
                selected = self._choose_kernel_incision_manual(ks)

                if selected is None:
                    self._kernel_log("Incisão manual cancelada.")
                    return

        except Exception as e:
            self._kernel_log(f"Erro ao calcular kernels: {e}")
            return

        self._kernel_log("")
        self._kernel_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._kernel_log(f"Kernels de A por α = {target}")
        self._kernel_log("")

        for line in self._format_numbered_sets(ks, "K"):
            self._kernel_log(line)

        self._kernel_log("")
        self._kernel_log(f"Estratégia atual: {self.kernel_strategy.get()}")

        if estrategia == "manual":
            self._kernel_log(f"Fórmulas escolhidas: {self._format_base(selected)}")

        self._kernel_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def _contract_kernel(self) -> None:
        target = self._get_kernel_target_formula()

        if not target:
            return

        if not self._warn_if_large_base(self.kernel_base):
            return

        estrategia = self._kernel_strategy_value()
        before = list(self.kernel_base.formulas)

        try:
            if estrategia == "manual":
                ks = kernels(self.kernel_base.formulas, target)
                selected = self._choose_kernel_incision_manual(ks)

                if selected is None:
                    self._kernel_log("Contração Kernel manual cancelada.")
                    return

                new_base, steps = kernel_contraction_manual_with_steps(
                    self.kernel_base,
                    target,
                    selected,
                )
            else:
                new_base, steps = kernel_contraction_with_steps(
                    self.kernel_base,
                    target,
                    estrategia=estrategia,
                )

            self.kernel_base = new_base

        except Exception as e:
            self._kernel_log(f"Erro na contração Kernel: {e}")
            return

        after = list(self.kernel_base.formulas)

        self._refresh_operator_base_view("kernel")

        self._kernel_log("")
        self._kernel_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._kernel_log("Resultado da contração Kernel")
        self._kernel_log("")

        for step in steps:
            self._kernel_log(step)

        self._kernel_log("")
        self._kernel_log(f"Antes:  {self._format_base(before)}")
        self._kernel_log(f"Depois: {self._format_base(after)}")
        self._kernel_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.last_operation = {
            "operator": "Kernel",
            "mode": "single",
            "strategy": self.kernel_strategy.get(),
            "target": target,
            "before": before,
            "after": after,
            "steps": steps,
        }

    def _show_all_kernel_incision_options(self, minimal_only: bool = False) -> None:
        target = self._get_kernel_target_formula()

        if not target:
            return

        if not self._warn_if_large_base(self.kernel_base):
            return

        before = list(self.kernel_base.formulas)

        try:
            kerns, options, steps = kernel_all_incision_options(
                self.kernel_base,
                target,
                minimal_only=minimal_only,
                max_options=512,
            )
        except Exception as e:
            self._kernel_log(f"Erro ao calcular incisões Kernel: {e}")
            return

        mode_title = (
            "Todas as incisões mínimas" if minimal_only else "Todas as incisões válidas"
        )

        display_steps: list[str] = []
        display_steps.extend(steps)
        display_steps.append("")
        display_steps.append("Kernels encontrados:")

        for line in self._format_numbered_sets(kerns, "K"):
            display_steps.append(line)

        display_steps.append("")
        display_steps.append(mode_title + ":")

        if not options:
            display_steps.append("Nenhuma incisão encontrada.")
        else:
            for option in options:
                incision = "; ".join(option.incision) if option.incision else "(nada)"

                removed = (
                    "; ".join(option.removed_formulas)
                    if option.removed_formulas
                    else "(nada)"
                )

                result = (
                    "; ".join(option.result_base)
                    if option.result_base
                    else "(base vazia)"
                )

                minimal = "sim" if option.is_minimal else "não"

                display_steps.append(f"Opção {option.option_id}: σ = {{ {incision} }}")
                display_steps.append(f"  Incisão minimal: {minimal}")
                display_steps.append(f"  Fórmulas removidas: {removed}")
                display_steps.append(f"  Base resultante: {result}")

        self._kernel_log("")
        self._kernel_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        self._kernel_log(f"Exploração Kernel — {mode_title}")
        self._kernel_log("")

        for step in display_steps:
            self._kernel_log(step)

        self._kernel_log("")
        self._kernel_log("A base não foi alterada.")
        self._kernel_log("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

        self.last_operation = {
            "operator": "Kernel",
            "mode": "all_minimal_incisions" if minimal_only else "all_incisions",
            "strategy": mode_title,
            "target": target,
            "before": before,
            "after": before,
            "steps": display_steps,
        }

    # ============================================================
    # CÁLCULO PROPOSICIONAL
    # ============================================================

    def _test_cp_formula(self) -> None:
        formula = normalize_formula_text(self.entry_cp_formula.get())

        if not formula:
            messagebox.showwarning("Aviso", "Introduz uma fórmula.")
            return

        if is_cp_formula(formula):
            self._cp_log(f"✓ '{formula}' é uma fórmula bem formada.")
        else:
            self._cp_log(f"✗ '{formula}' não é uma fórmula bem formada.")

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
            self._cp_log(f"✓ '{formula}' é uma tautologia.")
        else:
            self._cp_log(f"✗ '{formula}' não é uma tautologia.")

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
            self._cp_log(f"✓ {premises} ⊨ {conclusion}")
        else:
            self._cp_log(f"✗ {premises} ⊭ {conclusion}")

    # ============================================================
    # EXPORTAÇÃO
    # ============================================================

    def _export_last_operation_pdf(self, expected_operator: str | None = None) -> None:
        if not self.last_operation:
            messagebox.showwarning(
                "Exportar PDF",
                "Ainda não existe nenhuma operação para exportar.",
            )
            return

        operator = self.last_operation.get("operator", "operação")

        if expected_operator is not None and operator != expected_operator:
            messagebox.showwarning(
                "Exportar PDF",
                f"O último relatório é de {operator}, não de {expected_operator}.",
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

        if operator == "Partial Meet":
            self._pm_log(f"PDF exportado para: {path}")
        elif operator == "Kernel":
            self._kernel_log(f"PDF exportado para: {path}")
