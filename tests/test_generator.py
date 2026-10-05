"""Tests for MazeGenerator and generation algorithms."""

from mazegen.config import MazeConfig
from mazegen.generator import MazeGenerator


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
