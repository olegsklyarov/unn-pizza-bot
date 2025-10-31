.ONESHELL:

VENV_DIR = .venv

$(VENV_DIR):
	python3 -m venv $(VENV_DIR)

ACTIVATE_VENV := . $(VENV_DIR)/bin/activate


install: $(VENV_DIR)
	$(ACTIVATE_VENV) && pip install --upgrade pip
	$(ACTIVATE_VENV) && pip install --requirement requirements.txt

# Run black formatter
black: install
	$(ACTIVATE_VENV) && black bot/ tests/

# Run ruff linter
ruff: install
	$(ACTIVATE_VENV) && ruff check bot/ tests/

# Run pytest
pytest: install
	$(ACTIVATE_VENV) && PYTHONPATH=. pytest

# Run all tests (includes black, ruff, and pytest)
test: black ruff pytest
