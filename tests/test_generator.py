"""Tests for MazeGenerator and generation algorithms."""

from mazegen.config import MazeConfig
from mazegen.generator import MOVE_OFFSETS, Direction, MazeGenerator
import pytest


def test_generator_initialization() -> None:
    """Test if MazeGenerator initializes grid with all walls present."""
    config = MazeConfig(3, 3, (0, 0), (2, 2), "out.txt", True)
    gen = MazeGenerator(config)
    assert gen.width == 3
    assert gen.height == 3
    assert all(cell == 15 for row in gen.grid for cell in row)


def test_remove_wall_coherence() -> None:
    """Test if remove_wall updates both adjacent cells bilaterally."""
    config = MazeConfig(3, 3, (0, 0), (2, 2), "out.txt", True)
    gen = MazeGenerator(config)
    gen.remove_wall((0, 0), (1, 0))
    assert gen.grid[0][0] == 13
    assert gen.grid[0][1] == 7


def test_generate_backtracker_determinism() -> None:
    """Test if backtracker generates deterministic mazes with same seed."""
    config1 = MazeConfig(4, 4, (0, 0), (3, 3), "out.txt", True, seed=42)
    config2 = MazeConfig(4, 4, (0, 0), (3, 3), "out.txt", True, seed=42)
    gen1 = MazeGenerator(config1)
    gen2 = MazeGenerator(config2)
    gen1.generate_backtracker()
    gen2.generate_backtracker()
    assert gen1.grid == gen2.grid


def test_pattern_42_applied_on_large_grid() -> None:
    """Garante que o padrão '42' é desenhado em grades grandes."""
    config = MazeConfig(20, 15, (0, 0), (19, 14), "out.txt", True, seed=42)
    gen = MazeGenerator(config)
    gen._apply_pattern_42()
    # O padrão '42' possui 20 células de obstáculo
    assert len(gen.obstacles) == 20


def test_pattern_42_ignored_on_small_grid(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Garante aviso e 0 obstáculos em grades pequenas."""
    config = MazeConfig(4, 4, (0, 0), (3, 3), "out.txt", True, seed=42)
    gen = MazeGenerator(config)
    gen._apply_pattern_42()
    assert len(gen.obstacles) == 0
    captured = capsys.readouterr()
    expected_msg = "Warning: maze too small to draw the '42' pattern."
    assert expected_msg in captured.out


def test_shortest_path_single_step() -> None:
    """A single open wall between entry and exit gives a one-letter path."""
    config = MazeConfig(2, 1, (0, 0), (1, 0), "out.txt", True)
    gen = MazeGenerator(config)
    gen.remove_wall((0, 0), (1, 0))
    assert gen.shortest_path() == "E"


def test_shortest_path_unreachable_exit() -> None:
    """With every wall closed there is no path, so the result is empty."""
    config = MazeConfig(3, 3, (0, 0), (2, 2), "out.txt", True)
    gen = MazeGenerator(config)
    assert gen.shortest_path() == ""


def test_shortest_path_follows_open_walls_to_exit() -> None:
    """Walking the path from entry crosses only open walls and ends on exit."""
    config = MazeConfig(20, 15, (0, 0), (19, 14), "out.txt", True, seed=42)
    gen = MazeGenerator(config)
    gen.generate_backtracker()
    path = gen.shortest_path()
    assert path != ""

    letter_to_direction = {
        "N": Direction.NORTH,
        "E": Direction.EAST,
        "S": Direction.SOUTH,
        "W": Direction.WEST,
    }
    x, y = config.entry
    for letter in path:
        direction = letter_to_direction[letter]
        assert not gen.grid[y][x] & direction
        dx, dy = MOVE_OFFSETS[direction]
        x, y = x + dx, y + dy
    assert (x, y) == config.exit


def test_get_reachable_cells() -> None:
    """Garante que get_reachable_cells retorna todas as células conectadas."""
    config = MazeConfig(10, 10, (0, 0), (9, 9), "out.txt", True, seed=42)
    gen = MazeGenerator(config)
    gen.generate_backtracker()
    reachable = gen.get_reachable_cells(config.entry)
    expected_count = (gen.width * gen.height) - len(gen.obstacles)
    assert len(reachable) == expected_count


def test_ensure_full_connectivity() -> None:
    """Garante que a conectividade total (T3.2) elimina corredores isolados."""
    config = MazeConfig(15, 12, (0, 0), (14, 11), "out.txt", True, seed=42)
    gen = MazeGenerator(config)
    gen.generate_backtracker()
    reachable = gen.get_reachable_cells(config.entry)
    total_valid_cells = (gen.width * gen.height) - len(gen.obstacles)
    assert len(reachable) == total_valid_cells


def test_generate_perfect_base() -> None:
    """Garante a geração de uma base perfeita (T5.1) para o modo jogável."""
    config = MazeConfig(20, 15, (0, 0), (19, 14), "out.txt", False, seed=42)
    gen = MazeGenerator(config)
    gen.generate_perfect_base()
    reachable = gen.get_reachable_cells(config.entry)
    total_valid_cells = (gen.width * gen.height) - len(gen.obstacles)
    assert len(reachable) == total_valid_cells
