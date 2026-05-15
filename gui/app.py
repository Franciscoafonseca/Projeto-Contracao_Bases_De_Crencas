import customtkinter as ctk

from logica import BeliefBase

from .theme import COLORS
from .utils import resource_path
from .base_tab import build_tab_base
from .cp_tab import build_tab_cp
from .actions import AppActions


class BeliefApp(AppActions, ctk.CTk):
    def __init__(self):
        super().__init__()

        try:
            self.iconbitmap(resource_path("favicon.ico"))
        except Exception:
            pass

        self.title("Projeto Crenças – Operadores de Contração em Bases de Crenças")
        self.geometry("1180x700")
        self.minsize(980, 620)
        self.resizable(True, True)
        self.configure(fg_color=COLORS["bg_main"])
        self.last_operation = None
        self.font_title = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        self.font_section = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
        self.font_body = ctk.CTkFont(family="Segoe UI", size=12)
        self.font_small = ctk.CTkFont(family="Segoe UI", size=11)
        self.font_mono = ctk.CTkFont(family="Cascadia Code", size=12)

        self.base = BeliefBase()
        self.selected_index: int | None = None

        self.pm_strategy = ctk.StringVar(value="Full meet")
        self.kernel_strategy = ctk.StringVar(value="Comum se existir")

        self._build_ui()
        self._refresh_base_view()

    def _build_ui(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(8, 2))
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
            text="Operadores de Contração em Bases de Crenças — Partial Meet e Kernel",
            font=self.font_small,
            text_color=COLORS["muted"],
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 6))

        sep = ctk.CTkFrame(header, height=2, fg_color=COLORS["accent"])
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
        tabs.grid(row=1, column=0, sticky="nsew", padx=18, pady=(2, 12))

        tab_base = tabs.add("Base de Crenças")
        tab_cp = tabs.add("Cálculo Proposicional")

        tab_base.grid_rowconfigure(0, weight=1)
        tab_base.grid_columnconfigure(0, weight=1)
        tab_cp.grid_rowconfigure(0, weight=1)
        tab_cp.grid_columnconfigure(0, weight=1)

        base_scroll = ctk.CTkScrollableFrame(
            tab_base,
            fg_color="transparent",
            corner_radius=0,
        )
        base_scroll.grid(row=0, column=0, sticky="nsew")
        base_scroll.grid_columnconfigure(0, weight=1)
        base_scroll.grid_rowconfigure(0, weight=1)

        cp_scroll = ctk.CTkScrollableFrame(
            tab_cp,
            fg_color="transparent",
            corner_radius=0,
        )
        cp_scroll.grid(row=0, column=0, sticky="nsew")
        cp_scroll.grid_columnconfigure(0, weight=1)
        cp_scroll.grid_rowconfigure(0, weight=1)

        build_tab_base(self, base_scroll)
        build_tab_cp(self, cp_scroll)
