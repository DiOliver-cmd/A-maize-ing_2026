from dataclasses import dataclass
from typing import Optional


@dataclass
class MazeConfig:
    """Dataclass representing the maze configuration options."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None
    algorithm: str = "backtracker"


def parse_bool(value: str) -> bool:
    """Parse a string representation of a boolean value."""

    val = value.strip().lower()
    if val in ("true", "1", "yes", "y", "t"):
        return True
    if val in ("false", "0", "no", "n", "f"):
        return False
    raise ValueError(f"Valor booleano inválido: '{value}'")


def parse_tuple(value: str) -> tuple[int, int]:
    """Parse a coordinate string in '(x, y)' or 'x,y' format."""

    clean_val = value.replace("(", "").replace(")", "").strip()
    parts = clean_val.split(",")
    if len(parts) != 2:
        raise ValueError(
            f"Coordenadas inválido: '{value}'. Esperado '(x, y)' o 'x,y'."
            )
    return int(parts[0].strip()), int(parts[1].strip())


def parse_config(path: str) -> MazeConfig:
    """Parse the maze configuration from a file."""

    raw_data: dict[str, str] = {}

    with open(path, "r", encoding="utf-8") as file:
        for line_num, line in enumerate(file, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"Line {line_num}: invalid config: '{line}'.")
            key, value = line.split("=", 1)
            raw_data[key.strip().upper()] = value.strip()
    required_keys = [
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
        ]
    missing = [key for key in required_keys if key not in raw_data]
    if missing:
        msg = ", ".join(missing)
        raise ValueError(f"Missing required configuration keys: {msg}.")

    width = int(raw_data["WIDTH"])
    height = int(raw_data["HEIGHT"])
    entry = parse_tuple(raw_data["ENTRY"])
    exit = parse_tuple(raw_data["EXIT"])
    output_file = raw_data["OUTPUT_FILE"]
    perfect = parse_bool(raw_data["PERFECT"])

    seed: Optional[int] = None
    if "SEED" in raw_data and raw_data["SEED"]:
        seed = int(raw_data["SEED"])

    algorithm = raw_data.get("ALGORITHM", "backtracker")

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
        algorithm=algorithm
    )
