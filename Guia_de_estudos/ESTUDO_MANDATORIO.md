# Guia de Estudo — Parte Mandatória (A-Maze-ing)

> Este documento é um **guia de estudo** dos conceitos necessários para entender,
> implementar e defender a parte mandatória do projeto **A-Maze-ing** (currículo 42,
> versão 2.2). A explicação está em português, mas os **termos técnicos essenciais**
> (nomes de algoritmos, nomes de ferramentas, nomes de campos do subject) são
> mantidos em seu idioma nativo (inglês) para preservar a fidelidade ao enunciado.

---

## 0. Visão geral do projeto

O objetivo é construir, em **Python 3.10+**, um **gerador de labirintos** que:

1. Lê um arquivo de configuração (`config.txt`) no formato `KEY=VALUE`.
2. Gera um labirinto **aleatório porém reproduzível** (via *seed*).
3. Pode gerar um labirinto **perfeito** (`PERFECT=True`) ou um **tabuleiro jogável**
   estilo *Pac-Man* (`PERFECT=False`, padrão).
4. Escreve o labirinto em um arquivo de saída usando **codificação hexadecimal de
   paredes** (um dígito hex por célula).
5. Oferece uma **representação visual** (ASCII no terminal **ou** gráfica via
   **MiniLibX / MLX**) com interações do usuário.
6. Expõe a lógica de geração como uma **classe reutilizável** empacotável via `pip`
   (pacote `mazegen-*`).
7. Inclui `Makefile`, `README.md`, `LICENSE.md`, `.gitignore` e segue **flake8** e
   **mypy** (com *type hints* e *docstrings*).

O projeto é avaliado em **defesa (peer-evaluation)**, podendo haver uma **modificação
ao vivo** solicitada pelo avaliador.

---

## 1. Fundamentos de Teoria dos Grafos

O labirinto é, essencialmente, um **grafo**: cada célula é um **vértice (nó)** e cada
parede **aberta** entre duas células vizinhas é uma **aresta (edge)**.

### 1.1 Conceitos essenciais

- **Vértice (vertex / node):** uma célula da grade `(x, y)`.
- **Aresta (edge):** passagem aberta entre duas células adjacentes (N/E/S/W).
- **Grafo conexo (connected graph):** existe um caminho entre qualquer par de vértices.
  No labirinto, isso significa **conectividade total** (nenhum corredor isolado, exceto
  as células do padrão "42").
- **Ciclo (cycle / loop):** caminho fechado que retorna ao vértice de partida sem
  repetir arestas. Um labirinto **perfeito** tem **zero ciclos**.
- **Árvore geradora (spanning tree):** subgrafo que conecta todos os vértices sem
  formar ciclos. **Todo labirinto perfeito é uma spanning tree** do grafo da grade.
- **Grau (degree) de um vértice:** número de arestas incidentes. No labirinto, é o
  número de paredes **abertas** da célula (0 a 4).
- **Dead-end (beco sem saída):** vértice de grau 1 (uma única passagem aberta).
- **Número de ciclos independentes:** para um grafo conexo,
  `loops = arestas - vértices + 1` (fórmula do *circuit rank* / número de Betti).
  É exatamente a fórmula usada pelo `maze_analyzer.py`.

> **Por que isso importa:** o `maze_analyzer.py` valida o labirinto calculando
> `loops = open_passages - len(region) + 1`. Para `PERFECT=True` ele exige `loops == 0`;
> para `PERFECT=False` ele exige `loops >= 2` (no mínimo duas rotas independentes).

### 1.2 Conectividade e componentes

- **Componente conexa (connected component):** conjunto de vértices alcançáveis entre
  si. O analisador calcula a **maior região alcançável a partir da entry** (via BFS).
- **BFS (Breadth-First Search):** percorre o grafo em largura, usando uma fila
  (`collections.deque`). Útil para encontrar a região alcançável e o **caminho mais
  curto** (menor número de passos).
- **DFS (Depth-First Search):** percorre em profundidade, usando recursão ou pilha.
  É a base do algoritmo **recursive backtracker**.

### 1.3 Caminho mais curto (shortest path)

O subject exige que o arquivo de saída contenha **o caminho mais curto** da entry à
exit, codificado com as letras `N, E, S, W`.

- Em um labirinto **perfeito**, o caminho é **único** (basta qualquer travessia).
- Em um tabuleiro **jogável** (com loops), há vários caminhos; usa-se **BFS** para
  garantir o **menor** em número de passos.
- A BFS mantém um dicionário `pai[cell] = cell_anterior`; ao chegar na exit,
  reconstrói-se o caminho de trás para frente e converte cada passo em `N/E/S/W`.

> **Aprofundamento:**
> - *Introduction to Algorithms* (CLRS), 3ª ed., capítulos 22 (BFS) e 23 (Árvores
>   Geradoras Mínimas) — livro de referência acadêmica amplamente usado.
> - MIT OpenCourseWare 6.006, Lecture 9: Breadth-First Search (Erik Demaine):
>   https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/ — notas
>   de aula oficiais do MIT com prova de corretude e análise de complexidade.
> - Dasgupta, Papadimitriou & Vazirani, *Algorithms*, cap. 4 ("Paths in graphs"):
>   https://people.eecs.berkeley.edu/~vazirani/algorithms/chap4.pdf — livro-texto
>   acadêmico de acesso aberto com explicação detalhada de BFS e caminhos mais curtos.

> 🔧 **MARCO DE IMPLEMENTAÇÃO 1 — Estude e implemente em conjunto:**
> Após ler esta seção (Grafos + BFS/DFS), **antes** de avançar, implementem juntos
> (mesmo que em rascunho) um BFS simples sobre uma grade mock 3×3 para encontrar o
> caminho entre duas células. Isso fixa o conceito de `parent[v] = u` e a
> reconstrução do caminho. **Tempo alvo:** 30–45 min. *Dica:* use o
> `maze_analyzer.py` como referência de `region_of` (BFS com `deque`).

---

## 2. Algoritmos de Geração de Labirintos

Um labirinto perfeito é uma **spanning tree**. Os algoritmos clássicos constroem essa
árvore removendo paredes progressivamente.

### 2.1 Recursive Backtracker (DFS)

- **Como funciona:** começa em uma célula, marca como visitada, escolhe um vizinho
  não-visitado aleatoriamente, remove a parede entre eles, e recursa. Quando não há
  vizinhos não-visitados, faz *backtracking* (retrocede) até encontrar um que tenha.
- **Características:** produz labirintos com **muitos corredores longos** e poucos
  *dead-ends* curtos. É simples e eficiente.
- **Estrutura de dados:** pilha (explícita ou via recursão), conjunto de visitados.
- **Resultado:** sempre um labirinto **perfeito** (spanning tree).

### 2.2 Algoritmo de Prim

- **Como funciona:** começa com uma célula; mantém uma lista de "fronteiras" (vizinhos
  não-visitados de células visitadas). A cada passo, escolhe uma fronteira aleatória,
  conecta-a a uma célula já visitada, e adiciona suas próprias fronteiras.
- **Características:** produz labirintos com **muitos dead-ends curtos** e corredores
  mais ramificados.
- **Resultado:** também um labirinto **perfeito**.

### 2.3 Algoritmo de Kruskal

- **Como funciona:** considera todas as paredes internas como arestas possíveis.
  Embaralha-as e, para cada parede, se as duas células estão em **componentes
  diferentes** (verificado via **Union-Find / Disjoint Set Union**), remove a parede e
  une os componentes.
- **Características:** produz labirintos **muito ramificados e uniformes**.
- **Estrutura de dados:** **Union-Find** com *path compression* e *union by rank*.
- **Resultado:** labirinto **perfeito**.

> **Recomendação para o projeto:** o **recursive backtracker** é o mais simples de
> implementar e entender, e atende perfeitamente ao modo `PERFECT=True`. Para o modo
> jogável (`PERFECT=False`), parte-se de um labirinto perfeito e **remove-se paredes
> adicionais** para criar loops (ver seção 4).

> **Aprofundamento:**
> - Jamis Buck, *Mazes for Programmers* (Pragmatic Bookshelf, 2015) — livro dedicado
>   ao tema, com implementações e análise de cada algoritmo.
> - https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap (série do
>   Jamis Buck, referência clássica sobre geração de labirintos)
> - Walter D. Pullen, "Think Labyrinth: Maze Algorithms":
>   https://www.astrolog.org/labyrnth/algrithm.htm — referência histórica.

> 🔧 **MARCO DE IMPLEMENTAÇÃO 2 — Escolham o algoritmo e implementem o backtracker:**
> Antes de ler a próxima seção, decidam juntos qual algoritmo usar (recomendado:
> **recursive backtracker**). Implementem-no sobre uma grade 5×5 **sem** o "42" ainda,
> apenas para validar a lógica de pilha + visitados + `remove_wall`. Rodem o
> `maze_analyzer.py` no resultado — deve dar `PERFECT maze`. **Tempo alvo:** 1.5–2h.
> *Pessoa A lidera; Pessoa B revisa a coerência das paredes.*

---

## 3. Codificação Hexadecimal de Paredes (Output File Format)

Este é um dos pontos **mais cobrados em defesa**, pois o arquivo de saída pode ser
testado automaticamente por uma *Moulinette*.

### 3.1 O esquema de bits

Cada célula é representada por **um dígito hexadecimal** (0–F). Cada **bit** indica se
uma parede está **fechada (1)** ou **aberta (0)**:

| Bit | Direção | Valor decimal |
|-----|---------|---------------|
| 0 (LSB) | North (N) | 1 |
| 1       | East  (E) | 2 |
| 2       | South (S) | 4 |
| 3       | West  (W) | 8 |

- **Parede fechada → bit = 1.** Parede aberta → bit = 0.
- Exemplo do subject: `3` = `0011` binário → bits 0 e 1 setados → paredes **North e
  East fechadas** (South e West abertas). *(Nota: o subject diz "open to the south and
  west", o que é equivalente: fechadas ao N e E.)*
- Exemplo: `A` = `1010` → bits 1 e 3 setados → paredes **East e West fechadas**.
- **Célula totalmente fechada** (padrão "42"): `F` = `1111` = 15 (todas as 4 paredes
  fechadas).
- **Célula totalmente aberta**: `0` = `0000`.

### 3.2 Layout do arquivo

```
<linha 0: dígitos hex da linha 0 do labirinto>
<linha 1: dígitos hex da linha 1>
...
<linha HEIGHT-1>
<linha vazia>
<x_entry>,<y_entry>
<x_exit>,<y_exit>
<caminho mais curto como string de N/E/S/W>
```

- As células são armazenadas **linha por linha** (row-major), **uma linha por linha do
  arquivo**.
- Após a grade, há **uma linha vazia**.
- Em seguida, **3 linhas**: coordenadas da entry (`x,y`), coordenadas da exit (`x,y`),
  e o **camininho mais curto** usando as letras `N, E, S, W`.
- **Todas as linhas terminam com `\n`.**

### 3.3 Atenção crítica: coerência das paredes

> **Regra de ouro:** se a célula A tem uma parede fechada a **East**, então a célula B
> (vizinha imediatamente a leste de A) **deve** ter a parede **West** fechada também.

O `maze_analyzer.py` verifica isso em `incoherent_cells()`: para cada par de vizinhos,
compara o bit da parede compartilhada. **Qualquer divergência invalida o labirinto**
(veredito `INCOHERENT walls`). É o **primeiro** erro reportado — sem coerência, nada
mais é avaliado.

**Implementação segura:** ao remover uma parede entre A e B, **sempre atualize ambos os
lados simultaneamente**:
```python
grid[A] &= ~Direction.EAST      # limpa bit East de A
grid[B] &= ~Direction.WEST      # limpa bit West de B
```

### 3.4 Sistema de coordenadas (atenção!)

- O subject usa **(x, y)** onde **x = coluna** e **y = linha**.
- O `maze_analyzer.py` armazena internamente como `(row, col)` = `(y, x)`, e converte
  na hora de exibir (`_xy` faz `f"({cell[1]}, {cell[0]})"`).
- **Entry/Exit no config:** `ENTRY=0,0` significa `x=0, y=0` → canto superior esquerdo.
- **No arquivo de saída:** escreva `x,y` (coluna, linha) — **não** `row,col`.

> **Pegadinha clássica de defesa:** confundir `(x,y)` com `(row,col)`. Mantenha
> consistência: `x = coluna`, `y = linha`. Sempre.

> 🔧 **MARCO DE IMPLEMENTAÇÃO 3 — Implementem `Direction` + `remove_wall` + serialização:**
> Após dominar a codificação hex, implementem juntos: a classe `Direction` (IntFlag),
> a função `remove_wall(a, b)` que atualiza **ambos** os lados, e a serialização
> `write_output` (grade hex + footer). Testem com uma grade mock (ex.: 2×2 com paredes
> conhecidas) e rodem o `maze_analyzer.py` — deve dar `Wall coherence: OK`. **Tempo
> alvo:** 1–1.5h. *Pessoa A faz `Direction`/`remove_wall`; Pessoa B faz `write_output`.*
> **Não avancem** enquanto o analisador não confirmar coerência.

---

## 4. Os Dois Modos de Geração

### 4.1 Modo `PERFECT=True` (labirinto perfeito)

- **Exatamente um caminho** entre entry e exit.
- **Zero loops** (`loops == 0` no analisador).
- É uma **spanning tree**.
- Algoritmo natural: **recursive backtracker**, **Prim** ou **Kruskal**.
- Todos os outros corredores terminam em **dead-ends**.

### 4.2 Modo `PERFECT=False` (padrão — tabuleiro Pac-Man)

Este é o modo **mais exigente**. O labirinto deve ser **diretamente usável como um
tabuleiro de Pac-Man**:

1. **Conectividade total:** todo corredor é alcançável (nenhum corredor isolado além
   das células "42"). Caso contrário, o nível seria **injogável** (pac-gums
   inalcançáveis).
2. **Quatro cantos e centro abertos:** os cantos abrigam *ghosts* e *super-pac-gums*;
   o centro é onde o **jogador inicia**. O analisador verifica `unreachable_key_cells`.
3. **Pelo menos 2 rotas independentes (loops ≥ 2):** um labirinto perfeito com **uma
   única parede removida** (1 loop) **não é aceito** — o jogador perseguido precisa de
   alternativa.
4. **Dead-ends raros:** no máximo 2 tolerados (configurável via `--max-dead-ends`).
   **Zero dead-ends** é o **bônus** (tabuleiro *braided*).

**Estratégia de implementação:**
1. Gere um labirinto **perfeito** (ex.: recursive backtracker).
2. **Remova paredes adicionais** para criar loops, garantindo `loops >= 2`.
3. **Elimine dead-ends** abrindo paredes de células de grau 1 (conectando-as a um
   vizinho), produzindo um tabuleiro *braided*.
4. Garanta que **cantos e centro** permaneçam como corredores abertos.

> **Conceito — Braided maze:** labirinto sem dead-ends. Constrói-se abrindo, para cada
> dead-end, uma parede adicional que o conecta a outro corredor. Pode ser *totalmente*
> braided (zero dead-ends) ou *parcialmente*.

> 🔧 **MARCO DE IMPLEMENTAÇÃO 4 — Modo jogável (PERFECT=False) em conjunto:**
> Esta é a fase **mais complexa** do mandatório. Trabalhem juntos: partam do
> backtracker já validado (Marco 2), removam paredes adicionais para criar `loops >= 2`,
> garantam cantos/centro abertos, e controlem dead-ends (≤ 2). Rodem o analisador após
> cada ajuste — o veredito deve ser `Pac-Man-USABLE`. **Tempo alvo:** 3–4h (pode
> estender). *Pessoa A faz loops/dead-ends; Pessoa B garante cantos/centro; integram
> juntos.* Se travar, não hesitem em voltar ao estudo de braided mazes
> (`ESTUDO_BONUS.md` seção 1).

---

## 5. O Padrão "42"

- O labirinto deve conter, quando representado visualmente, um **"42" visível** desenhado
  por **células totalmente fechadas** (`F` / `1111`).
- Essas células são **isoladas** (não fazem parte da região jogável) e são **toleradas**
  pelo analisador (não contam como `disconnected_corridors`).
- **Se o labirinto for pequeno demais** para comportar o "42", o padrão **pode ser
  omitido**, mas o programa **deve imprimir uma mensagem de erro no console**.
- O "42" é desenhado em uma **área fixa** da grade, tipicamente reservando um bloco de
  células (ex.: 5 colunas × 5 linhas) e marcando como `F` apenas as células que formam
  os dígitos "4" e "2".

**Implementação típica:**
1. Defina um *bitmap* (matriz de pontos) para os dígitos "4" e "2".
2. Reserve uma região da grade (ex.: canto inferior direito).
3. Marque as células do bitmap como `F` (totalmente fechadas) **antes** de gerar o
   labirinto, e trate-as como **obstáculos** durante a geração (nunca as conecte).

> **Atenção:** o "42" **não pode** ser conectado ao labirinto, senão deixa de ser
> "totalmente fechado". E as células vizinhas ao "42" devem ter paredes coerentes
> (fechadas do lado que toca o "42").

> 🔧 **MARCO DE IMPLEMENTAÇÃO 5 — Integrem o "42" ao gerador:**
> Definam o bitmap dos dígitos "4" e "2", posicionem numa região fixa (combinem:
> ex.: canto inferior direito), marquem como obstáculos (`F`) **antes** do backtracker,
> e regenerem. Testem dois casos: (a) grade grande → "42" visível e isolado; (b) grade
> pequena (ex.: 5×5) → mensagem de erro no console e "42" omitido. Rodem o analisador
> em ambos — as células "42" não devem contar como `disconnected_corridors`.
> **Tempo alvo:** 1.5–2h. *Pessoa A implementa; Pessoa B valida o caso pequeno.*

---

## 6. Representação Visual

### 6.1 Opção ASCII (terminal)

- Renderize a grade usando caracteres: `+`, `-`, `|` para paredes; espaços para
  corredores; marcadores para entry/exit/caminho.
- Cada célula ocupa, tipicamente, 2 caracteres de largura para evitar distorção.
- **Interações obrigatórias** (via entrada do teclado no terminal):
  - **Re-gerar** um novo labirinto.
  - **Mostrar/Ocultar** o caminho mais curto.
  - **Mudar as cores das paredes** (usando *ANSI escape codes*).
  - *(Opcional)* cor específica para o padrão "42".

**ANSI colors** (exemplo): `\033[31m` = vermelho, `\033[32m` = verde,
`\033[0m` = reset. Permitem colorir paredes e caminho sem bibliotecas externas.

### 6.2 Opção MLX (MiniLibX)

- Biblioteca gráfica simples (originária do currículo 42, em C). O arquivo `mlx-2.2.tgz`
  acompanha o subject.
- Em Python, o MLX é acessível via *bindings* (ex.: `mlx` wrapper) ou via `ctypes`.
- Desenha pixels/janelas, captura eventos de teclado/mouse.
- **Atenção:** integrar MLX em Python é **não-trivial**; a opção ASCII é mais segura e
  **atende plenamente** ao mandatório. MLX é um diferencial visual, não obrigatório.

### 6.3 Interações (independente da opção)

| Interação | Obrigatória? |
|-----------|--------------|
| Re-gerar labirinto | Sim |
| Mostrar/Ocultar caminho mais curto | Sim |
| Mudar cor das paredes | Sim |
| Cor específica do "42" | Opcional |

> 🔧 **MARCO DE IMPLEMENTAÇÃO 6 — Visual ASCII + 3 interações:**
> Implementem o renderer ASCII e o loop de interação. Testem **cada** interação
> obrigatória: re-gerar (tecla `r`), mostrar/ocultar caminho (`p`), mudar cor das
> paredes (`c`). Validem visualmente que o "42" aparece e que o caminho mais curto
> está correto. **Tempo alvo:** 2–3h. *Pessoa B lidera; Pessoa A valida a corretude do
> caminho exibido.* Se a ASCII estiver 100%, considerem MLX (opcional).

---

## 7. Reusabilidade e Empacotamento (pip)

### 7.1 A classe `MazeGenerator`

- Deve estar em um **módulo standalone** (um único arquivo `.py`), **importável**.
- Expor uma **classe** (ex.: `MazeGenerator`) com:
  - Construtor recebendo parâmetros (tamanho, seed, algoritmo, etc.).
  - Método `generate()` que produz a estrutura do labirinto.
  - Acesso à **estrutura gerada** (grade de paredes).
  - Acesso a **pelo menos uma solução** (caminho entry→exit).
- **Documentação curta** (no próprio módulo e no `README.md`): como instanciar, passar
  parâmetros e acessar estrutura/solução, com **exemplo básico**.

> **Nota do subject:** o formato interno da estrutura **não precisa** ser igual ao do
> arquivo de saída. Pode ser uma lista de listas de `Direction`/`int`, etc.

### 7.2 Empacotamento (`mazegen-*`)

- O módulo reutilizável deve ser **instalável via `pip`**.
- Nome do pacote: `mazegen-*` (ex.: `mazegen-1.0.0-py3-none-any.whl`).
- Extensões aceitas: **`.tar.gz`** (sdist) ou **`.whl`** (wheel).
- O arquivo do pacote deve estar na **raiz do repositório Git**.
- **Todos os elementos necessários para o *build*** devem estar no repositório
  (arquivo `pyproject.toml` ou `setup.py` + `setup.cfg`).
- Na defesa, será pedido: **em um virtualenv, instalar as ferramentas e reconstruir o
  pacote a partir dos fontes**.

**Build moderno (recomendado):** use `pyproject.toml` com `setuptools` ou `flit`/`hatch`:
```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "mazegen"
version = "1.0.0"
description = "A reusable maze generator"
requires-python = ">=3.10"
```
Comandos de build:
```bash
python -m pip install --upgrade build
python -m build            # gera .tar.gz e .whl em dist/
```

### 7.3 `LICENSE.md`

- Arquivo **obrigatório** na raiz do repositório.
- Deve **explicitamente permitir reuso e distribuição** pelos projetos futuros.
- Escolher a licença **faz parte do trabalho** (primeiro contato com licenciamento de
  software / propriedade intelectual).
- Opções comuns: **MIT** (permissiva, simples), **Apache-2.0**, **BSD-3-Clause**.
- **MIT** é a recomendada para este caso (curta, permissiva, amplamente compreendida).

> **Aprofundamento:** https://choosealicense.com/ — guia oficial para escolha de
> licenças open-source.

> 🔧 **MARCO DE IMPLEMENTAÇÃO 7 — Empacotem e testem em virtualenv limpo:**
> Criem o `pyproject.toml`, rodem `python -m build`, copiem o `.whl` para a raiz do
> repo. **Crítico:** abram um virtualenv **limpo** (novo), façam `pip install
> ./mazegen-*.whl` e rodem um script externo que importa `MazeGenerator` e gera um
> labirinto. Escolham e escrevam a `LICENSE.md` (MIT). **Tempo alvo:** 1.5–2h. *Pessoa B
> lidera o build; Pessoa A finaliza a docstring/exemplo de uso do módulo.* Simulem a
> exigência da defesa: reconstruir o pacote do zero.

---

## 8. Qualidade de Código e Ferramentas (Common Instructions)

### 8.1 Python 3.10+ e *type hints*

- Use **type hints** em **todos** os parâmetros, retornos e variáveis aplicáveis
  (módulo `typing`).
- O subject exige que **todas as funções passem no mypy sem erros**.
- Recursos úteis do 3.10+: `match/case`, union com `|` (ex.: `int | None`),
  `ParamSpec`, etc.

### 8.2 flake8

- Padrão de estilo (PEP 8). Verifica indentação, linhas longas, imports não usados, etc.
- Comando: `flake8 .`

### 8.3 mypy (com flags obrigatórias)

O `Makefile` deve ter a regra `lint` executando:
```
flake8 .
mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
       --disallow-untyped-defs --check-untyped-defs
```
- `--disallow-untyped-defs`: proíbe funções sem anotações de tipo.
- `--check-untyped-defs`: verifica corpo de funções mesmo sem anotações completas.
- `--warn-return-any`: avisa se uma função retorna `Any`.
- `--warn-unused-ignores`: avisa sobre `# type: ignore` desnecessários.
- Recomendado: `lint-strict` com `mypy . --strict`.

### 8.4 Docstrings (PEP 257)

- Toda função e classe deve ter **docstring** documentando propósito, parâmetros e
  retorno.
- Estilos aceitos: **Google** ou **NumPy**.
- Exemplo (Google style):
```python
def generate(self) -> list[list[int]]:
    """Gera o labirinto e retorna a grade de paredes.

    Returns:
        Grade HEIGHT x WIDTH com o código de paredes de cada célula.
    """
```

### 8.5 Tratamento de exceções e recursos

- **Nunca** deixe o programa **crashar** com exceção não tratada durante a defesa.
- Use `try/except` para erros esperados (arquivo não encontrado, config inválido,
  parâmetros impossíveis) e exiba **mensagens claras**.
- Use **context managers** (`with`) para arquivos e conexões (limpeza automática).
- Erro não tratado = projeto considerado **não funcional**.

### 8.6 Makefile (regras obrigatórias)

| Regra | Ação |
|-------|------|
| `install` | Instala dependências (`pip`/`uv`/`pipx`) |
| `run` | Executa o script principal (`python3 a_maze_ing.py config.txt`) |
| `debug` | Roda com `pdb` (ex.: `python3 -m pdb a_maze_ing.py`) |
| `clean` | Remove `__pycache__`, `.mypy_cache`, etc. |
| `lint` | `flake8 .` + `mypy .` com as flags obrigatórias |
| `lint-strict` | (opcional) `flake8 .` + `mypy . --strict` |

### 8.7 Outros

- `.gitignore` para artefatos Python (`__pycache__/`, `*.pyc`, `.mypy_cache/`,
  `dist/`, `build/`, `*.egg-info/`, `venv/`).
- Uso de **virtualenv** recomendado.
- **Testes** com `pytest` ou `unittest` (não entregues/avaliados, mas recomendados para
  cobrir *edge cases*).

> 🔧 **MARCO DE IMPLEMENTAÇÃO 8 — Lint limpo (conjunto, não pular):**
> Rodem `make lint` e `make lint-strict`. Corrijam **todos** os erros: type hints
> faltantes, docstrings ausentes, linhas longas, imports não usados. **Dica:** adicionem
> type hints **desde o início** do projeto — corrigir no final é muito mais caro.
> **Tempo alvo:** 2–3h. *Cada um corrige seus próprios módulos; revisão cruzada no
> final.* Não marquem a Fase 11 como concluída enquanto `make lint` não passar limpo.

---

## 9. Arquivo de Configuração (`config.txt`)

### 9.1 Formato

- Uma linha por par `KEY=VALUE`.
- Linhas começando com `#` são **comentários** e ignoradas.
- Chaves **mandatórias**:

| Key | Descrição | Exemplo |
|-----|-----------|---------|
| `WIDTH` | Largura (número de células) | `WIDTH=20` |
| `HEIGHT` | Altura | `HEIGHT=15` |
| `ENTRY` | Coordenadas da entrada `(x,y)` | `ENTRY=0,0` |
| `EXIT` | Coordenadas da saída `(x,y)` | `EXIT=19,14` |
| `OUTPUT_FILE` | Nome do arquivo de saída | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Labirinto perfeito? | `PERFECT=True` |

- Chaves **opcionais** permitidas: `SEED`, `ALGORITHM`, `DISPLAY`, etc.
- Um arquivo de configuração **padrão** deve existir no repositório Git.

### 9.2 Validação (tratamento de erros)

O programa deve rejeitar graciosamente:
- Arquivo inexistente ou ilegível.
- Chave mandatória ausente.
- Valor inválido (ex.: `WIDTH=abc`, `ENTRY=-1,5`, `PERFECT=maybe`).
- Coordenadas fora dos limites (`ENTRY`/`EXIT` fora da grade).
- `ENTRY == EXIT`.
- Dimensões impossíveis (ex.: `WIDTH=0`).
- Sempre com **mensagem clara** e **sem crash**.

---

## 10. Validação com `maze_analyzer.py`

O script fornecido é sua **ferramenta de auto-verificação**. Use-o **sempre** antes da
defesa.

### 10.1 Uso

```bash
python3 maze_analyzer.py maze.txt
python3 maze_analyzer.py maze.txt --min-loops 2 --max-dead-ends 2
python3 maze_analyzer.py maze.txt --max-dead-ends 0   # para o bônus braided
```

### 10.2 O que ele verifica (em ordem)

1. **Parsing:** grade retangular de dígitos hex; footer com entry/exit/path.
2. **Coerência de paredes** (`incoherent_cells`): divergências entre vizinhos →
   `INCOHERENT walls` (erro fatal).
3. **Região alcançável** (BFS a partir da entry, ou maior componente).
4. **Corredores desconectados** (`disconnected_corridors`): corredores não-"42" fora da
   região → `NOT fully connected`.
5. **Loops** (`loops = open_passages - len(region) + 1`):
   - `== 0` → `PERFECT maze`.
   - `< min_loops` → `Not Pac-Man-ready`.
6. **Cantos e centro** (`unreachable_key_cells`): devem ser corredores alcançáveis.
7. **Dead-ends** (`dead_ends`): separa *real* (abertura possível) de *enclosed* (tolerado,
   cercado por "42"/borda). `real > max_dead_ends` → reprovado.

### 10.3 Vereditos possíveis

- `INCOHERENT walls` — inválido (corrija a codificação).
- `DEGENERATE` — entry sem passagem.
- `NOT fully connected` — corredor inalcançável.
- `PERFECT maze` — atende `PERFECT=True`.
- `Not Pac-Man-ready` — falha em cantos/centro, loops insuficientes ou dead-ends demais.
- `Pac-Man-USABLE` — atende `PERFECT=False` (com indicação de bônus se `real == 0`).

---

## 11. README.md (requisitos)

A primeira linha **deve** ser itálica e conter:
```
*This project has been created as part of the 42 curriculum by <login1>[, <login2>...].*
```

Seções **obrigatórias**:
- **Description:** objetivo e visão geral do projeto.
- **Instructions:** compilação, instalação e execução.
- **Resources:** referências (docs, artigos, tutoriais) **+ descrição de como a IA foi
  usada** (para quais tarefas e partes do projeto).

Conteúdo adicional **exigido** pelo subject:
- Estrutura e formato completos do arquivo de configuração.
- O algoritmo de geração escolhido.
- **Por que** escolheu esse algoritmo.
- Qual parte do código é reutilizável e como.
- **Gestão de equipe/projeto:**
  - Papel de cada membro.
  - Planejamento previsto e como evoluiu até o fim.
  - O que funcionou bem e o que melhorar.
  - Ferramentas utilizadas.

> Inglês é recomendado; alternativamente, o idioma principal do campus.

---

## 12. Checklist de Conceitos para Dominar (Mandatório)

- [ ] Teoria dos grafos: vértice, aresta, spanning tree, ciclo, conectividade, BFS/DFS.
- [ ] Fórmula `loops = arestas - vértices + 1` e seu significado.
- [ ] Pelo menos um algoritmo de geração (recursive backtracker recomendado).
- [ ] Codificação hex de paredes (bits N/E/S/W, fechado=1) e **coerência entre vizinhos**.
- [ ] Sistema de coordenadas `(x=coluna, y=linha)` vs `(row, col)`.
- [ ] Diferença entre `PERFECT=True` e `PERFECT=False` (Pac-Man-ready).
- [ ] Padrão "42" (células `F`, isoladas, toleradas; mensagem de erro se omitido).
- [ ] Caminho mais curto via BFS e codificação `N/E/S/W`.
- [ ] Representação visual (ASCII ou MLX) + 3 interações obrigatórias.
- [ ] Classe `MazeGenerator` reutilizável + empacotamento `pip` (`mazegen-*`).
- [ ] `pyproject.toml` / build do pacote (`python -m build`).
- [ ] `LICENSE.md` (MIT recomendada).
- [ ] `Makefile` com `install/run/debug/clean/lint[/lint-strict]`.
- [ ] flake8 + mypy (flags obrigatórias) + type hints + docstrings PEP 257.
- [ ] Tratamento de exceções e context managers (nunca crashar).
- [ ] `README.md` com todos os campos obrigatórios.
- [ ] Uso do `maze_analyzer.py` para auto-validação.

---

## 13. Referências para Aprofundamento

| Tema | Referência |
|------|------------|
| Teoria dos Grafos / BFS / Spanning Trees | *Introduction to Algorithms* (CLRS), 3ª ed., caps. 22–23 |
| BFS (notas de aula oficiais) | MIT OCW 6.006, Lecture 9 — https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/ |
| BFS (livro-texto aberto) | Dasgupta, Papadimitriou & Vazirani, *Algorithms*, cap. 4 — https://people.eecs.berkeley.edu/~vazirani/algorithms/chap4.pdf |
| Maze generation algorithms (livro) | Jamis Buck, *Mazes for Programmers* (Pragmatic Bookshelf, 2015) |
| Série Jamis Buck (algoritmos detalhados) | https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap |
| Think Labyrinth (referência histórica) | Walter D. Pullen — https://www.astrolog.org/labyrnth/algrithm.htm |
| Union-Find (DSU) | CP-Algorithms — https://cp-algorithms.com/data_structures/disjoint_set_union.html |
| Kruskal (MST) | CP-Algorithms — https://cp-algorithms.com/graph/mst_kruskal.html |
| PEP 8 / flake8 | https://flake8.pycqa.org/ |
| mypy | https://mypy.readthedocs.io/ |
| PEP 257 (docstrings) | https://peps.python.org/pep-0257/ |
| Empacotamento Python | https://packaging.python.org/en/latest/tutorials/packaging-projects/ |
| Escolha de licença | https://choosealicense.com/ |
| MiniLibX | Documentação interna 42 / `mlx-2.2.tgz` fornecido |
| ANSI escape codes | Real Python — https://realpython.com/lessons/terminal-output-ansi-escape-sequences/ |
| ANSI escape codes (docs Python) | Documentação `curses` — https://docs.python.org/3/library/curses.html |
