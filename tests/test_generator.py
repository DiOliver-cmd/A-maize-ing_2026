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


def test_generate_playable_creates_loops() -> None:
    """Garante que a geração jogável cria pelo menos 2 loops (T5.3)."""
    config = MazeConfig(20, 15, (0, 0), (19, 14), "out.txt", False, seed=42)
    gen = MazeGenerator(config)
    gen.generate_playable()

    # Count loops using the same formula as maze_analyzer
    reachable = gen.get_reachable_cells(config.entry)
    open_passages = 0
    for x, y in reachable:
        cell_walls = gen.grid[y][x]
        for direction, (dx, dy) in MOVE_OFFSETS.items():
            if not (cell_walls & direction.value):
                nx, ny = x + dx, y + dy
                if (nx, ny) in reachable and (nx, ny) > (x, y):
                    open_passages += 1
    loops = open_passages - len(reachable) + 1

    assert loops >= 2

    # Verify no 3x3 fully open area
    assert not gen._creates_open_area(0, 0)  # Check a few positions
    for y in range(gen.height - 2):
        for x in range(gen.width - 2):
            assert not gen._creates_open_area(x, y)


def test_generate_playable_controls_dead_ends() -> None:
    """Garante que a quantidade de dead-ends reais é reduzida a <= 2 (T5.4)."""
    config = MazeConfig(15, 12, (0, 0), (14, 11), "out.txt", False, seed=10)
    gen = MazeGenerator(config)
    gen.generate_playable()

    # Count real dead-ends (matching maze_analyzer definition)
    real_dead_ends = 0
    reachable = gen.get_reachable_cells(config.entry)
    for x, y in reachable:
        if (x, y) in gen.obstacles:
            continue
        # Count open passages
        open_count = 0
        cell_walls = gen.grid[y][x]
        for direction, (dx, dy) in MOVE_OFFSETS.items():
            if not (cell_walls & direction.value):
                nx, ny = x + dx, y + dy
                if gen.is_valid_cell(nx, ny) and (nx, ny) not in gen.obstacles:
                    open_count += 1
        if open_count == 1:
            # Check if it's a "real" dead-end (has openable wall to normal cell)
            has_openable = False
            for direction, (dx, dy) in MOVE_OFFSETS.items():
                if cell_walls & direction.value:
                    nx, ny = x + dx, y + dy
                    if (
                        gen.is_valid_cell(nx, ny)
                        and (nx, ny) not in gen.obstacles
                        and not (gen.grid[ny][nx] == Direction.ALL_WALLS)
                    ):
                        has_openable = True
                        break
            if has_openable:
                real_dead_ends += 1

    assert real_dead_ends <= 2


def test_generate_playable_key_cells_reachable() -> None:
    """Garante que cantos e centro são alcançáveis no modo jogável (T5.2)."""
    config = MazeConfig(20, 15, (0, 0), (19, 14), "out.txt", False, seed=42)
    gen = MazeGenerator(config)
    gen.generate_playable()

    reachable = gen.get_reachable_cells(config.entry)

    # Four corners
    corners = [
        (0, 0),
        (gen.width - 1, 0),
        (0, gen.height - 1),
        (gen.width - 1, gen.height - 1),
    ]
    for corner in corners:
        assert corner in reachable, f"Corner {corner} not reachable"

    # Center cell(s)
    center_candidates = set()
    if gen.width % 2 == 1 and gen.height % 2 == 1:
        center_candidates.add((gen.width // 2, gen.height // 2))
    elif gen.width % 2 == 0 and gen.height % 2 == 1:
        center_candidates.add((gen.width // 2 - 1, gen.height // 2))
        center_candidates.add((gen.width // 2, gen.height // 2))
    elif gen.width % 2 == 1 and gen.height % 2 == 0:
        center_candidates.add((gen.width // 2, gen.height // 2 - 1))
        center_candidates.add((gen.width // 2, gen.height // 2))
    else:
        center_candidates.add((gen.width // 2 - 1, gen.height // 2 - 1))
        center_candidates.add((gen.width // 2, gen.height // 2 - 1))
        center_candidates.add((gen.width // 2 - 1, gen.height // 2))
        center_candidates.add((gen.width // 2, gen.height // 2))

    assert any(c in reachable for c in center_candidates), "Center not reachable"


def test_generate_playable_wall_coherence() -> None:
    """Garante coerência de paredes no modo jogável."""
    config = MazeConfig(20, 15, (0, 0), (19, 14), "out.txt", False, seed=42)
    gen = MazeGenerator(config)
    gen.generate_playable()

    # Check all adjacent cells have matching walls
    for y in range(gen.height):
        for x in range(gen.width):
            if (x, y) in gen.obstacles:
                continue
            for direction, (dx, dy) in MOVE_OFFSETS.items():
                nx, ny = x + dx, y + dy
                if gen.is_valid_cell(nx, ny) and (nx, ny) not in gen.obstacles:
                    wall_a = bool(gen.grid[y][x] & direction.value)
                    opp = {
                        Direction.NORTH: Direction.SOUTH,
                        Direction.SOUTH: Direction.NORTH,
                        Direction.EAST: Direction.WEST,
                        Direction.WEST: Direction.EAST,
                    }[direction]
                    wall_b = bool(gen.grid[ny][nx] & opp.value)
                    assert wall_a == wall_b, (
                        f"Incoherent wall at ({x},{y}) {direction.name}"
                    )


def test_module_public_api() -> None:
    """Testa se a API pública do módulo funciona conforme exemplo do __init__.py."""
    from mazegen import MazeGenerator, MazeConfig

    config = MazeConfig(10, 10, (0, 0), (9, 9), "out.txt", True, seed=42)
    gen = MazeGenerator(config)
    gen.generate()  # método público adicionado
    assert gen.grid is not None
    path = gen.shortest_path()
    assert isinstance(path, str)


def test_generate_method_dispatch() -> None:
    """Verifica se generate() despacha para o modo correto."""
    from mazegen import MazeGenerator, MazeConfig

    # PERFECT=True -> loops == 0
    config1 = MazeConfig(10, 10, (0, 0), (9, 9), "out.txt", True, seed=42)
    gen1 = MazeGenerator(config1)
    gen1.generate()
    reachable = gen1.get_reachable_cells(config1.entry)
    open_passages = sum(
        1
        for x, y in reachable
        for d, (dx, dy) in MOVE_OFFSETS.items()
        if not (gen1.grid[y][x] & d.value)
        and (x + dx, y + dy) in reachable
        and (x + dx, y + dy) > (x, y)
    )
    loops = open_passages - len(reachable) + 1
    assert loops == 0

    # PERFECT=False -> loops >= 2
    config2 = MazeConfig(10, 10, (0, 0), (9, 9), "out.txt", False, seed=42)
    gen2 = MazeGenerator(config2)
    gen2.generate()
    reachable = gen2.get_reachable_cells(config2.entry)
    open_passages = sum(
        1
        for x, y in reachable
        for d, (dx, dy) in MOVE_OFFSETS.items()
        if not (gen2.grid[y][x] & d.value)
        and (x + dx, y + dy) in reachable
        and (x + dx, y + dy) > (x, y)
    )
    loops = open_passages - len(reachable) + 1
    assert loops >= 2
