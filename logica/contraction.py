# logica/contraction.py

from __future__ import annotations

from itertools import combinations
from typing import List, Set

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
# FORMATAÇÃO PARA explicaao
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


def format_set_of_sets_text(conjuntos: List[List[str]]) -> str:
    """
    Formata um conjunto de conjuntos.
    """
    if not conjuntos:
        return "∅"

    linhas = []

    for i, conjunto in enumerate(conjuntos, start=1):
        linhas.append(f"{i}. {format_set_text(conjunto)}")

    return "\n".join(linhas)


# ============================================================
# PARTIAL MEET — REMAINDERS
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

    Isto corresponde aos maiores conjuntos segundo inclusão.
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

    Isto é, os subconjuntos maximais de A que NÃO implicam alpha.
    """
    A = [normalizar_formula(f) for f in A if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    partes = conjunto_das_partes(A)
    nao_implicam = conjuntos_que_nao_implicam(partes, alpha)

    return maximais_por_inclusao(nao_implicam)


def selecionar_remainders(
    rems: List[List[str]],
    estrategia: str = "full",
) -> List[List[str]]:
    """
    Função de seleção γ para Partial Meet.

    Estratégias:
    - full:
        seleciona todos os remainders.
    - first:
        seleciona apenas o primeiro remainder.
    - max_cardinality:
        seleciona todos os remainders com maior cardinalidade.
    """
    if not rems:
        return []

    if estrategia == "first":
        return [rems[0]]

    if estrategia == "max_cardinality":
        maior = max(len(r) for r in rems)
        return [r for r in rems if len(r) == maior]

    # full meet por defeito
    return rems


def partial_meet_contraction_with_steps(
    base: BeliefBase,
    alpha: str,
    estrategia: str = "full",
) -> tuple[BeliefBase, List[str]]:
    """
    Contração Partial Meet com explicação passo a passo.
    """
    steps: List[str] = []

    A = [normalizar_formula(f) for f in base.formulas if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    steps.append("=== Partial Meet Contraction ===")
    steps.append(f"Base inicial A: {format_base_text(A)}")
    steps.append(f"Fórmula alvo α: {alpha}")
    steps.append(f"Estratégia γ: {estrategia}")

    if not alpha:
        steps.append("α é vazio. A base é devolvida sem alterações.")
        return BeliefBase(formulas=A), steps

    alpha_ast = parse_formula(alpha)

    # 1. Failure
    steps.append("")
    steps.append("1. Failure")

    if is_tautology(alpha_ast):
        steps.append(f"α = {alpha} é tautologia.")
        steps.append("Não é possível deixar de implicar uma tautologia.")
        steps.append("Resultado: base inalterada.")
        return BeliefBase(formulas=A), steps

    steps.append(f"α = {alpha} não é tautologia.")

    # 2. Vacuity
    steps.append("")
    steps.append("2. Vacuity")

    if not implica(A, alpha):
        steps.append(f"A não implica α, isto é, A ⊬ {alpha}.")
        steps.append("Logo, não é necessário remover nada.")
        steps.append("Resultado: base inalterada.")
        return BeliefBase(formulas=A), steps

    steps.append(f"A implica α, isto é, A ⊢ {alpha}.")
    steps.append("Logo, é necessário contrair a base.")

    # 3. Cálculo dos remainders
    steps.append("")
    steps.append("3. Cálculo dos remainders")

    partes = conjunto_das_partes(A)
    steps.append(f"Foram gerados {len(partes)} subconjuntos de A.")

    nao_implicam = conjuntos_que_nao_implicam(partes, alpha)
    steps.append(f"Desses, {len(nao_implicam)} não implicam α.")

    rems = maximais_por_inclusao(nao_implicam)
    steps.append("Remainders encontrados:")
    steps.append(format_set_of_sets_text(rems))

    # 4. Seleção γ
    steps.append("")
    steps.append("4. Aplicação da função de seleção γ")

    selecionados = selecionar_remainders(rems, estrategia=estrategia)

    steps.append("Remainders selecionados:")
    steps.append(format_set_of_sets_text(selecionados))

    # 5. Interseção
    steps.append("")
    steps.append("5. Interseção dos remainders selecionados")

    resultado = intersecao_de_conjuntos(selecionados)

    # Mantém a ordem original da base.
    resultado_ordenado = [f for f in A if f in resultado]

    steps.append(f"Resultado da interseção: {format_base_text(resultado_ordenado)}")
    steps.append("")
    steps.append(f"Base final: {format_base_text(resultado_ordenado)}")

    return BeliefBase(formulas=resultado_ordenado), steps


def partial_meet_contraction(
    base: BeliefBase,
    alpha: str,
    estrategia: str = "full",
) -> BeliefBase:
    """
    Contração Partial Meet sem explicação.

    Usa internamente a versão com passos, mas devolve apenas a nova base.
    """
    nova_base, _ = partial_meet_contraction_with_steps(
        base,
        alpha,
        estrategia=estrategia,
    )
    return nova_base


# ============================================================
# KERNEL CONTRACTION — KERNELS
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

    Isto corresponde aos menores conjuntos segundo inclusão.
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

    Isto é, os subconjuntos mínimos de A que implicam alpha.
    """
    A = [normalizar_formula(f) for f in A if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    partes = conjunto_das_partes(A)
    implicam_alpha = conjuntos_que_implicam(partes, alpha)

    return minimais_por_inclusao(implicam_alpha)


# ============================================================
# KERNEL CONTRACTION — INCISÃO
# ============================================================


def hitting_set_valido(candidato: Set[str], kerns: List[List[str]]) -> bool:
    """
    Um hitting set é válido se toca/interseta todos os kernels.
    """
    return all(candidato.intersection(set(k)) for k in kerns)


def incisao_minima(kerns: List[List[str]], base_order: List[str]) -> Set[str]:
    """
    Procura uma incisão com o menor número possível de fórmulas.

    Este método é exato, mas exponencial. Serve bem para bases pequenas/médias.
    """
    if not kerns:
        return set()

    universo: List[str] = []

    for f in base_order:
        if any(f in k for k in kerns):
            universo.append(f)

    for tamanho in range(1, len(universo) + 1):
        for comb in combinations(universo, tamanho):
            candidato = set(comb)

            if hitting_set_valido(candidato, kerns):
                return candidato

    return set()


def incisao(
    kerns: List[List[str]],
    base_order: List[str],
    estrategia: str = "common_first",
) -> Set[str]:
    """
    Função de incisão σ.

    Estratégias:
    - common_first:
        se houver fórmula comum a todos os kernels, remove-a;
        caso contrário, remove a primeira fórmula de cada kernel.
    - first_each:
        remove a primeira fórmula de cada kernel.
    - min_hitting:
        remove o menor conjunto possível que toca todos os kernels.
    """
    if not kerns:
        return set()

    if estrategia == "min_hitting":
        return incisao_minima(kerns, base_order)

    if estrategia == "first_each":
        remover: Set[str] = set()

        for kernel in kerns:
            for f in base_order:
                if f in kernel:
                    remover.add(f)
                    break

        return remover

    # common_first por defeito
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


def kernel_contraction_with_steps(
    base: BeliefBase,
    alpha: str,
    estrategia: str = "common_first",
) -> tuple[BeliefBase, List[str]]:
    """
    Contração Kernel com explicação passo a passo.
    """
    steps: List[str] = []

    A = [normalizar_formula(f) for f in base.formulas if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    steps.append("=== Kernel Contraction ===")
    steps.append(f"Base inicial A: {format_base_text(A)}")
    steps.append(f"Fórmula alvo α: {alpha}")
    steps.append(f"Estratégia σ: {estrategia}")

    if not alpha:
        steps.append("α é vazio. A base é devolvida sem alterações.")
        return BeliefBase(formulas=A), steps

    alpha_ast = parse_formula(alpha)

    # 1. Failure
    steps.append("")
    steps.append("1. Failure")

    if is_tautology(alpha_ast):
        steps.append(f"α = {alpha} é tautologia.")
        steps.append("Não é possível deixar de implicar uma tautologia.")
        steps.append("Resultado: base inalterada.")
        return BeliefBase(formulas=A), steps

    steps.append(f"α = {alpha} não é tautologia.")

    # 2. Vacuity
    steps.append("")
    steps.append("2. Vacuity")

    if not implica(A, alpha):
        steps.append(f"A não implica α, isto é, A ⊬ {alpha}.")
        steps.append("Logo, não é necessário remover nada.")
        steps.append("Resultado: base inalterada.")
        return BeliefBase(formulas=A), steps

    steps.append(f"A implica α, isto é, A ⊢ {alpha}.")
    steps.append("Logo, é necessário contrair a base.")

    # 3. Kernels
    steps.append("")
    steps.append("3. Cálculo dos kernels")

    partes = conjunto_das_partes(A)
    steps.append(f"Foram gerados {len(partes)} subconjuntos de A.")

    implicam_alpha = conjuntos_que_implicam(partes, alpha)
    steps.append(f"Desses, {len(implicam_alpha)} implicam α.")

    kerns = minimais_por_inclusao(implicam_alpha)
    steps.append("Kernels encontrados:")
    steps.append(format_set_of_sets_text(kerns))

    if not kerns:
        steps.append("Nenhum kernel encontrado. Base devolvida sem alterações.")
        return BeliefBase(formulas=A), steps

    # 4. Incisão
    steps.append("")
    steps.append("4. Aplicação da função de incisão σ")

    formulas_a_remover = incisao(kerns, A, estrategia=estrategia)

    steps.append(
        "Fórmulas escolhidas para remover: "
        + format_base_text([f for f in A if f in formulas_a_remover])
    )

    # 5. Resultado final
    steps.append("")
    steps.append("5. Remoção das fórmulas escolhidas")

    resultado = [f for f in A if f not in formulas_a_remover]

    steps.append(f"Base final: {format_base_text(resultado)}")

    return BeliefBase(formulas=resultado), steps


def kernel_contraction(
    base: BeliefBase,
    alpha: str,
    estrategia: str = "common_first",
) -> BeliefBase:
    """
    Contração Kernel sem explicação.

    Usa internamente a versão com passos, mas devolve apenas a nova base.
    """
    nova_base, _ = kernel_contraction_with_steps(
        base,
        alpha,
        estrategia=estrategia,
    )
    return nova_base
