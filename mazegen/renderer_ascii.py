"""Draw a maze in the terminal with ASCII characters and ANSI colours."""

from mazegen.generator import DIRECTION_LETTERS, MOVE_OFFSETS, Direction

RESET = "\033[0m"
ENTRY_MARK = "\033[1;35m E "
EXIT_MARK = "\033[1;31m X "
PATH_MARK = "\033[1;36m · "
BLOCK_MARK = "███"

WALL_COLORS: list[str] = [
    "\033[37m",  # white
    "\033[32m",  # green
    "\033[33m",  # yellow
    "\033[34m",  # blue
    "\033[35m",  # magenta
]


def path_cells(entry: tuple[int, int], path: str) -> set[tuple[int, int]]:
    """Return every cell visited when walking the path from the entry.

    Args:
        entry (tuple[int, int]): Starting cell (x, y).
        path (str): Direction letters, e.g. "EESN".

    Returns:
        set[tuple[int, int]]: The cells along the path, entry included.
    """
    letter_to_direction = {letter: d for d, letter in DIRECTION_LETTERS.items()}
    x, y = entry
    cells = {entry}
    for letter in path:
        dx, dy = MOVE_OFFSETS[letter_to_direction[letter]]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def render(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: set[tuple[int, int]],
    wall_color: str,
) -> str:
    """Draw the maze as text, each cell 3 characters wide.

    Args:
        grid (list[list[int]]): Wall bitmask of every cell, row by row.
        entry (tuple[int, int]): Entry cell (x, y).
        exit_ (tuple[int, int]): Exit cell (x, y).
        path (set[tuple[int, int]]): Cells to mark as the path (may be empty).
        wall_color (str): ANSI code used for the walls.

    Returns:
        str: The maze, ready to be printed.
    """
    lines: list[str] = []
    for y, row in enumerate(grid):
        top = "+"
        middle = ""
        for x, cell in enumerate(row):
            top += ("---" if cell & Direction.NORTH else "   ") + "+"
            middle += "|" if cell & Direction.WEST else " "
            if (x, y) == entry:
                middle += ENTRY_MARK + wall_color
            elif (x, y) == exit_:
                middle += EXIT_MARK + wall_color
            elif cell == Direction.ALL_WALLS:
                middle += BLOCK_MARK
            elif (x, y) in path:
                middle += PATH_MARK + wall_color
            else:
                middle += "   "
        middle += "|" if row[-1] & Direction.EAST else " "
        lines.append(wall_color + top + RESET)
        lines.append(wall_color + middle + RESET)

    bottom = "+"
    for cell in grid[-1]:
        bottom += ("---" if cell & Direction.SOUTH else "   ") + "+"
    lines.append(wall_color + bottom + RESET)
    return "\n".join(lines)
