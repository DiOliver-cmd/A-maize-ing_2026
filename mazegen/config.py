"""Read and validate the maze configuration file."""

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


def validate_config(config: MazeConfig) -> None:
    """Check that a parsed configuration describes a buildable maze.

    Args:
        config (MazeConfig): The configuration to check.

    Raises:
        ValueError: If a dimension is not positive, if entry or exit falls
            outside the maze bounds, if entry and exit are the same cell,
            or if the output filename is empty.
    """

    if config.width <= 0:
        raise ValueError(f"WIDTH must be greater than 0, got {config.width}.")
    if config.height <= 0:
        raise ValueError(f"HEIGHT must be greater than 0, got {config.height}.")

    last_x, last_y = config.width - 1, config.height - 1
    for name, (x, y) in (("ENTRY", config.entry), ("EXIT", config.exit)):
        if not (0 <= x < config.width and 0 <= y < config.height):
            raise ValueError(
                f"{name} {x},{y} is outside the maze bounds "
                f"(0,0 to {last_x},{last_y})."
            )

    if config.entry == config.exit:
        raise ValueError(
            f"ENTRY and EXIT must be different cells, "
            f"both are {config.entry[0]},{config.entry[1]}."
        )

    if not config.output_file:
        raise ValueError("OUTPUT_FILE must not be empty.")


def parse_int(key: str, value: str) -> int:
    """Parse an integer value, naming the key in the error message."""

    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{key} must be an integer, got '{value}'.")


def parse_bool(key: str, value: str) -> bool:
    """Parse a string representation of a boolean value."""

    val = value.strip().lower()
    if val in ("true", "1", "yes", "y", "t"):
        return True
    if val in ("false", "0", "no", "n", "f"):
        return False
    raise ValueError(f"{key} must be True or False, got '{value}'.")


def parse_tuple(key: str, value: str) -> tuple[int, int]:
    """Parse a coordinate string in '(x, y)' or 'x,y' format."""

    message = f"{key} must be two integers 'x,y', got '{value}'."
    parts = value.replace("(", "").replace(")", "").split(",")
    if len(parts) != 2:
        raise ValueError(message)
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        raise ValueError(message)


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

    width = parse_int("WIDTH", raw_data["WIDTH"])
    height = parse_int("HEIGHT", raw_data["HEIGHT"])
    entry = parse_tuple("ENTRY", raw_data["ENTRY"])
    exit = parse_tuple("EXIT", raw_data["EXIT"])
    output_file = raw_data["OUTPUT_FILE"]
    perfect = parse_bool("PERFECT", raw_data["PERFECT"])

    seed: Optional[int] = None
    if "SEED" in raw_data and raw_data["SEED"]:
        seed = parse_int("SEED", raw_data["SEED"])

    algorithm = raw_data.get("ALGORITHM", "backtracker")

    config = MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
        algorithm=algorithm
    )
    validate_config(config)
    return config
