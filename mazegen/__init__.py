"""mazegen - A reusable maze generator for A-Maze-ing (42 curriculum).

Example:
    >>> from mazegen import MazeGenerator, MazeConfig
    >>> config = MazeConfig(
    ...     width=20, height=15,
    ...     entry=(0, 0), exit=(19, 14),
    ...     output_file="maze.txt",
    ...     perfect=True, seed=42
    ... )
    >>> gen = MazeGenerator(config)
    >>> gen.generate()
    >>> grid = gen.grid
    >>> path = gen.shortest_path()
"""

from mazegen.config import MazeConfig, parse_config
from mazegen.generator import Direction, MazeGenerator

__all__ = ["MazeConfig", "parse_config", "MazeGenerator", "Direction"]
