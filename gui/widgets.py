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
        border_color=COLORS["border"],
    )


def section_title(
    parent,
    text: str,
    font,
    color_key: str = "accent",
) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(parent, fg_color="transparent", height=28)
    frame.grid_propagate(False)
    frame.pack_propagate(False)
    frame.grid_columnconfigure(1, weight=1)

    bar = ctk.CTkFrame(
        frame,
        width=4,
        height=22,
        fg_color=COLORS.get(color_key, COLORS["accent"]),
        corner_radius=99,
    )
    bar.grid(row=0, column=0, sticky="w", padx=(0, 8))

    label = ctk.CTkLabel(
        frame,
        text=text,
        font=font,
        text_color=COLORS["text"],
        anchor="w",
        height=26,
    )
    label.grid(row=0, column=1, sticky="w")

    return frame


_BUTTON_STYLES = {
    "neutral": {
        "fg": COLORS["primary"],
        "hover": COLORS["primary_hover"],
        "soft": COLORS["primary_soft"],
        "soft_hover": COLORS["primary_soft_hover"],
        "border": COLORS["primary"],
        "text": COLORS["primary"],
    },
    "pm": {
        "fg": COLORS["pm"],
        "hover": COLORS["pm_hover"],
        "soft": COLORS["pm_soft"],
        "soft_hover": COLORS["pm_soft_hover"],
        "border": COLORS["pm"],
        "text": COLORS["pm"],
    },
    "kernel": {
        "fg": COLORS["kernel"],
        "hover": COLORS["kernel_hover"],
        "soft": COLORS["kernel_soft"],
        "soft_hover": COLORS["kernel_soft_hover"],
        "border": COLORS["kernel"],
        "text": COLORS["kernel"],
    },
    "success": {
        "fg": COLORS["success"],
        "hover": COLORS["success_hover"],
        "soft": COLORS["success_soft"],
        "soft_hover": COLORS["success_soft"],
        "border": COLORS["success"],
        "text": COLORS["success"],
    },
    "danger": {
        "fg": COLORS["danger"],
        "hover": COLORS["danger_hover"],
        "soft": COLORS["danger_soft"],
        "soft_hover": COLORS["danger_soft_hover"],
        "border": COLORS["danger"],
        "text": COLORS["danger"],
    },
    "export": {
        "fg": COLORS["export"],
        "hover": COLORS["export_hover"],
        "soft": COLORS["export_soft"],
        "soft_hover": COLORS["export_soft_hover"],
        "border": COLORS["export"],
        "text": COLORS["export"],
    },
}


def action_button(
    parent,
    text: str,
    command,
    font,
    variant: str = "neutral",
    outline: bool = False,
    height: int = 38,
) -> ctk.CTkButton:
    style = _BUTTON_STYLES.get(variant, _BUTTON_STYLES["neutral"])

    if outline:
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            height=height,
            corner_radius=13,
            fg_color="transparent",
            hover_color=style["soft_hover"],
            border_width=1,
            border_color=style["border"],
            text_color=style["text"],
            font=font,
        )

    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        height=height,
        corner_radius=13,
        fg_color=style["fg"],
        hover_color=style["hover"],
        text_color="white",
        font=font,
    )


def primary_button(parent, text: str, command, font) -> ctk.CTkButton:
    return action_button(parent, text, command, font, variant="neutral")


def secondary_button(
    parent,
    text: str,
    command,
    font,
    variant: str = "neutral",
) -> ctk.CTkButton:
    return action_button(
        parent,
        text,
        command,
        font,
        variant=variant,
        outline=True,
    )


def success_button(parent, text: str, command, font) -> ctk.CTkButton:
    return action_button(parent, text, command, font, variant="success")


def danger_button(parent, text: str, command, font) -> ctk.CTkButton:
    return action_button(parent, text, command, font, variant="danger", outline=True)


def pm_button(parent, text: str, command, font) -> ctk.CTkButton:
    return action_button(parent, text, command, font, variant="pm")


def pm_outline_button(parent, text: str, command, font) -> ctk.CTkButton:
    return action_button(parent, text, command, font, variant="pm", outline=True)


def kernel_button(parent, text: str, command, font) -> ctk.CTkButton:
    return action_button(parent, text, command, font, variant="kernel")


def kernel_outline_button(parent, text: str, command, font) -> ctk.CTkButton:
    return action_button(parent, text, command, font, variant="kernel", outline=True)


def explore_button(
    parent,
    text: str,
    command,
    font,
    variant: str = "neutral",
) -> ctk.CTkButton:
    return action_button(
        parent,
        text,
        command,
        font,
        variant=variant,
        outline=True,
    )


def export_button(parent, text: str, command, font) -> ctk.CTkButton:
    return action_button(parent, text, command, font, variant="export", outline=True)
