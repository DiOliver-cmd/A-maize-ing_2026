#!/usr/bin/env python3
"""Generate a maze from a configuration file, write it and display it."""

import os
import random
import sys
from dataclasses import replace

from mazegen import MazeConfig, MazeGenerator, parse_config
from mazegen.renderer_ascii import WALL_COLORS, path_cells, render

CLEAR_SCREEN = "\033[2J\033[H"
MENU = (
    "=== A-Maze-ing ===\n"
    "1. Re-generate a new maze\n"
    "2. Show / Hide the shortest path\n"
    "3. Change the wall colour\n"
    "4. Quit"
)


def generate_maze(config: MazeConfig) -> tuple[MazeGenerator, str]:
    """Generate a maze, write it to the output file and return it.

    Args:
        config (MazeConfig): The validated configuration.

    Returns:
        tuple[MazeGenerator, str]: The generator and the shortest path.
    """
    generator = MazeGenerator(config)
    if config.perfect:
        generator.generate_perfect_base()
    else:
        generator.generate_playable()
    path = generator.shortest_path()
    generator.write_output(config.output_file, path)
    return generator, path


def run_graphical(config: MazeConfig) -> bool:
    """Open the interactive MLX window when MLX and a display are available.

    Args:
        config (MazeConfig): The validated configuration.

    Returns:
        bool: True if the graphical view was used, False to fall back to
            the terminal renderer.
    """
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        return False
    try:
        from mazegen.renderer_mlx import MLX_AVAILABLE, MazeWindow
    except ImportError:
        return False
    if not MLX_AVAILABLE:
        return False

    generator, path = generate_maze(config)
    try:
        MazeWindow(config, generator, path).run()
    except Exception as error:      # keep the program usable without X11
        print(f"MLX renderer unavailable: {error}")
        print("Falling back to the terminal renderer.")
        return False
    return True


def interact(config: MazeConfig) -> None:
    """Show the maze and react to the user's menu choices until they quit.

    Args:
        config (MazeConfig): The validated configuration.
    """
    generator, path = generate_maze(config)
    show_path = False
    color_index = 0

    while True:
        cells = path_cells(config.entry, path) if show_path else set()
        print(render(generator.grid, config.entry, config.exit, cells,
                     WALL_COLORS[color_index]))
        print(f"Seed: {config.seed}   Output: {config.output_file}")
        print(MENU)
        try:
            choice = input("Choice? (1-4): ").strip()
        except EOFError:
            return
        print(CLEAR_SCREEN, end="")

        if choice == "1":
            config = replace(config, seed=random.randrange(1_000_000))
            generator, path = generate_maze(config)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color_index = (color_index + 1) % len(WALL_COLORS)
        elif choice == "4":
            return


def main(argv: list[str]) -> int:
    """Run the maze generator.

    Args:
        argv (list[str]): Command-line arguments, without the program name.

    Returns:
        int: 0 on success, 1 on error.
    """
    if len(argv) != 1:
        print("Usage: python3 a_maze_ing.py <config_file>")
        return 1

    try:
        config = parse_config(argv[0])
        if not run_graphical(config):
            interact(config)
    except OSError as error:
        print(f"Error: {error.filename}: {error.strerror}.")
        return 1
    except ValueError as error:
        print(f"Error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
