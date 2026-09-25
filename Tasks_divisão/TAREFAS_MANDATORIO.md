# Tarefas de Execução — Parte Mandatória (A-Maze-ing)

> Plano de execução **passo a passo** da parte mandatória. Cada tarefa tem:
> **objetivo**, **arquivos afetados**, **critério de conclusão** e **dependências**.
> Termos técnicos essenciais em inglês; explicação em português.
>
> **Ordem recomendada:** seguir a numeração. As fases 1–3 (setup, config, núcleo) são
> pré-requisito de tudo. Não pular para a visualização antes do núcleo estar validado
> pelo `maze_analyzer.py`.

**Convenção de coordenadas usada em todo o projeto:** `x = coluna`, `y = linha`.
Internamente pode-se usar `(row, col)`, mas **sempre** converter ao ler/escrever o
arquivo (que usa `x,y`).

---

## Fase 0 — Setup do Repositório e Ambiente

### T0.1 — Inicializar repositório Git
- **Objetivo:** criar a base do projeto versionado.
- **Ações:**
  - `git init` no diretório do projeto.
  - Criar `.gitignore` com: `__pycache__/`, `*.pyc`, `.mypy_cache/`, `.pytest_cache/`,
    `dist/`, `build/`, `*.egg-info/`, `venv/`, `.venv/`, `*.whl`, `*.tar.gz` (opcional
    manter o `.whl` final na raiz — ver T6.4).
  - Criar a estrutura de diretórios sugerida:
    ```
    a_maze_ing.py          # entry point (nome obrigatório)
    mazegen/               # pacote reutilizável (ou mazegen.py — ver T6.1)
      __init__.py
      generator.py
    config.txt             # config padrão
    Makefile
    README.md
    LICENSE.md
    pyproject.toml
    tests/                 # testes (não avaliados, mas recomendados)
    ```
- **Critério:** `git status` limpo; estrutura criada.

### T0.2 — Criar e ativar virtualenv
- **Ações:** `python3 -m venv venv && source venv/bin/activate`.
- Instalar ferramentas de dev: `pip install flake8 mypy pytest build`.
- **Critério:** `python --version` ≥ 3.10; ferramentas instaladas.

### T0.3 — Criar o `Makefile`
- **Objetivo:** automatizar tarefas (regras obrigatórias do subject).
- **Conteúdo mínimo:**
  ```makefile
  .PHONY: install run debug clean lint lint-strict

  install:
  	pip install -e . flake8 mypy pytest build

  run:
  	python3 a_maze_ing.py config.txt

  debug:
  	python3 -m pdb a_maze_ing.py config.txt

  clean:
  	rm -rf __pycache__ .mypy_cache .pytest_cache dist build *.egg-info

  lint:
  	flake8 .
  	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
  	       --disallow-untyped-defs --check-untyped-defs

  lint-strict:
  	flake8 .
  	mypy . --strict
  ```
- **Critério:** `make lint` executa sem erro de sintaxe do Makefile.

---

## Fase 1 — Parser de Configuração

### T1.1 — Definir o modelo de configuração
- **Objetivo:** representar e validar as opções do `config.txt`.
- **Arquivos:** `mazegen/config.py` (ou dentro de `generator.py`).
- **Ações:**
  - Criar um `@dataclass` `MazeConfig` com campos: `width: int`, `height: int`,
    `entry: tuple[int,int]` (x,y), `exit: tuple[int,int]`, `output_file: str`,
    `perfect: bool`, e opcionais `seed: int | None`, `algorithm: str`.
  - Função `parse_config(path: str) -> MazeConfig` que:
    - Lê o arquivo linha a linha (context manager).
    - Ignora linhas em branco e linhas começando com `#`.
    - Faz split em `=` (primeiro `=` apenas, para permitir `=` em valores).
    - Faz *strip* de espaços.
    - Converte tipos (`int`, `bool` aceitando `True/False/1/0/yes/no`).
    - Valida presença de **todas** as chaves mandatórias.
- **Critério:** parseia o `config.txt` padrão; rejeita chaves ausentes com mensagem clara.

### T1.2 — Validação semântica
- **Ações:** em `parse_config` (ou função `validate`):
  - `width > 0`, `height > 0`.
  - `entry` e `exit` dentro dos limites: `0 <= x < width`, `0 <= y < height`.
  - `entry != exit`.
  - `output_file` não vazio.
  - Mensagens de erro **específicas** e em português/inglês (consistente).
- **Critério:** entradas inválidas geram `ValueError` com mensagem; **sem crash**.

### T1.3 — Criar `config.txt` padrão
- **Conteúdo exemplo:**
  ```
  # A-Maze-ing default configuration
  WIDTH=20
  HEIGHT=15
  ENTRY=0,0
  EXIT=19,14
  OUTPUT_FILE=maze.txt
  PERFECT=True
  SEED=42
  ```
- **Critério:** arquivo presente na raiz do repositório.

---

## Fase 2 — Núcleo do Gerador (Estrutura de Dados)

### T2.1 — Definir `Direction` (IntFlag)
- **Arquivos:** `mazegen/generator.py`.
- **Ações:**
  ```python
  from enum import IntFlag
  class Direction(IntFlag):
      NORTH = 1
      EAST  = 2
      SOUTH = 4
      WEST  = 8
  ```
  - Propriedades `opposite` e `step` (offset `(dr, dc)`), espelhando o `maze_analyzer.py`.
  - Constante `ALL_WALLS = NORTH|EAST|SOUTH|WEST` (=15).
- **Critério:** valores batem com o analisador (bit 0=N, 1=E, 2=S, 3=W).

### T2.2 — Definir a classe `MazeGenerator`
- **Ações:**
  - Construtor: `__init__(self, width, height, entry, exit, perfect=True, seed=None,
    algorithm="backtracker")`.
  - Atributos: `width`, `height`, `entry` (convertido para `(row,col)`), `exit`,
    `perfect`, `rng = random.Random(seed)`.
  - Estado interno: `grid: list[list[int]]` (inicializada com `ALL_WALLS` em toda célula).
  - Métodos previstos: `generate()`, `walls(cell)`, `remove_wall(a,b)`, `shortest_path()`.
- **Critério:** instanciável; `grid` inicializada corretamente.

### T2.3 — Helpers de parede (coerência garantida)
- **Ações:**
  - `remove_wall(a, b)`: determina a direção de `a`→`b`, limpa o bit correspondente em
    `a` **e** o bit oposto em `b` (sempre os dois lados).
  - `is_open(cell, side)`: verifica ambos os lados (como o analisador).
  - `neighbour(cell, side)`.
  - `in_bounds(cell)`.
- **Critério:** após qualquer `remove_wall`, `incoherent_cells` seria vazio.

---

## Fase 3 — Algoritmo de Geração (Perfeito)

### T3.1 — Implementar Recursive Backtracker
- **Ações:** função/método `_gen_backtracker()`:
  - Pré-condição: marcar células do "42" como **obstáculos** (ver Fase 4) e garantir
    bordas externas fechadas (já estão, pois `grid` inicia com `ALL_WALLS`).
  - Stack com célula inicial = `entry`.
  - Marca visitados em `set`.
  - Loop: enquanto stack não vazia:
    - `current = stack[-1]`.
    - Vizinhos não-visitados, dentro dos limites, **não-obstáculos**.
    - Se houver: escolhe um aleatoriamente (via `self.rng`), `remove_wall`, marca
      visitado, empilha.
    - Senão: `pop` (backtracking).
  - Garantir que **todas** as células não-obstáculo sejam visitadas (conectividade).
    Se a entry for obstáculo, escolher outra célula inicial válida.
- **Critério:** gera um labirinto perfeito (sem loops) — validar com analisador.

### T3.2 — Garantir conectividade total
- **Ações:**
  - Após a geração, verificar (BFS) que toda célula não-"42" é alcançável a partir da
    entry. Se não, reiniciar a partir de uma célula não-conectada (continuar o
    backtracker a partir dela, conectando ao componente existente).
  - Para `PERFECT=True`: o resultado é uma spanning tree única (loops==0).
- **Critério:** `maze_analyzer.py` reporta `PERFECT maze` e `disconnected_corridors == 0`.

---

## Fase 4 — Padrão "42"

### T4.1 — Definir o bitmap do "42"
- **Ações:**
  - Criar matrizes de pontos para os dígitos "4" e "2" (ex.: 5×5 cada).
  - Exemplo de "4" (5 colunas × 5 linhas):
    ```
    1 0 0 0 1
    1 0 0 0 1
    1 1 1 1 1
    0 0 0 0 1
    0 0 0 0 1
    ```
    (1 = célula totalmente fechada `F`).
  - Combinar "4" e "2" lado a lado, com 1 coluna de espaço entre eles.
- **Critério:** bitmap definido e legível.

### T4.2 — Posicionar o "42" na grade
- **Ações:**
  - Escolher uma região (ex.: canto inferior direito) que **caiba** o bitmap.
  - **Se a grade for pequena demais** (largura/altura insuficiente): **não** desenhar o
    "42" e **imprimir mensagem de erro no console** (ex.: `"Warning: maze too small to
    draw the '42' pattern."`).
  - Marcar as células do bitmap como `ALL_WALLS` (`F`) e registrá-las como
    **obstáculos** (não conectáveis).
- **Critério:** o "42" aparece como células `F` isoladas; mensagem de erro quando
  aplicável.

### T4.3 — Integrar o "42" à geração
- **Ações:**
  - Antes de chamar o algoritmo de geração, marcar obstáculos do "42".
  - Garantir que as células **vizinhas** ao "42" tenham a parede correspondente
    **fechada** (já é o caso, pois iniciam fechadas e o algoritmo só remove paredes
    entre células não-obstáculo).
- **Critério:** analisador não reporta `disconnected_corridors` para as células "42"
  (elas são `is_fully_closed`).

---

## Fase 5 — Modo Jogável (`PERFECT=False`)

### T5.1 — Gerar base perfeita
- **Ações:** reutilizar o backtracker (T3.1) como ponto de partida.

### T5.2 — Garantir cantos e centro abertos
- **Ações:**
  - Os 4 cantos `(0,0)`, `(0,W-1)`, `(H-1,0)`, `(H-1,W-1)` devem ser **corredores
    alcançáveis** (não obstáculos, não totalmente fechados).
  - O centro (célula(s) do meio) deve ser corredor.
  - Se o "42" ou a geração fecharem algum desses, ajustar (forçar abertura ou
    reposicionar o "42").
- **Critério:** `unreachable_key_cells` vazio no analisador.

### T5.3 — Criar loops (rotas independentes)
- **Ações:**
  - Após gerar a base perfeita, **remover paredes adicionais** para criar ciclos.
  - Estratégia: escolher pares de células adjacentes, não-obstáculo, com parede fechada,
    e removê-la (atualizando ambos os lados), **evitando** criar áreas 3×3 abertas.
  - Continuar até `loops >= 2` (idealmente mais, para robustez).
- **Critério:** `loops >= 2` no analisador.

### T5.4 — Controlar dead-ends (mandatório: ≤ 2)
- **Ações:**
  - Identificar dead-ends reais (grau 1, com parede abrível para vizinho normal).
  - Se `> 2`, abrir paredes para reduzir a ≤ 2 (conectando dead-ends a vizinhos).
  - **Não** é necessário chegar a 0 no mandatório (isso é bônus — ver `TAREFAS_BONUS.md`).
- **Critério:** `real_dead_ends <= 2` no analisador (com `--max-dead-ends 2`).

### T5.5 — Evitar áreas abertas grandes
- **Ações:**
  - Validar que **nenhuma** área 3×3 esteja totalmente aberta (corredor largura ≤ 2).
  - Implementar uma função de checagem pós-geração; se violar, reverter a última parede
    removida e tentar outra.
- **Critério:** inspeção visual + (opcional) teste automatizado confirma ausência de
  áreas 3×3.

---

## Fase 6 — Caminho Mais Curto e Saída

### T6.1 — Implementar BFS para caminho mais curto
- **Ações:**
  - `shortest_path() -> list[Direction]`: BFS da `entry` à `exit` sobre as passagens
    abertas.
  - Reconstruir o caminho via dicionário `parent`; converter cada passo em
    `Direction` (N/E/S/W).
  - Retornar lista de direções (ou string `"NESW..."`).
- **Critério:** caminho válido, conecta entry→exit, é o **menor** em passos.

### T6.2 — Serializar o arquivo de saída
- **Ações:** função `write_output(path, grid, entry, exit, path_str)`:
  - Escrever cada linha da grade como string de dígitos hex (minúsculos ou maiúsculos —
    o analisador aceita ambos; escolha um e seja consistente).
  - Linha vazia.
  - Linha `entry_x,entry_y` (formato `x,y`).
  - Linha `exit_x,exit_y`.
  - Linha com o caminho (`NESW...`).
  - Todas as linhas terminam com `\n`.
- **Critério:** arquivo gerado é parseado pelo `maze_analyzer.py` sem erro.

### T6.3 — Validar com o analisador
- **Ações:** rodar `python3 maze_analyzer.py maze.txt` para ambos os modos:
  - `PERFECT=True` → veredito `PERFECT maze`.
  - `PERFECT=False` → veredito `Pac-Man-USABLE`.
- **Critério:** ambos passam; `incoherent` vazio; `disconnected_corridors == 0`.

---

## Fase 7 — Entry Point `a_maze_ing.py`

### T7.1 — Implementar o `main`
- **Arquivos:** `a_maze_ing.py` (nome obrigatório).
- **Ações:**
  - `def main(argv: list[str]) -> int:`
  - Verificar `len(argv) == 2` (senão, mensagem de uso).
  - `try: config = parse_config(argv[1])` → `except` com mensagem clara, `return 1`.
  - Instanciar `MazeGenerator` a partir do config.
  - `gen.generate()`.
  - `gen.write_output(config.output_file)`.
  - Imprimir caminho mais curto no console (opcional, útil para defesa).
  - `return 0`.
  - `if __name__ == "__main__": sys.exit(main(sys.argv[1:]))`.
  - **Topo do arquivo:** `#!/usr/bin/env python3` e docstring do módulo.
- **Critério:** `python3 a_maze_ing.py config.txt` gera `maze.txt` sem crash.

### T7.2 — Tratamento robusto de erros
- **Ações:**
  - Capturar `FileNotFoundError`, `ValueError`, `MazeError` (próprios), e `Exception`
    genérico no topo, imprimindo mensagem amigável e retornando código ≠ 0.
  - Capturar `KeyboardInterrupt` (exit 130).
- **Critério:** nenhuma entrada/caminho inválido causa traceback não tratado.

---

## Fase 8 — Representação Visual (ASCII)

### T8.1 — Renderizador ASCII
- **Arquivos:** `mazegen/renderer_ascii.py` (ou dentro do main).
- **Ações:**
  - Função `render(grid, entry, exit, path=None, wall_color=None, show_42_color=False)`.
  - Cada célula desenhada em um bloco de caracteres (ex.: 2×1 ou 2×2).
  - Paredes: `+`, `-`, `|`. Corredor: espaço. Entry: `E`. Exit: `X`. Caminho: `·` ou
    setas. "42": bloco cheio (ex.: `█`).
  - Suporte a cores ANSI (parametrizável).
- **Critério:** labirinto legível no terminal; paredes, entry, exit e caminho visíveis.

### T8.2 — Loop de interação
- **Ações:**
  - Após gerar e exibir, entrar em um loop lendo teclas do usuário:
    - `r` → re-gerar (novo seed ou mesmo seed? — permitir ambos; ex.: `r` = novo seed,
      `R` = mesmo seed).
    - `p` → mostrar/ocultar caminho mais curto.
    - `c` → ciclar cor das paredes.
    - `4` → (opcional) alternar cor do "42".
    - `q` → sair.
  - Usar `input()` simples ou, melhor, leitura de tecla sem *enter* (ex.: `tty` + `termios`
    no Unix) para experiência fluida.
- **Critério:** todas as 3 interações obrigatórias funcionam.

### T8.3 — (Alternativa) Integração MLX
- **Ações:** se optar por MLX em vez de ASCII:
  - Extrair `mlx-2.2.tgz` e integrar via *bindings* Python ou `ctypes`.
  - Criar janela, desenhar grade, capturar eventos de teclado.
  - **Aviso:** complexidade alta; só fazer se o tempo permitir e a ASCII já estiver 100%.
- **Critério:** janela exibe labirinto; interações funcionam.

---

## Fase 9 — Reusabilidade e Empacotamento

### T9.1 — Finalizar a classe `MazeGenerator` como módulo standalone
- **Ações:**
  - Garantir que `mazegen/` é um pacote importável (`__init__.py` expondo
    `MazeGenerator`, `Direction`, `MazeConfig`).
  - Documentação (docstring do módulo + da classe) com **exemplo básico** de uso:
    ```python
    from mazegen import MazeGenerator
    gen = MazeGenerator(width=20, height=15, entry=(0,0), exit=(19,14),
                        perfect=True, seed=42)
    gen.generate()
    grid = gen.grid
    path = gen.shortest_path()
    ```
  - Métodos públicos: `generate()`, `grid` (property), `shortest_path()`,
    `write_output(path)`.
- **Critério:** `from mazegen import MazeGenerator` funciona em um projeto externo.

### T9.2 — `pyproject.toml`
- **Ações:**
  ```toml
  [build-system]
  requires = ["setuptools>=61.0"]
  build-backend = "setuptools.build_meta"

  [project]
  name = "mazegen"
  version = "1.0.0"
  description = "A reusable maze generator (A-Maze-ing, 42 curriculum)"
  requires-python = ">=3.10"
  license = { file = "LICENSE.md" }
  authors = [{ name = "<login>" }]

  [tool.setuptools.packages.find]
  include = ["mazegen*"]
  ```
- **Critério:** `python -m build` gera `dist/mazegen-1.0.0-*.whl` e `*.tar.gz`.

### T9.3 — Build do pacote
- **Ações:**
  - `python -m pip install --upgrade build`
  - `python -m build`
  - Copiar o `.whl` (ou `.tar.gz`) para a **raiz** do repositório (ex.: `mazegen-1.0.0-py3-none-any.whl`).
  - Testar instalação em um virtualenv limpo:
    `pip install ./mazegen-1.0.0-py3-none-any.whl` → `python -c "import mazegen"`.
- **Critério:** pacote instala e é importável em ambiente limpo.

### T9.4 — `LICENSE.md`
- **Ações:** escolher **MIT** (recomendada), preencher ano e nome.
  - Conteúdo: texto padrão MIT, permitindo uso, cópia, modificação e distribuição.
- **Critério:** arquivo na raiz; licença explicitamente permissiva.

---

## Fase 10 — Documentação e README

### T10.1 — `README.md`
- **Ações:** incluir **todos** os campos obrigatórios (ver `ESTUDO_MANDATORIO.md`
  seção 11):
  - Primeira linha itálica com logins.
  - Description, Instructions, Resources (com uso de IA).
  - Formato do config.
  - Algoritmo escolhido + justificativa.
  - Parte reutilizável + como usar.
  - Gestão de equipe/projeto (papéis, planejamento, o que funcionou/melhorar, ferramentas).
- **Critério:** todos os campos presentes; revisão por pares.

### T10.2 — Documentação do módulo reutilizável
- **Ações:** garantir que o `README.md` **também** contém a documentação curta de uso
  do `MazeGenerator` (instanciação, parâmetros, acesso à estrutura e solução).
- **Critério:** duplicado no README (exigência do subject).

---

## Fase 11 — Qualidade e Lint

### T11.1 — Type hints e docstrings em todo o código
- **Ações:** revisar **todas** as funções/métodos: parâmetros, retorno, docstring
  (Google ou NumPy style).
- **Critério:** `mypy . --disallow-untyped-defs --check-untyped-defs` sem erros.

### T11.2 — flake8 limpo
- **Ações:** corrigir avisos (linhas longas, imports não usados, espaços).
- **Critério:** `flake8 .` sem saída.

### T11.3 — mypy com flags obrigatórias
- **Ações:** rodar `make lint` (com as flags exatas do subject).
- **Critério:** zero erros.

### T11.4 — (Recomendado) `make lint-strict`
- **Ações:** corrigir até `mypy . --strict` passar (bônus de robustez).
- **Critério:** `make lint-strict` sem erros.

---

## Fase 12 — Testes (não avaliados, mas cruciais)

### T12.1 — Testes unitários com `pytest`
- **Arquivos:** `tests/`.
- **Ações:** cobrir:
  - Parser de config (válido, inválido, ausente).
  - `remove_wall` coerência (ambos os lados).
  - Geração perfeita: `loops == 0`, conectividade, coerência.
  - Geração jogável: `loops >= 2`, cantos/centro, dead-ends ≤ 2.
  - "42" presente e isolado; mensagem de erro quando grade pequena.
  - Caminho mais curto válido (conecta entry→exit).
  - Serialização/desserialização round-trip.
  - Reprodutibilidade: mesmo seed → mesmo labirinto.
- **Critério:** `pytest` passa; cobre *edge cases*.

### T12.2 — Testes de regressão com o analisador
- **Ações:** script que gera labirintos para vários tamanhos/seeds/modos e roda o
  `maze_analyzer.py`, falhando se o veredito não for o esperado.
- **Critério:** 100% dos casos passam.

---

## Fase 13 — Revisão Final e Preparação para Defesa

### T13.1 — Revisão de requisitos
- **Ações:** percorrer o checklist do `ESTUDO_MANDATORIO.md` seção 12, item a item.
- **Critério:** todos marcados.

### T13.2 — Limpeza do repositório
- **Ações:** `make clean`; garantir que apenas arquivos necessários estão commitados;
  `.whl` na raiz; `config.txt` padrão presente.
- **Critério:** repositório limpo e completo.

### T13.3 — Commit e push
- **Ações:** commit final com mensagem descritiva; push para o repositório remoto.
- **Critério:** repositório remoto atualizado.

### T13.4 — Ensaio da defesa
- **Ações:** simular a defesa usando o `TESTE_DEFESA_MANDATORIO.md`.
- **Critério:** conseguir explicar cada parte; pronto para modificação ao vivo.

---

## Resumo de Dependências

```
Fase 0 (setup) ──► Fase 1 (config) ──► Fase 2 (núcleo) ──► Fase 3 (backtracker)
                                                       │
                                                       ▼
                                          Fase 4 ("42") ──► Fase 5 (jogável)
                                                       │
                                                       ▼
                                          Fase 6 (caminho/saída) ──► Fase 7 (main)
                                                       │
                                                       ▼
                                          Fase 8 (visual) ──► Fase 9 (empacotamento)
                                                       │
                                                       ▼
                                          Fase 10 (docs) ──► Fase 11 (lint) ──► Fase 12 (testes)
                                                       │
                                                       ▼
                                          Fase 13 (revisão/defesa)
```

> **Regra de ouro:** **nunca** avance para a Fase 8 (visual) sem que a Fase 6 esteja
> validada pelo `maze_analyzer.py`. O núcleo é o coração do projeto.
