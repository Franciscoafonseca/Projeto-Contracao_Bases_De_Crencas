# gui/theme.py

import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ============================================================
# TIPOGRAFIA
# ============================================================
# Para experimentar outro aspeto visual, muda apenas esta linha.
# Exemplo: SELECTED_FONT_PRESET = "03_inter"
# O Tk faz fallback automaticamente se alguma fonte não existir no sistema.

SELECTED_FONT_PRESET = "01_segoe_variable"

FONT_PRESETS = {
    # 1. Melhor opção geral para apps modernas no Windows
    "01_segoe_variable": {
        "title": "Segoe UI Variable Display",
        "app": "Segoe UI Variable Text",
        "mono": "Cascadia Code",
    },
    # 2. Muito boa para interface moderna, títulos fortes e limpos
    "02_bahnschrift": {
        "title": "Bahnschrift SemiBold",
        "app": "Bahnschrift",
        "mono": "Cascadia Code",
    },
    # 3. Mais clássica, muito legível e elegante
    "03_calibri_light": {
        "title": "Calibri Light",
        "app": "Calibri",
        "mono": "Consolas",
    },
    # 4. Boa para uma interface suave e menos agressiva
    "04_corbel": {
        "title": "Corbel",
        "app": "Corbel",
        "mono": "Consolas",
    },
    # 5. Boa para leitura, com aspeto mais redondo
    "05_candara": {
        "title": "Candara",
        "app": "Candara",
        "mono": "Consolas",
    },
    # 6. Mais formal/académica
    "06_constantia": {
        "title": "Constantia",
        "app": "Constantia",
        "mono": "Consolas",
    },
    # 7. Muito legível, mas ocupa mais espaço
    "07_verdana": {
        "title": "Verdana",
        "app": "Verdana",
        "mono": "Consolas",
    },
    # 8. Moderna e leve, boa para botões e textos curtos
    "08_trebuchet": {
        "title": "Trebuchet MS",
        "app": "Trebuchet MS",
        "mono": "Consolas",
    },
    # 9. Títulos com mais personalidade
    "09_franklin": {
        "title": "Franklin Gothic Medium",
        "app": "Franklin Gothic Book",
        "mono": "Consolas",
    },
    # 10. Visual mais neutro e compacto
    "10_tahoma": {
        "title": "Tahoma",
        "app": "Tahoma",
        "mono": "Consolas",
    },
    # 11. Alternativa segura e universal
    "11_arial": {
        "title": "Arial",
        "app": "Arial",
        "mono": "Consolas",
    },
    # 12. Mais elegante, mas pode parecer menos “app moderna”
    "12_georgia": {
        "title": "Georgia",
        "app": "Georgia",
        "mono": "Consolas",
    },
    # 13. Boa para interface, parecida com Segoe mas diferente
    "13_leelawadee": {
        "title": "Leelawadee UI",
        "app": "Leelawadee UI",
        "mono": "Cascadia Code",
    },
    # 14. Muito limpa e discreta
    "14_microsoft_sans": {
        "title": "Microsoft Sans Serif",
        "app": "Microsoft Sans Serif",
        "mono": "Consolas",
    },
    # 15. Boa alternativa visual, com títulos elegantes
    "15_sitka": {
        "title": "Sitka Display",
        "app": "Sitka Text",
        "mono": "Consolas",
    },
}

_SELECTED_FONT = FONT_PRESETS.get(
    SELECTED_FONT_PRESET,
    FONT_PRESETS["01_segoe_variable"],
)

TITLE_FONT = _SELECTED_FONT["title"]
APP_FONT = _SELECTED_FONT["app"]
MONO_FONT = _SELECTED_FONT["mono"]
# ============================================================
# CORES
# ============================================================

COLORS = {
    # Estrutura
    "bg": "#f4f6fb",
    "bg_main": "#f4f6fb",
    "card": "#ffffff",
    "card_alt": "#f8fafc",
    "panel": "#ffffff",
    "input": "#ffffff",
    "log": "#ffffff",
    "log_header": "#f8fafc",
    # Texto
    "text": "#111827",
    "text_soft": "#334155",
    "muted": "#64748b",
    "muted_dark": "#334155",
    "border": "#dbe3ef",
    "selected": "#e0f2fe",
    "white": "#ffffff",
    # Tabs / neutro — sem azul dominante
    "tab": "#eef2f7",
    "tab_hover": "#e2e8f0",
    "tab_selected": "#ffffff",
    "tab_selected_hover": "#f8fafc",
    # Neutro / cálculo proposicional
    "primary": "#334155",
    "primary_hover": "#1f2937",
    "primary_light": "#475569",
    "primary_dark": "#0f172a",
    "primary_soft": "#f1f5f9",
    "primary_soft_hover": "#e2e8f0",
    "accent": "#334155",
    # Partial Meet — vermelho principal
    "pm": "#dc2626",
    "pm_hover": "#b91c1c",
    "pm_light": "#ef4444",
    "pm_dark": "#991b1b",
    "pm_soft": "#fff1f2",
    "pm_soft_hover": "#ffe4e6",
    "pm_panel": "#fff7f8",
    "pm_panel_strong": "#ffe4e6",
    "pm_border": "#fecdd3",
    # Cores extra só para a interface Partial Meet, não para o PDF.
    "pm_secondary": "#f97316",
    "pm_secondary_dark": "#c2410c",
    "pm_tertiary": "#7c3aed",
    "pm_tertiary_dark": "#4c1d95",
    "pm_info": "#2563eb",
    "pm_purple_soft": "#f3e8ff",
    "pm_blue_soft": "#dbeafe",
    "pm_green_soft": "#dcfce7",
    # Kernel — verde principal
    "kernel": "#059669",
    "kernel_hover": "#047857",
    "kernel_light": "#10b981",
    "kernel_dark": "#065f46",
    "kernel_soft": "#ecfdf5",
    "kernel_soft_hover": "#d1fae5",
    "kernel_panel": "#f0fdf4",
    "kernel_panel_strong": "#dcfce7",
    "kernel_border": "#a7f3d0",
    # Cores extra só para a interface Kernel, não para o PDF.
    "kernel_secondary": "#0d9488",
    "kernel_secondary_dark": "#0f766e",
    "kernel_tertiary": "#2563eb",
    "kernel_warning": "#ca8a04",
    "kernel_blue_soft": "#dbeafe",
    "kernel_amber_soft": "#fef3c7",
    # Estados
    "success": "#16a34a",
    "success_hover": "#15803d",
    "success_soft": "#f0fdf4",
    "warning": "#f59e0b",
    "warning_hover": "#d97706",
    "warning_soft": "#fffbeb",
    "danger": "#dc2626",
    "danger_hover": "#b91c1c",
    "danger_soft": "#fef2f2",
    "danger_soft_hover": "#fee2e2",
    # Exportação
    "export": "#0f766e",
    "export_hover": "#115e59",
    "export_soft": "#f0fdfa",
    "export_soft_hover": "#ccfbf1",
    # Ações neutras iguais em Partial Meet e Kernel
    "neutral": "#0f172a",
    "neutral_hover": "#1e293b",
    "neutral_dark": "#020617",
    "neutral_soft": "#f1f5f9",
    "neutral_soft_hover": "#e2e8f0",
    "neutral_border": "#cbd5e1",
    "neutral_text": "#0f172a",
    # Menu da função de seleção/incisão
    "choice": "#334155",
    "choice_hover": "#1f2937",
    "choice_button": "#0f172a",
    "choice_button_hover": "#020617",
}

MAX_SAFE_FORMULAS = 12
