# from __future__ import annotations

# from dataclasses import dataclass
# from turtle import st
# from typing import List

# from logica.belief_base import BeliefBase
# from logica.cp_logic import parse_formula, ParseError
# from logica.contraction import partial_meet_contraction  # <- o teu

# # ------------------------------------------------------------
# # Helpers de parsing/printing no formato "p; p imp q; f; ..."
# # ------------------------------------------------------------


# def parse_base_semicolons(s: str) -> List:
#     """
#     Converte "p; p imp q; f" -> [Formula(p), Formula(p imp q), Formula(f)]
#     Permite string vazia -> base vazia.
#     """
#     s = s.strip()
#     if not s:
#         return []
#     parts = [p.strip() for p in s.split(";") if p.strip()]
#     return [parse_formula(p) for p in parts]


# def base_to_semicolons(base: List) -> str:
#     """
#     Converte [Formula,...] -> "p; (p imp q); f"
#     Usa o __str__ da tua AST. Se quiseres outra “normalização”, é aqui.
#     """
#     return "; ".join(str(f) for f in base)


# def add_formulas(base: List, new_formulas: List) -> List:
#     """
#     Adiciona fórmulas à base (sem duplicados por igualdade estrutural).
#     """
#     out = list(base)
#     for f in new_formulas:
#         if f not in out:
#             out.append(f)
#     return out


# @dataclass
# class BeliefBaseState:
#     base: List


# # ------------------------------------------------------------
# # REPL
# # ------------------------------------------------------------

# HELP = """
# Comandos:
#   help
#       Mostra esta ajuda.

#   set <base>
#       Define a base atual a partir de uma string com ';'
#       Ex: set p; p imp q; f

#   show
#       Mostra a base atual.

#   add <formulas>
#       Adiciona uma ou várias fórmulas à base (separadas por ';')
#       Ex: add r
#       Ex: add (q imp r); neg f

#   contract <formula>
#       Aplica partial meet contraction por <formula>
#       Ex: contract q
#       Ex: contract (p imp q)

#   reset
#       Limpa a base.

#   quit
#       Sair.
# """


# def repl():
#     st = BeliefBaseState(base=[])

#     print("=== TESTE Partial Meet Contraction ===")
#     print("Formato da base: p; p imp q; f; ...")
#     print("Escreve 'help' para comandos.\n")

#     while True:
#         try:
#             line = input("> ").strip()
#         except (EOFError, KeyboardInterrupt):
#             print("\nBye!")
#             return

#         if not line:
#             continue

#         if line.lower() in {"quit", "exit", "q"}:
#             print("Bye!")
#             return

#         if line.lower() == "help":
#             print(HELP)
#             continue

#         if line.lower() == "show":
#             print(base_to_semicolons(st.base))
#             continue

#         if line.lower() == "reset":
#             st.base = []
#             print("[OK] Base limpa.")
#             continue

#         if line.startswith("set "):
#             s = line[len("set ") :].strip()
#             try:
#                 st.base = parse_base_semicolons(s)
#                 print("[OK] Base definida:")
#                 print(base_to_semicolons(st.base))
#             except ParseError as e:
#                 print(f"[ERRO] Sintaxe inválida: {e}")
#             continue

#         if line.startswith("add "):
#             s = line[len("add ") :].strip()
#             try:
#                 new_fs = parse_base_semicolons(s)
#                 st.base = add_formulas(st.base, new_fs)
#                 print("[OK] Base atualizada:")
#                 print(base_to_semicolons(st.base))
#             except ParseError as e:
#                 print(f"[ERRO] Sintaxe inválida: {e}")
#             continue

#         if line.startswith("contract "):
#             s = line[len("contract ") :].strip()
#             try:
#                 # alpha = parse_formula(s)

#                 # --- CHAMADA AO TEU OPERADOR ---
#                 # Se a tua função tiver outra assinatura, ajusta aqui.
#                 st.base = BeliefBase(
#                     formulas=[str(f) for f in st.base]
#                 )  # se st.base forem ASTs
#                 st.base = partial_meet_contraction(st.base, s)
#                 st.base = st.base.formulas  # volta a guardar como list para o teu REPL

#                 print("[OK] Após contração (partial meet):")
#                 print(base_to_semicolons(st.base))
#             except ParseError as e:
#                 print(f"[ERRO] Fórmula inválida: {e}")
#             except TypeError as e:
#                 print(
#                     "[ERRO] Assinatura de partial_meet_contraction não bate com o esperado."
#                 )
#                 print("Detalhe:", e)
#                 print(
#                     "Diz-me a assinatura exata (ou cola a função) e eu ajusto-te esta linha."
#                 )
#             continue

#         print("[ERRO] Comando desconhecido. Escreve 'help'.")


# if __name__ == "__main__":
#     repl()

from itertools import combinations
from typing import List

from logica.cp_logic import conseqlog_strings  # usa o teu motor


def entails(base: List[str], alpha: str) -> bool:
    """Retorna True se base ⊨ alpha (consequência lógica)."""
    base = [s.strip() for s in base if s.strip()]
    alpha = alpha.strip()
    return conseqlog_strings(base, alpha)


def all_subsets(A: List[str]) -> List[List[str]]:
    """Devolve todos os subconjuntos de A como listas."""
    n = len(A)
    subs = []
    for r in range(n + 1):
        for idxs in combinations(range(n), r):
            subs.append([A[i] for i in idxs])
    return subs


def is_subset(B: List[str], C: List[str]) -> bool:
    """B ⊆ C (comparação por strings)."""
    setC = set(C)
    return all(x in setC for x in B)


def remainders(A: List[str], alpha: str) -> List[List[str]]:
    """
    Calcula A ⊥ alpha:
    conjunto dos subconjuntos maximais de A que NÃO implicam alpha.
    """
    A = [s.strip() for s in A if s.strip()]
    alpha = alpha.strip()

    # 1) candidatos: não implicam alpha
    candidates = []
    for B in all_subsets(A):
        if not entails(B, alpha):
            candidates.append(B)

    # 2) maximais por inclusão:
    # B é remainder se NÃO existe B' maior com B ⊂ B' ⊆ A e B' ⊬ alpha
    maximals = []
    for B in candidates:
        maximal = True
        for B2 in candidates:
            if len(B2) > len(B) and is_subset(B, B2):
                # existe superconjunto B2 que também não implica alpha
                maximal = False
                break
        if maximal:
            maximals.append(B)

    return maximals


A = [
    "p1",
    "p1 imp q",
    "p2",
    "p2 imp q",
    "p3",
    "p3 imp q",
    "p4",
    "p4 imp q",
    "p5",
    "p5 imp q",
]
alpha = "q"
print(remainders(A, alpha))
