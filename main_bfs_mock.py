from bfs_mock import bfs_grid, path_to_directions

def run_test() -> None:
    mock_grid: list[list[int]] = [
      [0, 0, 0],
      [1, 1, 0],
      [0, 0, 0]
    ]

    start_position: tuple[int, int] = (0, 0)
    goal_position: tuple[int, int] = (2, 0)

    print("--- Executando Teste de Validação BFS e Rota Cardinal ---")
    caminho_calculado = bfs_grid(mock_grid, start_position, goal_position)

    print(f"Ponto de Entrada : {start_position}")
    print(f"Ponto de Saída   : {goal_position}")
    print(f"Caminho Gerado   : {caminho_calculado}")

    caminho_esperado: list[tuple[int, int]] = [
        (0, 0), (0, 1), (0, 2), (1, 2), (2, 2), (2, 1), (2, 0)
    ]

    assert caminho_calculado == caminho_esperado, (
        f"Falha no teste! Esperado: {caminho_esperado}, Obtido: {caminho_calculado}"
    )

    if caminho_calculado is not None:
        rota_cardinal = path_to_directions(caminho_calculado)
        print(f"Rota Cardinal    : {rota_cardinal}")

        assert rota_cardinal == "EESSWW", (
            f"Falha na conversão cardinal! Esperado 'EESSWW', obtido '{rota_cardinal}'"
        )

    print("✅ Sucesso: BFS e conversão cardinal validados com sucesso!")

if __name__ == "__main__":
    run_test()