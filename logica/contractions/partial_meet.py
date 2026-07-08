# logica/contractions/partial_meet.py

from __future__ import annotations

from typing import List

from ..belief_base import BeliefBase
from ..cp_logic import (
    parse_formula,
    is_tautology,
)
from .common import (
    normalizar_formula,
    e_subconjunto,
    conjunto_das_partes,
    implica,
    intersecao_de_conjuntos,
    format_base_text,
    format_set_of_sets_text,
)

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
    - full: seleciona todos os remainders.
    - first: seleciona apenas o primeiro remainder.
    - max_cardinality: seleciona todos os remainders com maior cardinalidade.
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


# ============================================================
# PARTIAL MEET — CONTRAÇÃO
# ============================================================


def partial_meet_contraction_with_steps(
    base: BeliefBase,
    alpha: str,
    estrategia: str = "full",
) -> tuple[BeliefBase, List[str]]:
    """
    Contração Partial Meet com explicação passo a passo.

    Mesmo quando α é tautologia ou quando A não implica α,
    a função continua a explicação até aos remainders, seleção γ
    e interseção, para o PDF não ficar incompleto.
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
    alpha_e_tautologia = is_tautology(alpha_ast)

    # 1. Failure
    steps.append("")
    steps.append("1. Failure")

    if alpha_e_tautologia:
        steps.append(f"α = {alpha} é tautologia.")
        steps.append("Não é possível deixar de implicar uma tautologia.")
        steps.append("A contração deve manter a base inalterada.")
    else:
        steps.append(f"α = {alpha} não é tautologia.")

    # 2. Cálculo dos remainders
    steps.append("")
    steps.append("2. Cálculo dos remainders")

    partes = conjunto_das_partes(A)
    steps.append(f"Foram gerados {len(partes)} subconjuntos de A.")

    if alpha_e_tautologia:
        nao_implicam = []
        rems = []
        steps.append("Como α é tautologia, todos os subconjuntos implicam α.")
        steps.append("Logo, não existem remainders próprios.")
    else:
        nao_implicam = conjuntos_que_nao_implicam(partes, alpha)
        rems = maximais_por_inclusao(nao_implicam)

        if not implica(A, alpha):
            steps.append(f"A não implica α, isto é, A ⊬ {alpha}.")
            steps.append("Assim, o próprio A é um remainder maximal.")
        else:
            steps.append(f"A implica α, isto é, A ⊢ {alpha}.")
            steps.append("Logo, é necessário procurar subconjuntos maximais que deixem de implicar α.")

        steps.append(f"Desses, {len(nao_implicam)} não implicam α.")

    steps.append("Remainders encontrados:")
    steps.append(format_set_of_sets_text(rems))

    # 3. Seleção γ
    steps.append("")
    steps.append("3. Aplicação da função de seleção γ")

    if alpha_e_tautologia:
        selecionados = []
        selecionados_para_resultado = [A]
        steps.append("Como A⊥α = ∅, aplica-se a convenção γ(∅) = {A}.")
        steps.append("Isto representa a escolha trivial que mantém a base inalterada.")
    else:
        selecionados = selecionar_remainders(rems, estrategia=estrategia)
        selecionados_para_resultado = selecionados

    steps.append("Remainders selecionados:")
    steps.append(format_set_of_sets_text(selecionados))

    # 4. Interseção
    steps.append("")
    steps.append("4. Interseção dos remainders selecionados")

    resultado = intersecao_de_conjuntos(selecionados_para_resultado)
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


def partial_meet_contraction_manual_with_steps(
    base: BeliefBase,
    alpha: str,
    remainders_selecionados: List[List[str]],
) -> tuple[BeliefBase, List[str]]:
    """
    Contração Partial Meet com seleção manual de remainders.

    Aceita seleção vazia quando α é tautologia, porque nesse caso
    A⊥α = ∅ e usa-se a convenção γ(∅) = {A}.
    """
    steps: List[str] = []

    A = [normalizar_formula(f) for f in base.formulas if normalizar_formula(f)]
    alpha = normalizar_formula(alpha)

    steps.append("=== Partial Meet Contraction - Seleção Manual ===")
    steps.append(f"Base inicial A: {format_base_text(A)}")
    steps.append(f"Fórmula alvo α: {alpha}")
    steps.append("Estratégia γ: manual")

    if not alpha:
        steps.append("α é vazio. A base é devolvida sem alterações.")
        return BeliefBase(formulas=A), steps

    alpha_ast = parse_formula(alpha)
    alpha_e_tautologia = is_tautology(alpha_ast)

    # 1. Failure
    steps.append("")
    steps.append("1. Failure")

    if alpha_e_tautologia:
        steps.append(f"α = {alpha} é tautologia.")
        steps.append("Não é possível deixar de implicar uma tautologia.")
        steps.append("A contração deve manter a base inalterada.")
    else:
        steps.append(f"α = {alpha} não é tautologia.")

    # 2. Cálculo dos remainders
    steps.append("")
    steps.append("2. Cálculo dos remainders")

    rems = remainders(A, alpha)

    if alpha_e_tautologia:
        steps.append("Como α é tautologia, não existem remainders próprios.")
    elif not implica(A, alpha):
        steps.append(f"A não implica α, isto é, A ⊬ {alpha}.")
        steps.append("Assim, o próprio A é um remainder maximal.")
    else:
        steps.append(f"A implica α, isto é, A ⊢ {alpha}.")

    steps.append("Remainders encontrados:")
    steps.append(format_set_of_sets_text(rems))

    # 3. Seleção manual γ
    steps.append("")
    steps.append("3. Seleção manual da função γ")

    if alpha_e_tautologia:
        selecionados_normalizados = []
        selecionados_para_resultado = [A]

        steps.append("O utilizador confirmou a seleção vazia.")
        steps.append("Como A⊥α = ∅, aplica-se a convenção γ(∅) = {A}.")
        steps.append("Remainders escolhidos pelo utilizador:")
        steps.append(format_set_of_sets_text(selecionados_normalizados))

    else:
        if not remainders_selecionados:
            raise ValueError("Na seleção manual, tens de escolher pelo menos um remainder.")

        rems_normalizados = {
            frozenset(normalizar_formula(f) for f in r)
            for r in rems
        }

        selecionados_normalizados: List[List[str]] = []

        for r in remainders_selecionados:
            r_norm = [normalizar_formula(f) for f in r if normalizar_formula(f)]

            if frozenset(r_norm) not in rems_normalizados:
                raise ValueError(
                    "A seleção manual contém um conjunto que não é remainder válido."
                )

            selecionados_normalizados.append(r_norm)

        selecionados_para_resultado = selecionados_normalizados

        steps.append("Remainders escolhidos pelo utilizador:")
        steps.append(format_set_of_sets_text(selecionados_normalizados))

    # 4. Interseção
    steps.append("")
    steps.append("4. Interseção dos remainders escolhidos")

    resultado = intersecao_de_conjuntos(selecionados_para_resultado)
    resultado_ordenado = [f for f in A if f in resultado]

    steps.append(f"Resultado da interseção: {format_base_text(resultado_ordenado)}")
    steps.append("")
    steps.append(f"Base final: {format_base_text(resultado_ordenado)}")

    return BeliefBase(formulas=resultado_ordenado), steps
