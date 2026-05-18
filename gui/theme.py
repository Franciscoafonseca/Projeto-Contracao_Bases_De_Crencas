# gui/theme.py

import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# O Tk faz fallback automaticamente se alguma fonte não existir.
# Fontes modernas no Windows.
# Se alguma não existir, o Tk faz fallback automaticamente.

TITLE_FONT = "Segoe UI Variable Display"
APP_FONT = "Segoe UI Variable Text"
MONO_FONT = "Cascadia Code"

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
    # Tabs / neutro — sem azul
    "tab": "#eef2f7",
    "tab_hover": "#e2e8f0",
    "tab_selected": "#ffffff",
    "tab_selected_hover": "#f8fafc",
    # Neutro / cálculo proposicional — sem azul
    "primary": "#334155",
    "primary_hover": "#1f2937",
    "primary_light": "#475569",
    "primary_dark": "#0f172a",
    "primary_soft": "#f1f5f9",
    "primary_soft_hover": "#e2e8f0",
    "accent": "#334155",
    # Partial Meet — vermelho
    "pm": "#dc2626",
    "pm_hover": "#b91c1c",
    "pm_light": "#ef4444",
    "pm_dark": "#991b1b",
    "pm_soft": "#fff1f2",
    "pm_soft_hover": "#ffe4e6",
    "pm_panel": "#fff7f8",
    "pm_panel_strong": "#ffe4e6",
    "pm_border": "#fecdd3",
    # Kernel — verde
    "kernel": "#059669",
    "kernel_hover": "#047857",
    "kernel_light": "#10b981",
    "kernel_dark": "#065f46",
    "kernel_soft": "#ecfdf5",
    "kernel_soft_hover": "#d1fae5",
    "kernel_panel": "#f0fdf4",
    "kernel_panel_strong": "#dcfce7",
    "kernel_border": "#a7f3d0",
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
}

MAX_SAFE_FORMULAS = 12
