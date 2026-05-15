import customtkinter as ctk
from tkinter import messagebox

from .theme import COLORS
from .widgets import primary_button, secondary_button


def choose_remainders_manual(
    parent,
    rems: list[list[str]],
    font_section,
    font_small,
) -> list[list[str]] | None:
    if not rems:
        messagebox.showwarning(
            "Sem remainders",
            "Não existem remainders para selecionar.",
        )
        return None

    dialog = ctk.CTkToplevel(parent)
    dialog.title("Seleção manual de remainders")
    dialog.geometry("620x460")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.configure(fg_color=COLORS["bg_main"])

    dialog.grid_rowconfigure(1, weight=1)
    dialog.grid_columnconfigure(0, weight=1)

    title = ctk.CTkLabel(
        dialog,
        text="Escolhe os remainders que γ deve selecionar",
        font=font_section,
        text_color=COLORS["text"],
    )
    title.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

    scroll = ctk.CTkScrollableFrame(
        dialog,
        fg_color=COLORS["card"],
        corner_radius=14,
        border_width=1,
        border_color=COLORS["border"],
    )
    scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 10))
    scroll.grid_columnconfigure(0, weight=1)

    vars_remainders: list[ctk.BooleanVar] = []

    for i, remainder in enumerate(rems, start=1):
        var = ctk.BooleanVar(value=True)
        vars_remainders.append(var)

        content = "; ".join(remainder) if remainder else "∅"

        checkbox = ctk.CTkCheckBox(
            scroll,
            text=f"R{i} = {{ {content} }}",
            variable=var,
            font=font_small,
            text_color=COLORS["text"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_light"],
        )
        checkbox.grid(row=i - 1, column=0, sticky="w", padx=12, pady=6)

    result: dict[str, list[list[str]] | None] = {"selected": None}

    def confirmar() -> None:
        selected = [rems[i] for i, var in enumerate(vars_remainders) if var.get()]

        if not selected:
            messagebox.showwarning(
                "Seleção inválida",
                "Tens de escolher pelo menos um remainder.",
                parent=dialog,
            )
            return

        result["selected"] = selected
        dialog.destroy()

    def cancelar() -> None:
        result["selected"] = None
        dialog.destroy()

    buttons = ctk.CTkFrame(dialog, fg_color="transparent")
    buttons.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
    buttons.grid_columnconfigure((0, 1), weight=1)

    secondary_button(
        buttons,
        "Cancelar",
        cancelar,
        font_small,
    ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

    primary_button(
        buttons,
        "Aplicar seleção",
        confirmar,
        font_small,
    ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    parent.wait_window(dialog)

    return result["selected"]


def choose_kernel_incision_manual(
    parent,
    kerns: list[list[str]],
    base_formulas: list[str],
    font_section,
    font_small,
) -> list[str] | None:
    """
    Abre uma janela para o utilizador escolher manualmente
    a incisão σ, isto é, as fórmulas a remover na Kernel Contraction.
    """

    if not kerns:
        messagebox.showwarning(
            "Sem kernels",
            "Não existem kernels para selecionar uma incisão.",
        )
        return None

    dialog = ctk.CTkToplevel(parent)
    dialog.title("Incisão manual de kernels")
    dialog.geometry("720x540")
    dialog.transient(parent)
    dialog.grab_set()
    dialog.configure(fg_color=COLORS["bg_main"])

    dialog.grid_rowconfigure(2, weight=1)
    dialog.grid_columnconfigure(0, weight=1)

    title = ctk.CTkLabel(
        dialog,
        text="Escolhe as fórmulas que σ deve remover",
        font=font_section,
        text_color=COLORS["text"],
    )
    title.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))

    subtitle = ctk.CTkLabel(
        dialog,
        text=(
            "A escolha é válida se pelo menos uma fórmula de cada kernel "
            "for selecionada."
        ),
        font=font_small,
        text_color=COLORS["muted"],
        wraplength=660,
        justify="center",
    )
    subtitle.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))

    body = ctk.CTkFrame(dialog, fg_color="transparent")
    body.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 10))
    body.grid_rowconfigure(0, weight=1)
    body.grid_columnconfigure(0, weight=1)
    body.grid_columnconfigure(1, weight=1)

    # -------------------------
    # Lado esquerdo: kernels
    # -------------------------
    kernels_frame = ctk.CTkScrollableFrame(
        body,
        fg_color=COLORS["card"],
        corner_radius=14,
        border_width=1,
        border_color=COLORS["border"],
    )
    kernels_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    kernels_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        kernels_frame,
        text="Kernels encontrados",
        font=font_section,
        text_color=COLORS["primary"],
    ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

    for i, kernel in enumerate(kerns, start=1):
        content = "; ".join(kernel) if kernel else "∅"

        label = ctk.CTkLabel(
            kernels_frame,
            text=f"K{i} = {{ {content} }}",
            font=font_small,
            text_color=COLORS["text"],
            anchor="w",
            justify="left",
            wraplength=300,
        )
        label.grid(row=i, column=0, sticky="ew", padx=12, pady=4)

    # -------------------------
    # Lado direito: fórmulas
    # -------------------------
    formulas_frame = ctk.CTkScrollableFrame(
        body,
        fg_color=COLORS["card"],
        corner_radius=14,
        border_width=1,
        border_color=COLORS["border"],
    )
    formulas_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
    formulas_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        formulas_frame,
        text="Fórmulas candidatas a remover",
        font=font_section,
        text_color=COLORS["primary"],
    ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

    # Só faz sentido mostrar fórmulas que aparecem em pelo menos um kernel.
    formulas_em_kernels = {formula for kernel in kerns for formula in kernel}

    candidates = [
        formula for formula in base_formulas if formula in formulas_em_kernels
    ]

    vars_formulas: list[ctk.BooleanVar] = []

    for i, formula in enumerate(candidates, start=1):
        var = ctk.BooleanVar(value=False)
        vars_formulas.append(var)

        checkbox = ctk.CTkCheckBox(
            formulas_frame,
            text=formula,
            variable=var,
            font=font_small,
            text_color=COLORS["text"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_light"],
        )
        checkbox.grid(row=i, column=0, sticky="w", padx=12, pady=6)

    result: dict[str, list[str] | None] = {"selected": None}

    def is_valid_hitting_set(selected: list[str]) -> bool:
        selected_set = set(selected)
        return all(selected_set.intersection(set(kernel)) for kernel in kerns)

    def confirmar() -> None:
        selected = [candidates[i] for i, var in enumerate(vars_formulas) if var.get()]

        if not selected:
            messagebox.showwarning(
                "Incisão inválida",
                "Tens de escolher pelo menos uma fórmula.",
                parent=dialog,
            )
            return

        if not is_valid_hitting_set(selected):
            messagebox.showwarning(
                "Incisão inválida",
                "A tua seleção não toca em todos os kernels.",
                parent=dialog,
            )
            return

        result["selected"] = selected
        dialog.destroy()

    def cancelar() -> None:
        result["selected"] = None
        dialog.destroy()

    buttons = ctk.CTkFrame(dialog, fg_color="transparent")
    buttons.grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 16))
    buttons.grid_columnconfigure((0, 1), weight=1)

    secondary_button(
        buttons,
        "Cancelar",
        cancelar,
        font_small,
    ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

    primary_button(
        buttons,
        "Aplicar incisão",
        confirmar,
        font_small,
    ).grid(row=0, column=1, sticky="ew", padx=(6, 0))

    parent.wait_window(dialog)

    return result["selected"]
