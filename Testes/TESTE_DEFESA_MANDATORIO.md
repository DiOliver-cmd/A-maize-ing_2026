# Guia de Teste e Defesa — Parte Mandatória (A-Maze-ing)

> Roteiro prático para **testar o projeto antes da defesa** e para **conduzir a defesa**
> (peer-evaluation). Pensado no que pode ser **avaliado ou solicitado** pelo avaliador,
> com base no subject (Capítulos III–IX). Termos técnicos em inglês; explicação em
> português.
>
> Use este roteiro como **ensaio**: simule cada item antes do dia da defesa.

---

## 1. Preparação do Ambiente de Defesa

Antes de o avaliador chegar, tenha pronto:

- [ ] Repositório Git clonado/limpo na máquina de defesa.
- [ ] `python3 --version` ≥ 3.10 visível.
- [ ] `virtualenv` criado e ativado.
- [ ] Dependências instaláveis via `make install`.
- [ ] `config.txt` padrão na raiz.
- [ ] `maze_analyzer.py` disponível (fornecido pelo subject).
- [ ] Terminal com fonte monoespaçada legível (para a renderização ASCII).
- [ ] (Se usar MLX) ambiente gráfico testado e funcionando.

---

## 2. Checklist de Validação Automatizada (rodar antes da defesa)

### 2.1 Lint e tipos
- [ ] `make lint` → **zero erros** (flake8 + mypy com as flags obrigatórias).
- [ ] (Recomendado) `make lint-strict` → zero erros.
- **Comando exato esperado pelo subject (regra `lint` do Makefile):**
  ```
  flake8 .
  mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
         --disallow-untyped-defs --check-untyped-defs
  ```
- **O que o avaliador pode pedir:** "rode o lint" — deve passar sem nenhuma saída.

### 2.2 Build do pacote reutilizável
- [ ] Em um **virtualenv limpo**: `python -m build` gera `dist/mazegen-*.whl` e
  `dist/mazegen-*.tar.gz`.
- [ ] `pip install ./dist/mazegen-*.whl` funciona.
- [ ] `python -c "from mazegen import MazeGenerator; print('ok')"` funciona.
- [ ] O `.whl` (ou `.tar.gz`) está na **raiz** do repositório.
- **O que o avaliador pode pedir:** "reconstrua o pacote a partir dos fontes em um
  virtualenv" — é exigência explícita do subject (Capítulo VI).

### 2.3 Makefile
- [ ] `make install` instala dependências.
- [ ] `make run` executa `python3 a_maze_ing.py config.txt`.
- [ ] `make debug` roda com `pdb`.
- [ ] `make clean` remove caches.
- [ ] `make lint` (e `make lint-strict` se existir).
- **O que o avaliador pode pedir:** "mostre o Makefile" e "rode cada regra".

---

## 3. Testes Funcionais — Modo `PERFECT=True`

### 3.1 Geração básica
- [ ] `python3 a_maze_ing.py config.txt` gera `maze.txt` sem erro.
- [ ] O arquivo tem `HEIGHT` linhas de dígitos hex, uma linha vazia, e 3 linhas
  (entry, exit, caminho).
- [ ] Todas as linhas terminam com `\n`.

### 3.2 Validação com o analisador
- [ ] `python3 maze_analyzer.py maze.txt` → veredito **`PERFECT maze`**.
- [ ] `Wall coherence: OK`.
- [ ] `Reachable region` = total de células não-"42".
- [ ] `disconnected_corridors == 0`.
- [ ] `Independent loops: 0`.
- [ ] `Dead-ends: 0 real + N enclosed` (enclosed tolerado).
- [ ] `Corners + centre: all reachable` (não se aplica estritamente ao perfeito, mas
  não deve haver erro de coerência).

### 3.3 Reprodutibilidade
- [ ] Rodar duas vezes com o **mesmo seed** → arquivos **idênticos** (diff vazio).
- [ ] Trocar o seed → labirinto diferente.
- **Comando:** `diff <(python3 a_maze_ing.py config.txt && cat maze.txt) ...` ou
  simplesmente gerar, copiar, gerar de novo e comparar.

### 3.4 Caminho mais curto
- [ ] O caminho no arquivo começa na entry e termina na exit (validar manualmente ou
  com um script que simula os passos `N/E/S/W`).
- [ ] O caminho é **válido** (não atravessa paredes).
- [ ] O caminho é o **mais curto** (comparar com uma BFS independente).

---

## 4. Testes Funcionais — Modo `PERFECT=False` (Pac-Man)

### 4.1 Geração
- [ ] Trocar `PERFECT=True` → `PERFECT=False` no config; gerar.
- [ ] `maze_analyzer.py maze.txt` → veredito **`Pac-Man-USABLE`**.

### 4.2 Critérios do tabuleiro jogável
- [ ] `Independent loops >= 2` (no mínimo 2 rotas).
- [ ] `Corners + centre: all reachable`.
- [ ] `Dead-ends: real <= 2` (com `--max-dead-ends 2`).
- [ ] `disconnected_corridors == 0`.
- [ ] `Wall coherence: OK`.

### 4.3 Inspeção visual
- [ ] Não há **área 3×3 totalmente aberta** (corredores largura ≤ 2).
- [ ] Os 4 cantos e o centro são corredores.

---

## 5. Testes do Padrão "42"

- [ ] No modo visual, o "42" é **visível** (células totalmente fechadas formando os
  dígitos).
- [ ] As células do "42" são `F` (15) no arquivo de saída.
- [ ] `maze_analyzer.py` **não** conta as células "42" como `disconnected_corridors`
  (elas são `is_fully_closed`).
- [ ] **Caso pequeno:** configurar `WIDTH=5 HEIGHT=5` (ou tamanho insuficiente) → o
  programa **imprime mensagem de erro no console** e **não desenha** o "42", mas ainda
  gera um labirinto válido.
- **O que o avaliador pode pedir:** "reduza o tamanho do labirinto e mostre o que
  acontece com o 42".

---

## 6. Testes de Representação Visual

### 6.1 Renderização
- [ ] Labirinto exibido no terminal (ou janela MLX) é **legível**.
- [ ] Paredes, entry (`E`), exit (`X`) e caminho visíveis.

### 6.2 Interações obrigatórias
- [ ] **Re-gerar** (tecla `r` ou similar) → novo labirinto exibido.
- [ ] **Mostrar/Ocultar caminho** (tecla `p`) → caminho aparece/desaparece.
- [ ] **Mudar cor das paredes** (tecla `c`) → cores mudam.
- [ ] (Opcional) **Cor do "42"** (tecla `4`) → funciona.
- **O que o avaliador pode pedir:** "mostre cada interação".

---

## 7. Testes de Tratamento de Erros (robustez)

O subject é **categórico**: o programa **nunca** pode crashar com exceção não tratada.
Teste **cada** caso e confirme mensagem clara + código de saída ≠ 0:

- [ ] Arquivo de config **inexistente**: `python3 a_maze_ing.py nao_existe.txt`.
- [ ] **Sem argumento**: `python3 a_maze_ing.py`.
- [ ] **Argumento demais**: `python3 a_maze_ing.py a b`.
- [ ] Config com **chave mandatória ausente** (remover `WIDTH=`).
- [ ] Config com **valor inválido**: `WIDTH=abc`, `PERFECT=maybe`, `ENTRY=x,y`.
- [ ] Config com `ENTRY`/`EXIT` **fora dos limites**: `ENTRY=100,100`.
- [ ] Config com `ENTRY == EXIT`.
- [ ] `WIDTH=0` ou `HEIGHT=0`.
- [ ] Arquivo de saída em **diretório sem permissão** (se aplicável).
- [ ] **Ctrl+C** durante a execução → sai limpo (exit 130), sem traceback feio.
- **O que o avaliador pode pedir:** qualquer um destes. É um ponto **fácil de perder**.

---

## 8. Testes de Reusabilidade do Módulo

- [ ] Em um **diretório externo**, com o pacote instalado via `pip`:
  ```python
  from mazegen import MazeGenerator
  gen = MazeGenerator(width=20, height=15, entry=(0,0), exit=(19,14),
                      perfect=True, seed=42)
  gen.generate()
  grid = gen.grid
  path = gen.shortest_path()
  print(len(path))
  ```
- [ ] Funciona sem importar nada do projeto principal.
- [ ] A documentação curta (no módulo e no README) cobre: instanciar, parâmetros,
  acessar estrutura e solução.
- **O que o avaliador pode pedir:** "use seu módulo em um script separado".

---

## 9. Testes de Documentação

- [ ] `README.md`:
  - [ ] Primeira linha itálica com logins (formato exato do subject).
  - [ ] Seção **Description**.
  - [ ] Seção **Instructions** (instalação/execução).
  - [ ] Seção **Resources** (referências + **uso de IA** descrito).
  - [ ] Formato do config documentado.
  - [ ] Algoritmo escolhido + **justificativa**.
  - [ ] Parte reutilizável + como usar.
  - [ ] Gestão de equipe (papéis, planejamento, o que funcionou/melhorar, ferramentas).
- [ ] `LICENSE.md` na raiz, permissiva (MIT recomendada).
- **O que o avaliador pode pedir:** "abra o README e explique cada seção".

---

## 10. Roteiro da Defesa (passo a passo sugerido)

1. **Apresentação (1–2 min):** o que é o projeto, objetivo.
2. **Estrutura do repo:** mostre a árvore de arquivos.
3. **Makefile:** mostre e rode `make install`, `make lint`.
4. **Config:** mostre o `config.txt`, explique cada chave.
5. **Execução mandatória:** `make run` → gere `maze.txt` (modo perfeito).
6. **Analisador:** rode `maze_analyzer.py maze.txt` → mostre `PERFECT maze`.
7. **Arquivo de saída:** abra `maze.txt`, explique a codificação hex (bits N/E/S/W),
   o footer (entry, exit, caminho).
8. **Visual:** mostre a renderização ASCII e **cada interação** (re-gerar, caminho,
   cores).
9. **"42":** aponte o padrão no visual e as células `F` no arquivo.
10. **Modo jogável:** troque `PERFECT=False`, gere, rode o analisador → `Pac-Man-USABLE`.
11. **Reusabilidade:** instale o `.whl` em virtualenv limpo, rode um script externo.
12. **Erros:** demonstre 2–3 casos de erro (config inválido) com mensagem clara.
13. **README/LICENSE:** mostre e explique.
14. **Bônus (se houver):** veja `TESTE_DEFESA_BONUS.md`.

---

## 11. Perguntas Frequentes que o Avaliador Pode Fazer

Prepare **respostas** para cada uma (saiba explicar, não só apontar o código):

1. **"Por que escolheu esse algoritmo de geração?"** → justifique (simplicidade,
   propriedades do labirinto gerado, desempenho).
2. **"Como garante que o labirinto é perfeito?"** → spanning tree, `loops == 0`,
   validação pelo analisador.
3. **"Como funciona a codificação hex das paredes?"** → bits N/E/S/W, fechado=1,
   exemplo numérico.
4. **"Como garante a coerência entre vizinhos?"** → `remove_wall` atualiza ambos os
   lados simultaneamente.
5. **"Qual a diferença entre os dois modos?"** → perfeito (1 caminho, 0 loops) vs
   jogável (loops ≥ 2, cantos/centro, dead-ends raros).
6. **"Como encontra o caminho mais curto?"** → BFS, reconstrução via `parent`.
7. **"Como o '42' é desenhado e por que não quebra a conectividade?"** → células `F`
   isoladas, tratadas como obstáculos, toleradas pelo analisador.
8. **"Como garante reprodutibilidade?"** → `random.Random(seed)` dedicado.
9. **"O que acontece se o labirinto for pequeno demais para o '42'?"** → mensagem de
   erro no console, padrão omitido.
10. **"Como o módulo é reutilizável?"** → classe standalone, empacotada, instalável
    via pip, com documentação.
11. **"Que licença escolheu e por quê?"** → MIT, permissiva, permite reuso.
12. **"Como usou IA?"** → descreva tarefas específicas (pesquisa, revisão), enfatize
    que **entende e se responsabiliza** por todo o código (regra do subject Cap. II).

---

## 12. Modificação ao Vivo (preparar-se)

O subject (Capítulo IX) prevê que o avaliador pode pedir uma **pequena modificação**
durante a defesa. Exemplos plausíveis — **pratique** cada um:

- [ ] **Mudar a cor padrão das paredes.**
- [ ] **Adicionar uma nova interação de teclado** (ex.: salvar o labirinto em PNG).
- [ ] **Modificar o formato do "42"** (ex.: trocar por outro número/símbolo).
- [ ] **Adicionar uma chave de config nova** (ex.: `BORDER_THICKNESS=2`) e usá-la.
- [ ] **Mudar o algoritmo padrão** no config.
- [ ] **Imprimir informações extras no console** (ex.: tamanho do caminho, número de
  loops).
- [ ] **Ajustar a estrutura de dados** para armazenar um novo atributo por célula.
- [ ] **Mudar o marcador de entry/exit** no visual.

**Estratégia:** mantenha o código **limpo e modular** para que mudanças pequenas sejam
rápidas. Conheça **cada função** para saber onde mexer.

---

## 13. Critérios de Falha (o que reprova)

Fique atento — qualquer um destes pode reprovar:

- ❌ Programa **crasha** com exceção não tratada durante a defesa.
- ❌ `make lint` **falha** (flake8 ou mypy com erros).
- ❌ Labirinto **incoerente** (paredes divergentes entre vizinhos).
- ❌ Modo perfeito **não é perfeito** (`loops != 0`).
- ❌ Modo jogável **não é jogável** (`loops < 2`, cantos/centro inacessíveis, dead-ends
  demais, corredores desconectados).
- ❌ "42" **ausente sem mensagem de erro** (quando o tamanho permitir).
- ❌ **Sem reprodutibilidade** por seed.
- ❌ **Pacote não instalável** / não reconstruível.
- ❌ **Sem LICENSE.md** ou licença não permissiva.
- ❌ **README incompleto** (campos obrigatórios ausentes).
- ❌ **Não saber explicar** o próprio código (regra do Cap. II — usar IA sem entender
  **reprova**).
- ❌ Nome do arquivo principal errado (deve ser `a_maze_ing.py`).

---

## 14. Checklist Final Pré-Defesa

- [ ] `make lint` limpo.
- [ ] `make lint-strict` limpo (recomendado).
- [ ] Ambos os modos passam no `maze_analyzer.py`.
- [ ] Reprodutibilidade confirmada (diff idêntico com mesmo seed).
- [ ] "42" visível + mensagem de erro quando grade pequena.
- [ ] Visual com 3 interações obrigatórias.
- [ ] Tratamento de erros testado (≥ 5 casos).
- [ ] Pacote `.whl` na raiz + reconstrução em virtualenv limpo.
- [ ] README completo + LICENSE permissiva.
- [ ] Consegue explicar cada item da seção 11.
- [ ] Praticou pelo menos 2 modificações ao vivo da seção 12.
