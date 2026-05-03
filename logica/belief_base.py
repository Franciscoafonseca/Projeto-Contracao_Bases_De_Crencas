# logica/belief_base.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class BeliefBase:
    """
    Representa uma base de crenças finita.

    A base guarda apenas crenças explícitas, isto é,
    as fórmulas que o utilizador introduziu diretamente.
    """

    formulas: List[str] = field(default_factory=list)

    def add(self, formula: str) -> None:
        formula = formula.strip()
        if formula and formula not in self.formulas:
            self.formulas.append(formula)

    def remove(self, formula: str) -> bool:
        formula = formula.strip()
        if formula in self.formulas:
            self.formulas.remove(formula)
            return True
        return False

    def remove_index(self, index: int) -> bool:
        if 0 <= index < len(self.formulas):
            del self.formulas[index]
            return True
        return False

    def clear(self) -> None:
        self.formulas.clear()

    def is_empty(self) -> bool:
        return len(self.formulas) == 0

    def copy(self) -> "BeliefBase":
        return BeliefBase(formulas=list(self.formulas))

    def as_string(self) -> str:
        return "; ".join(self.formulas)
