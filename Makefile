VENV = venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYTEST = $(VENV)/bin/pytest
FLAKE8 = $(VENV)/bin/flake8
MYPY = $(VENV)/bin/mypy

.PHONY: install test run debug clean lint lint-strict install-mlx

# Regra para criar o ambiente virtual
$(VENV):
	python3 -m venv $(VENV)

# Instalação das dependências
install: $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy pytest build

# Instalação opcional do MLX (para renderizador gráfico bonus)
install-mlx: $(VENV)
	$(PIP) install ./vendor/mlx-2.2-py3-none-any.whl

# Execução dos testes
test: $(VENV)
	$(PYTEST) -v

# Execução do projeto usando o Python da venv
run: $(VENV)
	$(PYTHON) a_maze_ing.py config.txt

debug: $(VENV)
	$(PYTHON) -m pdb a_maze_ing.py config.txt

# Limpeza de caches e arquivos temporários (recursivo em todos os diretórios)
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf dist build *.egg-info

# Verificação padrão de linter e tipagem nos pacotes do projeto
lint: $(VENV)
	$(FLAKE8) .
	$(MYPY) . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs

# Verificação estrita de tipagem
lint-strict: $(VENV)
	$(FLAKE8) .
	$(MYPY) . --strict