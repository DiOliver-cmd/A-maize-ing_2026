"""MLX-based graphical renderer for the maze (optional bonus).

This module provides a graphical window using MLX (Linux via X11).
Requires: mlx-2.2.tgz extracted and installed
(pip install ./ubuntu/mlx-2.2-py3-none-any.whl)

Usage:
    from mazegen.renderer_mlx import MazeWindow
    window = MazeWindow(grid, entry, exit, path=set())
    window.run()
"""

from mazegen.generator import Direction

try:
    from mlx import Mlx
    MLX_AVAILABLE = True
except ImportError:
    MLX_AVAILABLE = False
    Mlx = None


class MazeWindow:
    """MLX window for displaying and interacting with a maze."""

    CELL_SIZE = 20
    WALL_THICKNESS = 2

    # Colors in 0xAARRGGBB format (alpha=0xFF for opaque)
    COLOR_WALL = 0xFF777777      # Gray walls
    COLOR_BG = 0xFF1A1A1A        # Dark background
    COLOR_ENTRY = 0xFFFF00FF     # Magenta entry
    COLOR_EXIT = 0xFFFF0000      # Red exit
    COLOR_PATH = 0xFF00FFFF      # Cyan path
    COLOR_BLOCK = 0xFFFFFFFF     # White for "42" blocks

    def __init__(
        self,
        grid: list[list[int]],
        entry: tuple[int, int],
        exit_: tuple[int, int],
        path: set[tuple[int, int]] | None = None,
    ) -> None:
        """Initialize the maze window.

        Args:
            grid: Maze grid with wall bitmasks.
            entry: Entry coordinates (x, y).
            exit_: Exit coordinates (x, y).
            path: Set of cells to highlight as path.
        """
        if not MLX_AVAILABLE:
            raise RuntimeError(
                "MLX not available. Install with: "
                "pip install ./ubuntu/mlx-2.2-py3-none-any.whl"
            )

        self.grid = grid
        self.entry = entry
        self.exit = exit_
        self.path = path or set()
        self.height = len(grid)
        self.width = len(grid[0]) if grid else 0

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()

        win_w = self.width * self.CELL_SIZE
        win_h = self.height * self.CELL_SIZE
        self.win_ptr = self.mlx.mlx_new_window(self.mlx_ptr, win_w, win_h, "A-Maze-ing")

        # Create image buffer
        self.img_ptr = self.mlx.mlx_new_image(self.mlx_ptr, win_w, win_h)
        self.img_data, self.img_bpp, self.img_sl, self.img_endian = (
            self.mlx.mlx_get_data_addr(self.img_ptr)
        )

        # Set up hooks
        self.mlx.mlx_key_hook(self.win_ptr, self._on_key, self)
        self.mlx.mlx_expose_hook(self.win_ptr, self._on_expose, self)
        self.mlx.mlx_hook(self.win_ptr, 33, 0, self._on_close, self)  # WM_DELETE_WINDOW

        self._draw()

    def _draw(self) -> None:
        """Render the maze to the MLX image."""
        # Fill background
        for y in range(self.height * self.CELL_SIZE):
            row_offset = y * self.img_sl
            for x in range(self.width * self.CELL_SIZE):
                idx = row_offset + x * 4
                self.img_data[idx:idx+4] = self.COLOR_BG.to_bytes(4, 'little')

        # Draw each cell
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                px = x * self.CELL_SIZE
                py = y * self.CELL_SIZE

                # Determine cell color
                if (x, y) == self.entry:
                    cell_color = self.COLOR_ENTRY
                elif (x, y) == self.exit:
                    cell_color = self.COLOR_EXIT
                elif cell == Direction.ALL_WALLS:
                    cell_color = self.COLOR_BLOCK
                elif (x, y) in self.path:
                    cell_color = self.COLOR_PATH
                else:
                    cell_color = self.COLOR_BG

                # Fill cell background
                self._fill_rect(px, py, self.CELL_SIZE, self.CELL_SIZE, cell_color)

                # Draw walls
                if cell & Direction.NORTH:
                    self._fill_rect(
                        px, py, self.CELL_SIZE,
                        self.WALL_THICKNESS, self.COLOR_WALL
                    )
                if cell & Direction.SOUTH:
                    self._fill_rect(
                        px,
                        py + self.CELL_SIZE - self.WALL_THICKNESS,
                        self.CELL_SIZE,
                        self.WALL_THICKNESS,
                        self.COLOR_WALL,
                    )
                if cell & Direction.WEST:
                    self._fill_rect(
                        px, py, self.WALL_THICKNESS,
                        self.CELL_SIZE, self.COLOR_WALL
                    )
                if cell & Direction.EAST:
                    self._fill_rect(
                        px + self.CELL_SIZE - self.WALL_THICKNESS,
                        py,
                        self.WALL_THICKNESS,
                        self.CELL_SIZE,
                        self.COLOR_WALL,
                    )

        # Put image to window
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0)

    def _fill_rect(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        color: int,
    ) -> None:
        """Fill a rectangle with a color."""
        color_bytes = color.to_bytes(4, 'little')
        for dy in range(h):
            py = y + dy
            if py >= self.height * self.CELL_SIZE:
                break
            row_offset = py * self.img_sl
            for dx in range(w):
                px = x + dx
                if px >= self.width * self.CELL_SIZE:
                    break
                idx = row_offset + px * 4
                self.img_data[idx:idx+4] = color_bytes

    def _on_key(self, key: int, _data: object) -> int:
        """Handle keyboard input. Return 0 to continue, non-zero to exit."""
        # Key codes from mlxtest.py
        if key == 113:  # 'q' - quit
            self.mlx.mlx_loop_exit(self.mlx_ptr)
            return 0
        elif key == 114:  # 'r' - regenerate (placeholder)
            return 0
        elif key == 112:  # 'p' - toggle path (placeholder)
            return 0
        elif key == 99:  # 'c' - cycle colors (placeholder)
            return 0
        return 0

    def _on_expose(self, _data: object) -> int:
        """Handle expose event - redraw the window."""
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.img_ptr, 0, 0)
        return 0

    def _on_close(self, _data: object) -> int:
        """Handle window close event."""
        self.mlx.mlx_loop_exit(self.mlx_ptr)
        return 0

    def run(self) -> None:
        """Run the window event loop."""
        self.mlx.mlx_loop(self.mlx_ptr)

    def cleanup(self) -> None:
        """Clean up MLX resources."""
        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_release(self.mlx_ptr)
