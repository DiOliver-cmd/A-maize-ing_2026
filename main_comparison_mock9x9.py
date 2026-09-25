from bfs_mock import bfs_grid, path_to_directions
from dfs_mock import dfs_grid
from dfs_back_mock import dfs_recursive_grid

def run_triple_comparison() -> None:

    mock_grid_2paths: list[list[int]] = [ 
        [0, 0, 0, 0, 0, 0, 0, 0, 0], # Linha 0: Caminho do topo 
        [0, 1, 1, 1, 1, 1, 1, 1, 0], # Linha 1 
        [0, 1, 0, 0, 0, 0, 0, 1, 0], # Linha 2 
        [0, 1, 0, 1, 1, 1, 0, 1, 0], # Linha 3 
        [0, 1, 0, 0, 0, 0, 0, 1, 0], # Linha 4: Curva intermediária 
        [0, 1, 1, 1, 0, 1, 1, 1, 0], # Linha 5 
        [0, 1, 0, 0, 0, 0, 0, 0, 0], # Linha 6: Retorno da curva 
        [0, 1, 0, 1, 1, 1, 1, 1, 1], # Linha 7 
        [0, 0, 0, 0, 0, 0, 0, 0, 0], # Linha 8: Caminho direto do fundo 
        ]

    start_position: tuple[int, int] = (0, 0)
    goal_position: tuple[int, int] = (8, 8)

    print("==================================================================")
    print("   COMPARAÇÃO COMPLETA: BFS vs DFS ITERATIVO vs DFS RECURSIVO    ")
    print("==================================================================\n")

    # 1. BFS (Busca em Largura)
    caminho_bfs = bfs_grid(mock_grid_2paths, start_position, goal_position)
    if caminho_bfs:
        passos_bfs = len(caminho_bfs) - 1
        rota_bfs = path_to_directions(caminho_bfs)
        print("🔹 [1. BFS - Busca em Largura]")
        print(f"   Número de Passos : {passos_bfs}")
        print(f"   Rota Cardinal    : {rota_bfs}")
        print(f"   Caminho (Nós)    : {caminho_bfs}\n")

    # 2. DFS Iterativo (Pilha manual com while)
    caminho_dfs = dfs_grid(mock_grid_2paths, start_position, goal_position)
    if caminho_dfs:
        passos_dfs = len(caminho_dfs) - 1
        rota_dfs = path_to_directions(caminho_dfs)
        print("🔸 [2. DFS - Iterativo (Pilha Manual)]")
        print(f"   Número de Passos : {passos_dfs}")
        print(f"   Rota Cardinal    : {rota_dfs}")
        print(f"   Caminho (Nós)    : {caminho_dfs}\n")

    # 3. DFS Recursivo (Recursive Backtracker)
    caminho_dfs_rec = dfs_recursive_grid(mock_grid_2paths, start_position, goal_position)
    if caminho_dfs_rec:
        passos_dfs_rec = len(caminho_dfs_rec) - 1
        rota_dfs_rec = path_to_directions(caminho_dfs_rec)
        print("🔻 [3. DFS - Recursivo (Backtracker)]")
        print(f"   Número de Passos : {passos_dfs_rec}")
        print(f"   Rota Cardinal    : {rota_dfs_rec}")
        print(f"   Caminho (Nós)    : {caminho_dfs_rec}\n")

    print("==================================================================")
    print("ANÁLISE COMPARATIVA:")
    print(f" - BFS               : {len(caminho_bfs) - 1 if caminho_bfs else 'N/A'} passos (Caminho Mínimo)")
    print(f" - DFS Iterativo     : {len(caminho_dfs) - 1 if caminho_dfs else 'N/A'} passos")
    print(f" - DFS Recursivo     : {len(caminho_dfs_rec) - 1 if caminho_dfs_rec else 'N/A'} passos")
    print("==================================================================")

if __name__ == "__main__":
    run_triple_comparison()
