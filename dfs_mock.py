from __future__ import annotations

def dfs_grid(grid: list[list[int]], start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]] | None:
    rows: int = len(grid)
    cols: int = len(grid[0])
# estrutura de controle
    stack: list[tuple[int, int]] = [start]
    visited: set[tuple[int, int]] = {start}
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

    directions: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    found: bool = False
    while stack:
        # DFS usa: stack.pop()     (Remove o ÚLTIMO que entrou - LIFO)
        curr: tuple[int, int] = stack.pop()

        if curr == goal:
            found = True
            break

        r, c = curr
        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                neighbor: tuple[int, int] = (nr, nc)
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = curr
                    stack.append(neighbor)

    if not found:
        return None

    # Reconstrução do caminho (idêntico ao BFS)
    path: list[tuple[int, int]] = []
    curr_node: tuple[int, int] | None = goal
    while curr_node is not None:
        path.append(curr_node)
        curr_node = parent[curr_node]

    path.reverse()
    return path


def path_to_directions(path: list[tuple[int, int]]) -> str:
    if not path or len(path) < 2:
        return ""

    directions: list[str] = []
    for i in range(len(path) - 1):
        r1, c1 = path[i]
        r2, c2 = path[i + 1]

        dr = r2 - r1
        dc = c2 - c1

        if dr == -1 and dc == 0:
            directions.append("N")
        elif dr == 1 and dc == 0:
            directions.append("S")
        elif dr == 0 and dc == 1:
            directions.append("E")
        elif dr == 0 and dc == -1:
            directions.append("W")

    return "".join(directions)