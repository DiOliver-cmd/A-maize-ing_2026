# Guia de Estudo — Parte Bônus (A-Maze-ing)

> Este documento cobre os **conceitos necessários para os bônus** do projeto
> **A-Maze-ing** (versão 2.2). A explicação está em português; termos técnicos
> essenciais são mantidos em inglês para fidelidade ao enunciado.
>
> Os bônus **não são obrigatórios** para a aprovação, mas **adicionam pontos** e
> demonstram domínio avançado. Só devem ser atacados **após** a parte mandatória estar
> 100% funcional e validada pelo `maze_analyzer.py`.

---

## 0. Os Bônus Oficiais (do Capítulo VIII do subject)

O subject lista **exemplos** de bônus possíveis:

1. **Tabuleiro *braided* sem dead-ends** (`PERFECT=False` com **zero** dead-ends reais),
   verificado pelo analisador com `--max-dead-ends 0`.
2. **Suporte a múltiplos algoritmos** de geração de labirinto.
3. **Animação durante a geração** do labirinto.

> O subject diz "possible examples" — você pode propor **outros** bônus, mas estes três
> são os esperados/canônicos. Foque neles.

---

## 1. Bônus 1 — Tabuleiro *Braided* (Zero Dead-Ends)

### 1.1 O que é um *braided maze*

Um **braided maze** é um labirinto **sem becos sem saída** (dead-ends). Em um braided
maze **totalmente** braided, **toda célula tem grau ≥ 2** — sempre há uma rota de fuga.
Isso é o **ideal para Pac-Man**: o jogador perseguido nunca fica encurralado.

### 1.2 O critério de avaliação

O `maze_analyzer.py` aceita a flag `--max-dead-ends N`:
- Padrão (mandatório): `--max-dead-ends 2` (tolera até 2 dead-ends reais).
- **Bônus:** `--max-dead-ends 0` → exige **zero** dead-ends reais.

O analisador distingue:
- **Dead-end real:** célula de grau 1 cuja parede fechada poderia ser aberta para um
  vizinho **normal** (não-"42", dentro da grade).
- **Dead-end enclosed:** célula de grau 1 cercada apenas por células "42" totalmente
  fechadas ou pela borda externa — **tolerada** (não conta como real).

> **Para o bônus:** `real == 0`. Os `enclosed` (junto ao "42"/borda) **não** invalidam.

### 1.3 Algoritmo de *braiding* (transformar perfeito → braided)

Partindo de um labirinto **perfeito** (gerado por backtracker/Prim/Kruskal):

1. **Identifique todos os dead-ends** (células de grau 1).
2. Para cada dead-end, **abra uma parede adicional** conectando-o a um vizinho, de modo
   que seu grau passe a **≥ 2**.
   - Escolha um vizinho **não-"42"**, dentro dos limites, cuja parede compartilhada
     esteja fechada.
   - Prefira abrir para um vizinho que **não crie um dead-end novo** e que **mantenha**
     a coerência (atualize ambos os lados).
3. **Repita** até que não reste nenhum dead-end real.
4. **Valide** com `maze_analyzer.py --max-dead-ends 0`.

### 1.4 Armadilhas do braiding

- **Abrir parede demais** pode criar **áreas abertas grandes** (proibido: corredores
  não podem ter largura > 2; nada de área 3×3 aberta). Controle a escolha do vizinho.
- **Criar dead-end novo:** ao abrir uma parede, raramente cria-se um novo dead-end, mas
  verifique sempre o grau dos vizinhos afetados.
- **Manter loops ≥ 2:** o braiding naturalmente **aumenta** os loops (cada parede
  removida adiciona um ciclo), então `loops >= 2` fica satisfeito facilmente.
- **Cantos e centro:** continue garantindo que sejam corredores alcançáveis.

### 1.5 Estratégia alternativa: geração *braid-first*

Em vez de gerar perfeito e depois brair, pode-se gerar diretamente um grafo com grau
mínimo 2 (ex.: gerar spanning tree e depois adicionar arestas até `grau_mínimo >= 2`).
O método "perfeito + braiding" é mais simples e previsível.

> **Aprofundamento:**
> - Jamis Buck, *Mazes for Programmers* (Pragmatic Bookshelf, 2015) — capítulo
>   dedicado a braided mazes, com implementação e análise.
> - Walter D. Pullen, "Think Labyrinth: Maze Algorithms":
>   https://www.astrolog.org/labyrnth/algrithm.htm — referência histórica que
>   descreve braided mazes e suas variações.

> 🔧 **MARCO DE IMPLEMENTAÇÃO B1 — Braided (zero dead-ends):**
> Após ler esta seção, implementem juntos: detecção de dead-ends (real vs enclosed),
> algoritmo de braiding (abrir paredes sem criar áreas 3×3), e integração ao modo
> `PERFECT=False`. Validem com `maze_analyzer.py --max-dead-ends 0` → veredito deve
> conter `no real dead-end -> bonus-grade`. Testem em vários tamanhos (10×10, 30×30,
> 50×50). **Tempo alvo:** 3–4h. *Pessoa A implementa o braiding; Pessoa B escreve os
> testes de regressão.* **Não avancem** para o Bônus 2 enquanto o braided não passar
> em todos os tamanhos.

---

## 2. Bônus 2 — Múltiplos Algoritmos de Geração

### 2.1 Objetivo

Permitir que o usuário **escolha o algoritmo** via configuração (ex.: `ALGORITHM=kruskal`)
e/ou via interação no modo visual.

### 2.2 Algoritmos recomendados para implementar

| Algoritmo | Característica | Estrutura-chave |
|-----------|----------------|-----------------|
| **Recursive Backtracker** (DFS) | Corredores longos, poucos dead-ends curtos | Pilha / recursão |
| **Prim** | Muitos dead-ends curtos, ramificado | Fila de fronteiras |
| **Kruskal** | Muito ramificado e uniforme | **Union-Find (DSU)** |
| *(opcional)* **Wilson's / Aldous-Broder** | Labirintos uniformemente aleatórios | Caminhadas aleatórias |
| *(opcional)* **Eller's** | Geração linha-a-linha (baixa memória) | Conjuntos por linha |
| *(opcional)* **Hunt-and-Kill** | Variante do backtracker sem pilha grande | Varredura |

### 2.3 Arquitetura para suportar múltiplos algoritmos

Use um **padrão Strategy** (ou *dispatch* por nome):

```python
class MazeGenerator:
    ALGORITHMS = {
        "backtracker": _gen_backtracker,
        "prim":        _gen_prim,
        "kruskal":     _gen_kruskal,
    }

    def __init__(self, width, height, algorithm="backtracker", seed=None):
        if algorithm not in self.ALGORITHMS:
            raise ValueError(f"unknown algorithm: {algorithm}")
        ...
    def generate(self):
        return self.ALGORITHMS[self.algorithm](self)
```

- Cada algoritmo é uma função que recebe a grade e a preenche, **respeitando a mesma
  interface** (entrada: grade vazia com todas as paredes; saída: grade com paredes
  removidas formando spanning tree).
- O "42" e as bordas externas são tratados **antes** de chamar o algoritmo (pré-condição
  comum a todos).

### 2.4 Union-Find (Disjoint Set Union) — para Kruskal

Estrutura essencial para o algoritmo de Kruskal:

- `find(x)`: encontra o representante do conjunto de `x` (com *path compression*).
- `union(a, b)`: une os conjuntos de `a` e `b` (com *union by rank*).
- Complexidade quase constante (inversa de Ackermann).

```python
class DSU:
    def __init__(self, n): self.parent = list(range(n)); self.rank = [0]*n
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # path compression
            x = self.parent[x]
        return x
    def union(self, a, b) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb: return False
        if self.rank[ra] < self.rank[rb]: ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]: self.rank[ra] += 1
        return True
```

> **Aprofundamento:**
> - CP-Algorithms, "Disjoint Set Union":
>   https://cp-algorithms.com/data_structures/disjoint_set_union.html — referência
>   de programação competitiva, com prova de complexidade (inversa de Ackermann) e
>   implementações de path compression e union by rank.
> - CP-Algorithms, "Kruskal's algorithm for Minimum Spanning Tree":
>   https://cp-algorithms.com/graph/mst_kruskal.html — explicação do algoritmo de
>   Kruskal usando DSU, com código e análise.
> - *Introduction to Algorithms* (CLRS), 3ª ed., capítulo 23 (Árvores Geradoras
>   Mínimas) e capítulo 21 (Estruturas de dados para conjuntos disjuntos).

> 🔧 **MARCO DE IMPLEMENTAÇÃO B2 — Múltiplos algoritmos (Strategy + Prim + Kruskal):**
> Após ler esta seção, implementem juntos: o padrão Strategy (registro de algoritmos),
> o algoritmo de Prim, e o Kruskal com DSU. Para **cada** algoritmo, validem com o
> analisador em modo `PERFECT=True` (deve dar `PERFECT maze`) e `PERFECT=False`
> (`Pac-Man-USABLE`). Confirmem reprodutibilidade: mesmo seed + mesmo algoritmo →
> labirinto idêntico. **Tempo alvo:** 4–5h. *Pessoa A implementa os algoritmos; Pessoa
> B adiciona seleção via config/UI e os testes por algoritmo.* Trabalhem num branch
> conjunto para a refatoração Strategy.

### 2.5 Reprodutibilidade por *seed*

Cada algoritmo deve respeitar o `seed` (via `random.Random(seed)`) para que a saída seja
**reproduzível**. Use uma instância de `random.Random` **dedicada** por geração (não o
`random` global), para que a escolha do algoritmo não afete a sequência de outros
componentes.

---

## 3. Bônus 3 — Animação Durante a Geração

### 3.1 Objetivo

Mostrar, **ao vivo**, o labirinto sendo construído — paredes sendo removidas uma a uma,
criando um efeito visual didático e atraente.

### 3.2 Abordagens

#### 3.2.1 Animação no terminal (ASCII)

- Após cada passo do algoritmo (ex.: cada parede removida), **limpe a tela** e
  **reimprima** a grade.
- Use `os.system("clear")` (Linux/Mac) ou sequência ANSI `\033[H\033[2J`.
- Adicione um **pequeno delay** (`time.sleep(0.02)`) para a animação ser visível.
- **Atenção ao desempenho:** reimprimir a grade inteira a cada passo é custoso para
  labirintos grandes. Otimize reimprimindo apenas a célula alterada (posicionando o
  cursor com códigos ANSI).

#### 3.2.2 Animação com MLX (gráfica)

- Desenhe a grade em uma janela; a cada passo, **redesenhe apenas a célula afetada**
  (preencha o pixel/bloco correspondente).
- Use o *loop* de eventos do MLX (`mlx_loop`) para manter a janela responsiva.
- Permite animação **suave** e colorida.

### 3.3 Integração com o algoritmo

- O algoritmo de geração deve expor um **callback** ou ser um **gerador (yield)** que
  notifica a cada modificação:
```python
def _gen_backtracker(self):
    ...
    while stack:
        ...
        self._remove_wall(current, nxt)   # notifica o renderer
        yield (current, nxt)              # passo animável
```
- O renderer consome os *yields* e atualiza a tela. Assim, a **mesma** lógica de geração
  serve para modo estático e animado.

### 3.4 Controles de animação

- **Pausar/Retomar** a animação.
- **Acelerar/Desacelerar** (ajustar o delay).
- **Pular** direto para o resultado final.
- *(Opcional)* **Passo a passo** (avançar um passo por tecla).

> **Aprofundamento:**
> - Real Python, "Terminal Output with ANSI Escape Sequences":
>   https://realpython.com/lessons/terminal-output-ansi-escape-sequences/ — tutorial
>   prático sobre códigos ANSI para cores e posicionamento de cursor em Python.
> - Documentação oficial do Python, módulo `curses`:
>   https://docs.python.org/3/library/curses.html — alternativa robusta para controle
>   de terminal (posicionamento de cursor, cores, entrada sem *enter*).
> - MLX events: documentação interna 42.

> 🔧 **MARCO DE IMPLEMENTAÇÃO B3 — Animação (yield + renderer incremental):**
> Após ler esta seção, implementem juntos: refatorar os algoritmos para emitir passos
> via `yield`, e o renderer animado com redraw incremental (cursor ANSI). Validem que o
> labirinto final da animação é **idêntico** ao modo não-animado (mesmo seed — façam
> diff). Testem os controles: pausa, velocidade, skip. **Tempo alvo:** 2.5–3.5h.
> *Coordenação:* Pessoa A adapta os algoritmos para `yield`; Pessoa B implementa o
> renderer animado. Façam num branch conjunto. **Cuidado:** a animação **não** pode
> alterar o labirinto gerado.

---

## 4. Bônus Adicionais (sugestões, não exigidos)

Estes **não** estão no subject, mas agregam valor e demonstram iniciativa. Avalie o
tempo antes de investir:

- **Solver visual interativo:** animar a BFS/A* encontrando o caminho.
- **Exportação de imagem** (PNG/SVG) do labirinto via `Pillow` ou `matplotlib`.
- **Diferentes formatos de saída** (ex.: JSON, além do hex).
- **Geração de labirintos não-retangulares** (ex.: circular, hexagonal).
- **Persistência de seeds** favoritas.
- **Modo "desafio":** jogador percorre o labirinto com o teclado.

> **Cuidado:** bônus extras **não substituem** o mandatório. Se o mandatório falhar na
> defesa, os bônus não salvam a nota.

---

## 5. Conceitos Transversais aos Bônus

### 5.1 Padrões de projeto (design patterns)

- **Strategy:** múltiplos algoritmos com interface comum (bônus 2).
- **Observer / Callback:** notificar o renderer a cada passo (bônus 3).
- **Factory:** construir o gerador a partir do config.

### 5.2 Performance e complexidade

- Recursive backtracker: **O(W·H)** tempo e memória.
- Kruskal: **O(W·H · α(W·H))** com Union-Find (quase linear).
- Braiding: **O(W·H)** (uma passada para identificar dead-ends).
- Animação: cuidado com **redraw** — use *dirty rectangles* / atualização incremental.

### 5.3 Testabilidade dos bônus

- **Braided:** teste automatizado rodando `maze_analyzer.py --max-dead-ends 0` em vários
  seeds/tamanhos.
- **Múltiplos algoritmos:** para cada algoritmo, valide que a saída é um labirinto
  **válido e coerente** (passa no analisador) e, no modo `PERFECT=True`, é perfeito.
- **Animação:** teste manual (visual); valide que o resultado final é idêntico ao modo
  não-animado (a animação não deve alterar o labirinto gerado).

---

## 6. Checklist de Conceitos para Dominar (Bônus)

- [ ] Definição de *braided maze* e diferença entre dead-end *real* e *enclosed*.
- [ ] Algoritmo de braiding (perfeito → sem dead-ends) sem criar áreas 3×3.
- [ ] Validação com `--max-dead-ends 0`.
- [ ] Padrão Strategy para múltiplos algoritmos.
- [ ] Union-Find (DSU) com path compression e union by rank (para Kruskal).
- [ ] Pelo menos 2–3 algoritmos distintos (backtracker + Prim/Kruskal).
- [ ] Reprodutibilidade por `seed` independente do algoritmo.
- [ ] Animação via callback/yield, com redraw incremental.
- [ ] Controles de animação (pausa, velocidade, passo-a-passo).
- [ ] Garantir que bônus **não quebrem** o mandatório (regressão).

---

## 7. Referências para Aprofundamento (Bônus)

| Tema | Referência |
|------|------------|
| Braided mazes | Jamis Buck, *Mazes for Programmers* (Pragmatic Bookshelf, 2015) |
| Think Labyrinth (referência histórica) | Walter D. Pullen — https://www.astrolog.org/labyrnth/algrithm.htm |
| Union-Find (DSU) | CP-Algorithms — https://cp-algorithms.com/data_structures/disjoint_set_union.html |
| Kruskal (MST) | CP-Algorithms — https://cp-algorithms.com/graph/mst_kruskal.html |
| Prim (maze) | Jamis Buck — https://weblog.jamisbuck.org/2011/1/10/maze-generation-prim-s-algorithm |
| Wilson's / Aldous-Broder | Jamis Buck, *Mazes for Programmers* (caps. correspondentes) |
| Strategy pattern | Refactoring.Guru — https://refactoring.guru/design-patterns/strategy |
| ANSI escape codes (animação terminal) | Real Python — https://realpython.com/lessons/terminal-output-ansi-escape-sequences/ |
| Controle de terminal (curses) | Docs oficiais Python — https://docs.python.org/3/library/curses.html |
| Spanning trees / MST (teoria) | *Introduction to Algorithms* (CLRS), 3ª ed., cap. 23 |
| Pillow (exportação de imagem) | https://pillow.readthedocs.io/ |
