# Distribuição de Tarefas para 2 Pessoas (A-Maze-ing)

> Distribuição do trabalho entre **2 desenvolvedores** (Pessoa A e Pessoa B),
> otimizada para **paralelismo** (trabalho simultâneo com mínimas dependências) e
> **responsabilidade clara** (cada um "dona" de partes específicas para evitar
> conflitos de escrita). Baseada em `TAREFAS_MANDATORIO.md` e `TAREFAS_BONUS.md`.
>
> Termos técnicos em inglês; explicação em português.
>
> **Cada task tem o tempo estimado na frente do título** (intervalo em horas).
> Estimativas para trabalho **focado** (não incluem pausas). Com 2 pessoas em
> paralelo, o tempo de relógio é aproximadamente a metade do somatório (exceto nas
> integrações conjuntas).
>
> **Coordenação via Git/GitHub:** este documento assume o fluxo descrito em
> `GUIA_GIT_GITHUB.md` (branches por feature, PRs com revisão, Issues por task, CI com
> GitHub Actions, branch protection da `main`). **Leiam aquele guia antes de
> começar** — é o primeiro projeto em conjunto, e a coordenação via Git é
> fundamental para não quebrar a `main` e para dividir o trabalho sem conflitos.

---

## 0.0 Plano de MVP e Contingência (gestão de tempo)

> **Por que isto existe:** num projeto com deadline, é gestão de risco essencial.
> Sem uma hierarquia de entrega, a dupla corre o risco de gastar tempo no visual ou no
> "42" e **não entregar o modo jogável** — que é mandatório. Definam um **ponto de
> corte** e respeitem-no.

### Níveis de entrega (do mínimo ao completo)

| Nível | Conteúdo | Status |
|-------|----------|--------|
| **Nível 0 — mínimo para não zerar** | `PERFECT=True` funcionando + arquivo de saída válido + `maze_analyzer.py` passa + `a_maze_ing.py` + Makefile + README + LICENSE | Aprovável (mínimo) |
| **Nível 1 — aprovável sólido** | Nível 0 + `PERFECT=False` jogável (`Pac-Man-USABLE`) + visual ASCII com 3 interações + empacotamento `.whl` + lint limpo | Aprovável (recomendado) |
| **Nível 2 — completo** | Nível 1 + bônus (braided, múltiplos algoritmos, animação) | Diferencial |

### Pontos de corte (gatilhos de contingência)

| Quando (data/progresso) | Ação |
|--------------------------|------|
| **Dia 9 — modo jogável não passa no analisador** | **Congelar** visual, empacotamento e bônus. Focar 100% no modo jogável até passar. |
| **Dia 10 — lint não passa** | Parar novas features. Dedicação total a type hints, docstrings, flake8, mypy. |
| **Dia 11 — algo crítico ainda falha** | Reverter ao **Nível 0** confirmado e estabilizar. Bônus cancelados. |
| **Dia 12 (véspera da defesa)** | **Nenhum** código novo. Só revisão, ensaio da defesa e `make clean`. |

> **Regra de ouro:** é melhor entregar o **Nível 1 sólido** do que tentar o Nível 2 e
> quebrar o mandatório. O bônus **não** compensa falha no mandatório.

### Ordem de prioridade (se o tempo apertar)

1. `PERFECT=True` válido no analisador. *(inviolável)*
2. `PERFECT=False` jogável no analisador. *(mandatório)*
3. Tratamento de erros (sem crash). *(mandatório, fácil de perder ponto)*
4. Empacotamento `.whl` + LICENSE. *(mandatório)*
5. README completo. *(mandatório)*
6. Visual ASCII + 3 interações. *(mandatório)*
7. Lint limpo. *(mandatório)*
8. Bônus (nesta ordem: braided → múltiplos algoritmos → animação). *(opcional)*

---

## 0.1 Registro de Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **Modo `PERFECT=False` não atinge `loops >= 2`** | Alta | Alto | Após gerar base perfeita, remover paredes adicionais em pares não-adjacentes; validar com analisador após cada remoção. |
| **Braiding cria áreas 3×3 abertas** | Média | Alto | Função `_creates_open_area` simula a abertura e rejeita candidatos inválidos; tentar outro vizinho. |
| **Incoerência de paredes** (esquecer um lado no `remove_wall`) | Média | Fatal | `remove_wall` atualiza **ambos** os lados sempre; teste automatizado verifica `incoherent_cells == ()`. |
| **"42" cobre um canto ou o centro** | Média | Alto | Combinar **antes** a região do "42" (ex.: canto inferior direito); validar cantos/centro após posicionar. |
| **Lint falha no final** (type hints faltantes) | Alta | Médio | Adicionar type hints **desde o início**; rodar `make lint` localmente antes de todo commit. |
| **Pacote não instala em venv limpo** | Média | Alto | Testar o build **cedo** (Fase 9), não deixar para a véspera. |
| **Conflitos de merge no `generator.py`** | Média | Médio | Posse clara de arquivos (seção 2); Pessoa B usa a API pública de A, não edita a lógica interna. |
| **Animação altera o labirinto gerado** | Baixa | Médio | Validar com diff: animado vs não-animado (mesmo seed) deve ser idêntico. |
| **Não saber explicar o código na defesa** | Média | Fatal | Revisão por pares em todo PR; ensaio da defesa (Método 4); flashcards. |
| **Tempo acaba antes do Nível 1** | Média | Alto | Respeitar os pontos de corte (seção 0.0); priorizar mandatório sobre bônus. |

---

## 0. Estimativa Global de Tempo

### 0.1 Visão por bloco (2 pessoas, em paralelo)

| Bloco | Horas por pessoa | Tempo de relógio (paralelo) | Observação |
|-------|------------------|------------------------------|------------|
| **Estudo teórico** (com ensino cruzado) | 6–10h | 6–10h | Dividir temas + ensinar um ao outro |
| **Implementação mandatória** | 25–35h | 18–28h | Gargalo: integração + lint compartilhado |
| **Bônus** (opcional) | 8–13h | 6–10h | Após mandatório 100% |
| **Revisão + ensaio de defesa** | 3–5h | 3–5h | Conjunto |
| **TOTAL (mandatório)** | ~34–50h | ~27–43h | ~6–9 dias úteis part-time |
| **TOTAL (com bônus)** | ~42–63h | ~33–53h | ~8–11 dias úteis part-time |

> **Part-time** = ~4–5h/dia focado. Em dedicação full-time (~8h/dia), comprima para
> ~4–6 dias (mandatório) ou ~5–7 dias (com bônus).

### 0.2 Estudo teórico detalhado (dividir e ensinar)

| Tema | Horas | Quem estuda | Quem ensina |
|------|-------|-------------|------------|
| Teoria dos grafos (vértice, aresta, spanning tree, ciclo, BFS/DFS) | 3–5 | Pessoa A | A ensina B |
| Codificação hex de paredes + coerência + coords (x,y) | 1–2 | Pessoa B | B ensina A |
| Algoritmos de geração (backtracker, Prim, Kruskal) | 3–5 | Pessoa A | A ensina B |
| Union-Find (DSU) — só se Kruskal | 1–2 | Pessoa A | A ensina B |
| Empacotamento Python (pyproject.toml, build) | 1–2 | Pessoa B | B ensina A |
| flake8/mypy/type hints/docstrings | 1–2 | Pessoa B | B ensina A |
| **Subtotal (com ensino cruzado)** | **6–10h** | — | — |

> **Método:** cada um estuda sozinho (~3–4h), depois ensina ao outro em sessões de
> 30–45 min por tema. O "aluno" faz perguntas que o avaliador fará (use
> `TESTE_DEFESA_MANDATORIO.md` seção 11).

---

## 1. Princípios da Distribuição

1. **Paralelismo máximo:** as fases iniciais (setup, config, núcleo) são divididas para
   que ambas as pessoas trabalhem simultaneamente desde o dia 1.
2. **Posse clara de arquivos:** cada pessoa é "dona" de módulos específicos para evitar
   conflitos de merge. Quando ambos precisam editar o mesmo arquivo, combinam via
   *feature branches*.
3. **Dependências explícitas:** marcadas com "⏳ depende de". A pessoa B não começa uma
   tarefa dependente antes de A concluir a prévia.
4. **Integração contínua:** merges frequentes para a `main` (ou branch compartilhada),
   rodando `make lint` antes de cada merge.
5. **Revisão por pares:** toda tarefa concluída é revisada pela outra pessoa antes do
   merge (atende à regra do subject Cap. II sobre *peer review*).

---

## 2. Visão Geral das Responsabilidades

| Pessoa | Domínio principal | Arquivos "dona" |
|--------|-------------------|-----------------|
| **A — Núcleo & Algoritmos** | Geração, estrutura de dados, algoritmos, braiding, múltiplos algoritmos | `mazegen/generator.py`, `mazegen/dsu.py` (Kruskal), algoritmos |
| **B — I/O, Visual & Empacotamento** | Config, saída, visual, empacotamento, docs, Makefile | `a_maze_ing.py`, `mazegen/config.py`, `mazegen/renderer_ascii.py`, `pyproject.toml`, `README.md`, `Makefile`, `LICENSE.md` |

> **Nota:** ambos contribuem para testes e revisão. A divisão acima é a **posse
> primária**, não exclusividade absoluta.

---

## 3. Cronograma Detalhado (por fase, com tempos por task)

### Fase 0 — Setup (Dia 1, em paralelo) — ~3–5h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **A** | T0.1 (parcial) — Estrutura de diretórios | 0.5–1h | Criar `mazegen/`, `tests/`, `__init__.py`. |
| **B** | T0.1 (parcial) + T0.2 + T0.3 — Git/venv/Makefile | 2–3h | `git init`, `.gitignore`, virtualenv, `Makefile`, instalar ferramentas. |
| **Conjunto** | Revisão + merge do setup | 0.5–1h | Confirmar `make lint` roda (mesmo que vazio). |

**Entrega:** repositório base pronto, ambos com o ambiente funcional.

---

### Fase 1 — Parser de Config (Dia 1–2) — ~3–5h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **B** (dona) | T1.1 — Modelo `MazeConfig` | 1–2h | `mazegen/config.py`: dataclass + `parse_config`. |
| **B** | T1.2 — Validação semântica | 1–1.5h | Limites, `entry != exit`, mensagens claras. |
| **B** | T1.3 — `config.txt` padrão | 0.5h | Arquivo na raiz. |
| **A** | Revisão da interface | 0.5–1h | Garantir que `MazeConfig` atende ao gerador. |

**Entrega:** `parse_config("config.txt")` funciona e valida entradas.

---

### Fase 2 — Núcleo do Gerador (Dia 2–3, em paralelo) — ~4–6h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **A** (dona) | T2.1 — `Direction` (IntFlag) | 0.5–1h | Bits N/E/S/W batendo com o analisador. |
| **A** | T2.2 — Classe `MazeGenerator` | 1–1.5h | Construtor, `grid` inicializada com `ALL_WALLS`. |
| **A** | T2.3 — Helpers de parede (coerência) | 1.5–2h | `remove_wall` atualiza **ambos** os lados. |
| **B** | T6.2 (esboço) — Serialização | 1–1.5h | `write_output` com grade mock para testar. |

**Entrega:** `MazeGenerator` instanciável; `remove_wall` garante coerência.

---

### Fase 3 — Algoritmo de Geração Perfeito (Dia 3–4) — ~5–8h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **A** (dona) | T3.1 — Recursive Backtracker | 3–5h | Stack, visitados, backtracking, respeita obstáculos. |
| **A** | T3.2 — Conectividade total | 1–2h | BFS pós-geração; reconectar componentes isolados. |
| **B** | T6.1 (paralelo) — BFS caminho mais curto | 2–3h | Desenvolver/testar com grade mock. |

**Entrega:** backtracker gera labirinto perfeito; BFS funciona.

---

### Fase 4 — Padrão "42" (Dia 4) — ~4–6h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **A** (dona) | T4.1 — Bitmap do "42" | 1–1.5h | Matrizes de pontos para "4" e "2". |
| **A** | T4.2 — Posicionamento na grade | 1–2h | Região fixa; mensagem de erro se grade pequena. |
| **A** | T4.3 — Integração à geração | 1–1.5h | Marcar obstáculos antes do algoritmo. |
| **B** | Revisão | 0.5–1h | Validar coerência e conectividade. |

**Entrega:** "42" aparece como células `F` isoladas; mensagem de erro se grade pequena.

---

### Fase 5 — Modo Jogável (Dia 5) — ~6–10h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **A** (dona) | T5.1 — Base perfeita | 0.5h | Reutilizar backtracker. |
| **A** | T5.3 — Criar loops (≥2) | 2–3h | Remover paredes adicionais sem áreas 3×3. |
| **A** | T5.4 — Controlar dead-ends (≤2) | 1.5–2.5h | Abrir paredes de dead-ends reais. |
| **B** | T5.2 — Cantos e centro abertos | 1–2h | Coordenar com A sobre o "42". |
| **Conjunto** | T5.5 — Evitar áreas 3×3 | 1–2h | Função de checagem pós-geração. |

**Entrega:** `PERFECT=False` → `Pac-Man-USABLE` no analisador.

---

### Fase 6 — Caminho Mais Curto e Saída (Dia 5–6) — ~4–6h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **B** (dona) | T6.2 — Serialização final | 1–1.5h | Linhas hex + footer (entry, exit, caminho). |
| **B** | T6.3 — Validar com analisador | 0.5–1h | Ambos os modos passam. |
| **A** | Integração do `shortest_path()` | 1–1.5h | Conectar BFS (T6.1) ao `MazeGenerator` real. |
| **Conjunto** | Teste de reprodutibilidade | 0.5–1h | Mesmo seed → diff idêntico. |

**Entrega:** `maze.txt` gerado e validado pelo analisador para ambos os modos.

---

### Fase 7 — Entry Point (Dia 6) — ~3–5h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **B** (dona) | T7.1 — `main` | 1.5–2.5h | `a_maze_ing.py`, códigos de saída. |
| **B** | T7.2 — Tratamento robusto de erros | 1–2h | `try/except`, `KeyboardInterrupt`, sem traceback. |
| **A** | Revisão | 0.5–1h | Confirmar todos os caminhos de erro tratados. |

**Entrega:** `python3 a_maze_ing.py config.txt` funciona de ponta a ponta.

---

### Fase 8 — Representação Visual (Dia 7–8, em paralelo) — ~5–8h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **B** (dona) | T8.1 — Renderer ASCII | 2–3h | Paredes, entry/exit, caminho, cores ANSI. |
| **B** | T8.2 — Loop de interação | 2–3h | Re-gerar, caminho, cores; tecla sem enter. |
| **A** | T8.3 (opcional) — MLX | 2–4h | Só se ASCII 100% e sobrar tempo. |

**Entrega:** visual ASCII com 3 interações obrigatórias funcionando.

---

### Fase 9 — Reusabilidade e Empacotamento (Dia 8–9) — ~4–6h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **B** (dona) | T9.2 — `pyproject.toml` | 0.5–1h | Configuração do build. |
| **B** | T9.3 — Build do pacote | 1–1.5h | `python -m build`; `.whl` na raiz; teste em venv limpo. |
| **B** | T9.4 — `LICENSE.md` (MIT) | 0.5h | Texto padrão MIT. |
| **A** | T9.1 — Módulo standalone | 1.5–2h | Docstrings, exemplo de uso, métodos públicos. |

**Entrega:** pacote `mazegen-*.whl` na raiz; instala em virtualenv limpo; `LICENSE.md`.

---

### Fase 10 — Documentação (Dia 9) — ~4–6h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **B** (dona) | T10.1 — `README.md` completo | 2–3h | Todos os campos obrigatórios do subject. |
| **A** | T10.2 — Docs do módulo reutilizável | 1–2h | Para incluir no README. |
| **Conjunto** | Revisão cruzada | 0.5–1h | Garantir coerência e completude. |

**Entrega:** README completo; documentação do módulo duplicada no README.

---

### Fase 11 — Qualidade e Lint (Dia 10) — ~5–8h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **Conjunto** | T11.1 — Type hints + docstrings | 2–3h | Revisão cruzada; cada um corrige seus módulos. |
| **Conjunto** | T11.2 — flake8 limpo | 1–1.5h | Linhas longas, imports, espaços. |
| **Conjunto** | T11.3 — mypy (flags obrigatórias) | 1.5–2.5h | `make lint` sem erros. |
| **Conjunto** | T11.4 — (recomendado) `lint-strict` | 1–2h | `mypy . --strict`. |

**Entrega:** `make lint` e `make lint-strict` limpos.

---

### Fase 12 — Testes (Dia 10–11, em paralelo) — ~5–8h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **A** | T12.1 (núcleo) — Testes do gerador | 2.5–4h | Coerência, perfeito, conectividade, "42", seed. |
| **B** | T12.1 (I/O) + T12.2 — Config/serialização + regressão | 2.5–4h | Round-trip; script com o analisador. |

**Entrega:** `pytest` passa; cobre edge cases; regressão do analisador 100%.

---

### Fase 13 — Revisão Final e Defesa (Dia 11–12) — ~3–5h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **Conjunto** | T13.1 — Checklist de conceitos | 0.5–1h | `ESTUDO_MANDATORIO.md` seção 12. |
| **Conjunto** | T13.2 — Limpeza do repositório | 0.5h | `make clean`; só arquivos necessários. |
| **Conjunto** | T13.3 — Commit e push | 0.5h | Repositório remoto atualizado. |
| **Conjunto** | T13.4 — Ensaio da defesa | 1.5–3h | Usar `TESTE_DEFESA_MANDATORIO.md`; simular modificação ao vivo. |

**Entrega:** projeto pronto para defesa.

---

## 4. Bônus — Distribuição (após mandatório 100%) — ~15–25h

### Bônus 1 — Braided (Pessoa A, dona) — ~5–8h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **A** | B1.1 — Detecção de dead-ends | 1–1.5h | Real vs enclosed. |
| **A** | B1.2 — Algoritmo de braiding | 2–3h | Abrir paredes sem áreas 3×3. |
| **A** | B1.3 — Integração ao `PERFECT=False` | 1–1.5h | Manter loops ≥ 2 e cantos/centro. |
| **A** | B1.4 — Evitar áreas 3×3 | 1–1.5h | Função `_creates_open_area`. |
| **B** | B1.5 — Testes de regressão | 1–1.5h | Vários tamanhos/seeds com `--max-dead-ends 0`. |

### Bônus 2 — Múltiplos Algoritmos (Pessoa A, dona) — ~6–10h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **A** | B2.1 — Padrão Strategy | 1–1.5h | Registro `ALGORITHMS`. |
| **A** | B2.2 — Prim | 1.5–2.5h | Fronteiras. |
| **A** | B2.3 — Kruskal + DSU | 2–3h | Union-Find com path compression. |
| **A** | B2.4 — (opcional) algoritmo extra | 1.5–3h | Eller's / Wilson's. |
| **B** | B2.5 — Seleção via config/UI | 1–1.5h | `ALGORITHM=` + tecla no visual. |
| **B** | B2.6 — Reprodutibilidade | 0.5–1h | Mesmo seed + algoritmo → idêntico. |
| **B** | B2.7 — Testes por algoritmo | 1–1.5h | Válido em ambos os modos. |

### Bônus 3 — Animação (Pessoa B, dona) — ~4–7h

| Pessoa | Task | Tempo | Detalhe |
|--------|------|-------|---------|
| **B** | B3.1 — Refatorar para `yield` | 1–1.5h | Algoritmos emitem passos. |
| **B** | B3.2 — Renderer animado ASCII | 1.5–2.5h | Redraw incremental via cursor ANSI. |
| **B** | B3.4 — Desempenho | 0.5–1h | Batching/skip para labirintos grandes. |
| **B** | B3.5 — Menu de interações | 0.5–1h | Tecla `g` para animar. |
| **A** | B3.3 — Animação MLX (se aplicável) | 1–2h | Só se MLX já integrado. |

> **Coordenação B3.1:** a refatoração para `yield` afeta os algoritmos de A. Façam num
> branch compartilhado: A adapta os algoritmos, B adapta o renderer.

---

## 5. Linha do Tempo Resumida (estimativa de ~12 dias part-time)

```
Dia  1 (4–5h): Setup (A+B) + início do config (B) + estudo cruzado
Dia  2 (4–5h): Config (B) + núcleo/Direction (A) + estudo cruzado
Dia  3 (4–5h): Núcleo (A) + BFS caminho (B)
Dia  4 (4–5h): Backtracker (A) + "42" (A) + serialização esboço (B)
Dia  5 (4–5h): Modo jogável (A) + cantos/centro (B) + serialização final (B)
Dia  6 (4–5h): Entry point (B) + integração caminho (A)
Dia  7 (4–5h): Visual ASCII (B) + (opcional MLX - A)
Dia  8 (4–5h): Visual interações (B) + empacotamento (B) + módulo standalone (A)
Dia  9 (4–5h): README (B) + docs módulo (A) + LICENSE (B)
Dia 10 (4–5h): Lint (A+B) + testes (A+B em paralelo)
Dia 11 (4–5h): Testes finais + revisão (A+B)
Dia 12 (3–4h): Ensaio da defesa (A+B)
--- Bônus (se tempo permitir) ---
Dia 13 (4–5h): Braided (A) + testes (B)
Dia 14 (4–5h): Múltiplos algoritmos (A) + UI/testes (B)
Dia 15 (4–5h): Animação (B) + MLX (A)
```

> **Ajuste:** em dedicação full-time (~8h/dia), comprima para ~6–7 dias (mandatório) ou
> ~8–9 dias (com bônus).

---

## 6. Coordenação e Ferramentas

- **Controle de versão:** Git com branches por feature; merges via *pull request*
  revisados pela outra pessoa. **Fluxo completo, passo a passo (para iniciantes):
  ver `GUIA_GIT_GITHUB.md`** — inclui setup, branches, commits, PRs, Issues, GitHub
  Actions (CI automático com lint + testes) e proteção de branch da `main`.
- **Convenções de Git (resumo — detalhes no guia):**
  - Branches: `<tipo>/<descrição>-<nº-issue>` (ex.: `feat/backtracker-5`).
  - Commits: Conventional Commits (ex.: `feat: adiciona parser de config`).
  - PRs: descrição com "O que faz" + "Como testar" + `Closes #<n>`.
  - **Nenhum merge na `main` sem aprovação + CI verde** (branch protection ativa).
- **Issues:** uma issue por task do `TAREFAS_MANDATORIO.md`; vinculadas a PRs e
  branches; quadro **Projects** (Kanban) opcional para visão geral.
- **CI (GitHub Actions):** `.github/workflows/ci.yml` roda `flake8`, `mypy` (flags
  obrigatórias) e `pytest` a cada PR. PR vermelho **não** pode ser mesclado.
- **Comunicação:** sincronização curta diária sobre o que cada um fará e onde pode haver
  conflito de arquivos.
- **Integração contínua local:** rodar `make lint` antes de todo commit; rodar testes
  antes de marcar tarefa como concluída.
- **Registro:** manter o `README.md` (seção de gestão) atualizado com o planejamento
  previsto vs. real, papéis e ferramentas — é exigência do subject.

---

## 7. Divisão de Papéis (para o README)

Sugestão de descrição de papéis para a seção de gestão do `README.md`:

- **Pessoa A — Engenheira de Algoritmos:** responsável pela `MazeGenerator`, estrutura
  de dados de paredes, algoritmos de geração (backtracker, Prim, Kruskal), braiding,
  Union-Find, e a coerência/conectividade do labirinto.
- **Pessoa B — Engenheira de I/O e Interface:** responsável pelo parser de config,
  serialização do arquivo de saída, entry point, representação visual (ASCII/MLX),
  empacotamento (`pip`/`pyproject.toml`), `LICENSE.md`, `README.md` e `Makefile`.

> Ambos contribuem com testes, revisão de código e documentação.

---

## 8. Pontos de Atenção (riscos de coordenação)

1. **Interface `MazeConfig` ↔ `MazeGenerator`:** A precisa saber exatamente quais campos
   o config fornece. Definam o `dataclass` **juntos** no Dia 1 antes de divergir.
2. **Posicionamento do "42" vs. cantos/centro:** A posiciona o "42"; B garante
   cantos/centro. Se o "42" cobrir um canto, conflito. Combinem a região do "42"
   **antes** (ex.: sempre canto inferior direito).
3. **Refatoração para `yield` (B3.1):** afeta os algoritmos de A. Façam num branch
   conjunto; A adapta os algoritmos, B adapta o renderer.
4. **Mudanças no `generator.py` por B (serialização, UI):** B deve preferir **usar** a
   API pública de A (`gen.grid`, `gen.shortest_path()`) em vez de editar a lógica
   interna. Se precisar mexer, abra PR para A revisar.
5. **Lint compartilhado:** como `make lint` roda sobre todo o repo, um erro de A pode
   bloquear o merge de B. Rodem lint localmente antes de commitar.
6. **Gargalo do modo jogável (Fase 5):** é a fase mais complexa; reservem tempo extra e
   trabalhem juntos na integração se travar.
