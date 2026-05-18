# logica/contractions/__init__.py

from .common import (
    normalizar_formula,
    e_subconjunto,
    conjunto_das_partes,
    implica,
    intersecao_de_conjuntos,
    format_base_text,
    format_set_text,
    format_set_of_sets_text,
)

from .partial_meet import (
    conjuntos_que_nao_implicam,
    maximais_por_inclusao,
    remainders,
    selecionar_remainders,
    partial_meet_contraction,
    partial_meet_contraction_with_steps,
    partial_meet_contraction_manual_with_steps,
)

from .kernel import (
    conjuntos_que_implicam,
    minimais_por_inclusao,
    kernels,
    hitting_set_valido,
    incisao_minima,
    incisao,
    kernel_contraction,
    kernel_contraction_with_steps,
    kernel_contraction_manual_with_steps,
)

from .exhaustive import (
    partial_meet_all_selection_options,
    kernel_all_incision_options,
)
