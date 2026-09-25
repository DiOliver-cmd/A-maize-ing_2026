from dfs_back_mock import dfs_recursive_grid, path_to_directions

def run_test_dfs_recursive() -> None:
    # Grade 9x9 de teste
    mock_grid_9x9: list[list[int]] = [ 
            [0, 0, 0, 0, 0, 0, 0, 0, 0], # Linha 0: Caminho do topo livre 
            [0, 1, 1, 1, 1, 1, 1, 1, 0], # Linha 1 
            [0, 1, 1, 1, 1, 1, 1, 1, 0], # Linha 2 
            [0, 1, 1, 1, 1, 1, 1, 1, 0], # Linha 3 
            [0, 1, 1, 1, 0, 0, 0, 0, 0], # Linha 4: Curva intermediária 
            [0, 1, 1, 1, 0, 1, 1, 1, 1], # Linha 5 
            [0, 1, 1, 1, 0, 0, 0, 0, 0], # Linha 6: Retorno da curva 
            [0, 1, 1, 1, 1, 1, 1, 1, 0], # Linha 7 
            [0, 0, 0, 0, 0, 0, 0, 0, 0], # Linha 8: Caminho direto do fundo 
            ]

    start_position: tuple[int, int] = (0, 0)
    goal_position: tuple[int, int] = (8, 8)

    print("--- Executando Teste DFS RECURSIVO (Backtracker) ---")
    caminho_calculado = dfs_recursive_grid(mock_grid_9x9, start_position, goal_position)

    print(f"Ponto de Entrada : {start_position}")
    print(f"Ponto de Saída   : {goal_position}")

    if caminho_calculado is not None:
        print(f"Número de Passos : {len(caminho_calculado) - 1}")
        print(f"Caminho (Nós)   : {caminho_calculado}")

        rota_cardinal = path_to_directions(caminho_calculado)
        print(f"Rota Cardinal    : {rota_cardinal}")
        print("✅ Sucesso: O DFS Recursivo encontrou um caminho válido!")
    else:
        print("❌ Falha: Nenhum caminho foi encontrado.")

if __name__ == "__main__":
    run_test_dfs_recursive()