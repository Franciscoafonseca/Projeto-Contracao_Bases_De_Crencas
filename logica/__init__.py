# logica/__init__.py
#
# Facilita imports noutros sítios.

from .belief_base import BeliefBase
from .contraction import partial_meet_contraction, kernel_contraction

# ferramentas de cálculo proposicional
from .cp_logic import (
    Formula,
    Var,
    Neg,
    And,
    Or,
    Imp,
    Iff,
    ParseError,
    parse_formula,
    is_cp_formula,
    is_tautology,
    entails,
    conseqlog_strings,
)
