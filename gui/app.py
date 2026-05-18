# gui/app.py

import customtkinter as ctk

from logica import BeliefBase

from .theme import COLORS
from .utils import resource_path
from .cp_tab import build_tab_cp
from .partial_meet_tab import build_tab_partial_meet
from .kernel_tab import build_tab_kernel
from .actions import AppActions


class BeliefApp(AppActions, ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            self.iconbitmap(resource_path("favicon.ico"))
        except Exception:
            pass

        self.title("Projeto Crenças – Partial Meet e Kernel")
        self.geometry("1260x760")
        self.minsize(1080, 680)
        self.resizable(True, True)
        self.configure(fg_color=COLORS["bg_main"])

        self.last_operation = None

        self.font_title = ctk.CTkFont(
            family="Segoe UI",
            size=20,
            weight="bold",
        )
        self.font_section = ctk.CTkFont(
            family="Segoe UI",
            size=14,
            weight="bold",
        )
        self.font_body = ctk.CTkFont(
            family="Segoe UI",
            size=12,
        )
        self.font_small = ctk.CTkFont(
            family="Segoe UI",
            size=11,
        )
        self.font_mono = ctk.CTkFont(
            family="Cascadia Code",
            size=12,
        )

        # Cada operador tem a sua própria base.
        self.pm_base = BeliefBase()
        self.kernel_base = BeliefBase()

        self.pm_selected_index: int | None = None
        self.kernel_selected_index: int | None = None

        self.pm_strategy = ctk.StringVar(value="Full meet")
        self.kernel_strategy = ctk.StringVar(value="Comum se existir")

        self._build_ui()

        self._refresh_operator_base_view("pm")
        self._refresh_operator_base_view("kernel")

    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 4))
        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Projeto Crenças",
            font=self.font_title,
            text_color=COLORS["text"],
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header,
            text=(
                "Operadores de Contração em Bases de Crenças — "
                "bases independentes para Partial Meet e Kernel"
            ),
            font=self.font_small,
            text_color=COLORS["muted"],
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 8))

        sep = ctk.CTkFrame(
            header,
            height=2,
            fg_color=COLORS["accent"],
        )
        sep.grid(row=2, column=0, sticky="ew")

        tabs = ctk.CTkTabview(
            self,
            fg_color=COLORS["bg_main"],
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_light"],
            segmented_button_unselected_color="#ffffff",
            segmented_button_unselected_hover_color="#e5e7eb",
            text_color=COLORS["text"],
        )
        tabs.grid(row=1, column=0, sticky="nsew", padx=20, pady=(4, 14))

        tab_pm = tabs.add("Partial Meet")
        tab_kernel = tabs.add("Kernel")
        tab_cp = tabs.add("Cálculo Proposicional")

        for tab in (tab_pm, tab_kernel, tab_cp):
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)

        pm_scroll = ctk.CTkScrollableFrame(
            tab_pm,
            fg_color="transparent",
            corner_radius=0,
        )
        pm_scroll.grid(row=0, column=0, sticky="nsew")
        pm_scroll.grid_columnconfigure(0, weight=1)
        pm_scroll.grid_rowconfigure(0, weight=1)

        kernel_scroll = ctk.CTkScrollableFrame(
            tab_kernel,
            fg_color="transparent",
            corner_radius=0,
        )
        kernel_scroll.grid(row=0, column=0, sticky="nsew")
        kernel_scroll.grid_columnconfigure(0, weight=1)
        kernel_scroll.grid_rowconfigure(0, weight=1)

        cp_scroll = ctk.CTkScrollableFrame(
            tab_cp,
            fg_color="transparent",
            corner_radius=0,
        )
        cp_scroll.grid(row=0, column=0, sticky="nsew")
        cp_scroll.grid_columnconfigure(0, weight=1)
        cp_scroll.grid_rowconfigure(0, weight=1)

        build_tab_partial_meet(self, pm_scroll)
        build_tab_kernel(self, kernel_scroll)
        build_tab_cp(self, cp_scroll)
