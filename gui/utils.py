import sys
from pathlib import Path


def resource_path(relative: str) -> str:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return str(base_path / relative)


def normalize_formula_text(text: str) -> str:
    s = text.strip()
    s = s.replace("->", " imp ")
    s = s.replace("→", " imp ")
    s = s.replace("¬", " neg ")
    s = s.replace("~", " neg ")
    s = " ".join(s.split())
    return s


def split_formulas(text: str) -> list[str]:
    return [
        normalize_formula_text(part)
        for part in text.split(";")
        if normalize_formula_text(part)
    ]
