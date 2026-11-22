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
	$(PYTHON) -c "from pathlib import Path; Path('results').mkdir(exist_ok=True)"
	$(PYTHON) -m uvm.assembler examples/spec_tests.csv results/spec.bin --test
	$(PYTHON) -m uvm.assembler examples/copy_array.csv results/copy.bin
	$(PYTHON) -m uvm.interpreter results/copy.bin results/copy.json --range 200:202
	$(PYTHON) -m uvm.assembler examples/neg_demo.csv results/neg.bin
	$(PYTHON) -m uvm.interpreter results/neg.bin results/neg.json --range 300:304

clean:
	$(PYTHON) -c "$(CLEAN_CMD)" $(CLEAN_DIRS)
