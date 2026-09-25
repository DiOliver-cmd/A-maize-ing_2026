# Flashcards — A-Maze-ing (Spaced Repetition)

> Cartões de estudo para **memorização dos conceitos críticos** cobrados na defesa.
> Formato para impressão: cada cartão tem **FRENTE** (pergunta) e **VERSO** (resposta).
>
> **Como usar:**
> 1. Imprima as tabelas abaixo (uma por página ou frente/verso).
> 2. Recorte cada linha = 1 cartão.
> 3. Revise 10 min/dia nos dias que antecedem a defesa.
> 4. Marque os que errar; revise-os com mais frequência (spaced repetition).
>
> **Formato de impressão recomendado:** tabela 2 colunas (Frente | Verso), recortável.
> Alternativamente, use o app **Anki** e crie os cartões digitando frente/verso.

---

## Categoria 1 — Codificação Hex de Paredes

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| Qual o bit de cada direção na codificação hex? | North = bit 0 (valor 1); East = bit 1 (valor 2); South = bit 2 (valor 4); West = bit 3 (valor 8). |
| Parede fechada = bit 1 ou 0? | **Fechada = 1** (bit setado). Aberta = 0. |
| O que significa o dígito `3` (0011)? | Bits 0 e 1 setados → paredes **North e East fechadas** (South e West abertas). |
| O que significa o dígito `A` (1010)? | Bits 1 e 3 setados → paredes **East e West fechadas**. |
| Qual o valor de uma célula totalmente fechada (padrão "42")? | `F` (1111) = 15 (todas as 4 paredes fechadas). |
| Qual o valor de uma célula totalmente aberta? | `0` (0000). |
| Qual a regra de ouro da coerência entre vizinhos? | Se A tem parede East fechada, B (vizinho a leste) **deve** ter parede West fechada também. |
| Como garantir coerência ao remover uma parede? | Atualizar **ambos** os lados: limpar bit East de A **e** bit West de B simultaneamente. |
| O que o analisador reporta se houver incoerência? | `INCOHERENT walls` — erro **fatal**, nada mais é avaliado. |

---

## Categoria 2 — Sistema de Coordenadas

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| No subject, o que significa `x` e `y` em `ENTRY=x,y`? | `x = coluna`, `y = linha`. |
| `ENTRY=0,0` corresponde a qual canto? | Canto superior esquerdo (coluna 0, linha 0). |
| Internamente o analisador usa qual ordem? | `(row, col)` = `(y, x)`. |
| No arquivo de saída, como escrever a entry? | `x,y` (coluna, linha) — **não** `row,col`. |
| Pegadinha: confundir `(x,y)` com `(row,col)` causa o quê? | Labirinto transposto/espelhado; entry/exit errados; falha na defesa. |

---

## Categoria 3 — Modos de Geração

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| `PERFECT=True`: quantos caminhos entre entry e exit? | **Exatamente um** (spanning tree, zero loops). |
| `PERFECT=True`: qual o valor de `loops` no analisador? | `0`. |
| `PERFECT=False` (padrão): o que o labirinto deve ser? | Tabuleiro jogável estilo **Pac-Man**. |
| `PERFECT=False`: mínimo de rotas independentes (loops)? | **≥ 2** (1 loop não é aceito). |
| `PERFECT=False`: onde ficam ghosts e super-pac-gums? | Nos **4 cantos** (devem ser corredores abertos). |
| `PERFECT=False`: onde o jogador inicia? | No **centro** (deve ser corredor aberto). |
| `PERFECT=False`: máximo de dead-ends reais tolerados? | **2** (configurável via `--max-dead-ends`). |
| `PERFECT=False`: bônus de dead-ends exige qual valor? | `0` (tabuleiro *braided* perfeito). |
| `PERFECT=False`: o que é proibido quanto a áreas abertas? | Nenhuma área **3×3 totalmente aberta** (corredores largura ≤ 2). |

---

## Categoria 4 — Teoria dos Grafos

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| O que é uma spanning tree? | Subgrafo que conecta todos os vértices **sem ciclos**. Todo labirinto perfeito é uma. |
| Fórmula do número de ciclos independentes? | `loops = arestas - vértices + 1` (circuit rank). |
| Para `PERFECT=True`, o valor de `loops` deve ser? | `0` (arestas = vértices - 1). |
| O que é um dead-end em termos de grafos? | Vértice de **grau 1** (uma única passagem aberta). |
| Qual algoritmo encontra o caminho mais curto (não-ponderado)? | **BFS** (Breadth-First Search). |
| Complexidade da BFS? | `O(V + E)` (linear no tamanho do grafo). |
| Como a BFS reconstrói o caminho? | Via dicionário `parent[v] = u`; segue de trás para frente da exit até a entry. |
| Diferença BFS vs DFS? | BFS = fila, caminho mais curto; DFS = pilha/recursão, base do backtracker. |

---

## Categoria 5 — Algoritmos de Geração

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| Recursive Backtracker: qual estrutura base? | **DFS** com pilha (ou recursão) + backtracking. |
| Backtracker: característica do labirinto gerado? | Corredores longos, poucos dead-ends curtos. |
| Prim: como funciona? | Cresce a partir de **fronteiras** (vizinhos não-visitados de células visitadas). |
| Kruskal: qual estrutura de dados essencial? | **Union-Find (DSU)** com path compression e union by rank. |
| Kruskal: característica do labirinto? | Muito ramificado e uniforme. |
| Todos esses algoritmos geram labirinto perfeito? | **Sim** (todos produzem spanning tree, `loops == 0`). |
| Como garantir reprodutibilidade? | Usar `random.Random(seed)` **dedicado** (não o global). |

---

## Categoria 6 — Union-Find (DSU)

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| O que faz `find(x)`? | Encontra o representante do conjunto de `x` (com path compression). |
| O que faz `union(a, b)`? | Une os conjuntos de `a` e `b` (com union by rank). |
| Complexidade do Union-Find? | Quase constante: inversa da função de **Ackermann**. |
| Path compression faz o quê? | Achata a árvore: aponta `parent[x]` direto para a raiz durante `find`. |
| Union by rank faz o quê? | Anexa a árvore menor à maior (pela altura) para manter equilíbrio. |
| Quando Kruskal remove uma parede? | Quando `find(a) != find(b)` (células em componentes diferentes). |

---

## Categoria 7 — Padrão "42"

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| Como o "42" é desenhado? | Células **totalmente fechadas** (`F`/15) formando os dígitos. |
| As células "42" são conectadas ao labirinto? | **Não** — são isoladas (obstáculos). |
| O analisador conta "42" como corredor desconectado? | **Não** — são `is_fully_closed`, toleradas. |
| O que fazer se a grade for pequena demais para o "42"? | **Omitir** e **imprimir mensagem de erro no console**. |
| Dead-end "enclosed" vs "real": diferença? | Enclosed = cercado por "42"/borda (tolerado); real = tem parede abrível para vizinho normal. |

---

## Categoria 8 — Arquivo de Saída

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| Layout do arquivo de saída? | Grade (1 linha hex por linha) → linha vazia → entry `x,y` → exit `x,y` → caminho `NESW...`. |
| Como o caminho mais curto é codificado? | String com letras `N, E, S, W`. |
| Todas as linhas terminam com? | `\n`. |
| As células são armazenadas em qual ordem? | **Linha por linha** (row-major). |
| Quantas linhas após a grade vazia? | **3**: entry, exit, caminho. |

---

## Categoria 9 — Qualidade e Ferramentas

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| Versão mínima do Python? | **3.10** ou superior. |
| Padrão de código exigido? | **flake8** (PEP 8). |
| Verificador de tipos exigido? | **mypy** com type hints em todas as funções. |
| Flags obrigatórias do mypy no Makefile? | `--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`. |
| Regras obrigatórias do Makefile? | `install`, `run`, `debug`, `clean`, `lint` (+ `lint-strict` opcional). |
| Docstrings devem seguir qual padrão? | **PEP 257** (Google ou NumPy style). |
| O que acontece se o programa crashar na defesa? | Considerado **não funcional** — use `try/except` e context managers. |
| Nome obrigatório do arquivo principal? | `a_maze_ing.py`. |

---

## Categoria 10 — Reusabilidade e Empacotamento

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| A classe reutilizável deve se chamar? | `MazeGenerator` (exemplo do subject). |
| O pacote deve se chamar? | `mazegen-*` (ex.: `mazegen-1.0.0-py3-none-any.whl`). |
| Extensões aceitas para o pacote? | `.whl` e `.tar.gz`. |
| Onde o `.whl` deve ficar? | Na **raiz** do repositório Git. |
| Comando para buildar o pacote? | `python -m build` (gera `dist/*.whl` e `*.tar.gz`). |
| Arquivo de licença obrigatório? | `LICENSE.md` na raiz, **permissiva** (MIT recomendada). |
| O README deve conter o quê sobre o módulo? | Documentação curta: instanciar, parâmetros, acessar estrutura e solução. |
| Na defesa, o que será pedido sobre o pacote? | Reconstruir em **virtualenv limpo** a partir dos fontes. |

---

## Categoria 11 — README e Defesa

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| Primeira linha do README (formato exato)? | `*This project has been created as part of the 42 curriculum by <login1>[, <login2>...].*` (itálico). |
| Seções obrigatórias do README? | Description, Instructions, Resources (com uso de IA descrito). |
| O que o README deve incluir sobre o algoritmo? | Qual escolheu + **por quê**. |
| O que o README deve incluir sobre gestão? | Papéis, planejamento previsto vs real, o que funcionou/melhorou, ferramentas. |
| O subject prevê modificação ao vivo na defesa? | **Sim** — pequena mudança em poucos minutos. |
| Regra sobre uso de IA (Cap. II)? | Só use conteúdo que **entende e assume responsabilidade**; não saber explicar = reprova. |

---

## Categoria 12 — Visual e Interações

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| Opções de representação visual? | **ASCII** no terminal **ou** gráfica via **MiniLibX (MLX)**. |
| Interações obrigatórias (mínimo 3)? | Re-gerar, mostrar/ocultar caminho, mudar cor das paredes. |
| Interação opcional do "42"? | Cor específica para o padrão "42". |
| Como colorir no terminal sem bibliotecas? | **ANSI escape codes** (ex.: `\033[31m` = vermelho, `\033[0m` = reset). |

---

## Categoria 13 — maze_analyzer.py

| Frente (pergunta) | Verso (resposta) |
|-------------------|------------------|
| O analisador verifica o quê primeiro? | **Coerência das paredes** (`incoherent_cells`). |
| Como o analisador calcula loops? | `open_passages - len(region) + 1`. |
| Flag para exigir zero dead-ends (bônus)? | `--max-dead-ends 0`. |
| Flag para mínimo de rotas independentes? | `--min-loops 2` (padrão). |
| Veredito para `PERFECT=True` válido? | `PERFECT maze: a single path, no loop`. |
| Veredito para `PERFECT=False` válido? | `Pac-Man-USABLE`. |
| Veredito de bônus (zero dead-ends)? | `no real dead-end -> bonus-grade (perfectly braided)`. |
| O analisador escolhe a região a partir de quê? | Da **entry** (se válida no footer); senão, a maior componente. |

---

## Resumo de Uso

- **Total de cartões:** ~70 (13 categorias).
- **Frequência recomendada:** 10 min/dia, todos os dias, na semana da defesa.
- **Prioridade:** Categorias 1, 3, 4, 9, 13 são as mais cobradas em defesa.
- **Método:** se errar um cartão, revise-o no dia seguinte **e** marque para revisão
  mais frequente (spaced repetition clássico).
