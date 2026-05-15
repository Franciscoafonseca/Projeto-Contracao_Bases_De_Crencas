import customtkinter as ctk

from .theme import COLORS


def make_card(parent, alt: bool = False) -> ctk.CTkFrame:
    return ctk.CTkFrame(
        parent,
        fg_color=COLORS["card_alt" if alt else "card"],
        corner_radius=16,
        border_width=1,
        border_color=COLORS["border"],
    )


def section_title(parent, text: str, font) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(
        parent,
        fg_color="transparent",
        height=24,
    )
    frame.grid_propagate(False)
    frame.pack_propagate(False)

    bar = ctk.CTkFrame(
        frame,
        width=4,
        height=18,
        fg_color=COLORS["accent"],
        corner_radius=99,
    )
    bar.grid(row=0, column=0, sticky="w", padx=(0, 8))

    label = ctk.CTkLabel(
        frame,
        text=text,
        font=font,
        text_color=COLORS["text"],
        height=22,
    )
    label.grid(row=0, column=1, sticky="w")

    return frame


def primary_button(parent, text: str, command, font) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=34,
        corner_radius=10,
        fg_color=COLORS["primary"],
        hover_color=COLORS["primary_light"],
        text_color="white",
        font=font,
    )


def secondary_button(parent, text: str, command, font) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=34,
        corner_radius=10,
        fg_color="transparent",
        hover_color="#e0f2fe",
        border_width=1,
        border_color=COLORS["primary"],
        text_color=COLORS["primary"],
        font=font,
    )


def danger_button(parent, text: str, command, font) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=34,
        corner_radius=10,
        fg_color="transparent",
        hover_color="#fee2e2",
        border_width=1,
        border_color=COLORS["danger"],
        text_color=COLORS["danger"],
        font=font,
    )
