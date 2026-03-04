# from textual.app import App, ComposeResult
# from textual.widgets import Footer, Log, Input, Button, Static
# from textual.containers import Horizontal, Vertical

# from logica.belief_base import BeliefBase
# from logica.contraction import partial_meet_contraction, kernel_contraction

# # class BeliefApp(App):
# #     """Aplicação tipo Prolog, estilizada em Textual."""

# #     TITLE = "Projeto Crenças"
# #     SUB_TITLE = "Operadores de Contração em Bases de Crenças"

# #     ENABLE_COMMAND_PALETTE = False

# #     CSS = """
# #     Screen {
# #         background: #020617;  /* cinzento quase preto */
# #         color: #e5e7eb;       /* cinza claro */
# #     }

# #     #root {
# #         height: 1fr;
# #     }

# #     #top-bar {
# #         height: 3;
# #         background: #0f172a;
# #         color: #e5e7eb;
# #         content-align: left middle;
# #         padding: 0 2;
# #         text-style: bold;
# #         border-bottom: heavy #1e293b;
# #     }

# #     #subtitle {
# #         color: #9ca3af;
# #         text-style: italic;
# #         padding-left: 2;
# #     }

# #     #main {
# #         height: 1fr;
# #     }

# #     #left, #right {
# #         padding: 1;
# #     }

# #     #left {
# #         width: 2fr;
# #         border: tall #374151;
# #     }

# #     #right {
# #         width: 1fr;
# #         border: tall #4b5563;
# #     }

# #     #title-base, #title-out {
# #         height: 3;
# #         content-align: left middle;
# #         padding: 0 1;
# #         text-style: bold;
# #         background: #111827;
# #         color: #e5e7eb;
# #     }

# #     #log-base, #log-out {
# #         background: #020617;
# #     }

# #     #cmd-label {
# #         padding: 0 1;
# #     }

# #     #cmd-input {
# #         margin: 1 1 0 1;
# #     }

# #     #btn-run {
# #         margin: 1 1 1 1;
# #     }
# #     """

# #     def __init__(self):
# #         super().__init__()
# #         self.base = BeliefBase()

# #     # ---------- Layout ----------

# #     def compose(self) -> ComposeResult:
# #         # Barra superior personalizada (sem Header padrão)
# #         with Vertical(id="root"):
# #             with Vertical(id="top-bar"):
# #                 yield Static("Projeto Crenças", id="app-title")
# #                 yield Static("Operadores de Contração em Bases de Crenças", id="subtitle")

# #             with Horizontal(id="main"):
# #                 # Painel esquerdo: base de crenças
# #                 with Vertical(id="left"):
# #                     yield Static("Base de Crenças", id="title-base")
# #                     self.log_base = Log(id="log-base")
# #                     yield self.log_base

# #                 # Painel direito: saída + comandos
# #                 with Vertical(id="right"):
# #                     yield Static("Saída / Mensagens", id="title-out")
# #                     self.log_out = Log(id="log-out")
# #                     yield self.log_out

# #                     yield Static(
# #                         "Comando (ex: add p->q, contract p, help)",
# #                         id="cmd-label",
# #                     )
# #                     self.input_cmd = Input(
# #                         placeholder="add p, remove 1, contract p, show, help, quit",
# #                         id="cmd-input",
# #                     )
# #                     yield self.input_cmd

# #                     yield Button("Executar", id="btn-run")

# #             yield Footer()

# #     async def on_mount(self) -> None:
# #         self._refresh_base()
# #         self.log_out.write("Bem-vindo ao sistema de bases de crenças.")
# #         self.log_out.write("Escreve 'help' para ver os comandos.")
# #         # foco no campo de comando (sem await)
# #         self.set_focus(self.input_cmd)

# #     # ---------- Lógica de apoio ----------

# #     def _refresh_base(self) -> None:
# #         self.log_base.clear()
# #         if self.base.is_empty():
# #             self.log_base.write("(base vazia)")
# #         else:
# #             for i, f in enumerate(self.base.formulas, start=1):
# #                 self.log_base.write(f"{i}. {f}")

# #     async def _handle_command(self, cmd: str) -> None:
# #         cmd = cmd.strip()
# #         if not cmd:
# #             return

# #         parts = cmd.split(maxsplit=1)
# #         op = parts[0].lower()
# #         arg = parts[1] if len(parts) > 1 else ""

# #         if op == "add":
# #             if not arg:
# #                 self.log_out.write("Uso: add <fórmula>")
# #                 return
# #             self.base.add(arg)
# #             self._refresh_base()
# #             self.log_out.write(f"Adicionada: {arg}")

# #         elif op == "remove":
# #             if not arg.isdigit():
# #                 self.log_out.write("Uso: remove <índice>")
# #                 return
# #             idx = int(arg) - 1
# #             if self.base.remove_index(idx):
# #                 self._refresh_base()
# #                 self.log_out.write(f"Removida fórmula nº {arg}")
# #             else:
# #                 self.log_out.write("Índice inválido.")

# #         elif op == "show":
# #             self._refresh_base()
# #             self.log_out.write("Base atualizada no painel esquerdo.")

# #         elif op == "contract":
# #             if not arg:
# #                 self.log_out.write("Uso: contract <fórmula>")
# #                 return
# #             self.base = partial_meet_contraction(self.base, arg)
# #             self._refresh_base()
# #             self.log_out.write(f"Contração Partial Meet aplicada a {arg}")

# #         elif op == "contract_ker":
# #             if not arg:
# #                 self.log_out.write("Uso: contract_ker <fórmula>")
# #                 return
# #             self.base = kernel_contraction(self.base, arg)
# #             self._refresh_base()
# #             self.log_out.write(f"Contração Kernel aplicada a {arg}")

# #         elif op == "help":
# #             self.log_out.write(
# #                 "Comandos:\n"
# #                 "  add φ             - adiciona fórmula\n"
# #                 "  remove i          - remove fórmula nº i (1,2,...)\n"
# #                 "  show              - mostra/atualiza base\n"
# #                 "  contract φ        - contração Partial Meet (simples)\n"
# #                 "  contract_ker φ    - contração Kernel (simples)\n"
# #                 "  help              - mostra esta ajuda\n"
# #                 "  quit              - sair"
# #             )

# #         elif op in ("quit", "exit"):
# #             await self.action_quit()

# #         else:
# #             self.log_out.write(f"Comando desconhecido: {op}")

# #     # ---------- Eventos da interface ----------

# #     async def on_button_pressed(self, event: Button.Pressed) -> None:
# #         if event.button.id == "btn-run":
# #             cmd = self.input_cmd.value
# #             self.input_cmd.value = ""
# #             await self._handle_command(cmd)

# #     async def on_input_submitted(self, event: Input.Submitted) -> None:
# #         if event.input.id == "cmd-input":
# #             cmd = event.value
# #             self.input_cmd.value = ""
# #             await self._handle_command(cmd)


# # if __name__ == "__main__":
# #     BeliefApp().run()

# # test_sp_terminal.py
# #
# # Executa testes no terminal para o Sistema de Sequentes (Sp) e para o parser CP.
# # Usa:
# #   - parse_formula(s)      -> Formula
# #   - is_tautology_sp(phi)  -> bool     (tautologia via Sp)
# #   - conseqlog(prem, conc) -> bool     (Γ ⊨ φ via Sp)
# #
# # Como correr:
# #   python test_sp_terminal.py
# #
# # Exemplos de input:
# #   taut (p ou neg p)
# #   taut (p imp q)
# #   ent p imp q; p |- q
# #   parse (p e (q ou r))
# #   quit

# from __future__ import annotations

# from logica.cp_logic import parse_formula, ParseError
# from logica.cp_logic import is_tautology, conseqlog, conseqlog_strings
# from logica.contraction import partial_meet_contraction, kernel_contraction


# HELP = """
# Comandos:
#   help
#       Mostra esta ajuda.

#   taut <formula>
#       Testa se <formula> é tautologia usando o Sistema Sp.
#       Ex: taut (p ou neg p)

#   ent <premissas> |- <conclusao>
#       Testa se as premissas implicam a conclusão (Γ ⊨ φ) usando o Sistema Sp.
#       Premissas separadas por ';'
#       Ex: ent p imp q; p |- q

#   parse <formula>
#       Faz parsing e mostra a fórmula normalizada (print da árvore).
#       Ex: parse (p e (q ou r))

#   quit
#       Sair.
# """

# def parse_premises(premises_str: str):
#     parts = [p.strip() for p in premises_str.split(";") if p.strip()]
#     return [parse_formula(p) for p in parts]


# def repl():
#     print("=== Testador do Sistema Sp (Sequentes) ===")
#     print("Escreve 'help' para ver os comandos.")
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

#         # taut <formula>
#         if line.startswith("taut "):
#             s = line[len("taut "):].strip()
#             try:
#                 f = parse_formula(s)
#             except ParseError as e:
#                 print(f"[ERRO] Fórmula inválida: {e}")
#                 continue

#             res = is_tautology(f)
#             print(f"[TAUTOLOGIA] {res}")
#             continue

#         # parse <formula>
#         if line.startswith("parse "):
#             s = line[len("parse "):].strip()
#             try:
#                 f = parse_formula(s)
#             except ParseError as e:
#                 print(f"[ERRO] Fórmula inválida: {e}")
#                 continue
#             print(f"[OK] {f}")
#             continue

#         # ent <premissas> |- <conclusao>
#         if line.startswith("ent "):
#             rest = line[len("ent "):].strip()
#             if "|-" not in rest:
#                 print("[ERRO] Formato: ent <premissas> |- <conclusao>")
#                 continue

#             prem_str, concl_str = rest.split("|-", 1)
#             prem_str = prem_str.strip()
#             concl_str = concl_str.strip()

#             try:
#                 premises = parse_premises(prem_str)
#                 conclusion = parse_formula(concl_str)
#             except ParseError as e:
#                 print(f"[ERRO] Sintaxe inválida: {e}")
#                 continue

#             res = conseqlog_strings(premises, conclusion)
#             print(f"[ENTAILS] {res}   (Γ ⊨ φ)")
#             continue

#         print("[ERRO] Comando desconhecido. Escreve 'help'.")


# if __name__ == "__main__":
#     repl()
# def inclusion(A, Cn):
#     CnA = Cn(A)
#     for formula in A:
#         if formula not in CnA:
#             return False
#     return True


# def Cn(A):
#     consequences = set(A)

#     if "p" in A and "p -> q" in A:
#         consequences.add("q")
#     return consequences


# A = {"p", "p -> g", "hf hs2"}

# print(inclusion(A, Cn))  # True

from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Set, Iterable
from dataclasses import dataclass
from itertools import product
import re

# ==================================
# ---------- BASES -----------------
# ==================================


# ---------- Classe base ----------
class Formula:
    def vars(self) -> Set[str]:
        """Conjunto das variáveis proposicionais usadas na fórmula."""
        raise NotImplementedError

    def eval(self, val: Dict[str, bool]) -> bool:
        """Avalia a fórmula numa valoração val[p] = True/False."""
        raise NotImplementedError


# ---------- determinacao variavel ----------
@dataclass(frozen=True)
class Var(Formula):
    name: str

    def vars(self) -> Set[str]:
        return {self.name}

    def eval(self, val: Dict[str, bool]) -> bool:
        return bool(val[self.name])

    def __str__(self) -> str:
        return self.name


# ---------- funcao negacao ----------
@dataclass(frozen=True)
class Neg(Formula):
    arg: Formula

    def vars(self) -> Set[str]:
        return self.arg.vars()

    def eval(self, val: Dict[str, bool]) -> bool:
        return not self.arg.eval(val)

    def __str__(self) -> str:
        return f"neg {self.arg}"


# ---------- funcao e ----------
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


# ---------- funcao ou ----------
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


# ---------- funcao implicacao ----------
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


# ---------- funcao equivalente ----------
@dataclass(frozen=True)
class Eqv(Formula):
    left: Formula
    right: Formula

    def vars(self) -> Set[str]:
        return self.left.vars() | self.right.vars()

    def eval(self, val: Dict[str, bool]) -> bool:
        return self.left.eval(val) == self.right.eval(val)

    def __str__(self) -> str:
        return f"({self.left} eq {self.right})"


# ---------- Tabelas de verdade ----------
def all_valuations(vars_: List[str]) -> List[Dict[str, bool]]:
    """Todas as combinações verdade/falso para uma lista de variáveis."""
    vals = []
    for bits in product([False, True], repeat=len(vars_)):
        vals.append(dict(zip(vars_, bits)))
    return vals


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
    numa árvore Formula (Var, Neg, And, Or, Imp, Eqv).
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
                left = Eqv(left, right)
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


# ==================================
# ------- DESENVOLVIMENTO ----------
# ==================================


# --- 1) Eliminar Imp e Eqv (eq) para {neg, e, ou} ---
def eliminate_imp_eq(f: Formula) -> Formula:
    """
    Converte Imp e Eqv para apenas Neg/And/Or.
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
    if isinstance(f, Eqv):
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
# ---------- Teste ------------
# ==============================

import multiprocessing
import time


def run_tt(formula_str, queue):
    f = parse_formula(formula_str)
    res = is_tautology_tt(f)
    queue.put(("TT", res))


def run_sat(formula_str, queue):
    f = parse_formula(formula_str)
    res = is_tautology_sat(f)
    queue.put(("SAT", res))


def is_tautology_race(formula_str):
    queue = multiprocessing.Queue()

    p1 = multiprocessing.Process(target=run_tt, args=(formula_str, queue))
    p2 = multiprocessing.Process(target=run_sat, args=(formula_str, queue))

    p1.start()
    p2.start()

    method, result = queue.get()  # primeiro que terminar

    # terminar o outro processo
    p1.terminate()
    p2.terminate()

    return method, result


if __name__ == "__main__":
    formula = input("Fórmula para testar tautologia: \n")
    start = time.perf_counter()
    method, result = is_tautology_race(formula)
    end = time.perf_counter()

    print("Metodo vencedor:", method)
    print("Resultado:", result)
    print("Tempo:", round(end - start, 4), "s")


# def benchmark(formula_str):
#     f = parse_formula(formula_str)

#     print("\n==============================")
#     print("Formula com", len(f.vars()), "variaveis")

#     # Truth table
#     t1 = time.perf_counter()
#     r1 = is_tautology_tt(f)
#     t2 = time.perf_counter()

#     # SAT
#     t3 = time.perf_counter()
#     r2 = is_tautology_sat(f)
#     t4 = time.perf_counter()

#     print("TT result:", r1, "tempo:", round(t2 - t1, 4), "s")
#     print("SAT result:", r2, "tempo:", round(t4 - t3, 4), "s")


# if __name__ == "__main__":
#     inp = input(
#         "Fórmula para testar tautologia (ex: '(p imp q) eq (neg q imp neg p)'):\n"
#     )
#     benchmark(inp)
