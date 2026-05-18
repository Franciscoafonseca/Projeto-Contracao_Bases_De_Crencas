# gui/widgets.py

import customtkinter as ctk

from .theme import COLORS


def make_card(parent, alt: bool = False) -> ctk.CTkFrame:
    return ctk.CTkFrame(
        parent,
        fg_color=COLORS["card_alt" if alt else "card"],
        corner_radius=18,
        border_width=1,
        border_color=COLORS["border"],
    )


def make_log_card(parent) -> ctk.CTkFrame:
    return ctk.CTkFrame(
        parent,
        fg_color=COLORS["log"],
        corner_radius=18,
        border_width=1,
        border_color=COLORS["log_border"],
    )


def section_title(
    parent,
    text: str,
    font,
    color_key: str = "accent",
) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(
        parent,
        fg_color="transparent",
        height=26,
    )
    frame.grid_propagate(False)
    frame.pack_propagate(False)

    bar = ctk.CTkFrame(
        frame,
        width=5,
        height=20,
        fg_color=COLORS.get(color_key, COLORS["accent"]),
        corner_radius=99,
    )
    bar.grid(row=0, column=0, sticky="w", padx=(0, 8))

    label = ctk.CTkLabel(
        frame,
        text=text,
        font=font,
        text_color=COLORS["text"],
        height=24,
    )
    label.grid(row=0, column=1, sticky="w")

    return frame


def solid_button(
    parent,
    text: str,
    command,
    font,
    color_key: str,
) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=36,
        corner_radius=12,
        fg_color=COLORS[color_key],
        hover_color=COLORS.get(f"{color_key}_light", COLORS[color_key]),
        text_color="white",
        font=font,
    )


def outline_button(
    parent,
    text: str,
    command,
    font,
    color_key: str,
) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=36,
        corner_radius=12,
        fg_color="transparent",
        hover_color=COLORS.get(f"{color_key}_soft", "#e5e7eb"),
        border_width=1,
        border_color=COLORS[color_key],
        text_color=COLORS[color_key],
        font=font,
    )


def primary_button(parent, text: str, command, font) -> ctk.CTkButton:
    return solid_button(parent, text, command, font, "primary")


def secondary_button(parent, text: str, command, font) -> ctk.CTkButton:
    return outline_button(parent, text, command, font, "info")


def danger_button(parent, text: str, command, font) -> ctk.CTkButton:
    return outline_button(parent, text, command, font, "danger")


def success_button(parent, text: str, command, font) -> ctk.CTkButton:
    return solid_button(parent, text, command, font, "success")


def pm_button(parent, text: str, command, font) -> ctk.CTkButton:
    return solid_button(parent, text, command, font, "pm")


def kernel_button(parent, text: str, command, font) -> ctk.CTkButton:
    return solid_button(parent, text, command, font, "kernel")


def explore_button(parent, text: str, command, font) -> ctk.CTkButton:
    return solid_button(parent, text, command, font, "warning")


def export_button(parent, text: str, command, font) -> ctk.CTkButton:
    return solid_button(parent, text, command, font, "export")
