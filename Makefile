.DEFAULT_GOAL := help

.PHONY: install install-runtime metadata quick validate validate-all ci \
	test test-unit test-property test-architecture test-smoke test-integration \
	test-external test-slow coverage lint lint-fix format format-check typecheck \
	deptry imports dead-code complexity docstrings security-static security-deps \
	security package mutation mutation-results mutation-browse mutation-clean \
	install-mlflow mlflow-ui mlflow-clean doctor outdated clean help

POETRY ?= poetry
SRC_DIRS := src tests scripts
PYTEST_DEFAULT_MARKERS := not external and not slow
MLFLOW_HOST ?= 127.0.0.1
MLFLOW_PORT ?= 5000
MLFLOW_BACKEND_STORE ?= ./mlruns

install:
	$(POETRY) install

install-runtime:
	$(POETRY) install --only main

metadata:
	$(POETRY) check

quick: format-check typecheck test-unit test-smoke

validate: metadata format-check typecheck test deptry imports

validate-all: validate dead-code complexity docstrings security-static

ci: validate package

test:
	$(POETRY) run pytest -m "$(PYTEST_DEFAULT_MARKERS)"

test-unit:
	$(POETRY) run pytest tests/unit

test-property:
	$(POETRY) run pytest -m property

test-architecture:
	$(POETRY) run pytest -m architecture

test-smoke:
	$(POETRY) run pytest -m smoke

test-integration:
	$(POETRY) run pytest tests/integration -m "$(PYTEST_DEFAULT_MARKERS)"

test-external:
	$(POETRY) run pytest -m external

test-slow:
	$(POETRY) run pytest -m slow

coverage:
	$(POETRY) run pytest -m "$(PYTEST_DEFAULT_MARKERS)" --cov=skeleton_package --cov-report=term-missing --cov-report=xml

lint:
	$(POETRY) run ruff check $(SRC_DIRS)

lint-fix:
	$(POETRY) run ruff check --fix $(SRC_DIRS)

format:
	$(POETRY) run ruff format $(SRC_DIRS)
	$(POETRY) run ruff check --fix $(SRC_DIRS)

format-check:
	$(POETRY) run ruff format --check $(SRC_DIRS)
	$(POETRY) run ruff check $(SRC_DIRS)

typecheck:
	$(POETRY) run pyright

deptry:
	$(POETRY) run deptry .

imports:
	$(POETRY) run lint-imports

dead-code:
	$(POETRY) run vulture src scripts tests --min-confidence 80

complexity:
	$(POETRY) run radon cc src scripts --min B
	$(POETRY) run radon mi src scripts --min B

docstrings:
	$(POETRY) run dfc check src/

security-static:
	$(POETRY) run bandit -r src scripts -q

security-deps:
	$(POETRY) run pip-audit

security: security-static security-deps

package:
	$(POETRY) build

mutation:
	$(POETRY) run mutmut run

mutation-results:
	$(POETRY) run mutmut results

mutation-browse:
	$(POETRY) run mutmut browse

mutation-clean:
	rm -rf .mutmut-cache mutants

install-mlflow:
	$(POETRY) install --with mlops

mlflow-ui:
	@$(POETRY) run python -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('mlflow') else 1)" || \
		(echo "MLflow is not installed. Run: make install-mlflow" && exit 1)
	mkdir -p $(MLFLOW_BACKEND_STORE)
	MLFLOW_TRACKING_URI=file:$(MLFLOW_BACKEND_STORE) $(POETRY) run mlflow ui \
		--backend-store-uri $(MLFLOW_BACKEND_STORE) \
		--host $(MLFLOW_HOST) \
		--port $(MLFLOW_PORT)

mlflow-clean:
	rm -rf mlruns mlartifacts

doctor:
	$(POETRY) --version
	$(POETRY) run python --version
	$(POETRY) run ruff --version
	$(POETRY) run pyright --version
	$(POETRY) run pytest --version

outdated:
	$(POETRY) show --outdated

clean:
	rm -rf .pytest_cache .ruff_cache .hypothesis .mutmut-cache mutants htmlcov \
		coverage.xml .coverage .coverage.* dist build *.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

help:
	@echo "Setup:"
	@echo "  make install          Install package and default dev tooling"
	@echo "  make install-runtime  Install only runtime dependencies"
	@echo "  make doctor           Print key tool versions"
	@echo ""
	@echo "Daily loop:"
	@echo "  make quick            Fast confidence loop: format-check, Pyright, unit, smoke"
	@echo "  make format           Format code and apply safe Ruff fixes"
	@echo "  make format-check     Verify formatting and lint rules without modifying files"
	@echo "  make validate         Main local/CI quality gate"
	@echo "  make validate-all     Validate plus heavier static quality checks"
	@echo "  make ci               Run validate and package build"
	@echo ""
	@echo "Tests:"
	@echo "  make test             Run default tests, excluding external and slow tests"
	@echo "  make test-unit        Run unit tests"
	@echo "  make test-property    Run property-marked tests wherever they live"
	@echo "  make test-integration Run local integration tests"
	@echo "  make test-architecture Run static architecture tests"
	@echo "  make test-smoke       Run import and script --help smoke tests"
	@echo "  make test-slow        Run tests marked slow"
	@echo "  make test-external    Run tests requiring external services or credentials"
	@echo "  make coverage         Run tests with coverage reporting"
	@echo ""
	@echo "Quality tools:"
	@echo "  make lint             Run Ruff lint checks"
	@echo "  make lint-fix         Run Ruff auto-fixes without formatting"
	@echo "  make typecheck        Run Pyright"
	@echo "  make deptry           Check dependency declarations"
	@echo "  make imports          Enforce Import Linter architecture contracts"
	@echo "  make dead-code        Run vulture"
	@echo "  make complexity       Run radon complexity and maintainability checks"
	@echo "  make docstrings       Run docstring-format-checker on src/"
	@echo "  make security-static  Run Bandit against src/ and scripts/"
	@echo "  make security-deps    Audit installed dependencies for known vulnerabilities"
	@echo "  make mutation         Run mutation testing"
	@echo ""
	@echo "Packaging and optional infrastructure:"
	@echo "  make package          Build source and wheel distributions"
	@echo "  make install-mlflow   Install optional local MLflow support"
	@echo "  make mlflow-ui        Run a local MLflow UI after MLflow is installed"
	@echo "  make outdated         Show outdated Poetry dependencies"
	@echo "  make clean            Remove local generated artifacts"
