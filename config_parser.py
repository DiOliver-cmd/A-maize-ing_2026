from __future__ import annotations
from dataclasses import dataclass
import os
import re

@dataclass
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool

def parse_tuple(value_str: str) -> tuple[int, int]:
    """Converte strings como '(0, 0)' ou '0, 0' em tupla de inteiros (x, y)."""
    cleaned = value_str.strip().strip("()")
    parts = [p.strip() for p in cleaned.split(",")]
    if len(parts) != 2:
        raise ValueError(f"Formato de coordenada inválido: '{value_str}' (esperado '(x, y)')")
    return int(parts[0]), int(parts[1])

def parse_bool(value_str: str) -> bool:
    """Converte 'True'/'False', '1'/'0', 'yes'/'no' em bool."""
    val = value_str.strip().lower()
    if val in ("true", "1", "yes"):
        return True
    if val in ("false", "0", "no"):
        return False
    raise ValueError(f"Valor booleano inválido: '{value_str}'")

def load_config(filepath: str) -> Config:
    """Lê, interpreta e valida o arquivo config.txt."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: '{filepath}'")

    raw_data: dict[str, str] = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            # Ignora linhas em branco e comentários
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(f"Erro de sintaxe na linha {line_num}: '{line}' (esperado CHAVE=VALOR)")
            key, value = line.split("=", 1)
            raw_data[key.strip().upper()] = value.strip()

    # Checa se todas as chaves obrigatórias existem
    required_keys = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
    missing = required_keys - set(raw_data.keys())
    if missing:
        raise ValueError(f"Chaves obrigatórias ausentes no config.txt: {missing}")

    # Conversão de tipos
    try:
        width = int(raw_data["WIDTH"])
        height = int(raw_data["HEIGHT"])
        entry = parse_tuple(raw_data["ENTRY"])
        exit_pos = parse_tuple(raw_data["EXIT"])
        output_file = raw_data["OUTPUT_FILE"]
        perfect = parse_bool(raw_data["PERFECT"])
    except ValueError as e:
        raise ValueError(f"Erro de conversão de dados no config: {e}")

    # Validações de limites e regras de negócio
    if width < 3 or height < 3:
        raise ValueError(f"Dimensões inválidas ({width}x{height}). O tamanho mínimo é 3x3.")

    entry_x, entry_y = entry
    if not (0 <= entry_x < width and 0 <= entry_y < height):
        raise ValueError(f"Ponto de ENTRY {entry} está fora dos limites da grade ({width}x{height}).")

    exit_x, exit_y = exit_pos
    if not (0 <= exit_x < width and 0 <= exit_y < height):
        raise ValueError(f"Ponto de EXIT {exit_pos} está fora dos limites da grade ({width}x{height}).")

    if entry == exit_pos:
        raise ValueError(f"ENTRY {entry} e EXIT {exit_pos} não podem ser iguais.")

    if not output_file.endswith(".txt"):
        raise ValueError(f"OUTPUT_FILE '{output_file}' deve ter extensão .txt.")

    return Config(
        width=width,
        height=height,
        entry=entry,
        exit=exit_pos,
        output_file=output_file,
        perfect=perfect,
    )