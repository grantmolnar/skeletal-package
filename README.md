# Skeleton Package

Reusable baseline for Python repositories using Poetry, a `src/` package layout, tests, linting,
Pyright type-checking, dependency checks, mutation testing, dead-code checks, docstring checks, complexity
checks, security checks, smoke tests, architecture import contracts, and GitHub Actions CI.

## Repository layout

```text
.
├── docs/
│   ├── architecture.md
│   └── standards.md
├── scripts/
│   └── example_cli.py
├── src/
│   └── skeleton_package/
│       ├── application/
│       ├── domain/
│       ├── infrastructure/
│       └── interfaces/
├── tests/
│   ├── architecture/
│   ├── integration/
│   ├── smoke/
│   ├── support/
│   └── unit/
├── Makefile
├── pyproject.toml
└── README.md
```

## Set up the environment

Install Poetry, then run:

```bash
poetry install
```

Alternatively, use the Makefile:

```bash
make install
```

## Command philosophy

The Makefile is organized around workflows, not synonyms. Each public target should either run a
distinct tool or encode a distinct working loop:

- **setup**: install the package and default development tooling;
- **daily loop**: format, type-check, and run the tests most likely to fail while editing;
- **normal validation**: the gate expected before a commit, push, or pull request;
- **heavier validation**: slower checks for larger changes and periodic maintenance;
- **optional infrastructure**: MLflow, external-service tests, and dependency vulnerability audits.

Plain `make` prints help. It does not install dependencies, mutate files, or run a long validation
suite implicitly. Avoid adding aliases unless a new target represents a genuinely different workflow.

## Common commands

```bash
make install          # install package and default dev tooling
make install-runtime  # install only runtime dependencies
make doctor           # print key tool versions
make quick            # fast local confidence loop: format-check, typecheck, unit, smoke
make format           # run Ruff formatting and safe Ruff auto-fixes
make format-check     # verify formatting and lint rules without modifying files
make validate         # run the main local/CI validation gate
make validate-all     # run validate plus slower local static quality checks
make ci               # run validate and package build
make test             # run default tests, excluding external and slow tests
make test-unit        # run unit tests
make test-property    # run property-marked tests wherever they live
make test-integration # run local integration tests, excluding external and slow tests
make test-architecture # run static architecture and script-contract tests
make test-smoke       # run import and script --help smoke tests
make test-slow        # run tests marked slow
make test-external    # run tests that need external services or credentials
make coverage         # run default tests with coverage reporting
make lint             # run Ruff lint checks
make lint-fix         # run Ruff auto-fixes without formatting
make typecheck        # run Pyright
make deptry           # check dependency declarations
make imports          # enforce Import Linter architecture contracts
make dead-code        # run vulture
make complexity       # run radon cyclomatic-complexity and maintainability checks
make docstrings       # run docstring-format-checker on src/
make security-static  # run Bandit against src/ and scripts/
make security-deps    # audit installed dependencies for known vulnerabilities
make security         # run both security checks
make package          # build source and wheel distributions
make mutation         # run mutmut mutation testing
make mutation-results # summarize surviving mutants
make mutation-browse  # inspect mutation results interactively
make install-mlflow   # optionally add MLflow to a separate dependency group
make mlflow-ui        # run a local MLflow UI after MLflow is installed
make outdated         # show outdated Poetry dependencies
make clean            # remove local generated artifacts
make help             # print grouped command help
```

`make quick` is the edit-loop command. `make validate` is the normal pre-commit/pre-push quality
gate. `make validate-all` is useful before larger pull requests. Run `make security-deps` separately
for dependency vulnerability audits, because those checks depend on external advisory data.
`make mutation` is intentionally separate because mutation testing is valuable but usually too slow
for the standard loop.

## CI and maintenance automation

The skeleton includes a conservative GitHub Actions CI workflow. It runs `make validate` on Python
3.11, 3.12, and 3.13 for pushes to `main` and pull requests, then verifies that the package can be
built. Locally, `make ci` runs both `make validate` and `make package`. This is CI, not deployment automation. Add CD only when the derived repo has a real release
target, credentials model, artifact destination, and rollback story.

The skeleton also includes `.github/dependabot.yml` for weekly GitHub Actions and Poetry dependency
updates. Dependabot uses the `pip` ecosystem value for Poetry projects.

Security-related commands are available but not part of `make validate`:

```bash
make security-static  # local AST-based security linting
make security-deps    # dependency vulnerability audit; may need network access
make security         # both of the above
```

`make validate-all` includes `security-static`, but not `security-deps`, because dependency
vulnerability data is external, time-sensitive, and may fail for reasons unrelated to the current
change.

## Optional local MLflow setup

This skeleton declares MLflow in an optional `mlops` dependency group. It is not installed by
plain `poetry install` or `make install`, and it is not part of the default validation gate.
For a repo that needs lightweight local experiment tracking, install the optional group deliberately:

```bash
make install-mlflow
```

Then start a local UI backed by a repo-local tracking directory:

```bash
make mlflow-ui
```

By default, this uses:

```text
MLFLOW_BACKEND_STORE=./mlruns
MLFLOW_HOST=127.0.0.1
MLFLOW_PORT=5000
```

Override these from the shell when needed:

```bash
MLFLOW_PORT=5050 make mlflow-ui
```

The generated `mlruns/` and `mlartifacts/` directories are ignored by Git. Commit explicit MLflow
setup only when the project actually needs it; do not make experiment-tracking infrastructure part
of the baseline validation gate.

## Baseline guardrails

The skeleton starts with discovery-based tests that make new files accountable automatically:

- Every package module under `src/skeleton_package` must import cleanly in a fresh Python subprocess.
- Package imports must not print to stdout or stderr.
- Every Python script under `scripts/` must be importable without executing its CLI behavior.
- Every Python script under `scripts/` must pass `--help`.
- Integration tests under `tests/integration/` exercise package-boundary wiring without external services.
- Tests requiring network, credentials, service daemons, or non-local infrastructure use the
  `external` marker and run through `make test-external`.
- Tests that are locally repeatable but too slow for the normal loop use the `slow` marker and run
  through `make test-slow`.
- Every script must expose `parse_args(argv)` and `main(argv)`.
- Every script must end with `if __name__ == "__main__": raise SystemExit(main())`.
- Runtime code must avoid common shell/path hacks such as `os.system`, `sys.path.append`, and
  `subprocess(..., shell=True)`.
- The default clean-architecture dependency direction is enforced both by pytest architecture tests
  and by Import Linter.

## Test organization

Organize tests by the behavior and layer they exercise, not by assertion technique. Property-based
tests are unit or integration tests that happen to use generated examples, so they should live beside
the behavior they cover. The `property` marker exists for selective runs; it is not a top-level test
directory.

The default layout is:

```text
tests/architecture/  # repo-wide static design rules
tests/integration/   # local component/process-boundary wiring
tests/smoke/         # broad import and --help checks
tests/unit/          # domain/application/interface/infrastructure units
```

Keep external-service tests marked as `external`; they are intentionally outside the default
validation loop until a project deliberately introduces and documents that infrastructure.

## Turning this skeleton into a real repo

1. Rename the Poetry project metadata in `pyproject.toml`:
   - `project.name`
   - `project.description`
   - `project.authors`
2. Rename `src/skeleton_package` to the real import package name.
3. Update all package-name references:
   - `tool.poetry.packages = [{ include = "...", from = "src" }]`
   - `tool.ruff.lint.isort.known-first-party`
   - `tool.deptry.known_first_party`
   - `tool.importlinter.root_package`
   - import-linter contract layers
   - `tests/support/paths.py`
   - package imports in tests
4. Replace this README with project-specific usage, architecture, deployment, and support guidance.
5. Fill in `docs/architecture.md` with the internal dependency graph and architectural invariants.
6. Fill in `docs/standards.md` with the repo-specific code, test, documentation, and review standards.
7. Adjust the import-linter contract if your architecture is not the default clean-architecture layering.
8. Add runtime dependencies with `poetry add <package>` and dev-only dependencies with
   `poetry add --group dev <package>`.
9. Run `make format` and then `make validate` before the first real commit.

## Placeholder: project-specific guidance

Document the following before substantial implementation begins:

- Project purpose and non-goals.
- Supported Python versions.
- Core domain concepts.
- Public APIs and CLI entry points.
- Required external services or local infrastructure, including optional MLflow usage.
- Data, model, cache, or artifact locations.
- Deployment or packaging expectations.
- Security, privacy, and licensing constraints.

## Placeholder: contribution workflow

A typical local workflow is:

```bash
make install
make format
make validate
```

Before opening a larger pull request, also consider:

```bash
make validate-all
make audit
make mutation
make mutation-results
```
