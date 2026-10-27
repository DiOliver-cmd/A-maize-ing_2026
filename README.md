*This project has been created as part of the 42 curriculum by dilferre, vimauric.*

# A-Maze-ing

## Description

**A-Maze-ing** is a maze generator written in Python. It reads a configuration file,
generates a random (but reproducible) maze, writes it to a file using a hexadecimal
wall encoding, and displays it with an interactive menu.

Two kinds of mazes can be generated:

- **Perfect maze** (`PERFECT=True`): exactly one path between any two cells, no loops.
- **Playable board** (`PERFECT=False`): a board usable by a Pac-Man-like game. Every
  corridor is reachable, the four corners and the centre are open, there are several
  independent routes (loops) and at most two dead-ends.

In both modes the maze contains a visible **"42"** drawn with fully closed cells, has
walls all around its border, and never contains a 3x3 open area.

The generation logic lives in a reusable package, **`mazegen`**, which is shipped as
`mazegen-1.0.0-py3-none-any.whl` at the root of this repository.

## Instructions

### Requirements

- Python **3.10** or later
- `make`

### Install and run

```bash
make install                        # create venv/ and install flake8, mypy, pytest, build
make run                            # = venv/bin/python a_maze_ing.py config.txt
```

Or directly:

```bash
python3 a_maze_ing.py config.txt
```

The program generates the maze, writes it to `OUTPUT_FILE` and shows it in the terminal
with this menu:

```
=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Change the wall colour
4. Quit
```

Option 1 draws a new random seed (shown on screen) and rewrites the output file.

### Graphical display (optional, MiniLibX)

If the MLX Python wheel provided with the subject (`mlx-2.2-py3-none-any.whl`) is
installed in the same environment **and** a display is available, the program opens a
graphical window instead of the terminal menu:

```bash
venv/bin/pip install /path/to/mlx-2.2-py3-none-any.whl
make run
```

| Key | Action |
|---|---|
| `1` / `R` | Re-generate a new maze |
| `2` / `P` | Show / hide the shortest path |
| `3` / `C` | Change the wall colour |
| `T` | Change the colour of the "42" pattern |
| `4` / `Q` / `Esc` | Quit |

Without MLX or without a display, the terminal renderer is used automatically.

### Makefile rules

| Rule | Description |
|---|---|
| `install` | Create `venv/` and install the development tools |
| `run` | Run `a_maze_ing.py config.txt` |
| `debug` | Run the program under `pdb` |
| `test` | Run the unit tests with `pytest` |
| `lint` | `flake8 .` and `mypy .` with the flags required by the subject |
| `lint-strict` | `flake8 .` and `mypy . --strict` |
| `build` | Build `mazegen-*.whl` at the root of the repository |
| `clean` | Remove caches and build leftovers |

### Rebuild and install the package

```bash
make install && make build          # creates mazegen-1.0.0-py3-none-any.whl
python3 -m venv /tmp/test_env       # any other, empty environment
/tmp/test_env/bin/pip install mazegen-1.0.0-py3-none-any.whl
/tmp/test_env/bin/python a_maze_ing.py config.txt
```

## Configuration file

One `KEY=VALUE` pair per line. Lines starting with `#` and empty lines are ignored.
Keys are case-insensitive.

| Key | Required | Description | Example |
|---|---|---|---|
| `WIDTH` | yes | Maze width, in cells (integer > 0) | `WIDTH=20` |
| `HEIGHT` | yes | Maze height, in cells (integer > 0) | `HEIGHT=15` |
| `ENTRY` | yes | Entry cell `x,y` (`(x, y)` is also accepted) | `ENTRY=0,0` |
| `EXIT` | yes | Exit cell `x,y`, different from the entry | `EXIT=19,14` |
| `OUTPUT_FILE` | yes | Path of the output file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | yes | `True` = perfect maze, `False` = playable board | `PERFECT=False` |
| `SEED` | no | Integer seed. Same seed + same config = same maze. Without it, every run is different | `SEED=42` |
| `ALGORITHM` | no | Generation algorithm. Only `backtracker` is available (default) | `ALGORITHM=backtracker` |

`PERFECT` accepts `True/False`, `yes/no`, `y/n`, `t/f` and `1/0` (any case).

Default configuration (`config.txt`):

```
# A-Maze-ing default configuration
WIDTH=15
HEIGHT=15
ENTRY=0,0
EXIT=14,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=backtracker
```

Any problem in the file (missing file, missing key, line without `=`, letters instead of
numbers, invalid boolean, malformed coordinates, entry/exit outside the maze or equal,
size ≤ 0, unwritable output file) stops the program with a clear `Error: ...` message
and exit code 1. It never ends with a traceback.

The "42" pattern needs a maze of at least **9x7** cells. On a smaller maze it is omitted
and a warning is printed.

### Output file

One hexadecimal digit per cell, one row per line. Each bit is a **closed** wall:
bit 0 = North, bit 1 = East, bit 2 = South, bit 3 = West (e.g. `A` = East and West
closed, `F` = fully closed). After an empty line come the entry `x,y`, the exit `x,y`
and the shortest path from entry to exit written with the letters `N`, `E`, `S`, `W`.

The file can be checked with the provided analyzer:

```bash
python3 maze_analyzer.py maze.txt
```

## Maze generation algorithm

We use the **recursive backtracker** (randomised depth-first search), implemented with
an explicit stack instead of recursion so large mazes cannot hit Python's recursion
limit:

1. Start with every cell fully closed and reserve the cells of the "42" pattern.
2. Push the entry cell on the stack and mark it visited.
3. While the stack is not empty: look at the top cell; if it has unvisited neighbours,
   pick one at random (`random.Random(seed)`), remove the wall between them (on both
   sides, so the encoding stays coherent) and push it; otherwise pop.
4. A final connectivity pass guarantees that every cell outside the "42" is reachable.

The result is a **perfect maze** (a spanning tree of the grid). For `PERFECT=False`, the
perfect maze is the base and is post-processed:

1. open the four corners and the centre;
2. remove extra walls until there are at least two independent routes (loops);
3. open walls next to dead-ends until at most two remain;
4. check connectivity again.

Before opening any extra wall, the generator checks that it does not create a **3x3
open area** (`_creates_open_area`), so corridors are never wider than 2 cells.

The shortest path is computed with a **breadth-first search (BFS)**, which always finds a
path with the minimum number of steps.

### Why this algorithm

- It is **simple**: a stack, a `visited` set and a random choice. Easy to implement, to
  test and to explain.
- It is a **classic**: it is one of the algorithms named in the subject, and it is well
  documented.
- It produces **perfect mazes with long, winding corridors**, exactly what
  `PERFECT=True` needs, and a good base to turn into a playable board by adding loops.

The choice was a team consensus.

## Reusable module: `mazegen`

The whole generator is the `mazegen` package (class `MazeGenerator`). It does not depend
on the renderers or on `a_maze_ing.py`.

### Install

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic example

```python
from mazegen import MazeConfig, MazeGenerator

config = MazeConfig(
    width=20, height=15,
    entry=(0, 0), exit=(19, 14),
    output_file="maze.txt",
    perfect=False,
    seed=42,
)
generator = MazeGenerator(config)
generator.generate()                 # perfect maze or playable board, per config
path = generator.shortest_path()     # e.g. "SSSSSESWSSEEEEE..."
generator.write_output(config.output_file, path)
```

### Custom parameters

All parameters are fields of `MazeConfig`: `width`, `height`, `entry`, `exit`,
`output_file`, `perfect`, `seed` (optional, `None` = random) and `algorithm` (optional).
A configuration can also be read and validated from a file:

```python
from mazegen import parse_config

config = parse_config("config.txt")  # raises ValueError / OSError on a bad file
```

### Accessing the structure and the solution

| Attribute / method | Content |
|---|---|
| `generator.grid` | `list[list[int]]`, accessed as `grid[y][x]`: the wall bitmask of each cell |
| `Direction` | `IntFlag` with `NORTH=1`, `EAST=2`, `SOUTH=4`, `WEST=8` |
| `generator.obstacles` | `set[tuple[int, int]]`: the `(x, y)` cells of the "42" |
| `generator.shortest_path()` | `str` of `N`/`E`/`S`/`W` from entry to exit (`""` if unreachable) |
| `generator.write_output(file, path)` | Write the maze in the subject's hexadecimal format |

```python
from mazegen import Direction

if generator.grid[0][0] & Direction.EAST:
    print("cell (0, 0) has a wall on its east side")
```

## Team and project management

### Roles

| Member | Role |
|---|---|
| **dilferre** | Core and algorithms: config parser, `MazeGenerator` (walls, backtracker, "42" pattern, connectivity, playable mode, 3x3 check), MLX renderer, `LICENSE.md`, CI, Makefile base, generator tests |
| **vimauric** | I/O, visual and packaging: config validation, BFS shortest path, `a_maze_ing.py` (entry point, error handling, menu), ASCII renderer, `pyproject.toml` and package build, README, config/renderer tests |

### Planning and how it evolved

We split the project into phases, with one GitHub issue per task and one owner per
file, and agreed to finish the mandatory part before any extra.

| Period | Planned | What happened |
|---|---|---|
| Oct 1–5 | Tooling, config parser, generator base | Makefile, CI (GitHub Actions), `MazeConfig` parser, wall model and backtracker, first tests |
| Oct 8–13 | Validation, "42" pattern, shortest path | Config validation, "42" pattern, BFS — on schedule |
| Oct 14–17 | Playable mode, entry point, visual | Full connectivity, Pac-Man playable mode, `a_maze_ing.py`, ASCII renderer and menu |
| Oct 22–25 | License, docs | `LICENSE.md` and module docs, plus an **MLX window** that was only planned "if time allows" |
| Oct 26 | Packaging, README | `pyproject.toml`, `.whl`, this README |

Main changes to the plan: the visual was planned as ASCII only, and ended with both
renderers (MLX when available, ASCII as fallback). Packaging and README were left for
the end.

### What worked well and what could be improved

- Everything 🙃

**Worked well**

- One issue per task, one branch per issue and a pull request reviewed by the other
  member before every merge. `main` always stayed working.
- CI running `flake8`, `mypy` (subject flags) and `pytest` on every pull request caught
  problems before review.
- Using the provided `maze_analyzer.py` as an acceptance test, plus stress tests on many
  sizes and seeds, gave us confidence in both modes.
- Clear file ownership kept merge conflicts rare.

**Could be improved**

- Some tasks overlapped (e.g. the output writer was planned for one member and done by
  the other). Checking issue ownership before starting would avoid it.
- Docstrings, the README and the packaging were left for the end. Doing them
  alongside the code would have been easier.
- The `ALGORITHM` key is read but only one algorithm exists. A second algorithm would
  make it useful.
- Small environment differences (line endings, Git identity on campus machines) cost
  some time. A shared setup checklist would help.

### Tools

- **Git and GitHub**: issues, branches, pull requests and reviews
- **GitHub Actions**: CI with `flake8`, `mypy` and `pytest`
- **flake8**, **mypy**, **pytest**: style, type checking and unit tests
- **venv** and **make**: isolated environment and task automation
- **setuptools** and **build**: packaging of `mazegen`
- **maze_analyzer.py** (provided with the subject): validation of the output files
- **AI assistants**: see Resources

## Resources

- [Maze generation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- Jamis Buck, [Maze Generation: Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking)
  and the book *Mazes for Programmers* (Pragmatic Bookshelf, 2015)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- Python documentation: [`random`](https://docs.python.org/3/library/random.html),
  [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque),
  [`dataclasses`](https://docs.python.org/3/library/dataclasses.html),
  [`enum.IntFlag`](https://docs.python.org/3/library/enum.html#enum.IntFlag)
- [Python Packaging User Guide — Writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [PEP 257 — Docstring Conventions](https://peps.python.org/pep-0257/)
- [mypy documentation](https://mypy.readthedocs.io/) and [flake8 documentation](https://flake8.pycqa.org/)
- [Choose a License — MIT](https://choosealicense.com/licenses/mit/)

### How AI was used

AI assistants were used as a **consultation tool** (to clarify concepts, Python and
packaging documentation, and to discuss ideas) and to **organise the tasks** of the
project. All code was written, tested and reviewed by the team members, who can explain
every part of it.
