# logica/contractions/exhaustive.py

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import List, Set

from ..belief_base import BeliefBase
from ..cp_logic import parse_formula, is_tautology

from .common import (
    normalizar_formula,
    implica,
    intersecao_de_conjuntos,
)

from .partial_meet import remainders
from .kernel import kernels, hitting_set_valido


@dataclass(frozen=True)
class PartialMeetOption:
    option_id: int
    selected_indices: List[int]
    selected_remainders: List[List[str]]
    result_base: List[str]
    removed_formulas: List[str]


@dataclass(frozen=True)
class KernelIncisionOption:
    option_id: int
    incision: List[str]
    result_base: List[str]
    removed_formulas: List[str]
    is_minimal: bool


def _all_non_empty_index_subsets(n: int):
    """
    Gera todos os subconjuntos não vazios de índices 0..n-1.
    """
    indices = list(range(n))

    for size in range(1, n + 1):
        for comb in combinations(indices, size):
            yield list(comb)


def _all_non_empty_formula_subsets(formulas: List[str]):
    """
    Gera todos os subconjuntos não vazios de uma lista de fórmulas.
    """
    for size in range(1, len(formulas) + 1):
        for comb in combinations(formulas, size):
            yield set(comb)


def partial_meet_all_selection_options(
    base: BeliefBase,
    alpha: str,
    max_options: int = 512,
) -> tuple[List[List[str]], List[PartialMeetOption], List[str]]:
    """
    Calcula todas as seleções possíveis de remainders para Partial Meet.

    Se houver n remainders, existem 2^n - 1 seleções possíveis.
    Cada seleção gera uma base final pela interseção dos remainders escolhidos.
    """
    steps: List[str] = []

    A = [normalizar_formula(f) for f in base.formulas if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    steps.append("=== Partial Meet - Todas as seleções possíveis ===")
    steps.append(f"Base inicial: {'; '.join(A) if A else '(base vazia)'}")
    steps.append(f"Fórmula alvo α: {alpha}")

    if not alpha:
        steps.append("α vazio. Não há opções para calcular.")
        return [], [], steps

    alpha_ast = parse_formula(alpha)

    if is_tautology(alpha_ast):
        steps.append(
            "α é tautologia. Pela condição de failure, a base fica inalterada."
        )
        return [], [], steps

    rems = remainders(A, alpha)

    steps.append(f"Foram encontrados {len(rems)} remainders.")

    if not rems:
        steps.append("Não existem remainders.")
        return rems, [], steps

    total_possible = (2 ** len(rems)) - 1

    steps.append(f"Número de seleções possíveis: {total_possible}")

    if total_possible > max_options:
        raise ValueError(
            f"Há {total_possible} seleções possíveis. "
            f"O limite atual é {max_options}. "
            "Aumenta o limite ou usa uma base menor."
        )

    options: List[PartialMeetOption] = []

    for option_id, selected_indices in enumerate(
        _all_non_empty_index_subsets(len(rems)),
        start=1,
    ):
        selected_remainders = [rems[i] for i in selected_indices]

        result = intersecao_de_conjuntos(selected_remainders)
        result_ordered = [f for f in A if f in result]
        removed = [f for f in A if f not in result_ordered]

        options.append(
            PartialMeetOption(
                option_id=option_id,
                selected_indices=[i + 1 for i in selected_indices],
                selected_remainders=selected_remainders,
                result_base=result_ordered,
                removed_formulas=removed,
            )
        )

    steps.append(f"Foram geradas {len(options)} opções.")

    return rems, options, steps


def _is_minimal_hitting_set(candidate: Set[str], kerns: List[List[str]]) -> bool:
    """
    Verifica se candidate é hitting set minimal.

    É minimal se for válido e se remover qualquer fórmula dele
    fizer deixar de tocar todos os kernels.
    """
    if not hitting_set_valido(candidate, kerns):
        return False

    for formula in list(candidate):
        smaller = set(candidate)
        smaller.remove(formula)

        if smaller and hitting_set_valido(smaller, kerns):
            return False

    return True


def kernel_all_incision_options(
    base: BeliefBase,
    alpha: str,
    minimal_only: bool = False,
    max_options: int = 512,
) -> tuple[List[List[str]], List[KernelIncisionOption], List[str]]:
    """
    Calcula todas as incisões válidas para Kernel.

    Uma incisão é válida se toca todos os kernels.

    Se minimal_only=True, devolve apenas incisões minimais.
    """
    steps: List[str] = []

    A = [normalizar_formula(f) for f in base.formulas if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    steps.append("=== Kernel - Todas as incisões válidas ===")
    steps.append(f"Base inicial: {'; '.join(A) if A else '(base vazia)'}")
    steps.append(f"Fórmula alvo α: {alpha}")

    if not alpha:
        steps.append("α vazio. Não há incisões para calcular.")
        return [], [], steps

    alpha_ast = parse_formula(alpha)

    if is_tautology(alpha_ast):
        steps.append(
            "α é tautologia. Pela condição de failure, a base fica inalterada."
        )
        return [], [], steps

    if not implica(A, alpha):
        steps.append("A não implica α. Não há kernels relevantes.")
        return [], [], steps

    kerns = kernels(A, alpha)

    steps.append(f"Foram encontrados {len(kerns)} kernels.")

    if not kerns:
        steps.append("Não existem kernels.")
        return kerns, [], steps

    universe = []

    for f in A:
        if any(f in k for k in kerns):
            universe.append(f)

    total_candidates = (2 ** len(universe)) - 1

    steps.append(f"Fórmulas presentes nos kernels: {len(universe)}")
    steps.append(f"Candidatos possíveis antes do filtro: {total_candidates}")

    if total_candidates > max_options * 8:
        raise ValueError(
            f"Há {total_candidates} candidatos possíveis antes do filtro. "
            f"Isto pode ser pesado. Usa uma base menor ou aumenta o limite."
        )

    options: List[KernelIncisionOption] = []

    for candidate in _all_non_empty_formula_subsets(universe):
        if not hitting_set_valido(candidate, kerns):
            continue

        is_minimal = _is_minimal_hitting_set(candidate, kerns)

        if minimal_only and not is_minimal:
            continue

        incision_ordered = [f for f in A if f in candidate]
        result = [f for f in A if f not in candidate]
        removed = incision_ordered

        options.append(
            KernelIncisionOption(
                option_id=len(options) + 1,
                incision=incision_ordered,
                result_base=result,
                removed_formulas=removed,
                is_minimal=is_minimal,
            )
        )

        if len(options) > max_options:
            raise ValueError(
                f"Foram encontradas mais de {max_options} incisões. "
                "Reduz a base ou aumenta o limite."
            )

    steps.append(f"Foram geradas {len(options)} incisões válidas.")

    return kerns, options, steps
