# logica/contraction.py
#
# Implementações "corretas para teste" (bases finitas, custo exponencial):
#   - partial_meet_contraction (remainders + seleção + interseção)
#   - kernel_contraction       (kernels + incisão)
#
# Requer:
#   - BeliefBase em logica/belief_base.py com atributo .formulas: List[str]
#   - parse_formula e conseqlog_strings em logica/cp_logic.py

from __future__ import annotations

from itertools import combinations
from typing import List, Iterable, Set

from .belief_base import BeliefBase
from .cp_logic import parse_formula, conseqlog_strings, ParseError


# --------------------------
# Helpers
# --------------------------


def _norm_str(s: str) -> str:
    return s.strip()


def _parse_list(str_formulas: List[str]):
    return [parse_formula(_norm_str(x)) for x in str_formulas if _norm_str(x)]


def entails(base_strs: List[str], alpha_str: str) -> bool:
    """
    base_strs ⊨ alpha_str usando conseqlog_strings, que já faz parse internamente.
    """
    base_clean = [x.strip() for x in base_strs if x.strip()]
    alpha_clean = alpha_str.strip()
    return conseqlog_strings(base_clean, alpha_clean)


def _all_subsets(lst: List[str]) -> Iterable[List[str]]:
    """
    Todos os subconjuntos (listas) de lst.
    """
    n = len(lst)
    for r in range(n + 1):
        for idxs in combinations(range(n), r):
            yield [lst[i] for i in idxs]


def _is_subset(a: List[str], b: List[str]) -> bool:
    sb = set(b)
    return all(x in sb for x in a)


def _maximal_non_entailing_subsets(base: List[str], alpha: str) -> List[List[str]]:
    """
    Remainders: subconjuntos maximais de base que NÃO implicam alpha.
    """
    candidates = []
    for sub in _all_subsets(base):
        if not entails(sub, alpha):
            candidates.append(sub)

    maximals = []
    for s in candidates:
        is_max = True
        for t in candidates:
            if len(t) > len(s) and _is_subset(s, t):
                is_max = False
                break
        if is_max:
            maximals.append(s)
    return maximals


def _minimal_entailing_subsets(base: List[str], alpha: str) -> List[List[str]]:
    """
    Kernels: subconjuntos mínimos de base que implicam alpha.
    """
    candidates = []
    for sub in _all_subsets(base):
        if entails(sub, alpha):
            candidates.append(sub)

    minimals = []
    for s in candidates:
        is_min = True
        for t in candidates:
            if len(t) < len(s) and _is_subset(t, s):
                is_min = False
                break
        if is_min:
            minimals.append(s)
    return minimals


def _choose_remainders(remainders: List[List[str]]) -> List[List[str]]:
    """
    Função de seleção γ.
    Heurística: escolhe os remainders de maior tamanho (mudança mínima).
    """
    if not remainders:
        return []
    max_len = max(len(r) for r in remainders)
    return [r for r in remainders if len(r) == max_len]


def _incision(kernels: List[List[str]], base_order: List[str]) -> Set[str]:
    """
    Função de incisão σ:
    escolher pelo menos 1 fórmula de cada kernel para remover.

    Heurística simples:
    - escolhe, para cada kernel, a primeira fórmula do kernel conforme a ordem original da base.
    """
    to_remove: Set[str] = set()
    for ker in kernels:
        for f in base_order:
            if f in ker:
                to_remove.add(f)
                break
    return to_remove


# --------------------------
# Operadores
# --------------------------


def partial_meet_contraction(base: BeliefBase, formula: str) -> BeliefBase:
    """
    Partial meet contraction (para bases finitas):
      1) Se base ⊭ α => devolve base (vacuity)
      2) Calcula remainders (subconjuntos maximais que não implicam α)
      3) Seleciona alguns remainders (γ)
      4) Interseção dos selecionados

    Resultado: BeliefBase com strings (mesmo formato de entrada).
    """
    alpha = _norm_str(formula)
    if not alpha:
        return BeliefBase(formulas=list(base.formulas))

    base_list = [_norm_str(x) for x in base.formulas if _norm_str(x)]

    # Se não implica alpha, não muda (vacuity)
    if not entails(base_list, alpha):
        return BeliefBase(formulas=list(base_list))

    # Remainders
    remainders = _maximal_non_entailing_subsets(base_list, alpha)
    if not remainders:
        # Caso extremo: remove tudo
        return BeliefBase(formulas=[])

    selected = _choose_remainders(remainders)
    if not selected:
        return BeliefBase(formulas=[])

    # Interseção
    inter = set(selected[0])
    for r in selected[1:]:
        inter.intersection_update(r)

    # manter ordem original
    result = [x for x in base_list if x in inter]
    return BeliefBase(formulas=result)


def kernel_contraction(base: BeliefBase, formula: str) -> BeliefBase:
    """
    Kernel contraction (para bases finitas):
      1) Se base ⊭ α => devolve base (vacuity)
      2) Calcula kernels (subconjuntos mínimos que implicam α)
      3) σ escolhe pelo menos um elemento de cada kernel para remover
      4) Remove os escolhidos

    Resultado: BeliefBase com strings.
    """
    alpha = _norm_str(formula)
    if not alpha:
        return BeliefBase(formulas=list(base.formulas))

    base_list = [_norm_str(x) for x in base.formulas if _norm_str(x)]

    if not entails(base_list, alpha):
        return BeliefBase(formulas=list(base_list))

    kernels = _minimal_entailing_subsets(base_list, alpha)
    if not kernels:
        return BeliefBase(formulas=list(base_list))

    to_remove = _incision(kernels, base_list)
    result = [x for x in base_list if x not in to_remove]
    return BeliefBase(formulas=result)
