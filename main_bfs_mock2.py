from bfs_mock import bfs_grid, path_to_directions

def run_test_bfs_9x9() -> None:
    # Matriz 9x9 (0 = caminho livre, 1 = parede)
    mock_grid_9x9: list[list[int]] = [ 
        [0, 0, 0, 0, 0, 1, 0, 0, 0], # Linha 0 
        [1, 1, 0, 1, 0, 1, 0, 1, 0], # Linha 1 
        [0, 0, 0, 1, 0, 0, 0, 1, 0], # Linha 2 
        [0, 1, 1, 1, 1, 1, 0, 1, 0], # Linha 3 
        [0, 0, 0, 0, 0, 0, 0, 1, 0], # Linha 4 
        [1, 1, 1, 1, 1, 1, 0, 1, 0], # Linha 5 
        [0, 0, 0, 0, 0, 0, 0, 0, 0], # Linha 6 
        [0, 1, 1, 1, 1, 1, 1, 1, 0], # Linha 7 
        [0, 0, 0, 0, 0, 0, 0, 0, 0], # Linha 8 
        ]

    start_position: tuple[int, int] = (0, 0)
    goal_position: tuple[int, int] = (8, 8)

    print("--- Executando Teste BFS em Grade 9x9 ---")
    caminho_calculado = bfs_grid(mock_grid_9x9, start_position, goal_position)

    print(f"Ponto de Entrada : {start_position}")
    print(f"Ponto de Saída   : {goal_position}")

    if caminho_calculado is not None:
        print(f"Número de Passos : {len(caminho_calculado) - 1}")
        print(f"Caminho (Nós)   : {caminho_calculado}")

        rota_cardinal = path_to_directions(caminho_calculado)
        print(f"Rota Cardinal    : {rota_cardinal}")
        print("✅ Sucesso: O BFS encontrou uma rota válida até a saída!")
    else:
        print("❌ Falha: Nenhum caminho foi encontrado.")

if __name__ == "__main__":
    run_test_bfs_9x9()