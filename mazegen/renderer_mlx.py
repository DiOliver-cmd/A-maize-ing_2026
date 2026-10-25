"""Interactive MLX (X11) renderer for the maze (graphical bonus).

The window shows the maze, the entry/exit, the ``42`` obstacle and the
shortest path.  It can be driven entirely from the keyboard:

======  =============================================
Key     Action
======  =============================================
1 / R   Regenerate a maze with a new random seed.
2 / P   Show or hide the shortest path.
3 / C   Cycle through the wall colours.
T       Cycle through the colour used for the ``42``.
4/Q/Esc Quit.
======  =============================================

MLX (``vendor/mlx-2.2-py3-none-any.whl``) is an optional dependency: this
module can always be imported, and only :class:`MazeWindow` needs it.
"""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Any, Optional

from mazegen.config import MazeConfig
from mazegen.generator import (
    DIRECTION_LETTERS,
    MOVE_OFFSETS,
    Direction,
    MazeGenerator,
)
from mazegen.renderer_ascii import path_cells

import importlib

_mlx: Any = None
MLX_AVAILABLE = False
try:  # pragma: no cover - the import depends on the optional MLX wheel
    _mlx = importlib.import_module("mlx")
    MLX_AVAILABLE = True
except ImportError:  # pragma: no cover - machines without MLX
    pass


# ``(name, colour)`` pairs; colours are 0xAARRGGBB as expected by MLX.
WALL_PALETTE: tuple[tuple[str, int], ...] = (
    ("White", 0xFFF1F1F5),
    ("Mint", 0xFF4ADE80),
    ("Amber", 0xFFFBBF24),
    ("Sky", 0xFF60A5FA),
    ("Violet", 0xFFC084FC),
    ("Coral", 0xFFFB7185),
)

PATTERN_PALETTE: tuple[tuple[str, int], ...] = (
    ("Violet", 0xFF7C3AED),
    ("Teal", 0xFF14B8A6),
    ("Rose", 0xFFE11D48),
    ("Indigo", 0xFF6366F1),
)

COLOR_BG = 0xFF101014
COLOR_HUD = 0xFF17171F
COLOR_SEPARATOR = 0xFF2B2B38
COLOR_CORRIDOR_A = 0xFF1E1E26
COLOR_CORRIDOR_B = 0xFF23232C
COLOR_ENTRY = 0xFF22C55E
COLOR_EXIT = 0xFFEF4444
COLOR_PATH = 0xFF22D3EE
COLOR_PATH_TINT = 0xFF0E3A44
COLOR_TITLE = 0xFF22D3EE
COLOR_TEXT = 0xFFE8E8F0
COLOR_TEXT_DIM = 0xFF8A8F9C
COLOR_LABEL = 0xFF0B0B0F


class MazeSession:
    """Mutable view state shared by the window and the headless tests.

    It owns the configuration, the generator, the current shortest path and
    the presentation choices (path visibility and colour indexes).  Keeping
    this logic outside :class:`MazeWindow` makes it testable without X11.
    """

    def __init__(
        self,
        config: MazeConfig,
        generator: MazeGenerator,
        path: str,
        show_path: bool = True,
    ) -> None:
        """Store the initial maze and presentation state.

        Args:
            config (MazeConfig): Configuration used to build the maze.
            generator (MazeGenerator): The already generated maze.
            path (str): Shortest path from the entry to the exit.
            show_path (bool): Whether the path starts visible.
        """
        self.config = config
        self.generator = generator
        self.path = path
        self.show_path = show_path
        self.wall_color_index = 0
        self.pattern_color_index = 0

    @property
    def wall_color_name(self) -> str:
        """Name of the wall colour currently selected."""
        return WALL_PALETTE[self.wall_color_index][0]

    @property
    def wall_color(self) -> int:
        """MLX colour currently used to draw walls."""
        return WALL_PALETTE[self.wall_color_index][1]

    @property
    def pattern_color_name(self) -> str:
        """Name of the ``42`` colour currently selected."""
        return PATTERN_PALETTE[self.pattern_color_index][0]

    @property
    def pattern_color(self) -> int:
        """MLX colour currently used to draw the ``42`` cells."""
        return PATTERN_PALETTE[self.pattern_color_index][1]

    def path_cell_set(self) -> set[tuple[int, int]]:
        """Cells on the path, or an empty set while the path is hidden."""
        if not self.show_path or not self.path:
            return set()
        return path_cells(self.config.entry, self.path)

    def path_points(self) -> list[tuple[int, int]]:
        """Ordered cells visited by the shortest path, entry first."""
        letter_to_direction = {
            letter: direction for direction, letter in DIRECTION_LETTERS.items()
        }
        x, y = self.config.entry
        points = [(x, y)]
        for letter in self.path:
            direction = letter_to_direction.get(letter)
            if direction is None:
                break
            dx, dy = MOVE_OFFSETS[direction]
            x, y = x + dx, y + dy
            points.append((x, y))
        return points

    def toggle_path(self) -> None:
        """Show the path if it is hidden and hide it otherwise."""
        self.show_path = not self.show_path

    def cycle_wall_color(self) -> None:
        """Advance to the next wall colour."""
        self.wall_color_index = (self.wall_color_index + 1) % len(WALL_PALETTE)

    def cycle_pattern_color(self) -> None:
        """Advance to the next ``42`` colour."""
        self.pattern_color_index = (
            self.pattern_color_index + 1
        ) % len(PATTERN_PALETTE)

    def regenerate(self, seed: Optional[int] = None) -> None:
        """Build a new maze, rewrite the output file and keep view settings.

        Args:
            seed (Optional[int]): Seed to use.  A random one is drawn when
                omitted.
        """
        if seed is None:
            seed = random.randrange(1_000_000)
        self.config = replace(self.config, seed=seed)
        self.generator = MazeGenerator(self.config)
        self.generator.generate()
        self.path = self.generator.shortest_path()
        self.generator.write_output(self.config.output_file, self.path)

    def status_text(self) -> str:
        """One-line summary shown in the window footer."""
        path_state = "ON" if self.show_path else "OFF"
        return (
            f"seed {self.config.seed}   path {path_state}   "
            f"walls {self.wall_color_name}   42 {self.pattern_color_name}"
        )


class MazeWindow:
    """Interactive MLX window displaying a :class:`MazeSession`."""

    PAD = 10
    TOP_BAR = 38
    BOTTOM_BAR = 58
    MIN_CELL = 4
    MAX_CELL = 40
    MIN_WIN_WIDTH = 560
    WALL_THICKNESS = 2
    PATH_THICKNESS = 3
    FONT_WIDTH = 10
    FONT_HEIGHT = 20

    def __init__(
        self,
        config: MazeConfig,
        generator: MazeGenerator,
        path: str,
    ) -> None:
        """Create the window and draw the initial frame.

        Args:
            config (MazeConfig): Configuration used to build the maze.
            generator (MazeGenerator): The already generated maze.
            path (str): Shortest path from the entry to the exit.

        Raises:
            RuntimeError: If MLX is not installed or no display is available.
        """
        if not MLX_AVAILABLE or _mlx is None:
            raise RuntimeError(
                "MLX is not available. Install it with: "
                "pip install ./vendor/mlx-2.2-py3-none-any.whl"
            )

        self.session = MazeSession(config, generator, path)
        self._closed = False
        self._dirty = False
        self.mlx: Any = _mlx.Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        if not self.mlx_ptr:
            raise RuntimeError("MLX could not open a display (check DISPLAY).")

        screen_width, screen_height = self._screen_size()
        self.cell = self._cell_size(screen_width, screen_height)
        self.maze_w = self.session.config.width * self.cell
        self.maze_h = self.session.config.height * self.cell
        self.win_w = max(self.maze_w + 2 * self.PAD, self.MIN_WIN_WIDTH)
        self.win_h = self.maze_h + self.TOP_BAR + self.BOTTOM_BAR
        self.maze_x = (self.win_w - self.maze_w) // 2

        self.win = self.mlx.mlx_new_window(
            self.mlx_ptr, self.win_w, self.win_h, "A-Maze-ing"
        )
        if not self.win:
            raise RuntimeError("MLX could not create the window.")
        self.img = self.mlx.mlx_new_image(self.mlx_ptr, self.win_w, self.win_h)
        data, bpp, size_line, _format = self.mlx.mlx_get_data_addr(self.img)
        if bpp != 32:
            raise RuntimeError(f"Unsupported MLX pixel depth: {bpp} bits.")
        self.pixels = data
        self.size_line = size_line

        self.mlx.mlx_do_key_autorepeatoff(self.mlx_ptr)
        self.mlx.mlx_key_hook(self.win, self._on_key, self)
        self.mlx.mlx_expose_hook(self.win, self._on_expose, self)
        self.mlx.mlx_hook(self.win, 33, 0, self._on_close, self)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self._on_loop, self)
        self._draw()

    # -- geometry -------------------------------------------------------- #
    def _screen_size(self) -> tuple[int, int]:
        """Return the screen size, falling back to a sane default."""
        try:
            _status, width, height = self.mlx.mlx_get_screen_size(self.mlx_ptr)
        except Exception:
            return 1280, 800
        if width <= 0 or height <= 0:
            return 1280, 800
        return int(width), int(height)

    def _cell_size(self, screen_width: int, screen_height: int) -> int:
        """Pick the largest cell that keeps the window on screen."""
        available_w = int(screen_width * 0.92) - 2 * self.PAD
        available_h = int(screen_height * 0.92) - self.TOP_BAR - self.BOTTOM_BAR
        fit_w = available_w // max(self.session.config.width, 1)
        fit_h = available_h // max(self.session.config.height, 1)
        return max(self.MIN_CELL, min(self.MAX_CELL, fit_w, fit_h))

    # -- pixel helpers --------------------------------------------------- #
    def _fill_rect(
        self, x: int, y: int, width: int, height: int, color: int
    ) -> None:
        """Fill a clipped rectangle using one slice write per row."""
        if width <= 0 or height <= 0:
            return
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.win_w, x + width)
        y1 = min(self.win_h, y + height)
        if x0 >= x1 or y0 >= y1:
            return
        count = x1 - x0
        row = color.to_bytes(4, "little") * count
        for py in range(y0, y1):
            start = py * self.size_line + x0 * 4
            self.pixels[start:start + count * 4] = row

    # -- drawing --------------------------------------------------------- #
    def _draw(self) -> None:
        """Redraw the whole scene and its HUD."""
        if self._closed:
            return
        self._fill_rect(0, 0, self.win_w, self.win_h, COLOR_BG)
        self._fill_rect(0, 0, self.win_w, self.TOP_BAR, COLOR_HUD)
        self._fill_rect(
            0,
            self.win_h - self.BOTTOM_BAR,
            self.win_w,
            self.BOTTOM_BAR,
            COLOR_HUD,
        )
        self._fill_rect(0, self.TOP_BAR - 1, self.win_w, 1, COLOR_SEPARATOR)
        self._fill_rect(
            0,
            self.win_h - self.BOTTOM_BAR,
            self.win_w,
            1,
            COLOR_SEPARATOR,
        )
        self._draw_cells()
        self._draw_path()
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win, self.img, 0, 0
        )
        self._draw_text()
        self.mlx.mlx_do_sync(self.mlx_ptr)
        self._dirty = False

    def _draw_cells(self) -> None:
        """Draw cell backgrounds, the ``42`` pattern and every wall."""
        grid = self.session.generator.grid
        entry = self.session.config.entry
        exit_ = self.session.config.exit
        obstacles = self.session.generator.obstacles
        path = self.session.path_cell_set()
        wall_color = self.session.wall_color
        pattern_color = self.session.pattern_color

        for y, row in enumerate(grid):
            py = self.TOP_BAR + y * self.cell
            for x, cell in enumerate(row):
                px = self.maze_x + x * self.cell
                if (x, y) == entry:
                    color = COLOR_ENTRY
                elif (x, y) == exit_:
                    color = COLOR_EXIT
                elif (x, y) in obstacles:
                    color = pattern_color
                elif (x, y) in path:
                    color = COLOR_PATH_TINT
                elif (x + y) % 2:
                    color = COLOR_CORRIDOR_A
                else:
                    color = COLOR_CORRIDOR_B
                self._fill_rect(px, py, self.cell, self.cell, color)

        thickness = self.WALL_THICKNESS
        for y, row in enumerate(grid):
            py = self.TOP_BAR + y * self.cell
            for x, cell in enumerate(row):
                px = self.maze_x + x * self.cell
                if cell & Direction.NORTH:
                    self._fill_rect(px, py, self.cell, thickness, wall_color)
                if cell & Direction.SOUTH:
                    self._fill_rect(
                        px,
                        py + self.cell - thickness,
                        self.cell,
                        thickness,
                        wall_color,
                    )
                if cell & Direction.WEST:
                    self._fill_rect(px, py, thickness, self.cell, wall_color)
                if cell & Direction.EAST:
                    self._fill_rect(
                        px + self.cell - thickness,
                        py,
                        thickness,
                        self.cell,
                        wall_color,
                    )

    def _draw_path(self) -> None:
        """Draw the shortest path as an axis-aligned polyline."""
        if not self.session.show_path or not self.session.path:
            return
        points = self.session.path_points()
        half = self.PATH_THICKNESS // 2
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            cx1 = self.maze_x + x1 * self.cell + self.cell // 2
            cy1 = self.TOP_BAR + y1 * self.cell + self.cell // 2
            cx2 = self.maze_x + x2 * self.cell + self.cell // 2
            cy2 = self.TOP_BAR + y2 * self.cell + self.cell // 2
            if cy1 == cy2:
                left = min(cx1, cx2)
                self._fill_rect(
                    left,
                    cy1 - half,
                    abs(cx2 - cx1) + 1,
                    self.PATH_THICKNESS,
                    COLOR_PATH,
                )
            else:
                top = min(cy1, cy2)
                self._fill_rect(
                    cx1 - half,
                    top,
                    self.PATH_THICKNESS,
                    abs(cy2 - cy1) + 1,
                    COLOR_PATH,
                )

    def _draw_text(self) -> None:
        """Draw the HUD and the entry/exit labels on top of the image."""
        put = self.mlx.mlx_string_put
        put(
            self.mlx_ptr, self.win, 12, 8, COLOR_TITLE, "A-Maze-ing"
        )
        mode = "PERFECT" if self.session.config.perfect else "PLAYABLE"
        size = (
            f"{self.session.config.width}x{self.session.config.height}  {mode}"
        )
        size_x = self.win_w - 12 - len(size) * self.FONT_WIDTH
        if size_x > 100:
            put(self.mlx_ptr, self.win, size_x, 8, COLOR_TEXT_DIM, size)

        legend = self._fit(
            "1/R new  2/P path  3/C wall  4/Q quit  T 42 colour",
            self.win_w - 24,
        )
        put(
            self.mlx_ptr,
            self.win,
            12,
            self.win_h - 52,
            COLOR_TEXT_DIM,
            legend,
        )
        status = self._fit(
            self.session.status_text(), self.win_w - 24
        )
        put(
            self.mlx_ptr,
            self.win,
            12,
            self.win_h - 26,
            COLOR_TEXT,
            status,
        )

        if self.cell < 20:
            return
        for cell, label in (
            (self.session.config.entry, "E"),
            (self.session.config.exit, "X"),
        ):
            x, y = cell
            px = self.maze_x + x * self.cell + (self.cell - 10) // 2
            py = self.TOP_BAR + y * self.cell + (self.cell - 20) // 2
            put(self.mlx_ptr, self.win, px, py, COLOR_LABEL, label)

    def _fit(self, text: str, max_width: int) -> str:
        """Shorten *text* so it fits in *max_width* pixels."""
        limit = max(1, max_width // self.FONT_WIDTH)
        if len(text) <= limit:
            return text
        if limit <= 3:
            return text[:limit]
        return text[:limit - 3] + "..."

    # -- events ---------------------------------------------------------- #
    def _on_key(self, key: int, _param: object) -> None:
        """React to a key press; returns None as required by the wrapper."""
        if self._closed:
            return
        if key in (49, 114, 82):        # 1 / r / R
            self.session.regenerate()
            self._dirty = True
        elif key in (50, 112, 80):      # 2 / p / P
            self.session.toggle_path()
            self._dirty = True
        elif key in (51, 99, 67):       # 3 / c / C
            self.session.cycle_wall_color()
            self._dirty = True
        elif key in (116, 84):          # t / T
            self.session.cycle_pattern_color()
            self._dirty = True
        elif key in (52, 113, 81, 65307):  # 4 / q / Q / Esc
            self._quit()

    def _on_loop(self, _param: object) -> None:
        """Redraw pending state once per loop, outside input callbacks."""
        if self._dirty and not self._closed:
            self._draw()

    def _on_expose(self, _param: object) -> None:
        """Request a redraw after the window manager exposed the window."""
        self._dirty = True

    def _on_close(self, _param: object) -> None:
        """Stop the event loop when the window is closed."""
        self._quit()

    def _quit(self) -> None:
        """Ask MLX to leave the event loop (cleanup happens in run)."""
        if not self._closed:
            self.mlx.mlx_loop_exit(self.mlx_ptr)

    # -- lifecycle ------------------------------------------------------- #
    def run(self) -> None:
        """Run the MLX event loop until the window is closed."""
        print("MLX: click the window, then use 1/R 2/P 3/C T 4/Q/Esc.")
        try:
            self.mlx.mlx_loop(self.mlx_ptr)
        finally:
            self.cleanup()

    def cleanup(self) -> None:
        """Release MLX resources exactly once."""
        if self._closed:
            return
        self._closed = True
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win)
        self.mlx.mlx_release(self.mlx_ptr)
