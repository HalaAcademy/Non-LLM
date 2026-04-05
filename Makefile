.PHONY: setup test test-fast lint check coverage ci bench status clean

# === Setup ===
setup:
	pip install -e ".[dev]"

# === Testing ===
test:
	pytest tests/ -v

test-fast:
	pytest tests/ -v -m "not slow" --timeout=30

test-lexer:
	pytest tests/copl/lexer/ -v

test-parser:
	pytest tests/copl/parser/ -v

test-semantic:
	pytest tests/copl/semantic/ -v

test-codegen:
	pytest tests/copl/codegen/ -v

coverage:
	pytest tests/ --cov=src/copl --cov-report=html --cov-report=term-missing
	@echo "HTML report: htmlcov/index.html"

# === Code Quality ===
lint:
	ruff check src/ tests/

lint-fix:
	ruff check src/ tests/ --fix

check:
	mypy src/copl/
	ruff check src/ tests/

# === Full CI Pipeline ===
ci: lint check test coverage
	@echo "✅ All CI checks passed"

# === Compiler Usage ===
parse:
	python -m copl parse $(FILE)

build-example:
	python -m copl build examples/01_minimal.copl --target c

# === Project Status ===
status:
	@echo "=== COPL Compiler Status ==="
	@python -m pytest tests/ --co -q 2>/dev/null | tail -1 || echo "No tests yet"
	@echo ""
	@echo "Source files:"
	@find src/ -name "*.py" | wc -l | xargs echo "  .py files:"
	@find tests/ -name "*.py" | wc -l | xargs echo "  test files:"

# === Cleanup ===
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf htmlcov/ .coverage .mypy_cache/ .ruff_cache/
	@echo "Cleaned."
