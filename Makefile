VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
FLAKE8 = $(VENV)/bin/flake8
MYPY = $(VENV)/bin/mypy

.PHONY: install test run debug clean lint lint-strict

# Regra para criar o ambiente virtual
$(VENV):
	python3 -m venv $(VENV)

# Instalação das dependências
install: $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy pytest build

# Execução dos testes
test: $(VENV)
	$(PYTEST) -v

# Execução do projeto usando o Python da venv
run: $(VENV)
	$(PYTHON) a_maze_ing.py config.txt

debug: $(VENV)
	$(PYTHON) -m pdb a_maze_ing.py config.txt

# Limpeza de caches e arquivos temporários
clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache dist build *.egg-info

# Verificação padrão de linter e tipagem nos pacotes do projeto
lint: $(VENV)
	$(FLAKE8) mazegen tests
	$(MYPY) mazegen tests

# Verificação estrita de tipagem
lint-strict: $(VENV)
	$(FLAKE8) mazegen tests
	$(MYPY) --strict mazegen tests