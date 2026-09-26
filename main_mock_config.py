import os
from config_parser import load_config


def run_config_test() -> None:
    # 1. Cria um config.txt válido para teste
    test_config_content = """# Arquivo de Teste A-Maze-ing
WIDTH=10
HEIGHT=10
ENTRY=(0, 0)
EXIT=(9, 9)
OUTPUT_FILE=maze.txt
PERFECT=True
"""
    config_filename = "config_test.txt"
    with open(config_filename, "w", encoding="utf-8") as f:
        f.write(test_config_content)

    print("--- Executando Teste de Leitura do config.txt ---")
    try:
        cfg = load_config(config_filename)
        print("✅ Configuração carregada com sucesso!")
        print(f"  Largura (WIDTH)  : {cfg.width}")
        print(f"  Altura (HEIGHT)  : {cfg.height}")
        print(f"  Entrada (ENTRY)  : {cfg.entry}")
        print(f"  Saída (EXIT)     : {cfg.exit}")
        print(f"  Arquivo de Saída : {cfg.output_file}")
        print(f"  Perfeito (PERFECT): {cfg.perfect}")
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
    finally:
        # Limpa o arquivo de teste após executar
        if os.path.exists(config_filename):
            os.remove(config_filename)


if __name__ == "__main__":
    run_config_test()