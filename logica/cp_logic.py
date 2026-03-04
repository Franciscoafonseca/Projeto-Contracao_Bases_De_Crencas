# logica/cp_logic.py
#
# Implementa:
#   - Classes para fórmulas proposicionais (Var, Neg, And, Or, Imp, Iff).
#   - Parser a partir de strings usando a sintaxe:
#         p
#         neg p
#         (p imp q)
#         (p e (q ou r))
#   - Funções:
#         is_cp_formula(s: str)         -> bool
#         parse_formula(s: str)         -> Formula
#         is_tautology(formula)        -> bool
#         entails(premises, conclusion) -> bool
#         conseqlog_strings([...], "q") -> bool   (versão Python do conseqlog)


from __future__ import annotations

from dataclasses import dataclass
from typing import Set, Dict, List, Iterable
from itertools import product
import re


# ---------- Classe base ----------
class Formula:
    def vars(self) -> Set[str]:
        """Conjunto das variáveis proposicionais usadas na fórmula."""
        raise NotImplementedError

    def eval(self, val: Dict[str, bool]) -> bool:
        """Avalia a fórmula numa valoração val[p] = True/False."""
        raise NotImplementedError


# ---------- Construtores ----------
@dataclass(frozen=True)
class Var(Formula):
    name: str

    def vars(self) -> Set[str]:
        return {self.name}

    def eval(self, val: Dict[str, bool]) -> bool:
        return bool(val[self.name])

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Neg(Formula):
    arg: Formula

    def vars(self) -> Set[str]:
        return self.arg.vars()

    def eval(self, val: Dict[str, bool]) -> bool:
        return not self.arg.eval(val)

    def __str__(self) -> str:
        return f"neg {self.arg}"


@dataclass(frozen=True)
class And(Formula):
    left: Formula
    right: Formula

    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()

    def eval(self, val: Dict[str, bool]) -> bool:
        return self.left.eval(val) and self.right.eval(val)

    def __str__(self) -> str:
        return f"({self.left} e {self.right})"


@dataclass(frozen=True)
class Or(Formula):
    left: Formula
    right: Formula

    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()

    def eval(self, val: Dict[str, bool]) -> bool:
        return self.left.eval(val) or self.right.eval(val)

    def __str__(self) -> str:
        return f"({self.left} ou {self.right})"


@dataclass(frozen=True)
class Imp(Formula):
    left: Formula
    right: Formula

    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()

    def eval(self, val: Dict[str, bool]) -> bool:
        # p -> q é falso só quando p=True, q=False
        return (not self.left.eval(val)) or self.right.eval(val)

    def __str__(self) -> str:
        return f"({self.left} imp {self.right})"


@dataclass(frozen=True)
class Iff(Formula):
    left: Formula
    right: Formula

    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()

    def eval(self, val: Dict[str, bool]) -> bool:
        return self.left.eval(val) == self.right.eval(val)

    def __str__(self) -> str:
        return f"({self.left} eq {self.right})"


# ---------- Parser ----------
Token = str


class ParseError(Exception):
    """Erro de parsing de fórmula CP."""


def tokenize(s: str) -> List[Token]:
    """Divide a string em tokens (parênteses e palavras)."""
    s = s.replace("(", " ( ").replace(")", " ) ")
    tokens = s.split()
    return tokens


def parse_formula(s: str) -> Formula:
    """
    Converte uma string como:
        "p"
        "neg p"
        "(p imp q)"
        "(p e (q ou r))"
    numa árvore Formula (Var, Neg, And, Or, Imp, Iff).
    """

    tokens = tokenize(s)
    pos = 0

    def parse_atom() -> Formula:
        nonlocal pos
        if pos >= len(tokens):
            raise ParseError("Fim inesperado da fórmula")

        tok = tokens[pos]

        # Subfórmula entre parênteses
        if tok == "(":
            pos += 1
            subf = parse_formula_inner()
            if pos >= len(tokens) or tokens[pos] != ")":
                raise ParseError("')' esperado.")
            pos += 1
            return subf

        # Negação prefixa: neg φ
        if tok == "neg":
            pos += 1
            arg = parse_atom()
            return Neg(arg)

        # Variável proposicional
        if re.fullmatch(r"[a-zA-Z]\w*", tok):
            pos += 1
            return Var(tok)

        raise ParseError(f"Token inesperado: {tok}")

    def parse_formula_inner() -> Formula:
        nonlocal pos
        left = parse_atom()
        # operadores binários (e, ou, imp, eq)
        while pos < len(tokens) and tokens[pos] in {"e", "ou", "imp", "eq"}:
            op = tokens[pos]
            pos += 1
            right = parse_atom()
            if op == "e":
                left = And(left, right)
            elif op == "ou":
                left = Or(left, right)
            elif op == "imp":
                left = Imp(left, right)
            elif op == "eq":
                left = Iff(left, right)
        return left

    result = parse_formula_inner()
    if pos != len(tokens):
        raise ParseError("Tokens extra no fim da fórmula.")
    return result


def is_cp_formula(s: str) -> bool:
    """Devolve True se 's' é uma fórmula bem formada do cálculo proposicional."""
    try:
        parse_formula(s)
        return True
    except ParseError:
        return False


# ---------- Tabelas de verdade ----------
def all_valuations(vars_: List[str]) -> List[Dict[str, bool]]:
    """Todas as combinações verdade/falso para uma lista de variáveis."""
    vals = []
    for bits in product([False, True], repeat=len(vars_)):
        vals.append(dict(zip(vars_, bits)))
    return vals


def is_tautology(formula: Formula) -> bool:
    """Verifica se uma fórmula é tautologia (verdadeira em todas as valorizações)."""
    vs = sorted(list(formula.vars()))
    for val in all_valuations(vs):
        if not formula.eval(val):
            return False
    return True


def entails(premises: List[Formula], conclusion: Formula) -> bool:
    """
    Premissas ⊨ conclusão (consequência lógica em CP).

    Definição usada:
        Γ ⊨ φ   sse   (γ1 ∧ γ2 ∧ ... ∧ γn) -> φ  é uma tautologia

    Isto é equivalente à definição pela tabela de verdade original,
    mas é mais simples de implementar e menos sujeito a bugs.
    """
    # sem premissas
    if not premises:
        return is_tautology(conclusion)

    # Faz a conjunção de todas as premissas: γ1 ∧ γ2 ∧ ... ∧ γn
    conj = premises[0]
    for f in premises[1:]:
        conj = And(conj, f)

    # Fórmula (γ1 ∧ ... ∧ γn) -> φ
    impl = Imp(conj, conclusion)

    # Γ ⊨ φ  sse  esta implicação é tautologia
    return is_tautology(impl)


def conseqlog_strings(premises_str: List[str], conclusion_str: str) -> bool:
    """
    Versão Python do  Prolog
    conseqlog_strings(["p imp q", "p"], "q") -> True
    """
    premises = [parse_formula(s) for s in premises_str]
    conclusion = parse_formula(conclusion_str)
    print("Premissas:", premises)
    print("Conclusão:", conclusion)
    return entails(premises, conclusion)


# ==============================
#  TAUTOLOGIA: Truth-table vs SAT
# ==============================

from typing import Dict, List, Tuple, Optional, Set


# --- 1) Eliminar Imp e Iff (eq) para {neg, e, ou} ---
def eliminate_imp_eq(f: Formula) -> Formula:
    """
    Converte Imp e Iff para apenas Neg/And/Or.
      (a imp b)  == (neg a) ou b
      (a eq b)   == (a imp b) e (b imp a)
    """
    if isinstance(f, Var):
        return f
    if isinstance(f, Neg):
        return Neg(eliminate_imp_eq(f.arg))
    if isinstance(f, And):
        return And(eliminate_imp_eq(f.left), eliminate_imp_eq(f.right))
    if isinstance(f, Or):
        return Or(eliminate_imp_eq(f.left), eliminate_imp_eq(f.right))
    if isinstance(f, Imp):
        a = eliminate_imp_eq(f.left)
        b = eliminate_imp_eq(f.right)
        return Or(Neg(a), b)
    if isinstance(f, Iff):
        a = eliminate_imp_eq(f.left)
        b = eliminate_imp_eq(f.right)
        return And(Or(Neg(a), b), Or(Neg(b), a))  # (a->b) ∧ (b->a)
    raise TypeError(f"Tipo de fórmula inesperado: {type(f)}")


# --- 2) Tautologia por tabelas de verdade (como tens) ---
def is_tautology_tt(formula: Formula) -> bool:
    """
    Igual ao teu is_tautology atual: força bruta.
    """
    vs = sorted(list(formula.vars()))
    for val in all_valuations(vs):
        if not formula.eval(val):
            return False
    return True


# --- 3) Tseitin CNF para SAT ---
Clause = List[int]  # ex: [1, -3, 7]
CNF = List[Clause]  # ex: [[1, -3], [2, 3, -4]]


def tseitin_cnf(formula: Formula) -> Tuple[CNF, int]:
    """
    Constrói CNF por Tseitin.
    Retorna (cnf, top_var) onde top_var é o id (positivo) que representa a fórmula.
    Literais: int (positivo = var, negativo = negação da var)
    """
    cnf: CNF = []
    var_ids: Dict[str, int] = {}
    next_id = 1

    def get_var_id(name: str) -> int:
        nonlocal next_id
        if name not in var_ids:
            var_ids[name] = next_id
            next_id += 1
        return var_ids[name]

    def new_aux_var() -> int:
        nonlocal next_id
        v = next_id
        next_id += 1
        return v

    def enc(f: Formula) -> int:
        """
        Devolve um ID positivo que representa a subfórmula f.
        Adiciona cláusulas Tseitin ao cnf para garantir equivalência.
        """
        if isinstance(f, Var):
            return get_var_id(f.name)

        if isinstance(f, Neg):
            a = enc(f.arg)
            x = new_aux_var()
            # x <-> ¬a
            # (¬x ∨ ¬a) ∧ (x ∨ a)
            cnf.append([-x, -a])
            cnf.append([x, a])
            return x

        if isinstance(f, And):
            a = enc(f.left)
            b = enc(f.right)
            x = new_aux_var()
            # x <-> (a ∧ b)
            # (¬x ∨ a) ∧ (¬x ∨ b) ∧ (x ∨ ¬a ∨ ¬b)
            cnf.append([-x, a])
            cnf.append([-x, b])
            cnf.append([x, -a, -b])
            return x

        if isinstance(f, Or):
            a = enc(f.left)
            b = enc(f.right)
            x = new_aux_var()
            # x <-> (a ∨ b)
            # (¬x ∨ a ∨ b) ∧ (x ∨ ¬a) ∧ (x ∨ ¬b)
            cnf.append([-x, a, b])
            cnf.append([x, -a])
            cnf.append([x, -b])
            return x

        # Se chegar aqui, é porque não eliminaste imp/eq antes
        raise TypeError(
            "Tseitin só aceita Var/Neg/And/Or. Usa eliminate_imp_eq() antes."
        )

    top = enc(formula)
    return cnf, top


# --- 4) SAT solver simples (DPLL) ---
def dpll_is_sat(cnf: CNF) -> bool:
    """
    Decide satisfazibilidade de uma CNF (DPLL simples).
    """
    # remove cláusulas triviais duplicadas etc (opcional)
    cnf = [cl[:] for cl in cnf]

    def simplify(cnf: CNF, var: int, value: bool) -> Optional[CNF]:
        """
        Aplica a atribuição var=value e devolve CNF simplificada.
        Se alguma cláusula ficar vazia -> conflito -> None
        """
        lit_true = var if value else -var
        lit_false = -lit_true

        new_cnf: CNF = []
        for clause in cnf:
            if lit_true in clause:
                continue  # cláusula satisfeita
            if lit_false in clause:
                new_clause = [l for l in clause if l != lit_false]
                if len(new_clause) == 0:
                    return None
                new_cnf.append(new_clause)
            else:
                new_cnf.append(clause)
        return new_cnf

    def unit_propagate(cnf: CNF) -> Tuple[Optional[CNF], Dict[int, bool]]:
        """
        Propagação unitária: se existir [l], força l=True.
        """
        assignment: Dict[int, bool] = {}
        changed = True
        while changed:
            changed = False
            unit_lit = None
            for clause in cnf:
                if len(clause) == 1:
                    unit_lit = clause[0]
                    break
            if unit_lit is not None:
                changed = True
                v = abs(unit_lit)
                val = unit_lit > 0
                # se já atribuído em conflito
                if v in assignment and assignment[v] != val:
                    return None, assignment
                assignment[v] = val
                cnf2 = simplify(cnf, v, val)
                if cnf2 is None:
                    return None, assignment
                cnf = cnf2
        return cnf, assignment

    def pure_literal_elim(cnf: CNF) -> Tuple[CNF, Dict[int, bool]]:
        """
        Elimina literais puros (apenas aparece com um sinal).
        """
        counts: Dict[int, int] = {}
        for clause in cnf:
            for lit in clause:
                counts[lit] = counts.get(lit, 0) + 1

        assignment: Dict[int, bool] = {}
        vars_seen: Set[int] = set(abs(l) for l in counts.keys())
        for v in vars_seen:
            pos = counts.get(v, 0)
            neg = counts.get(-v, 0)
            if pos > 0 and neg == 0:
                assignment[v] = True
            elif neg > 0 and pos == 0:
                assignment[v] = False

        for v, val in assignment.items():
            cnf2 = simplify(cnf, v, val)
            if cnf2 is None:
                return [[]], assignment  # força UNSAT
            cnf = cnf2
        return cnf, assignment

    def choose_var(cnf: CNF) -> int:
        for clause in cnf:
            for lit in clause:
                return abs(lit)
        return 1

    def rec(cnf: CNF) -> bool:
        # CNF vazia => SAT
        if not cnf:
            return True
        # cláusula vazia => UNSAT
        if any(len(cl) == 0 for cl in cnf):
            return False

        # unit propagation
        cnf_u, _ = unit_propagate(cnf)
        if cnf_u is None:
            return False
        cnf = cnf_u
        if not cnf:
            return True
        if any(len(cl) == 0 for cl in cnf):
            return False

        # pure literals
        cnf, _ = pure_literal_elim(cnf)
        if not cnf:
            return True
        if any(len(cl) == 0 for cl in cnf):
            return False

        v = choose_var(cnf)

        # tenta v=True
        cnf_t = simplify(cnf, v, True)
        if cnf_t is not None and rec(cnf_t):
            return True

        # tenta v=False
        cnf_f = simplify(cnf, v, False)
        if cnf_f is not None and rec(cnf_f):
            return True

        return False

    return rec(cnf)


# --- 5) Tautologia via SAT: φ é tautologia ⇔ ¬φ é UNSAT ---
def is_tautology_sat(formula: Formula) -> bool:
    """
    Tautologia por SAT:
      φ é tautologia  <=>  ¬φ é UNSAT
    Passos:
      1) elimina imp/eq
      2) constrói ¬φ
      3) Tseitin CNF
      4) testa SAT; se SAT => não é tautologia; se UNSAT => tautologia
    """
    f = eliminate_imp_eq(formula)
    neg_f = Neg(f)
    cnf, top = tseitin_cnf(neg_f)
    cnf.append([top])  # força a fórmula (¬φ) a ser verdadeira
    sat = dpll_is_sat(cnf)
    return not sat


# ==============================
#  Teste rápido no terminal
# ==============================

import time


def benchmark(formula_str):
    f = parse_formula(formula_str)

    print("\n==============================")
    print("Formula com", len(f.vars()), "variaveis")

    # Truth table
    t1 = time.perf_counter()
    r1 = is_tautology_tt(f)
    t2 = time.perf_counter()

    # SAT
    t3 = time.perf_counter()
    r2 = is_tautology_sat(f)
    t4 = time.perf_counter()

    print("TT result:", r1, "tempo:", round(t2 - t1, 4), "s")
    print("SAT result:", r2, "tempo:", round(t4 - t3, 4), "s")


if __name__ == "__main__":
    inp = input(
        "Fórmula para testar tautologia (ex: '(p imp q) eq (neg q imp neg p)'):\n"
    )
    benchmark(inp)
