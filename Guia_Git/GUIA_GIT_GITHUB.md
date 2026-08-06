# Guia Git & GitHub — A-Maze-ing (para iniciantes, passo a passo)

> Guia completo para vocês **coordenarem o projeto via Git/GitHub**, considerando que é
> o **primeiro projeto em conjunto** e que **nunca trabalharam com branches antes**.
> Cada passo é detalhado, com comandos exatos e o que esperar.
>
> Termos técnicos em inglês (git, branch, commit, pull request, etc.); explicação em
> português.
>
> **Pré-requisito:** contas no GitHub criadas; Git instalado (`git --version`).

---

## Sumário

1. [Conceitos essenciais (leia primeiro)](#1-conceitos-essenciais)
2. [Setup inicial do repositório](#2-setup-inicial)
3. [Fluxo de trabalho diário (o "Git Flow" simplificado)](#3-fluxo-diário)
4. [Branches: criar, trocar, mesclar](#4-branches)
5. [Commits: boas práticas](#5-commits)
6. [Sincronização: pull, push, conflitos](#6-sincronização)
7. [Pull Requests (PRs): revisão antes do merge](#7-pull-requests)
8. [Issues: organizar tarefas](#8-issues)
9. [GitHub Actions: CI automático (lint + testes)](#9-github-actions)
10. [Proteção de branch: impedir merges que quebram](#10-proteção-de-branch)
11. [Convenções do projeto A-Maze-ing](#11-convenções)
12. [Cenários comuns (resolução de problemas)](#12-cenários-comuns)
13. [Checklist final](#13-checklist)

---

## 1. Conceitos essenciais

Antes de qualquer comando, entendam estes 5 conceitos:

### 1.1 Repositório (repo)
A "pasta do projeto" versionada. Pode ser **local** (na sua máquina) ou **remoto**
(no GitHub). O remoto é a "fonte da verdade" compartilhada entre vocês.

### 1.2 Commit
Um **snapshot** (foto) do seu código em um momento. Cada commit tem:
- Uma mensagem descritiva.
- Um identificador único (hash).
- O autor e a data.

> Pense num commit como "salvar o jogo" — você pode voltar a qualquer commit se algo
> quebrar.

### 1.3 Branch (ramo)
Uma **linha paralela de desenvolvimento**. A principal chama-se `main` (ou `master`).
Vocês criam branches para trabalhar em features sem mexer na `main`.

```
main:        A---B---C---D---E  (estável, testado)
                  \
feature/X:        F---G---H     (trabalho em andamento)
```

Quando `feature/X` estiver pronta, vocês **mesclam** (merge) de volta na `main`.

### 1.4 Pull Request (PR)
Um **pedido formal** para mesclar uma branch na `main`. No PR, a outra pessoa **revisa**
o código antes de aprovar. É o mecanismo de **controle de qualidade**.

### 1.5 Issue
Um **ticket** no GitHub para registrar uma tarefa, bug ou ideia. Funciona como uma
to-do list compartilhada. Pode ser vinculada a um PR e a uma branch.

---

## 2. Setup inicial

### 2.1 Configurar Git (uma vez por máquina)

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
git config --global init.defaultBranch main
git config --global pull.rebase false
```

> Usem o **mesmo email** que usaram no GitHub (para os commits aparecerem com seu
> perfil).

### 2.2 Criar o repositório no GitHub

1. Acessem https://github.com/new
2. **Repository name:** `A-Maze-ing` (ou o nome que quiserem).
3. **Description:** "Maze generator — 42 curriculum".
4. **Private** (recomendado para projetos de curso).
5. **NÃO** marquem "Add a README" nem ".gitignore" (vamos criar localmente).
6. Cliquem em **Create repository**.

O GitHub vai mostrar comandos para "push an existing repository". Guardem essa URL:
`https://github.com/<usuario>/A-Maze-ing.git`

### 2.3 Inicializar localmente e enviar para o GitHub

Na pasta do projeto (`/mnt/c/Users/Ruan/Desktop/A-Maze-ing`):

```bash
# Inicializa o Git local
git init

# Cria o .gitignore (impede que arquivos desnecessários subam)
# (use o Write tool ou crie o arquivo com este conteúdo)
```

Conteúdo do `.gitignore`:
```
__pycache__/
*.pyc
*.pyo
.mypy_cache/
.pytest_cache/
.venv/
venv/
dist/
build/
*.egg-info/
*.whl
*.tar.gz
.idea/
.vscode/
```

> **Atenção:** o `.whl` final do pacote deve estar na raiz do repo (exigência do
> subject). Por isso ele está no `.gitignore` para não subir builds acidentais, mas
> vocês farão `git add -f mazegen-*.whl` no final para forçar o envio da versão final.

```bash
# Primeiro commit
git add .gitignore
git commit -m "chore: initial commit with .gitignore"

# Conecta ao GitHub (substitua pela URL real)
git remote add origin https://github.com/<usuario>/A-Maze-ing.git

# Renomeia a branch principal para main (se necessário)
git branch -M main

# Envia para o GitHub
git push -u origin main
```

### 2.4 Adicionar a parceira como colaboradora

1. No GitHub: **Settings** → **Collaborators** → **Add people**.
2. Digitem o username/email da parceira.
3. Ela receberá um convite por email — deve aceitar.

> Agora ambas podem fazer `push` para o repo.

### 2.5 Clonar na máquina da parceira

Na máquina da Pessoa B:
```bash
git clone https://github.com/<usuario>/A-Maze-ing.git
cd A-Maze-ing
```

> A partir daqui, **ambas** têm o repo local e o remoto no GitHub.

---

## 3. Fluxo diário

Este é o **ciclo** que vocês repetirão todos os dias. Memorizem:

```
1. git pull            ← baixa as novidades da parceira (do GitHub)
2. (trabalhar no código)
3. git status          ← ver o que mudou
4. git add <arquivos>  ← escolher o que salvar
5. git commit -m "..."  ← salvar (snapshot)
6. git push            ← enviar para o GitHub
```

> **Regra de ouro:** **sempre** façam `git pull` **antes** de começar a trabalhar.
> Evita conflitos. Se esquecerem e a parceira tiver enviado código, o `push` será
> rejeitado e vocês terão que resolver (seção 6).

---

## 4. Branches

### 4.1 Por que usar branches?

Trabalhar direto na `main` é perigoso: se quebrarem algo, o projeto inteiro fica
instável. Com branches, vocês desenvolvem em **paralelo** sem se atrapalhar.

### 4.2 Criar e trocar de branch

```bash
# Criar uma nova branch E trocar para ela (atalho -b)
git checkout -b feat/config-parser

# Verificar em qual branch você está
git branch

# Trocar de volta para a main
git checkout main

# Voltar para a branch
git checkout feat/config-parser
```

> **Convenção de nomes:** `<tipo>/<descrição-curta>`. Tipos: `feat` (nova feature),
> `fix` (correção), `docs` (documentação), `chore` (infra/limpeza), `test` (testes).
> Ex.: `feat/backtracker`, `fix/wall-coherence`, `docs/readme`.

### 4.3 Enviar uma branch nova para o GitHub

```bash
git push -u origin feat/config-parser
```

> O `-u` cria o "vínculo" entre a branch local e a remota. Nas próximas vezes, basta
> `git push`.

### 4.4 Mesclar uma branch na main (via PR — recomendado)

**Não façam merge direto na main**. Usem Pull Requests (seção 7). Mas se precisarem
fazer localmente (ex.: para testar integração):

```bash
git checkout main
git pull
git merge feat/config-parser
git push
```

### 4.5 Deletar uma branch após o merge

```bash
git branch -d feat/config-parser          # local
git push origin --delete feat/config-parser  # remoto
```

---

## 5. Commits

### 5.1 O que commitar

- **Commits pequenos e frequentes** > um commit gigante no final.
- Cada commit deve representar **uma mudança lógica** (ex.: "adiciona parser de
  config", não "adiciona parser + visual + README tudo misturado").

### 5.2 Mensagens de commit (convenção)

Usem o formato **Conventional Commits** (padrão da indústria):

```
<tipo>: <descrição no imperativo>
```

Exemplos:
```
feat: adiciona parser de configuração (MazeConfig)
fix: corrige coerência de paredes no remove_wall
docs: adiciona seção de algoritmo no README
test: cobre edge cases do parser
chore: configura pyproject.toml
refactor: extrai algoritmos para padrão Strategy
```

> **Imperativo:** "adiciona", "corrige", "adiciona" — não "adicionado" nem
> "adicionando". Pense: "Se aplicado, este commit <mensagem>."

### 5.3 Comandos

```bash
# Ver o que mudou
git status

# Adicionar arquivos específicos (recomendado)
git add mazegen/config.py tests/test_config.py

# Adicionar tudo (cuidado: pode incluir arquivos indesejados)
git add .

# Commitar
git commit -m "feat: adiciona parser de configuração (MazeConfig)"

# Ver histórico
git log --oneline -10
```

### 5.4 Desfazer

```bash
# Desfazer mudanças não commitadas em um arquivo
git checkout -- mazegen/config.py

# Desfazer o último commit (mantendo as mudanças)
git reset --soft HEAD~1

# Desfazer o último commit E as mudanças (cuidado!)
git reset --hard HEAD~1
```

---

## 6. Sincronização

### 6.1 Pull (baixar novidades)

```bash
git pull
```

> Sempre façam isso **antes** de começar a trabalhar e **antes** de um push que foi
> rejeitado.

### 6.2 Push (enviar)

```bash
git push
```

Se aparecer `! [rejected]`:
```bash
git pull          # baixa as mudanças da parceira
# (resolva conflitos se houver — seção 6.3)
git push
```

### 6.3 Conflitos de merge

Acontecem quando vocês editaram as **mesmas linhas** do mesmo arquivo. O Git não sabe
qual versão manter. Resolução:

1. `git pull` mostra: `CONFLICT (content): Merge conflict in mazegen/generator.py`
2. Abram o arquivo. Verão marcações:
   ```
   <<<<<<< HEAD
   (seu código)
   =======
   (código da parceira)
   >>>>>>> origin/main
   ```
3. **Editem** manualmente, escolhendo o que manter (ou combinando ambos).
4. Removam as marcações `<<<<<<<`, `=======`, `>>>>>>>`.
5. Salvem o arquivo.
6. ```bash
   git add mazegen/generator.py
   git commit -m "merge: resolve conflito em generator.py"
   git push
   ```

> **Dica para evitar conflitos:** comuniquem-se! Se ambos forem mexer no
> `generator.py`, combinem quem faz o quê, ou trabalhem em arquivos diferentes.

---

## 7. Pull Requests

O PR é o **coração** da colaboração. Ele garante que **nenhum código entra na `main`
sem revisão**.

### 7.1 Criar um PR

1. Façam push da branch (seção 4.3).
2. No GitHub, vão para a aba **Pull requests** → **New pull request**.
3. **Base:** `main` | **Compare:** `feat/config-parser`.
4. Cliquem em **Create pull request**.
5. Escrevam um **título** e uma **descrição**:
   ```
   ## O que faz
   Adiciona o parser de configuração (MazeConfig) com validação.

   ## Como testar
   - `python3 -c "from mazegen.config import parse_config; print(parse_config('config.txt'))"`
   - `make lint` passa

   ## Issue relacionada
   Closes #3
   ```

### 7.2 Revisar um PR

A **outra** pessoa revisa:
1. Vão em **Pull requests** → cliquem no PR.
2. Cliquem em **Files changed**.
3. Passem por cada arquivo:
   - Comentários em linhas específicas (passe o mouse → botão `+`).
   - Sugestões de mudança.
4. Cliquem em **Review** → **Approve** (se estiver bom) ou **Request changes**.
5. Se aprovado, cliquem em **Merge pull request** → **Confirm merge**.

### 7.3 Regras do PR para o A-Maze-ing

- **Nenhum PR é mesclado sem aprovação da outra pessoa.** (Configurado na seção 10.)
- O PR **só pode ser mesclado se o CI (GitHub Actions) passar** — ou seja, `make lint`
  e os testes não falham (seção 9).
- **Descrição obrigatória** com "O que faz" e "Como testar".
- **Vinculem a Issue** (ex.: `Closes #3`) para fechar a issue automaticamente.

---

## 8. Issues

Issues são a **to-do list compartilhada**. Usem para cada tarefa do
`TAREFAS_MANDATORIO.md`.

### 8.1 Criar uma issue

1. GitHub → aba **Issues** → **New issue**.
2. Título: `T1.1 — Modelo MazeConfig (parser de config)`.
3. Corpo:
   ```markdown
   ## Objetivo
   Criar o dataclass `MazeConfig` e a função `parse_config`.

   ## Critério de conclusão
   - [ ] `parse_config("config.txt")` funciona
   - [ ] Rejeita entradas inválidas com mensagem clara
   - [ ] `make lint` passa

   ## Responsável
   @pessoaB

   ## Referência
   `TAREFAS_MANDATORIO.md` Fase 1
   ```
4. Atribuam a uma pessoa (**Assignees**).
5. (Opcional) Adicionem **labels**: `feature`, `bug`, `docs`, etc.

### 8.2 Vincular issue a PR e branch

- No PR: `Closes #3` (fecha a issue ao mesclar).
- No commit: `git commit -m "feat: parser de config (closes #3)"`.
- Nome da branch pode referenciar: `feat/config-parser-3`.

### 8.3 Quadro de projetos (opcional, mas útil)

GitHub → **Projects** → criem um **board** estilo Kanban com colunas:
`To do` | `In progress` | `Review` | `Done`. Vinculem as issues. Dá visão geral do
progresso.

---

## 9. GitHub Actions

GitHub Actions é o **CI (Integração Contínua)**: roda `make lint` e os testes
**automaticamente** a cada push/PR. Se falhar, o PR **não pode ser mesclado**.

### 9.1 Criar o arquivo de workflow

Criem o arquivo `.github/workflows/ci.yml` no repo:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout do código
        uses: actions/checkout@v4

      - name: Configurar Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: "3.10"

      - name: Instalar dependências
        run: |
          python -m pip install --upgrade pip
          pip install flake8 mypy pytest build

      - name: flake8
        run: flake8 .

      - name: mypy (flags obrigatórias)
        run: |
          mypy . --warn-return-any --warn-unused-ignores \
                 --ignore-missing-imports --disallow-untyped-defs \
                 --check-untyped-defs

      - name: pytest
        run: pytest -q
```

### 9.2 Como funciona

- A cada `push` na `main` ou `pull_request` para a `main`, o GitHub **roda
  automaticamente** em um servidor Ubuntu.
- Instala Python 3.10, as dependências, e roda flake8 + mypy + pytest.
- O resultado aparece na aba **Actions** do GitHub e como **check** no PR (✅ verde ou
  ❌ vermelho).

### 9.3 Verificar o resultado

- No PR, vejam a seção **Checks**. Se estiver vermelho, cliquem em **Details** para ver
  o erro.
- **Corrijam** na branch, façam push, e o CI re-roda automaticamente.

> **Benefício:** vocês **nunca** mesclam código que falha no lint ou nos testes. É a
> rede de segurança que impede a `main` de quebrar.

---

## 10. Proteção de branch

Para **forçar** que nenhum PR seja mesclado sem revisão e sem CI verde:

### 10.1 Configurar

1. GitHub → **Settings** → **Branches** → **Add branch protection rule**.
2. **Branch name pattern:** `main`.
3. Marquem:
   - ✅ **Require a pull request before merging**
     - ✅ **Require approvals:** `1` (precisa de 1 aprovação da parceira).
   - ✅ **Require status checks to pass before merging**
     - Cliquem em **Search** e selecionem `lint-and-test` (aparecerá após o primeiro CI
       rodar — se não aparecer, façam um PR de teste primeiro).
   - ✅ **Require branches to be up to date before merging**.
   - ✅ **Do not allow bypassing the above settings**.
4. **Create**.

### 10.2 Efeito

- Ninguém pode fazer `push` direto na `main` (deve ser via PR).
- Todo PR precisa de **1 aprovação**.
- Todo PR precisa do **CI verde**.
- A `main` fica **sempre estável e testada**.

> **Atenção:** com essa regra, vocês **não** podem mais fazer `git push` direto na
> `main`. Tudo via PR. É o comportamento desejado.

---

## 11. Convenções do projeto A-Maze-ing

### 11.1 Nome de branches
```
<tipo>/<descrição-curta>-<nº-da-issue>
```
Exemplos:
- `feat/config-parser-3`
- `feat/backtracker-5`
- `fix/wall-coherence-7`
- `docs/readme-12`
- `test/parser-edge-cases-4`

### 11.2 Mensagens de commit (Conventional Commits)
```
<tipo>: <descrição no imperativo>
```
Tipos: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`, `style`, `ci`.

### 11.3 Estrutura de PR
```
## O que faz
<descrição>

## Como testar
<comandos>

## Issue relacionada
Closes #<n>
```

### 11.4 Posse de arquivos (evita conflitos)

| Pessoa A (dona) | Pessoa B (dona) |
|-----------------|-----------------|
| `mazegen/generator.py` | `a_maze_ing.py` |
| `mazegen/dsu.py` | `mazegen/config.py` |
| Algoritmos | `mazegen/renderer_ascii.py` |
| | `pyproject.toml`, `README.md`, `Makefile`, `LICENSE.md` |

> Se a Pessoa B precisar mexer num arquivo da Pessoa A, **abra um PR e peça revisão
> dela**. Nunca editem diretamente o arquivo da outra sem avisar.

### 11.5 Branch compartilhada (para integrações conjuntas)

Para fases que ambas precisam editar o mesmo arquivo (ex.: Fase 5 modo jogável, B3.1
refatoração para `yield`), criem uma **branch compartilhada**:
```bash
git checkout main
git pull
git checkout -b feat/jogavel-integration
git push -u origin feat/jogavel-integration
```
Ambas fazem `git pull` nessa branch frequentemente e `push` incremental. Quando
estiver estável, abrem **um PR** da `feat/jogavel-integration` para a `main`.

---

## 12. Cenários comuns

### 12.1 "Fiz mudanças mas não lembro o que mudei"
```bash
git status          # arquivos modificados
git diff            # mudanças detalhadas
git diff mazegen/generator.py   # de um arquivo específico
```

### 12.2 "Commitei algo errado"
```bash
git reset --soft HEAD~1   # desfaz o commit, mantém as mudanças
# edite, add de novo, commite de novo
```

### 12.3 "Quero descartar tudo que fiz e voltar ao último commit"
```bash
git checkout -- .         # descarta mudanças não commitadas
# CUIDADO: não recuperável
```

### 12.4 "O push foi rejeitado"
```bash
git pull
# se houver conflito: resolva (seção 6.3)
git push
```

### 12.5 "Apaguei um arquivo sem querer"
```bash
git checkout HEAD -- mazegen/generator.py   # restaura do último commit
```

### 12.6 "Quero ver o histórico"
```bash
git log --oneline --graph -20
```

### 12.7 "O CI falhou no PR"
1. Cliquem em **Details** no check vermelho.
2. Vejam o erro (ex.: `flake8: line too long`).
3. Corrijam na branch local.
4. `git add`, `git commit -m "fix: corrige linha longa"`, `git push`.
5. O CI re-roda automaticamente.

### 12.8 "Preciso voltar a um commit antigo"
```bash
git log --oneline              # encontrem o hash (ex.: a1b2c3d)
git checkout a1b2c3d           # modo "detached" — só para inspecionar
# para voltar:
git checkout main
```

---

## 13. Checklist

### Setup (uma vez)
- [ ] `git config --global user.name/email` em ambas as máquinas.
- [ ] Repo criado no GitHub (private).
- [ ] `.gitignore` com artefatos Python.
- [ ] Parceira adicionada como colaboradora.
- [ ] Repo clonado na máquina da parceira.
- [ ] `.github/workflows/ci.yml` criado e enviado.
- [ ] Branch protection da `main` configurada.

### Diário
- [ ] `git pull` antes de começar.
- [ ] Trabalhar em uma branch `feat/...` (não na `main`).
- [ ] Commits pequenos com mensagens Conventional Commits.
- [ ] `git push` ao final de cada bloco de trabalho.
- [ ] Abrir PR ao concluir uma feature.
- [ ] Revisar o PR da parceira (approve ou request changes).
- [ ] Mesclar só com CI verde + aprovação.

### Antes da defesa
- [ ] `main` estável e limpa.
- [ ] Último commit com mensagem descritiva.
- [ ] `git push` final enviado.
- [ ] Repo remoto acessível ao avaliador.

---

## Referências para aprofundamento

| Tema | Fonte |
|------|-------|
| Git (documentação oficial) | https://git-scm.com/doc |
| Pro Git (livro gratuito, cap. 1–5) | https://git-scm.com/book/pt-br/v2 (em português) |
| GitHub Docs (PRs, Issues, Actions) | https://docs.github.com/ |
| Conventional Commits | https://www.conventionalcommits.org/ |
| GitHub Actions (Python) | https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python |
| Branch protection | https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets |
