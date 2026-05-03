# logica/cp_logic.py

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, List, Set

# ============================================================
# ERROS
# ============================================================


class ParseError(Exception):
    """Erro lançado quando uma fórmula não é bem formada."""

    pass


# ============================================================
# AST DAS FÓRMULAS
# ============================================================


@dataclass(frozen=True)
class Formula:
    pass


@dataclass(frozen=True)
class Var(Formula):
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Neg(Formula):
    sub: Formula

    def __str__(self) -> str:
        return f"neg {self.sub}"


@dataclass(frozen=True)
class And(Formula):
    left: Formula
    right: Formula

    def __str__(self) -> str:
        return f"({self.left} e {self.right})"


@dataclass(frozen=True)
class Or(Formula):
    left: Formula
    right: Formula

    def __str__(self) -> str:
        return f"({self.left} ou {self.right})"


@dataclass(frozen=True)
class Imp(Formula):
    left: Formula
    right: Formula

    def __str__(self) -> str:
        return f"({self.left} imp {self.right})"


@dataclass(frozen=True)
class Iff(Formula):
    left: Formula
    right: Formula

    def __str__(self) -> str:
        return f"({self.left} iff {self.right})"


# ============================================================
# NORMALIZAÇÃO / TOKENIZAÇÃO
# ============================================================


def normalize_input(s: str) -> str:
    """
    Aceita algumas variantes comuns e converte para a sintaxe interna:
    neg, e, ou, imp, iff.
    """
    s = s.strip()

    replacements = {
        "¬": " neg ",
        "~": " neg ",
        "∧": " e ",
        "&": " e ",
        "∨": " ou ",
        "|": " ou ",
        "->": " imp ",
        "→": " imp ",
        "<->": " iff ",
        "↔": " iff ",
    }

    for old, new in replacements.items():
        s = s.replace(old, new)

    return " ".join(s.split())


def tokenize(s: str) -> List[str]:
    s = normalize_input(s)
    s = s.replace("(", " ( ").replace(")", " ) ")
    return [tok for tok in s.split() if tok]


# ============================================================
# PARSER
# Precedência:
#   neg
#   e
#   ou
#   imp
#   iff
# ============================================================


class Parser:
    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.pos = 0

    def current(self) -> str | None:
        if self.pos >= len(self.tokens):
            return None
        return self.tokens[self.pos]

    def consume(self, expected: str | None = None) -> str:
        tok = self.current()

        if tok is None:
            raise ParseError("Fim inesperado da fórmula.")

        if expected is not None and tok != expected:
            raise ParseError(f"Esperado '{expected}', mas encontrei '{tok}'.")

        self.pos += 1
        return tok

    def parse(self) -> Formula:
        if not self.tokens:
            raise ParseError("Fórmula vazia.")

        formula = self.parse_iff()

        if self.current() is not None:
            raise ParseError(f"Token inesperado: '{self.current()}'.")

        return formula

    def parse_iff(self) -> Formula:
        left = self.parse_imp()

        while self.current() == "iff":
            self.consume("iff")
            right = self.parse_imp()
            left = Iff(left, right)

        return left

    def parse_imp(self) -> Formula:
        left = self.parse_or()

        if self.current() == "imp":
            self.consume("imp")
            right = self.parse_imp()
            return Imp(left, right)

        return left

    def parse_or(self) -> Formula:
        left = self.parse_and()

        while self.current() == "ou":
            self.consume("ou")
            right = self.parse_and()
            left = Or(left, right)

        return left

    def parse_and(self) -> Formula:
        left = self.parse_neg()

        while self.current() == "e":
            self.consume("e")
            right = self.parse_neg()
            left = And(left, right)

        return left

    def parse_neg(self) -> Formula:
        if self.current() == "neg":
            self.consume("neg")
            return Neg(self.parse_neg())

        return self.parse_atom()

    def parse_atom(self) -> Formula:
        tok = self.current()

        if tok is None:
            raise ParseError("Esperava uma fórmula, mas encontrei fim da entrada.")

        if tok == "(":
            self.consume("(")
            inside = self.parse_iff()
            self.consume(")")
            return inside

        if tok in {"e", "ou", "imp", "iff", ")"}:
            raise ParseError(f"Token inesperado: '{tok}'.")

        self.consume()
        return Var(tok)


def parse_formula(s: str) -> Formula:
    return Parser(tokenize(s)).parse()


def is_cp_formula(s: str) -> bool:
    try:
        parse_formula(s)
        return True
    except ParseError:
        return False


# ============================================================
# SEMÂNTICA
# ============================================================


def atoms(formula: Formula) -> Set[str]:
    if isinstance(formula, Var):
        return {formula.name}

    if isinstance(formula, Neg):
        return atoms(formula.sub)

    if isinstance(formula, (And, Or, Imp, Iff)):
        return atoms(formula.left) | atoms(formula.right)

    raise TypeError(f"Tipo de fórmula desconhecido: {type(formula)}")


def eval_formula(formula: Formula, valuation: Dict[str, bool]) -> bool:
    if isinstance(formula, Var):
        return valuation[formula.name]

    if isinstance(formula, Neg):
        return not eval_formula(formula.sub, valuation)

    if isinstance(formula, And):
        return eval_formula(formula.left, valuation) and eval_formula(
            formula.right, valuation
        )

    if isinstance(formula, Or):
        return eval_formula(formula.left, valuation) or eval_formula(
            formula.right, valuation
        )

    if isinstance(formula, Imp):
        return (not eval_formula(formula.left, valuation)) or eval_formula(
            formula.right, valuation
        )

    if isinstance(formula, Iff):
        return eval_formula(formula.left, valuation) == eval_formula(
            formula.right, valuation
        )

    raise TypeError(f"Tipo de fórmula desconhecido: {type(formula)}")


def all_valuations(atom_names: Set[str]):
    names = sorted(atom_names)

    for values in product([False, True], repeat=len(names)):
        yield dict(zip(names, values))


def is_tautology(formula: Formula) -> bool:
    atom_names = atoms(formula)

    for valuation in all_valuations(atom_names):
        if not eval_formula(formula, valuation):
            return False

    return True


def is_contradiction(formula: Formula) -> bool:
    atom_names = atoms(formula)

    for valuation in all_valuations(atom_names):
        if eval_formula(formula, valuation):
            return False

    return True


def entails(premises: List[Formula], conclusion: Formula) -> bool:
    """
    Γ ⊨ φ
    Isto é: em toda a valoração em que todas as premissas são verdadeiras,
    a conclusão também é verdadeira.
    """
    atom_names: Set[str] = set()

    for p in premises:
        atom_names |= atoms(p)

    atom_names |= atoms(conclusion)

    for valuation in all_valuations(atom_names):
        all_premises_true = all(eval_formula(p, valuation) for p in premises)

        if all_premises_true and not eval_formula(conclusion, valuation):
            return False

    return True


def conseqlog_strings(premises_str: List[str], conclusion_str: str) -> bool:
    premises = [parse_formula(s) for s in premises_str if s.strip()]
    conclusion = parse_formula(conclusion_str)
    return entails(premises, conclusion)
