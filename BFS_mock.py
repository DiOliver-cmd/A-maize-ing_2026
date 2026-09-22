from collections import deque

def bfs_grid(grid: list[list[int]], start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]] | None:
    rows: int = len(grid)
    cols: int = len(grid)
    # Estrutura de controle
    queue: deque[tuple[int, int]] = deque([start])
    visited: set[tuple[int, int]] = {start}
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    # Deslocamento cardial
    directions: list[tuple[int, int]] = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    # Execução do loop
    found: bool = False
    while queue:
        curr: tuple[int, int] = queue.popleft()

        if curr == goal:
            found = True
            break

        r, c = curr
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            # validando o limite da matriz e verificação de paredes (0 = livre, 1 = parede)
            if 0 <= nr < rows and 0 <= nc < cols and grid [nr][nc] == 0:
                neighbor: tuple[int, int] = (nr, nc)
                if neighbor not is visited:
                visited.add(neighbor)
                parent[neighbor] = curr # vincula o nó pai ao vizinho descoberto
                queue.append(neigbor)
            if not found:
                return None
            # Reconstrução do caminho a partir do dicionario de parent
            path: list[tuple[int, int]] = []
            curr_node: tuple[int, int] | None = goal
            while curr_node is not None:
                path.append(curr_node)
                curr_node = parent[curr_node]
            path.reverse() # Reverte para obter a ordem do inicio até o objetivo
            return path