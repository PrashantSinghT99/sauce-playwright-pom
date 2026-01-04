# Makefile for sauce-playwright-pom
# Usage: make <target>
# This Makefile prefers `uv run` if available. Set `UV=uv` to change.

.PHONY: venv install run smoke sanity clear resume help

UV ?= uv
VENV ?= .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

venv:
	python3 -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# run default discovery under src
run:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run runner.py -p src; \
	else \
		$(PY) runner.py -p src; \
	fi

smoke:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run runner.py -p src --markers smoke; \
	else \
		$(PY) runner.py -p src --markers smoke; \
	fi

sanity:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run runner.py -p src --markers sanity; \
	else \
		$(PY) runner.py -p src --markers sanity; \
	fi

clear:
	-rm -rf reports/* videos/* screenshots/* logs/* || true

resume:
	@if command -v $(UV) >/dev/null 2>&1; then \
		$(UV) run runner.py --resume; \
	else \
		$(PY) runner.py --resume; \
	fi


help:
	@echo "Makefile targets:"
	@echo "  venv      - create virtualenv at $(VENV)"
	@echo "  install   - create venv and install requirements"
	@echo "  run       - discover and run tests under src (uses 'uv run' if available)"
	@echo "  smoke     - run smoke-marked tests"
	@echo "  sanity    - run sanity-marked tests"
	@echo "  clear     - remove reports, videos, screenshots and logs"
	@echo "  resume    - resume last session (retry failed tests)"
