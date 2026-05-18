# logica/contractions/common.py

from __future__ import annotations

from itertools import combinations
from typing import List

from ..cp_logic import conseqlog_strings

# ============================================================
# HELPERS GERAIS
# ============================================================


def normalizar_formula(s: str) -> str:
    """
    Remove espaços desnecessários de uma fórmula.
    """
    return " ".join(s.strip().split())


def e_subconjunto(A: List[str], B: List[str]) -> bool:
    """
    Verifica se A ⊆ B.
    """
    return set(A).issubset(set(B))


def conjunto_das_partes(A: List[str]) -> List[List[str]]:
    """
    Calcula P(A), o conjunto de todos os subconjuntos de A.
    """
    A = [normalizar_formula(f) for f in A if normalizar_formula(f)]

    partes: List[List[str]] = []

    for tamanho in range(len(A) + 1):
        for comb in combinations(A, tamanho):
            partes.append(list(comb))

    return partes


def implica(A: List[str], alpha: str) -> bool:
    """
    Verifica se A ⊢ alpha.
    """
    A = [normalizar_formula(f) for f in A if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    return conseqlog_strings(A, alpha)


def intersecao_de_conjuntos(conjuntos: List[List[str]]) -> List[str]:
    """
    Faz a interseção de vários conjuntos.
    """
    if not conjuntos:
        return []

    inter = set(conjuntos[0])

    for conjunto in conjuntos[1:]:
        inter.intersection_update(set(conjunto))

    return list(inter)


# ============================================================
# FORMATAÇÃO PARA EXPLICAÇÃO
# ============================================================


def format_base_text(A: List[str]) -> str:
    """
    Formata uma base de crenças para texto.
    """
    return "; ".join(A) if A else "(base vazia)"


def format_set_text(A: List[str]) -> str:
    """
    Formata um conjunto de fórmulas.
    """
    if not A:
        return "{ }"

    return "{ " + "; ".join(A) + " }"


def format_set_of_sets_text(sets: List[List[str]]) -> str:
    """
    Formata uma lista de conjuntos de fórmulas.
    """
    if not sets:
        return "∅"

    lines = []

    for i, conjunto in enumerate(sets, start=1):
        content = "; ".join(conjunto) if conjunto else "∅"
        lines.append(f"{i}. {{ {content} }}")

    return "\n".join(lines)
