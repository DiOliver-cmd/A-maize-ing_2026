"""Module for maze structure definition and generation logic."""

import random
from collections import deque
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

# Letter used for each direction in the output file path
DIRECTION_LETTERS: dict[Direction, str] = {
    Direction.NORTH: "N",
    Direction.EAST: "E",
    Direction.SOUTH: "S",
    Direction.WEST: "W",
}

# Bitmaps for the '42' obstacle pattern (5x3 matrices)
PATTERN_4: list[list[int]] = [
    [1, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

PATTERN_2: list[list[int]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]


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
        # Coordinates reserved for obstacle pattern '42'
        self.obstacles: set[tuple[int, int]] = set()

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

    def get_unvisited_neighbors(
        self, x: int, y: int, visited: set[tuple[int, int]]
    ) -> list[tuple[int, int]]:

        neighbors: list[tuple[int, int]] = []
        for direction, (dx, dy) in MOVE_OFFSETS.items():
            nx, ny = x + dx, y + dy
            if self.is_valid_cell(nx, ny) and (nx, ny) not in visited:
                neighbors.append((nx, ny))
        return neighbors

    def _apply_pattern_42(self) -> None:
        """Apply the '42' obstacle pattern if grid dimensions are at least 9x7."""
        pattern_w = 7  # 3 (digit 4) + 1 (spacing) + 3 (digit 2)
        pattern_h = 5  # 5 rows height

        if self.width < pattern_w + 2 or self.height < pattern_h + 2:
            print("Warning: maze too small to draw the '42' pattern.")
            return

        start_x = (self.width - pattern_w) // 2
        start_y = (self.height - pattern_h) // 2

        # Process digit '4'
        for r in range(5):
            for c in range(3):
                if PATTERN_4[r][c] == 1:
                    pos = (start_x + c, start_y + r)
                    if pos != self.config.entry and pos != self.config.exit:
                        self.obstacles.add(pos)

        # Process digit '2'
        for r in range(5):
            for c in range(3):
                if PATTERN_2[r][c] == 1:
                    pos = (start_x + 4 + c, start_y + r)
                    if pos != self.config.entry and pos != self.config.exit:
                        self.obstacles.add(pos)

    def generate_backtracker(self) -> None:
        """Generate maze paths using the Recursive Backtracker algorithm."""
        self._apply_pattern_42()
        rng = random.Random(self.config.seed)
        start_cell = self.config.entry
        visited: set[tuple[int, int]] = set(self.obstacles)
        visited.add(start_cell)
        stack: list[tuple[int, int]] = [start_cell]

        while stack:
            curr_x, curr_y = stack[-1]
            neighbors = self.get_unvisited_neighbors(curr_x, curr_y, visited)

            if neighbors:
                next_cell = rng.choice(neighbors)
                self.remove_wall((curr_x, curr_y), next_cell)
                visited.add(next_cell)
                stack.append(next_cell)
            else:
                stack.pop()
        self.ensure_full_connectivity()

    def write_output(self, filename: str, path_str: str = "") -> None:
        """Write maze configuration and hex matrix to output file.

        Args:
            filename (str): Target output file path.
            path_str (str): Shortest path representation (optional).
        """
        with open(filename, "w", encoding="utf-8") as f:
            for row in self.grid:
                f.write("".join(f"{cell:X}" for cell in row) + "\n")
            f.write("\n")
            entry_x, entry_y = self.config.entry
            f.write(f"{entry_x},{entry_y}\n")
            exit_x, exit_y = self.config.exit
            f.write(f"{exit_x},{exit_y}\n")
            f.write(f"{path_str}\n")

    def shortest_path(self) -> str:
        """Find the shortest path from entry to exit with a BFS.

        Returns:
            str: The path as direction letters (ex: "EESN"), or an empty
                string if the exit cannot be reached from the entry.
        """
        start = self.config.entry
        goal = self.config.exit
        visited: set[tuple[int, int]] = {start}
        parent: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
        queue: deque[tuple[int, int]] = deque([start])

        while queue:
            x, y = queue.popleft()
            if (x, y) == goal:
                break
            for direction, (dx, dy) in MOVE_OFFSETS.items():
                neighbor = (x + dx, y + dy)
                wall_closed = self.grid[y][x] & direction
                if wall_closed or neighbor in visited:
                    continue
                if not self.is_valid_cell(*neighbor):
                    continue
                visited.add(neighbor)
                parent[neighbor] = ((x, y), DIRECTION_LETTERS[direction])
                queue.append(neighbor)

        if goal not in visited:
            return ""

        letters: list[str] = []
        cell = goal
        while cell != start:
            cell, letter = parent[cell]
            letters.append(letter)
        return "".join(reversed(letters))

    def get_reachable_cells(
        self, start_cell: tuple[int, int]
    ) -> set[tuple[int, int]]:
        reachable: set[tuple[int, int]] = {start_cell}
        queue: deque[tuple[int, int]] = deque([start_cell])
        while queue:
            curr_x, curr_y = queue.popleft()
            cell_walls = self.grid[curr_y][curr_x]
            for direction, (dx, dy) in MOVE_OFFSETS.items():
                if not (cell_walls & direction.value):
                    nx, ny = curr_x + dx, curr_y + dy
                    if (
                        self.is_valid_cell(nx, ny)
                        and (nx, ny) not in reachable
                        and (nx, ny) not in self.obstacles
                    ):
                        reachable.add((nx, ny))
                        queue.append((nx, ny))
        return reachable

    def ensure_full_connectivity(self) -> None:
        all_cells = {
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if (x, y) not in self.obstacles
        }
        while True:
            reachable = self.get_reachable_cells(self.config.entry)
            unreachable = all_cells - reachable
            if not unreachable:
                break
            connected = False
            for unreach_x, unreach_y in unreachable:
                for _, (dx, dy) in MOVE_OFFSETS.items():
                    nx, ny = unreach_x + dx, unreach_y + dy
                    if (nx, ny) in reachable:
                        self.remove_wall((unreach_x, unreach_y), (nx, ny))
                        connected = True
                        break
                if connected:
                    break
            if not connected:
                target = next(iter(unreachable))
                tx, ty = target
                for _, (dx, dy) in MOVE_OFFSETS.items():
                    nx, ny = tx + dx, ty + dy
                    if self.is_valid_cell(nx, ny) and (nx, ny) not in self.obstacles:
                        self.remove_wall(target, (nx, ny))
                        break

    def generate_perfect_base(self) -> None:
        self.generate_backtracker()

    def _count_open_passages(self, x: int, y: int) -> int:
        """Count the number of open passages from a cell."""
        count = 0
        cell_walls = self.grid[y][x]
        for direction, (dx, dy) in MOVE_OFFSETS.items():
            if not (cell_walls & direction.value):
                nx, ny = x + dx, y + dy
                if self.is_valid_cell(nx, ny) and (nx, ny) not in self.obstacles:
                    count += 1
        return count

    def _get_real_dead_ends(self) -> list[tuple[int, int]]:
        """Get all real dead-ends (degree 1 cells with an openable
        wall to a normal cell)."""
        dead_ends = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.obstacles:
                    continue
                if self._count_open_passages(x, y) == 1:
                    # Check if it has an openable wall to a normal cell
                    cell_walls = self.grid[y][x]
                    for direction, (dx, dy) in MOVE_OFFSETS.items():
                        if cell_walls & direction.value:
                            nx, ny = x + dx, y + dy
                            if (self.is_valid_cell(nx, ny)
                                    and (nx, ny) not in self.obstacles
                                    and not (self.grid[ny][nx] == Direction.ALL_WALLS)):
                                dead_ends.append((x, y))
                                break
        return dead_ends

    def _creates_open_area(self, x: int, y: int) -> bool:
        """Check if opening a wall at (x,y) would create a 3x3 fully open area.

        A 3x3 area is "fully open" if all internal walls between the 9 cells are open
        (i.e., corridor width would be 3, violating the max width of 2).
        """
        # Check all 3x3 regions that include (x,y)
        for ry in range(max(0, y - 2), min(self.height - 2, y + 1)):
            for rx in range(max(0, x - 2), min(self.width - 2, x + 1)):
                # Check if this 3x3 region would be fully open (all internal walls open)
                all_internal_open = True
                for dy in range(3):
                    for dx in range(3):
                        cx, cy = rx + dx, ry + dy
                        if (cx, cy) in self.obstacles:
                            all_internal_open = False
                            break
                        # Check walls to the right (EAST) and down (SOUTH)
                        # within the 3x3
                        if dx < 2:  # Not the rightmost column - check EAST wall
                            if self.grid[cy][cx] & Direction.EAST.value:
                                all_internal_open = False
                                break
                        if dy < 2:  # Not the bottom row - check SOUTH wall
                            if self.grid[cy][cx] & Direction.SOUTH.value:
                                all_internal_open = False
                                break
                    if not all_internal_open:
                        break
                if all_internal_open:
                    return True
        return False

    def _ensure_key_cells_open(self) -> None:
        """Ensure the four corners and center cell(s) are open corridors."""
        # Four corners
        corners = [
            (0, 0),
            (self.width - 1, 0),
            (0, self.height - 1),
            (self.width - 1, self.height - 1),
        ]
        # Center cell(s)
        center_cells = []
        if self.width % 2 == 1 and self.height % 2 == 1:
            center_cells.append((self.width // 2, self.height // 2))
        elif self.width % 2 == 0 and self.height % 2 == 1:
            center_cells.append((self.width // 2 - 1, self.height // 2))
            center_cells.append((self.width // 2, self.height // 2))
        elif self.width % 2 == 1 and self.height % 2 == 0:
            center_cells.append((self.width // 2, self.height // 2 - 1))
            center_cells.append((self.width // 2, self.height // 2))
        else:
            center_cells.append((self.width // 2 - 1, self.height // 2 - 1))
            center_cells.append((self.width // 2, self.height // 2 - 1))
            center_cells.append((self.width // 2 - 1, self.height // 2))
            center_cells.append((self.width // 2, self.height // 2))

        key_cells = corners + center_cells

        for x, y in key_cells:
            if (x, y) in self.obstacles:
                # If a key cell is an obstacle, we need to handle it
                # For now, remove from obstacles if it's entry/exit
                if (x, y) == self.config.entry or (x, y) == self.config.exit:
                    self.obstacles.discard((x, y))
                continue
            # Ensure the cell is not fully closed
            if self.grid[y][x] == Direction.ALL_WALLS:
                # Open a wall to a valid neighbor
                for direction, (dx, dy) in MOVE_OFFSETS.items():
                    nx, ny = x + dx, y + dy
                    if self.is_valid_cell(nx, ny) and (nx, ny) not in self.obstacles:
                        self.remove_wall((x, y), (nx, ny))
                        break

    def _add_loops(self, min_loops: int = 2) -> None:
        """Add loops by removing additional walls until we have at least min_loops."""
        base_seed = self.config.seed if self.config.seed is not None else 0
        rng = random.Random(base_seed + 1000)  # Different seed for loop addition

        # Calculate current loops using the same formula as analyzer
        def count_loops() -> int:
            reachable = self.get_reachable_cells(self.config.entry)
            open_passages = 0
            for x, y in reachable:
                cell_walls = self.grid[y][x]
                for direction, (dx, dy) in MOVE_OFFSETS.items():
                    if not (cell_walls & direction.value):
                        nx, ny = x + dx, y + dy
                        if (nx, ny) in reachable and (nx, ny) > (x, y):
                            open_passages += 1
            return open_passages - len(reachable) + 1

        current_loops = count_loops()
        attempts = 0
        max_attempts = self.width * self.height * 4

        while current_loops < min_loops and attempts < max_attempts:
            # Find candidate walls to remove (between two non-obstacle cells)
            candidates = []
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) in self.obstacles:
                        continue
                    for direction, (dx, dy) in MOVE_OFFSETS.items():
                        nx, ny = x + dx, y + dy
                        if not self.is_valid_cell(nx, ny):
                            continue
                        if (nx, ny) in self.obstacles:
                            continue
                        # Only consider walls that are currently closed
                        if self.grid[y][x] & direction.value:
                            # Check if removing this wall would create a 3x3 open area
                            # Temporarily remove and check
                            self.grid[y][x] &= ~direction.value
                            self.grid[ny][nx] &= ~OPPOSITE[direction].value
                            creates_open = (
                                self._creates_open_area(x, y)
                                or self._creates_open_area(nx, ny)
                            )
                            # Restore
                            self.grid[y][x] |= direction.value
                            self.grid[ny][nx] |= OPPOSITE[direction].value
                            if not creates_open:
                                candidates.append(((x, y), (nx, ny), direction))

            if not candidates:
                break

            # Pick a random candidate
            (x1, y1), (x2, y2), direction = rng.choice(candidates)
            self.remove_wall((x1, y1), (x2, y2))
            current_loops = count_loops()
            attempts += 1

    def _reduce_dead_ends(self, max_dead_ends: int = 2) -> None:
        """Reduce real dead-ends to at most max_dead_ends by opening walls."""
        base_seed = self.config.seed if self.config.seed is not None else 0
        rng = random.Random(base_seed + 2000)  # Different seed for dead-end reduction

        max_attempts = self.width * self.height * 4
        attempts = 0

        while attempts < max_attempts:
            dead_ends = self._get_real_dead_ends()
            if len(dead_ends) <= max_dead_ends:
                break

            # Pick a random dead-end
            x, y = rng.choice(dead_ends)

            # Find a closed wall to a normal cell (not obstacle, not fully closed)
            cell_walls = self.grid[y][x]
            candidates = []
            for direction, (dx, dy) in MOVE_OFFSETS.items():
                if cell_walls & direction.value:
                    nx, ny = x + dx, y + dy
                    if (self.is_valid_cell(nx, ny)
                            and (nx, ny) not in self.obstacles
                            and not (self.grid[ny][nx] == Direction.ALL_WALLS)):
                        # Check if opening this wall would create a 3x3 open area
                        self.grid[y][x] &= ~direction.value
                        self.grid[ny][nx] &= ~OPPOSITE[direction].value
                        creates_open = (
                            self._creates_open_area(x, y)
                            or self._creates_open_area(nx, ny)
                        )
                        # Restore
                        self.grid[y][x] |= direction.value
                        self.grid[ny][nx] |= OPPOSITE[direction].value
                        if not creates_open:
                            candidates.append((direction, (nx, ny)))

            if candidates:
                direction, (nx, ny) = rng.choice(candidates)
                self.remove_wall((x, y), (nx, ny))
            else:
                # If no candidates for this dead-end, try another one
                pass

            attempts += 1

    def generate_playable(self) -> None:
        """Generate a playable maze (PERFECT=False) with loops,
        controlled dead-ends, and open key cells."""
        # Step 1: Generate perfect base
        self.generate_perfect_base()

        # Step 2: Ensure key cells (corners and center) are open
        self._ensure_key_cells_open()

        # Step 3: Add loops (at least 2)
        self._add_loops(min_loops=2)

        # Step 4: Reduce dead-ends to at most 2
        self._reduce_dead_ends(max_dead_ends=2)

        # Step 5: Final connectivity check
        self.ensure_full_connectivity()
