from .belief_base import BeliefBase

from .cp_logic import (
    ParseError,
    Formula,
    Var,
    Neg,
    And,
    Or,
    Imp,
    Iff,
    parse_formula,
    is_cp_formula,
    is_tautology,
    is_contradiction,
    conseqlog_strings,
)

from .contraction import (
    e_subconjunto,
    conjunto_das_partes,
    implica,
    remainders,
    kernels,
    selecionar_remainders,
    incisao,
    partial_meet_contraction,
    kernel_contraction,
    partial_meet_contraction_with_steps,
    partial_meet_contraction_manual_with_steps,
    kernel_contraction_with_steps,
    kernel_contraction_manual_with_steps,
)
