# logica/contraction.py

from __future__ import annotations

from itertools import combinations
from typing import Iterable, List, Set

from .belief_base import BeliefBase
from .cp_logic import (
    parse_formula,
    is_tautology,
    conseqlog_strings,
)

# ============================================================
# HELPERS GERAIS
# ============================================================


def normalizar_formula(s: str) -> str:
    return " ".join(s.strip().split())


def e_subconjunto(A: List[str], B: List[str]) -> bool:
    """
    Verifica se A ⊆ B.
    """
    return set(A).issubset(set(B))


def conjunto_das_partes(A: List[str]) -> List[List[str]]:
    """
    Calcula P(A), isto é, o conjunto de todos os subconjuntos de A.
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
    Interseção de vários conjuntos.
    """
    if not conjuntos:
        return []

    inter = set(conjuntos[0])

    for conjunto in conjuntos[1:]:
        inter.intersection_update(set(conjunto))

    return list(inter)


# ============================================================
# PARTIAL MEET
# ============================================================


def conjuntos_que_nao_implicam(P: List[List[str]], alpha: str) -> List[List[str]]:
    """
    Recebe P ⊆ P(A) e devolve os conjuntos que NÃO implicam alpha.
    """
    resultado: List[List[str]] = []

    for conjunto in P:
        if not implica(conjunto, alpha):
            resultado.append(conjunto)

    return resultado


def maximais_por_inclusao(T: List[List[str]]) -> List[List[str]]:
    """
    Devolve os elementos de T que não estão contidos propriamente
    em nenhum outro elemento de T.
    """
    maximais: List[List[str]] = []

    for B in T:
        B_e_maximal = True

        for C in T:
            if B != C and e_subconjunto(B, C):
                B_e_maximal = False
                break

        if B_e_maximal:
            maximais.append(B)

    return maximais


def remainders(A: List[str], alpha: str) -> List[List[str]]:
    """
    Calcula A ⊥ alpha.

    Ou seja, os subconjuntos maximais de A que não implicam alpha.
    """
    A = [normalizar_formula(f) for f in A if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    partes = conjunto_das_partes(A)
    nao_implicam = conjuntos_que_nao_implicam(partes, alpha)

    return maximais_por_inclusao(nao_implicam)


def selecionar_remainders(
    rems: List[List[str]], estrategia: str = "full"
) -> List[List[str]]:
    """
    Função de seleção γ.

    Estratégias:
    - full: seleciona todos os remainders
    - max_cardinality: seleciona os remainders com maior cardinalidade
    - first: seleciona apenas o primeiro remainder
    """
    if not rems:
        return []

    if estrategia == "first":
        return [rems[0]]

    if estrategia == "max_cardinality":
        maior = max(len(r) for r in rems)
        return [r for r in rems if len(r) == maior]

    return rems


def partial_meet_contraction(
    base: BeliefBase,
    alpha: str,
    estrategia: str = "full",
) -> BeliefBase:
    """
    Contração partial meet para bases finitas.

    Por defeito usa estratégia full meet:
    seleciona todos os remainders e faz a interseção.
    """
    A = [normalizar_formula(f) for f in base.formulas if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    if not alpha:
        return BeliefBase(formulas=A)

    alpha_ast = parse_formula(alpha)

    # Failure: se alpha é tautologia, não há contração útil.
    if is_tautology(alpha_ast):
        return BeliefBase(formulas=A)

    # Vacuity: se A já não implica alpha, não remove nada.
    if not implica(A, alpha):
        return BeliefBase(formulas=A)

    rems = remainders(A, alpha)
    selecionados = selecionar_remainders(rems, estrategia=estrategia)
    resultado = intersecao_de_conjuntos(selecionados)

    # Mantém a ordem original da base.
    resultado_ordenado = [f for f in A if f in resultado]

    return BeliefBase(formulas=resultado_ordenado)


# ============================================================
# KERNEL CONTRACTION
# ============================================================


def conjuntos_que_implicam(P: List[List[str]], alpha: str) -> List[List[str]]:
    """
    Recebe P ⊆ P(A) e devolve os conjuntos que implicam alpha.
    """
    resultado: List[List[str]] = []

    for conjunto in P:
        if implica(conjunto, alpha):
            resultado.append(conjunto)

    return resultado


def minimais_por_inclusao(T: List[List[str]]) -> List[List[str]]:
    """
    Devolve os elementos de T que não contêm propriamente
    nenhum outro elemento de T.
    """
    minimais: List[List[str]] = []

    for B in T:
        B_e_minimal = True

        for C in T:
            if B != C and e_subconjunto(C, B):
                B_e_minimal = False
                break

        if B_e_minimal:
            minimais.append(B)

    return minimais


def kernels(A: List[str], alpha: str) -> List[List[str]]:
    """
    Calcula A ⊥⊥ alpha.

    Ou seja, os subconjuntos mínimos de A que implicam alpha.
    """
    A = [normalizar_formula(f) for f in A if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    partes = conjunto_das_partes(A)
    implicam_alpha = conjuntos_que_implicam(partes, alpha)

    return minimais_por_inclusao(implicam_alpha)


def incisao(kerns: List[List[str]], base_order: List[str]) -> Set[str]:
    """
    Função de incisão σ.

    Critério usado:
    1. Se houver uma fórmula comum a todos os kernels, remove essa fórmula.
    2. Caso contrário, remove a primeira fórmula de cada kernel,
       seguindo a ordem original da base.

    Isto garante que pelo menos uma fórmula de cada kernel é removida.
    """
    if not kerns:
        return set()

    comum = set(kerns[0])

    for k in kerns[1:]:
        comum.intersection_update(set(k))

    if comum:
        for f in base_order:
            if f in comum:
                return {f}

    remover: Set[str] = set()

    for kernel in kerns:
        for f in base_order:
            if f in kernel:
                remover.add(f)
                break

    return remover


def kernel_contraction(base: BeliefBase, alpha: str) -> BeliefBase:
    """
    Contração kernel para bases finitas.
    """
    A = [normalizar_formula(f) for f in base.formulas if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    if not alpha:
        return BeliefBase(formulas=A)

    alpha_ast = parse_formula(alpha)

    # Failure
    if is_tautology(alpha_ast):
        return BeliefBase(formulas=A)

    # Vacuity
    if not implica(A, alpha):
        return BeliefBase(formulas=A)

    kerns = kernels(A, alpha)

    if not kerns:
        return BeliefBase(formulas=A)

    formulas_a_remover = incisao(kerns, A)

    resultado = [f for f in A if f not in formulas_a_remover]

    return BeliefBase(formulas=resultado)
