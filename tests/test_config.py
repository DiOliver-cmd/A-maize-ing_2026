"""Tests for MazeConfig dataclass and config parsing."""

from pathlib import Path
import pytest
from mazegen.config import MazeConfig, parse_config


def test_maze_config_instantiation() -> None:
    """Test valid MazeConfig dataclass creation."""
    config = MazeConfig(
        width=10,
        height=10,
        entry=(0, 0),
        exit=(9, 9),
        output_file="out.txt",
        perfect=True,
        seed=42,
    )
    assert config.width == 10
    assert config.height == 10
    assert config.entry == (0, 0)
    assert config.exit == (9, 9)
    assert config.output_file == "out.txt"
    assert config.perfect is True
    assert config.seed == 42


def test_parse_config_valid_file(tmp_path: Path) -> None:
    """Test parsing a valid config file."""
    config_file = tmp_path / "config.txt"
    config_content = (
        "WIDTH=20\n"
        "HEIGHT=15\n"
        "ENTRY=0,0\n"
        "EXIT=19,14\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=True\n"
        "SEED=42\n"
    )
    config_file.write_text(config_content)

    config = parse_config(str(config_file))
    assert config.width == 20
    assert config.height == 15
    assert config.entry == (0, 0)
    assert config.exit == (19, 14)
    assert config.output_file == "maze.txt"
    assert config.perfect is True
    assert config.seed == 42

@pytest.mark.xfail(reason="Aguardando implementação da T1.2 pela dupla")
def test_parse_config_invalid_dimensions(tmp_path: Path) -> None:
    ...

def test_parse_config_invalid_dimensions(tmp_path: Path) -> None:
    """Test that invalid dimensions raise ValueError."""
    config_file = tmp_path / "invalid.txt"
    config_content = (
        "WIDTH=0\n"
        "HEIGHT=15\n"
        "ENTRY=0,0\n"
        "EXIT=19,14\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=True\n"
    )
    config_file.write_text(config_content)

    with pytest.raises(ValueError):
        parse_config(str(config_file))
        