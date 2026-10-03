"""Module for maze structure definition and generation logic."""

from enum import IntFlag
from typing import Optional
from mazegen.config import MazeConfig


class Direction(IntFlag):
    """Bitmask representing wall directions for a grid cell.

    Values:
    NORTH (1): Wall to the North (y - 1).
    EAST (2): Wall to the East (x + 1).
    SOUTH (4): Wall to the South (y + 1).
    WEST (8): Wall to the West (x - 1).
    ALL_WALLS (15): All four walls present.
    """

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8
    ALL_WALLS = 15


# Mapping opposite directions for bilateral wall updates
OPPOSITE: dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.EAST: Direction.WEST,
    Direction.SOUTH: Direction.NORTH,
    Direction.WEST: Direction.EAST,
}

# Offsets (dx, dy) corresponding to each direction
MOVE_OFFSETS: dict[Direction, tuple[int, int]] = {
    Direction.NORTH: (0, -1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, 1),
    Direction.WEST: (-1, 0),
}


class MazeGenerator:
    """Class responsible for initializing and generating maze grids.

    Attributes:
    config (MazeConfig): The parsed configuration options.
    width (int): Grid width (columns).
    height (int): Grid height (rows).
    grid (list[list[int]]): 2D matrix storing cell wall bitmasks.
    """

    def __init__(self, config: MazeConfig) -> None:
        """Initialize the maze generator with configuration parameters.

        Args:
            config (MazeConfig): Validated maze configuration instance.
        """
        self.config: MazeConfig = config
        self.width: int = config.width
        self.height: int = config.height
        # Initialize grid with all walls present (15 / 0b1111)
        self.grid: list[list[int]] = [
            [int(Direction.ALL_WALLS) for _ in range(self.width)]
            for _ in range(self.height)
        ]

    def is_valid_cell(self, x: int, y: int) -> bool:
        """Check if coordinates lie within the maze boundaries.

        Args:
            x (int): Column coordinate.
            y (int): Row coordinate.

        Returns:
            bool: True if coordinates are valid, False otherwise.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def get_direction(
        self, cell_a: tuple[int, int], cell_b: tuple[int, int]
    ) -> Optional[Direction]:
        """Determine the movement direction from cell_a to cell_b.

        Args:
            cell_a (tuple[int, int]): Source cell coordinates (x, y).
            cell_b (tuple[int, int]): Destination cell coordinates (x, y).

        Returns:
            Optional[Direction]: The direction from A to B if adjacent, None otherwise.
        """
        dx = cell_b[0] - cell_a[0]
        dy = cell_b[1] - cell_a[1]
        for direction, offset in MOVE_OFFSETS.items():
            if offset == (dx, dy):
                return direction
        return None

    def remove_wall(
        self, cell_a: tuple[int, int], cell_b: tuple[int, int]
    ) -> None:
        """Remove the wall between two adjacent cells in a bilateral manner.

        Clears the wall bit in both cell_a and cell_b to ensure wall coherence
        across the grid interface.

        Args:
            cell_a (tuple[int, int]): First cell coordinates (x, y).
            cell_b (tuple[int, int]): Second cell coordinates (x, y).

        Raises:
            ValueError: If cells are not adjacent or outside grid boundaries.
        """
        x1, y1 = cell_a
        x2, y2 = cell_b

        if not (self.is_valid_cell(x1, y1) and self.is_valid_cell(x2, y2)):
            raise ValueError(f"Coordenadas fora dos limites: {cell_a}, {cell_b}")

        direction_a_to_b = self.get_direction(cell_a, cell_b)
        if direction_a_to_b is None:
            raise ValueError(f"Células não são adjacentes: {cell_a}, {cell_b}")

        direction_b_to_a = OPPOSITE[direction_a_to_b]
        # Clear wall bit in both cells
        self.grid[y1][x1] &= ~direction_a_to_b.value
        self.grid[y2][x2] &= ~direction_b_to_a.value
