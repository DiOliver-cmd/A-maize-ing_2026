# Tarefas de Execução — Parte Bônus (A-Maze-ing)

> Plano de execução **passo a passo** dos bônus. **Pré-requisito absoluto:** a parte
> mandatória (`TAREFAS_MANDATORIO.md`) está 100% funcional e validada pelo
> `maze_analyzer.py`. Bônus **nunca** compensam falhas no mandatório.
>
> Termos técnicos essenciais em inglês; explicação em português.

**Ordem recomendada:** B1 (braided) → B2 (múltiplos algoritmos) → B3 (animação).
O B1 é o mais "valioso" (validável objetivamente pelo analisador) e o mais cobrado em
defesa. B2 e B3 são diferenciais visuais/arquiteturais.

---

## Bônus 1 — Tabuleiro *Braided* (Zero Dead-Ends)

### B1.1 — Implementar detecção de dead-ends
- **Arquivos:** `mazegen/generator.py`.
- **Ações:**
  - Método `dead_ends() -> list[tuple[int,int]]`: retorna células da região jogável com
    **grau 1** (uma única passagem aberta).
  - Distinguir **real** (tem parede abrível para vizinho normal) de **enclosed**
    (cercado por "42"/borda) — espelhar a lógica do `maze_analyzer.py`.
- **Critério:** contagem bate com o analisador para um labirinto de teste.

### B1.2 — Implementar o algoritmo de *braiding*
- **Ações:** método `braid()`:
  - Para cada dead-end **real**:
    - Encontrar um vizinho **não-obstáculo**, dentro dos limites, com parede fechada,
      tal que abri-la **não** crie uma área 3×3 aberta.
    - `remove_wall(dead_end, vizinho)` (atualiza ambos os lados).
  - Repetir até `real_dead_ends == 0`.
  - **Cuidado:** ao abrir uma parede, o dead-end deixa de sê-lo (grau vira ≥ 2), mas pode
    criar um novo dead-end no vizinho se ele tinha grau 1 — verificar e continuar.
- **Critério:** após `braid()`, `real_dead_ends == 0`.

### B1.3 — Integrar ao modo `PERFECT=False`
- **Ações:**
  - Adicionar opção de config `BRAIDED=True` (ou um modo `PERFECT=False` que sempre
    brai, ou um sub-flag).
  - Fluxo: gerar base perfeita → criar loops (T5.3) → `braid()`.
  - Garantir que o braiding **mantém** `loops >= 2` (na verdade aumenta) e cantos/centro
    acessíveis.
- **Critério:** `maze_analyzer.py --max-dead-ends 0` reporta `Pac-Man-USABLE` com
  "no real dead-end -> bonus-grade".

### B1.4 — Evitar áreas abertas grandes durante o braiding
- **Ações:**
  - Função `_creates_open_area(a, b) -> bool`: simula a abertura e verifica se surge
    alguma janela 3×3 totalmente aberta.
  - Se a abertura candidata criar área proibida, **pular** para outro vizinho.
- **Critério:** inspeção visual sem áreas 3×3; teste automatizado confirma.

### B1.5 — Testes de regressão do braided
- **Ações:** gerar labirintos braided para vários tamanhos/seeds e validar:
  - `--max-dead-ends 0` → `real == 0`.
  - `loops >= 2`.
  - coerência OK.
  - sem áreas 3×3.
- **Critério:** 100% dos casos passam.

---

## Bônus 2 — Múltiplos Algoritmos de Geração

### B2.1 — Refatorar para o padrão Strategy
- **Arquivos:** `mazegen/generator.py`.
- **Ações:**
  - Extrair a interface de geração: cada algoritmo é uma função
    `_gen_xxx(self) -> None` que preenche `self.grid` (respeitando obstáculos do "42").
  - Registro `ALGORITHMS: dict[str, Callable]` na classe.
  - Construtor valida `algorithm` contra o registro.
- **Critério:** `algorithm="backtracker"` funciona como antes; nomes inválidos geram
  erro claro.

### B2.2 — Implementar Prim
- **Ações:** `_gen_prim(self)`:
  - Iniciar com uma célula aleatória (não-obstáculo) marcada como visitada.
  - Manter lista de **fronteiras** (vizinhos não-visitados de células visitadas).
  - A cada passo: escolher uma fronteira aleatória, conectá-la a uma célula visitada
    vizinha (remover parede), marcar visitada, adicionar suas fronteiras.
  - Repetir até todas as células não-obstáculo visitadas.
- **Critério:** gera labirinto perfeito válido (passa no analisador).

### B2.3 — Implementar Kruskal (com Union-Find)
- **Ações:**
  - Implementar classe `DSU` (path compression + union by rank) — ver
    `ESTUDO_BONUS.md` seção 2.4.
  - `_gen_kruskal(self)`:
    - Listar todas as paredes internas (entre células não-obstáculo adjacentes).
    - Embaralhar com `self.rng`.
    - Para cada parede: se `find(a) != find(b)`, `remove_wall(a,b)` e `union(a,b)`.
- **Critério:** gera labirinto perfeito válido; `loops == 0`.

### B2.4 — (Opcional) Algoritmo adicional
- **Ações:** implementar **Eller's** ou **Wilson's** ou **Hunt-and-Kill** como
  diferencial extra.
- **Critério:** válido no analisador.

### B2.5 — Seleção via config e via UI
- **Ações:**
  - Suportar `ALGORITHM=prim` no `config.txt`.
  - No modo visual, permitir trocar o algoritmo com uma tecla (ex.: `a` cicla entre os
    disponíveis) e re-gerar.
- **Critério:** usuário consegue escolher o algoritmo em ambos os pontos.

### B2.6 — Reprodutibilidade independente do algoritmo
- **Ações:** garantir que o `seed` produz resultados reproduzíveis **por algoritmo**
  (mesmo seed + mesmo algoritmo → mesmo labirinto). Usar `self.rng` dedicado.
- **Critério:** teste confirma.

### B2.7 — Testes para cada algoritmo
- **Ações:** para cada algoritmo, validar (em modo `PERFECT=True`):
  - `loops == 0`, conectividade, coerência, "42" isolado.
  - Em modo jogável: `loops >= 2`, cantos/centro, dead-ends ≤ 2.
- **Critério:** todos passam.

---

## Bônus 3 — Animação Durante a Geração

### B3.1 — Refatorar a geração para emitir passos
- **Arquivos:** `mazegen/generator.py`.
- **Ações:**
  - Converter os algoritmos em **geradores** (`yield`) que emitem cada modificação:
    ```python
    def _gen_backtracker(self):
        ...
        self.remove_wall(current, nxt)
        yield ("remove_wall", current, nxt)
    ```
  - Manter um modo **não-animado** que apenas consome o gerador sem renderizar
    (compatibilidade com o uso existente).
- **Critério:** geração animável e não-animada produzem o **mesmo** labirinto (mesmo
  seed).

### B3.2 — Renderer animado (ASCII)
- **Arquivos:** `mazegen/renderer_ascii.py`.
- **Ações:**
  - Função `animate(generator, ...)` que itera sobre os *yields* e, a cada passo:
    - Atualiza a célula afetada na tela (redraw **incremental** via posicionamento de
      cursor ANSI, não reimpressão total).
    - `time.sleep(delay)` (delay configurável).
  - Suportar **pausa** (tecla espaço), **velocidade** (`+`/`-`), **passo-a-passo**
    (seta), e **pular ao final** (`f`).
- **Critério:** animação visível e fluida para labirintos pequenos/médios.

### B3.3 — Renderer animado (MLX, se aplicável)
- **Ações:** se MLX já estiver integrado (T8.3), adicionar o modo animado desenhando
  cada passo na janela.
- **Critério:** animação gráfica funcional.

### B3.4 — Controle de desempenho
- **Ações:**
  - Para labirintos grandes, o redraw por passo pode ser lento. Estratégias:
    - *Batching:* renderizar a cada N passos.
    - *Skip:* permitir pular a animação e mostrar só o resultado.
  - Garantir que o resultado final é correto independentemente da animação.
- **Critério:** labirinto 50×50 anima em tempo razoável (< 30s) ou permite pular.

### B3.5 — Integração no menu de interações
- **Ações:** adicionar tecla `g` (ou similar) para **re-gerar com animação**.
- **Critério:** usuário pode acionar a animação a partir do modo visual.

---

## Bônus Extras (opcionais, se sobrar tempo)

### BX.1 — Solver visual animado
- Animar a BFS encontrando o caminho (células visitadas coloridas progressivamente).

### BX.2 — Exportação de imagem (PNG/SVG)
- Usar `Pillow` para gerar PNG do labirinto. Útil para o README e para a defesa.

### BX.3 — Múltiplos formatos de saída
- Além do hex, suportar JSON (estrutura + caminho).

### BX.4 — Modo desafio (jogável)
- Jogador percorre o labirinto com setas do teclado; cronômetro.

> **Aviso:** bônus extras têm **baixo peso** na avaliação em comparação com B1–B3.
> Invista neles apenas se B1–B3 estiverem sólidos.

---

## Resumo de Dependências (Bônus)

```
Mandatório 100% validado
        │
        ▼
B1 (braided) ──► B1.5 (testes)
        │
        ▼
B2 (Strategy) ──► B2.2 (Prim) ──► B2.3 (Kruskal) ──► B2.7 (testes)
        │
        ▼
B3 (animação) ──► B3.1 (yield) ──► B3.2 (ASCII anim) ──► B3.5 (menu)
        │
        ▼
BX (extras opcionais)
```

> **Regra de ouro:** após **cada** bônus, rodar `make lint` e os testes de regressão
> do mandatório para garantir que **nada quebrou**.
