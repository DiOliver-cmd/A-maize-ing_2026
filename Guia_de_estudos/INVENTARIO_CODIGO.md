# Inventário do Código — A-Maze-ing

> Mapa completo de **classes, métodos e funções** da implementação, agrupados por
> módulo, com uma descrição curta do papel de cada um. Serve como guia de leitura do
> código e como apoio à defesa do projeto.
>
> Convenções: `F` = função livre, `C` = classe, `M` = método. Assinaturas simplificadas
> (sem `self`/tipos) para leitura rápida.

---

## 1. Visão geral da arquitetura

```
a_maze_ing.py            ponto de entrada / menu / escolha do renderizador
├── mazegen/config.py        leitura e validação do config.txt
├── mazegen/generator.py     geração, algoritmos, BFS, escrita do output
├── mazegen/renderer_ascii.py  vista de texto (fallback)
└── mazegen/renderer_mlx.py    vista gráfica interativa (MLX)

maze_analyzer.py         validador independente (lê o arquivo gerado)
tests/                   testes de config, generator e renderer
```

Fluxo principal: `parse_config` → `MazeGenerator.generate` → `shortest_path` →
`write_output` → `render` (ASCII ou MLX). O `maze_analyzer.py` é um **leitor
independente**: ele não reutiliza o gerador, apenas interpreta o arquivo final.

---

## 2. `a_maze_ing.py` — entrada do programa

| Item | O que faz |
|---|---|
| `F generate_maze(config)` | Gera o labirinto, calcula o caminho mais curto, grava `OUTPUT_FILE` e devolve `(generator, path)`. |
| `F run_graphical(config)` | Abre a janela MLX interativa quando MLX e um display estão disponíveis; devolve `False` para permitir o fallback ASCII. |
| `F interact(config)` | Menu de texto com as 4 opções clássicas (regerar, mostrar/ocultar caminho, cor, sair), redesenhando a cada ação. |
| `F main(argv)` | Ponto de entrada: lê argumentos, valida a configuração e escolhe MLX ou ASCII. |

---

## 3. `maze_analyzer.py` — validador independente

### 3.1 Tipos básicos

| Item | O que faz |
|---|---|
| `C Direction` (enum) | Um lado de parede. O valor inteiro **é** o bit usado na codificação hexadecimal. |
| `M Direction.opposite()` | O mesmo lado visto da célula vizinha. |
| `M Direction.step()` | Offset `(row, col)` até o vizinho desse lado. |
| `C MazeError` | Exceção para arquivo que não pode ser interpretado como labirinto. |

### 3.2 `C Maze` — leitura e consultas sobre a grelha

| Item | O que faz |
|---|---|
| `M __init__(grid, entry, exit)` | Guarda a grelha de máscaras e as células opcionais de entrada/saída. |
| `M from_file(path)` *(classmethod)* | Faz o parse do arquivo; valida linhas hexadecimais e formato retangular. |
| `M _parse_row(text, number, grid)` | Converte uma linha hexadecimal e impõe largura constante. |
| `M _parse_coordinate(text)` | Converte a linha de rodapé `x,y` para a representação interna `(row, col)`. |
| `M __contains__(cell)` | `True` se a célula está dentro dos limites. |
| `M __iter__()` | Itera todas as células em ordem de linhas. |
| `M walls(cell)` | Devolve a máscara de paredes da célula. |
| `M is_fully_closed(cell)` | `True` para as células isoladas que desenham o padrão obrigatório “42”. |
| `M neighbour(cell, side)` | Célula adjacente naquele lado. |
| `M is_open(cell, side)` | `True` apenas se a parede está aberta **dos dois lados** (coerência). |
| `M passages(cell)` | Vizinhos com os quais a célula partilha uma passagem aberta. |
| `M region_of(start)` | BFS: conjunto de células alcançáveis a partir de `start`. |
| `M largest_region()` | Maior componente conexa, obtida numa única passagem linear. |
| `M incoherent_cells()` | Células cuja codificação de parede contradiz o vizinho. |

### 3.3 `C MazeReport` — métricas de conectividade

| Item | O que faz |
|---|---|
| `M open_passages()` | Arestas reais do grafo da região (cada uma contada uma vez). |
| `M potential_passages()` | Arestas que existiriam se todas as paredes internas fossem abertas. |
| `M loops()` | Ciclos independentes: `edges - nodes + 1` para uma componente. |
| `M max_loops()` | Arestas além de uma árvore geradora (máximo de loops possível). |
| `M path_ratio()` | Loops como fração do máximo possível. |
| `M isolated()` | Número de células fora da região analisada. |
| `M disconnected_corridors()` | Células fora da região jogável que não fazem parte do “42”. |
| `M exit_reachable()` | Se a saída do rodapé pertence à região analisada. |
| `M dead_ends()` | Contagem `(reais, fechados pelo “42”)` de células com uma só abertura. |
| `M _has_openable_wall(cell)` | `True` se alguma parede fechada da célula dá para um corredor normal. |
| `M unreachable_key_cells()` | Pac-Man exige os quatro cantos e o centro como corredores. |
| `M _centre_candidates()` | A(s) célula(s) em torno do meio, considerando dimensões pares. |

### 3.4 Funções de análise e de relatório

| Item | O que faz |
|---|---|
| `F analyze(maze)` | Escolhe a região jogável (entrada ou a maior) e calcula as métricas. |
| `F verdict(report, min_loops, max_dead_ends)` | Devolve a conclusão de uma linha (aprovado/reprovado). |
| `F render(report, min_loops, max_dead_ends)` | Constrói o relatório humano completo. |
| `F _xy(cell)` | Converte `(row, col)` interno para o `(x, y)` do enunciado. |
| `F _exit(report)` | Formata a coordenada de saída e se é alcançável. |
| `F _key_cells(cells)` | Formata as células-chave inalcançáveis. |
| `F _coherence(cells)` | Resume as incoerências de paredes. |
| `F parse_args(argv)` | Faz o parse dos argumentos de linha de comando. |
| `F main(argv)` | Lê, analisa e imprime o relatório; devolve o código de saída. |

---

## 4. `mazegen/config.py` — configuração

| Item | O que faz |
|---|---|
| `C MazeConfig` | Dataclass com dimensões, entrada, saída, arquivo de output, `PERFECT`, seed e algoritmo. |
| `F validate_config(config)` | Rejeita dimensões inválidas, coordenadas fora dos limites, entrada igual à saída e output vazio. |
| `F parse_int(key, value)` | Converte inteiro, nomeando a chave na mensagem de erro. |
| `F parse_bool(key, value)` | Converte representações textuais de booleano. |
| `F parse_tuple(key, value)` | Converte coordenadas em `(x, y)` ou `x,y`. |
| `F parse_config(path)` | Lê o arquivo `KEY=VALUE`, aplica defaults e valida o resultado. |

---

## 5. `mazegen/generator.py` — geração

| Item | O que faz |
|---|---|
| `C Direction` (IntEnum) | Bits N/E/S/W usados na máscara de paredes. |
| `C MazeGenerator` | Constrói e transforma a grelha a partir da configuração. |

### Métodos de `MazeGenerator`

| Item | O que faz |
|---|---|
| `M __init__(config)` | Inicializa a grelha toda fechada (`0xF`), espaços de trabalho e obstáculos. |
| `M is_valid_cell(x, y)` | Verifica se as coordenadas estão dentro dos limites. |
| `M get_direction(cell_a, cell_b)` | Determina a direção de movimento de A para B. |
| `M remove_wall(cell_a, cell_b)` | Abre a parede entre duas células de forma **bilateral**. |
| `M get_unvisited_neighbors(x, y, visited)` | Vizinhos dentro dos limites ainda não visitados. |
| `M _apply_pattern_42()` | Aplica o padrão “42” como células-obstáculo totalmente fechadas. |
| `M generate_backtracker()` | Escava o labirinto com *recursive backtracker* (reprodutível pela seed). |
| `M write_output(filename, path_str)` | Grava a grelha hexadecimal, entrada/saída e caminho no arquivo. |
| `M shortest_path()` | BFS da entrada à saída; devolve a string de letras (`N/E/S/W`). |
| `M get_reachable_cells(start_cell)` | Todas as células não-obstáculo alcançáveis a partir de uma célula. |
| `M ensure_full_connectivity()` | Abre paredes até não restarem corredores isolados. |
| `M generate_perfect_base()` | Cria uma base perfeita (um único caminho entre quaisquer duas células). |
| `M _count_open_passages(x, y)` | Conta as passagens abertas de uma célula (o seu grau). |
| `M _get_real_dead_ends()` | Dead-ends reais (grau 1, excluindo células do “42”). |
| `M _creates_open_area(x, y)` | Evita abrir uma área 3×3 totalmente livre. |
| `M _ensure_key_cells_open()` | Garante cantos e centro como corredores abertos. |
| `M _add_loops(min_loops)` | Remove paredes até atingir o número mínimo de loops. |
| `M _reduce_dead_ends(max_dead_ends)` | Abre paredes para reduzir os dead-ends reais ao limite. |
| `M generate_playable()` | Modo `PERFECT=False`: base perfeita + loops + dead-ends controlados. |
| `M generate()` | Despacha para backtracker puro (perfeito) ou modo jogável. |

---

## 6. `mazegen/renderer_ascii.py` — vista de texto

| Item | O que faz |
|---|---|
| `F path_cells(entry, path)` | Converte a string de letras nas células visitadas. |
| `F render(grid, entry, exit_, path, wall_color)` | Desenha o labirinto em ASCII/ANSI, 3 caracteres por célula, com cores. |

---

## 7. `mazegen/renderer_mlx.py` — vista gráfica interativa

### 7.1 `C MazeSession` — estado mutável da vista

| Item | O que faz |
|---|---|
| `M __init__(config, generator, path, show_path)` | Guarda o labirinto inicial e o estado de apresentação. |
| `M wall_color_name()` / `M wall_color()` | Nome e valor MLX da cor de parede atual. |
| `M pattern_color_name()` / `M pattern_color()` | Idem para as células do “42”. |
| `M path_cell_set()` | Células do caminho, ou conjunto vazio enquanto o caminho está oculto. |
| `M path_points()` | Células do caminho mais curto, em ordem, começando na entrada. |
| `M toggle_path()` | Mostra o caminho se estiver oculto; oculta se estiver visível. |
| `M cycle_wall_color()` | Avança para a próxima cor de parede. |
| `M cycle_pattern_color()` | Avança para a próxima cor do “42”. |
| `M regenerate(seed)` | Cria novo labirinto, reescreve o arquivo e preserva as preferências da vista. |
| `M status_text()` | Resumo de uma linha mostrado no rodapé da janela. |

### 7.2 `C MazeWindow` — janela e desenho

| Item | O que faz |
|---|---|
| `M __init__(config, generator, path)` | Cria a janela, a imagem, os hooks de eventos e desenha o primeiro frame. |
| `M _screen_size()` | Devolve o tamanho do ecrã, com um valor padrão seguro. |
| `M _cell_size(screen_width, screen_height)` | Escolhe a maior célula que mantém a janela visível. |
| `M _fill_rect(x, y, width, height, color)` | Preenche um retângulo recortado (uma escrita de *slice* por linha). |
| `M _draw()` | Redesenha a cena completa e o HUD. |
| `M _draw_cells()` | Desenha fundos, padrão “42” e todas as paredes. |
| `M _draw_path()` | Desenha o caminho mais curto como polilinha ortogonal. |
| `M _draw_text()` | Desenha o HUD e os rótulos `E`/`X` sobre a imagem. |
| `M _fit(text, max_width)` | Encurta o texto com `...` para caber na largura dada. |
| `M _on_key(key, _param)` | Trata teclas: `1/R`, `2/P`, `3/C`, `T`, `4/Q/Esc`; apenas marca `_dirty`. |
| `M _on_loop(_param)` | Redesenha o estado pendente **fora** do callback de eventos, seguido de `mlx_do_sync`. |
| `M _on_expose(_param)` | Pede redesenho depois de o window manager expor a janela. |
| `M _on_close(_param)` | Termina o loop quando a janela é fechada. |
| `M _quit()` | Pede ao MLX para sair do loop (a limpeza acontece em `run`). |
| `M run()` | Corre o loop de eventos até a janela fechar. |
| `M cleanup()` | Liberta os recursos MLX exatamente uma vez. |

---

## 8. Testes

Os testes não fazem parte da aplicação, mas documentam o comportamento esperado.

### 8.1 `tests/test_config.py` (11 testes)

Criação da dataclass; parse de arquivo válido; dimensões inválidas; validação de
entrada/saída dentro dos limites; entrada ≠ saída; output não vazio; rejeição de
`int`, `tuple` e `bool` malformados.

### 8.2 `tests/test_generator.py` (17 testes)

Inicialização da grelha; coerência bilateral de `remove_wall`; determinismo por seed;
padrão “42” em grelhas grandes e pequenas; BFS (passo único, sem caminho, caminho que
atravessa apenas paredes abertas); alcançabilidade; conectividade total; base perfeita;
loops mínimos; controlo de dead-ends; cantos/centro alcançáveis; coerência de paredes;
API pública; despacho de `generate()`.

### 8.3 `tests/test_renderer.py` (`plain` + 5 testes)

`plain(text)` remove códigos ANSI; verifica `path_cells`; número de linhas
(`2 * H + 1`); marcação de entrada/saída/caminho; células fechadas como bloco; e o
import do renderizador MLX (ou `RuntimeError` quando indisponível).

---

## 9. Módulos sem símbolos próprios

| Arquivo | Conteúdo |
|---|---|
| `mazegen/__init__.py` | Apenas reexporta a API pública (`MazeConfig`, `parse_config`, `MazeGenerator`, ...). |
| `conftest.py` | Apenas configuração de caminho para o pytest. |
