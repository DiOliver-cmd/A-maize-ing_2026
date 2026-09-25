# Guia de Teste e Defesa — Parte Bônus (A-Maze-ing)

> Roteiro prático para **testar os bônus** e conduzir a parte de bônus da defesa
> (peer-evaluation). Pensado no que pode ser **avaliado ou solicitado** com base no
> Capítulo VIII do subject. Termos técnicos em inglês; explicação em português.
>
> **Pré-requisito:** a parte mandatória (`TESTE_DEFESA_MANDATORIO.md`) já passou em
> todos os itens. Bônus só são avaliados se o mandatório estiver aprovado.

---

## 1. Preparação Específica para os Bônus

- [ ] Modo braided implementado e testado.
- [ ] Múltiplos algoritmos implementados (no mínimo 2 além do backtracker, idealmente
  Prim + Kruskal).
- [ ] Animação de geração implementada (ASCII e/ou MLX).
- [ ] `make lint` e `make lint-strict` continuam limpos (bônus não quebraram o mandatório).
- [ ] Testes de regressão do mandatório re-executados após cada bônus.
- [ ] README atualizado descrevendo os bônus implementados.

---

## 2. Bônus 1 — Tabuleiro *Braided* (Zero Dead-Ends)

### 2.1 Validação automatizada (a mais importante — é objetiva)
- [ ] Gerar labirinto em modo `PERFECT=False` com braiding ativado.
- [ ] Rodar: `python3 maze_analyzer.py maze.txt --max-dead-ends 0`
- [ ] Veredito esperado: **`Pac-Man-USABLE`** com a frase
  **`no real dead-end -> bonus-grade (perfectly braided)`**.
- [ ] Confirmar: `Dead-ends: 0 real + N enclosed` (enclosed tolerado, junto ao "42").

### 2.2 Validação dos demais critérios (não podem quebrar)
- [ ] `Independent loops >= 2` (braiding tende a aumentar loops).
- [ ] `Corners + centre: all reachable`.
- [ ] `disconnected_corridors == 0`.
- [ ] `Wall coherence: OK`.

### 2.3 Inspeção visual
- [ ] No visual, **nenhum** beco sem saída real (todo corredor tem ≥ 2 saídas).
- [ ] **Nenhuma área 3×3 totalmente aberta** (corredores largura ≤ 2).
- [ ] O "42" permanece visível e isolado.

### 2.4 Teste de regressão (vários tamanhos/seeds)
- [ ] Gerar braided para tamanhos: 10×10, 20×15, 30×30, 50×50.
- [ ] Para cada um, `--max-dead-ends 0` → `bonus-grade`.
- [ ] Nenhum caso falha.

### 2.5 Perguntas que o avaliador pode fazer
1. **"O que é um braided maze?"** → labirinto sem dead-ends; todo corredor tem rota de
   fuga; ideal para Pac-Man.
2. **"Como você eliminou os dead-ends?"** → após gerar a base perfeita, para cada dead-end
   real abriu-se uma parede adicional conectando-o a um vizinho normal, sem criar áreas
   3×3.
3. **"Qual a diferença entre dead-end real e enclosed?"** → real tem parede abrível para
   vizinho normal; enclosed está cercado por "42"/borda (tolerado).
4. **"Por que o braiding não quebra a coerência das paredes?"** → `remove_wall` atualiza
   sempre ambos os lados.
5. **"Como evitou áreas 3×3 abertas?"** → função `_creates_open_area` simula a abertura e
   rejeita candidatos inválidos.

---

## 3. Bônus 2 — Múltiplos Algoritmos de Geração

### 3.1 Validação por algoritmo (modo `PERFECT=True`)
Para **cada** algoritmo (backtracker, Prim, Kruskal, e qualquer extra):
- [ ] `ALGORITHM=<nome>` no config → gera sem erro.
- [ ] `maze_analyzer.py maze.txt` → **`PERFECT maze`**.
- [ ] `Wall coherence: OK`.
- [ ] `disconnected_corridors == 0`.
- [ ] "42" presente e isolado (ou mensagem de erro se grade pequena).

### 3.2 Validação por algoritmo (modo `PERFECT=False`)
Para cada algoritmo:
- [ ] Gera tabuleiro jogável → `Pac-Man-USABLE`.
- [ ] `loops >= 2`, cantos/centro acessíveis, dead-ends ≤ 2.

### 3.3 Reprodutibilidade por algoritmo
- [ ] Mesmo seed + mesmo algoritmo → labirinto idêntico (diff vazio).
- [ ] Mesmo seed + algoritmos diferentes → labirintos diferentes (esperado).

### 3.4 Seleção via UI
- [ ] No modo visual, tecla para trocar de algoritmo funciona.
- [ ] Após trocar, re-gerar usa o algoritmo recém-selecionado.

### 3.5 Algoritmo inválido
- [ ] `ALGORITHM=inexistente` → mensagem de erro clara, sem crash, listando os
  algoritmos disponíveis.

### 3.6 Perguntas que o avaliador pode fazer
1. **"Por que implementou múltiplos algoritmos?"** → demonstrar domínio, comparar
   propriedades (corredores longos vs. ramificados).
2. **"Qual a diferença entre Prim e Kruskal?"** → Prim cresce a partir de fronteiras;
   Kruskal une componentes via Union-Find.
3. **"Explique o Union-Find."** → find com path compression, union by rank, complexidade
   quase constante (inversa de Ackermann).
4. **"Como o seed interage com algoritmos diferentes?"** → `random.Random(seed)`
   dedicado por geração; mesmo algoritmo+seed reproduz, mas algoritmos diferentes
   produzem labirintos diferentes.
5. **"Qual algoritmo produz labirintos mais ramificados?"** → Kruskal/Prim; backtracker
   produz corredores longos.

---

## 4. Bônus 3 — Animação Durante a Geração

### 4.1 Validação visual
- [ ] Acionar a animação (tecla `g` ou similar) → labirinto é desenhado progressivamente.
- [ ] Paredes sendo removidas uma a uma são visíveis.
- [ ] Animação termina com o labirinto **completo e correto**.

### 4.2 Correção do resultado
- [ ] O labirinto final da animação é **idêntico** ao gerado sem animação (mesmo seed).
  - Teste: gerar com animação, salvar; gerar sem animação, salvar; diff vazio.
- [ ] Passa no `maze_analyzer.py` (mesmo veredito do modo não-animado).

### 4.3 Controles de animação
- [ ] **Pausar/Retomar** (espaço).
- [ ] **Acelerar/Desacelerar** (`+`/`-`).
- [ ] **Passo a passo** (seta ou tecla).
- [ ] **Pular ao final** (`f`).

### 4.4 Desempenho
- [ ] Labirinto 20×15 anima em tempo razoável (< 10s).
- [ ] Labirinto 50×50 anima ou permite pular (< 30s ou skip).
- [ ] Redraw é incremental (não reimprime a grade inteira a cada passo) — confirmar
  pelo código ou pela fluidez.

### 4.5 Perguntas que o avaliador pode fazer
1. **"Como você animou a geração sem duplicar a lógica?"** → algoritmos refatorados
   como geradores (`yield`); o renderer consome os passos; modo não-animado apenas
   itera sem renderizar.
2. **"Como evitou reimprimir a tela inteira?"** → posicionamento de cursor ANSI
   (redraw incremental da célula afetada).
3. **"A animação altera o labirinto gerado?"** → não; o resultado é idêntico ao modo
   não-animado (mesmo seed).
4. **"Como controla a velocidade?"** → `time.sleep(delay)` ajustável.

---

## 5. Testes de Regressão do Mandatório (após bônus)

**Crítico:** os bônus **não podem** ter quebrado o mandatório. Re-rode:

- [ ] `make lint` limpo.
- [ ] Modo `PERFECT=True` → `PERFECT maze` no analisador.
- [ ] Modo `PERFECT=False` (sem braiding) → `Pac-Man-USABLE`.
- [ ] Reprodutibilidade (mesmo seed → idêntico).
- [ ] Tratamento de erros (2–3 casos).
- [ ] Pacote `.whl` ainda instala em virtualenv limpo.
- [ ] README atualizado com os bônus.

---

## 6. Roteiro da Defesa — Parte Bônus (sugestão de ordem)

Após concluir o roteiro mandatório (`TESTE_DEFESA_MANDATORIO.md` seção 10):

1. **Braided:** gere um labirinto `PERFECT=False` braided e rode
   `maze_analyzer.py --max-dead-ends 0` → mostre `bonus-grade`.
2. **Múltiplos algoritmos:** mostre a troca via config e via UI; gere com cada algoritmo
   e valide no analisador.
3. **Animação:** acione a animação, mostre os controles (pausa, velocidade, skip).
4. **Comparação:** se possível, mostre lado a lado (ou em sequência) labirintos gerados
   por algoritmos diferentes, destacando as diferenças visuais.
5. **Extras (se houver):** exportação de imagem, solver animado, etc.

---

## 7. Modificações ao Vivo Plausíveis (bônus)

O avaliador pode pedir pequenas modificações relacionadas aos bônus:

- [ ] **Adicionar um novo algoritmo** (ex.: Eller's) — ter a interface Strategy pronta
  facilita.
- [ ] **Mudar a cor da animação** por etapa.
- [ ] **Adicionar uma tecla de atalho** nova (ex.: alternar entre algoritmos com setas).
- [ ] **Modificar o critério de braiding** (ex.: permitir N dead-ends configurável).
- [ ] **Exportar o labirinto animado** como GIF/sequência de frames.
- [ ] **Adicionar um novo padrão** além do "42" (ex.: "AI").

**Estratégia:** mantenha a arquitetura extensível (Strategy, callbacks) para que
adições sejam rápidas.

---

## 8. Critérios de Falha dos Bônus

Os bônus **não** devem prejudicar a nota do mandatório. Fique atento:

- ❌ Braided **não atinge** `real == 0` (falha no `--max-dead-ends 0`).
- ❌ Braiding **quebra** a coerência das paredes ou cria áreas 3×3.
- ❌ Algoritmo adicional **não gera** labirinto perfeito válido.
- ❌ Animação **altera** o labirinto final (diferente do modo não-animado).
- ❌ Animação é tão lenta que trava o programa (sem opção de skip).
- ❌ Bônus introduziu **regressão** no mandatório (lint falha, modo perfeito quebra).
- ❌ **Não saber explicar** o Union-Find ou o algoritmo de Prim/Kruskal.

> **Regra de ouro:** se um bônus estiver instável, **desative-o** antes da defesa em vez
> de arriscar uma regressão. É melhor não ter o bônus do que perder pontos do
> mandatório por causa dele.

---

## 9. Checklist Final Pré-Defesa (Bônus)

- [ ] Braided: `--max-dead-ends 0` → `bonus-grade` em vários tamanhos.
- [ ] ≥ 2 algoritmos além do backtracker, todos válidos em ambos os modos.
- [ ] Reprodutibilidade por algoritmo confirmada.
- [ ] Animação funcional com controles (pausa/velocidade/skip).
- [ ] Animação produz labirinto idêntico ao modo não-animado (mesmo seed).
- [ ] Mandatório re-validado após bônus (sem regressão).
- [ ] README descreve os bônus implementados.
- [ ] Consegue explicar Union-Find, Prim, Kruskal, braiding.
- [ ] Praticou pelo menos 1 modificação ao vivo de bônus (seção 7).
