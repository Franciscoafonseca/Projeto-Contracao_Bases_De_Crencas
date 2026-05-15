import json
from pathlib import Path


def save_base_json(path: str | Path, formulas: list[str]) -> None:
    data = {
        "version": 1,
        "type": "belief_base",
        "formulas": formulas,
    }

    path = Path(path)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_base_json(path: str | Path) -> list[str]:
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("type") != "belief_base":
        raise ValueError("O ficheiro não contém uma base de crenças válida.")

    formulas = data.get("formulas")

    if not isinstance(formulas, list):
        raise ValueError("O campo 'formulas' é inválido.")

    return [str(f).strip() for f in formulas if str(f).strip()]


def save_base_txt(path: str | Path, formulas: list[str]) -> None:
    path = Path(path)

    with path.open("w", encoding="utf-8") as f:
        for formula in formulas:
            f.write(str(formula).strip() + "\n")


def load_base_txt(path: str | Path) -> list[str]:
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        content = f.read()

    # Aceita fórmulas separadas por linhas ou por ;
    raw_parts: list[str] = []

    for line in content.splitlines():
        line = line.strip()

        if not line:
            continue

        # Permite comentários em ficheiros .txt
        if line.startswith("#"):
            continue

        raw_parts.extend(line.split(";"))

    return [part.strip() for part in raw_parts if part.strip()]


def save_base(path: str | Path, formulas: list[str]) -> None:
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".json":
        save_base_json(path, formulas)
        return

    if suffix == ".txt":
        save_base_txt(path, formulas)
        return

    raise ValueError("Formato não suportado. Usa .json ou .txt.")


def load_base(path: str | Path) -> list[str]:
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".json":
        return load_base_json(path)

    if suffix == ".txt":
        return load_base_txt(path)

    raise ValueError("Formato não suportado. Usa .json ou .txt.")
