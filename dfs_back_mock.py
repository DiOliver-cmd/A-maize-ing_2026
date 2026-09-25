from __future__ import annotations

def dfs_recursive_grid(grid: list[list[int]], start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]] | None:

    rows: int = len(grid)
    cols: int = len(grid[0])
    visited: set[tuple[int, int]] = set()
    directions: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def solve(curr: tuple[int, int]) -> list[tuple[int, int]] | None:

        if curr == goal:
            return [curr]
        
        visited.add(curr)
        r, c = curr
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            # Valida os limites da matriz e se a célula está livre (0)
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                neighbor: tuple[int, int] = (nr, nc)
                if neighbor not in visited:
                    # Chamada recursiva para avançar na profundidade
                    path_rest = solve(neighbor)
                    if path_rest is not None:
                        return [curr] + path_rest

        # BACKTRACK: Se nenhuma das direções funcionou nesta célula,
        # retorna None para indicar falha neste ramo e voltar ao nível anterior
        return None

    # Inicia a recursão a partir da posição inicial
    return solve(start)

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
