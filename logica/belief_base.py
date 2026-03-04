# logica/belief_base.py
#
# Define a estrutura de dados que representa uma BASE DE CRENÇAS.
# Nesta base guardamos fórmulas como strings (ex: "p", "p -> q").


from dataclasses import dataclass, field
from typing import List


@dataclass
class BeliefBase:
    """
    Base de crenças muito simples: guarda fórmulas como strings.

    Exemplo de conteúdo:
        ["p", "p -> q", "¬q"]
    """

    formulas: List[str] = field(default_factory=list)

    def add(self, formula: str) -> None:
        """
        Adiciona uma fórmula à base, se ainda não existir.

        - Remove espaços antes/depois.
        - Ignora strings vazias.
        - Evita duplicados.
        """
        formula = formula.strip()
        if formula and formula not in self.formulas:
            self.formulas.append(formula)

    def remove_index(self, index: int) -> bool:
        """
        Remove a fórmula na posição dada (0-based).
        Devolve True se conseguiu remover, False caso contrário.
        """
        if 0 <= index < len(self.formulas):
            self.formulas.pop(index)
            return True
        return False

    def is_empty(self) -> bool:
        """Devolve True se a base está vazia."""
        return len(self.formulas) == 0

    def __str__(self) -> str:
        """
        Representação legível da base, útil para debug:
            1. p
            2. p -> q
        """
        if not self.formulas:
            return "(base vazia)"
        linhas = []
        for i, f in enumerate(self.formulas, start=1):
            linhas.append(f"{i}. {f}")
        return "\n".join(linhas)
