"""Tests for the ASCII renderer."""

import re

from mazegen.config import MazeConfig
from mazegen.generator import MazeGenerator
from mazegen.renderer_ascii import BLOCK_MARK, WALL_COLORS, path_cells, render

ANSI_CODE = re.compile(r"\033\[[0-9;]*m")


def plain(text: str) -> str:
    """Remove the ANSI colour codes so the drawing can be checked."""
    return ANSI_CODE.sub("", text)


def test_path_cells_follows_the_letters() -> None:
    """Walking 'ES' from (0, 0) visits three cells."""
    assert path_cells((0, 0), "ES") == {(0, 0), (1, 0), (1, 1)}


def test_render_has_two_lines_per_row_plus_bottom() -> None:
    """A maze with H rows is drawn on 2 * H + 1 lines."""
    config = MazeConfig(4, 3, (0, 0), (3, 2), "out.txt", True, seed=1)
    gen = MazeGenerator(config)
    gen.generate_perfect_base()
    drawing = render(gen.grid, config.entry, config.exit, set(), WALL_COLORS[0])
    assert len(plain(drawing).splitlines()) == 2 * 3 + 1


def test_render_marks_entry_exit_and_path() -> None:
    """Entry, exit and every path cell in between are drawn."""
    config = MazeConfig(20, 15, (0, 0), (19, 14), "out.txt", True, seed=42)
    gen = MazeGenerator(config)
    gen.generate_perfect_base()
    cells = path_cells(config.entry, gen.shortest_path())
    drawing = plain(
        render(gen.grid, config.entry, config.exit, cells, WALL_COLORS[0])
    )
    assert drawing.count(" E ") == 1
    assert drawing.count(" X ") == 1
    assert drawing.count("·") == len(cells) - 2


def test_render_draws_closed_cells_as_blocks() -> None:
    """A cell with all four walls closed is drawn as a full block."""
    grid = [[15, 15, 15]]
    drawing = plain(render(grid, (0, 0), (2, 0), set(), WALL_COLORS[0]))
    assert drawing.count(BLOCK_MARK) == 1


def test_mlx_renderer_import() -> None:
    """Verifica se o renderizador MLX pode ser importado (se instalado)."""
    from mazegen.renderer_mlx import MazeWindow, MLX_AVAILABLE

    if MLX_AVAILABLE:
        # MLX instalado: import deve funcionar e classe disponível
        assert MazeWindow is not None
    else:
        # MLX não instalado: instanciar deve levantar RuntimeError
        try:
            MazeWindow([], (0, 0), (0, 0))
            assert False, "Expected RuntimeError when MLX not available"
        except RuntimeError:
            pass
