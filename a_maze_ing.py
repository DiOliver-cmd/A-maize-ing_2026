#!/usr/bin/env python3
"""Generate a maze from a configuration file and write it to disk."""

import sys

from mazegen import MazeGenerator, parse_config


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
        generator = MazeGenerator(config)
        if config.perfect:
            generator.generate_perfect_base()
        else:
            generator.generate_playable()
        path = generator.shortest_path()
        generator.write_output(config.output_file, path)
    except OSError as error:
        print(f"Error: {error.filename}: {error.strerror}.")
        return 1
    except ValueError as error:
        print(f"Error: {error}")
        return 1

    print(f"Maze written to '{config.output_file}'.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
