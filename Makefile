PYTHON ?= python
export PYTHONPATH := src
export PYTHONDONTWRITEBYTECODE := 1
CLEAN_DIRS := .ruff_cache .pytest_cache build dist results
CLEAN_DIRS += __pycache__ src/uvm/__pycache__ tests/__pycache__
CLEAN_CMD := import shutil, sys; from pathlib import Path; \
             [shutil.rmtree(p) for p in map(Path, sys.argv[1:]) if p.is_dir()]

.PHONY: test lint examples clean

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check --no-cache .

examples:
	$(PYTHON) -m uvm.assembler examples/spec_tests.csv result.bin --test

clean:
	$(PYTHON) -c "$(CLEAN_CMD)" $(CLEAN_DIRS)
