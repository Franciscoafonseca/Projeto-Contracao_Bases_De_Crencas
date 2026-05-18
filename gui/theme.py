# gui/theme.py

import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

COLORS = {
    # Fundo geral
    "bg_main": "#f3f6fb",
    # Cartões
    "card": "#ffffff",
    "card_alt": "#f8fafc",
    "surface": "#eef4ff",
    # Texto
    "text": "#0f172a",
    "muted": "#64748b",
    "muted_dark": "#475569",
    # Bordas e campos
    "border": "#d6dee8",
    "border_strong": "#b6c2d1",
    "input": "#f8fafc",
    # Cores principais
    "primary": "#2563eb",
    "primary_light": "#3b82f6",
    # Partial Meet
    "pm": "#7c3aed",
    "pm_light": "#8b5cf6",
    "pm_soft": "#ede9fe",
    # Kernel
    "kernel": "#059669",
    "kernel_light": "#10b981",
    "kernel_soft": "#d1fae5",
    # Ações
    "info": "#0284c7",
    "info_light": "#0ea5e9",
    "info_soft": "#e0f2fe",
    "warning": "#f59e0b",
    "warning_light": "#fbbf24",
    "warning_soft": "#fef3c7",
    "success": "#16a34a",
    "success_light": "#22c55e",
    "success_soft": "#dcfce7",
    "danger": "#dc2626",
    "danger_light": "#ef4444",
    "danger_soft": "#fee2e2",
    "export": "#0f766e",
    "export_light": "#14b8a6",
    "export_soft": "#ccfbf1",
    # Resultados
    "log": "#f8fafc",
    "log_header": "#eaf1fb",
    "log_border": "#dbe4ee",
    # Seleção
    "selected": "#dbeafe",
    # Barra de destaque
    "accent": "#f59e0b",
}

MAX_SAFE_FORMULAS = 12
