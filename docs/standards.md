# Standards

We adhere Robert C. Martin's Clean Code / Clean Architecture discipline: small
units, clear names, inward-pointing dependencies, explicit boundaries, and tests that make design
pressure visible early.

## Architecture

### Dependency rule

Dependencies should point inward:

```text
interfaces / infrastructure -> application -> domain
```

- `domain` contains the core vocabulary, rules, entities, value objects, and pure calculations.
- `application` orchestrates use cases. It may coordinate domain logic, ports, and workflows.
- `interfaces` adapts the outside world into application calls: CLIs, HTTP handlers, notebooks,
  scheduled jobs, or user-facing entrypoints.
- `infrastructure` implements technical details: filesystems, databases, remote APIs, MLflow,
  subprocesses, logging sinks, and framework-specific behavior.

Domain code must not import frameworks, storage, network clients, CLIs, or process-level concerns.
When a boundary is needed, define a small port/protocol near the use case and implement it at the
edge.

### Module shape

- One module should tell one coherent story.
- Split files when they accumulate unrelated reasons to change.
- Prefer small packages with explicit boundaries over large utility modules.
- Avoid circular imports. A cycle usually means the concept boundary is wrong.
- Keep compatibility facades thin and temporary; put the real implementation behind them.
- Do not add abstractions speculatively. Wait until there are at least two clean users of the
  abstraction.

### Side effects

- Importing modules should define names, not perform work.
- Put I/O at the edge. Keep domain and use-case logic testable without files, services, or clocks.
- Pass dependencies explicitly. Avoid hidden global state, ambient configuration, and singleton
  service locators.
- Return structured results from package code. Print only in interface code.

## Code

### Names and functions

- Use intention-revealing names. Prefer `resolved_config_path` to `p`, `task`, or `data`.
- Functions should operate at one level of abstraction. A function that parses CLI flags should not
  also perform domain calculations and write output files.
- Keep functions small because they are conceptually small, not because of an arbitrary line limit.
- Prefer command-query separation: a function should either return information or cause an effect;
  mixing both should be deliberate.
- Make invalid states unrepresentable where practical with types, enums, dataclasses, value objects,
  or validation at boundaries.

### Simplicity and duplication

- Prefer clear code over clever code.
- Remove dead code rather than preserving it for imagined future use.
- Centralize shared helpers only after duplication is real and the shared concept has a stable name.
- Keep configuration explicit and close to the boundary that consumes it.
- Avoid stringly typed protocols when the type system can express the constraint.
- Keep Pyright clean. Type-checking failures are design feedback, not cosmetic noise.

### Comments and docstrings

First try to make the code clear enough that the comment is unnecessary. Comments are not 
a substitute for good names, small functions, tests, or better boundaries.

Good comments explain one of these things:

- why a non-obvious decision exists;
- which invariant is being protected;
- which external constraint forced an awkward shape;
- what warning a future maintainer must not miss;
- what public API behavior, units, side effects, or failure modes are not obvious from the
  signature.

Bad comments usually do one of these things:

- restate the implementation;
- apologize for unclear code instead of improving it;
- preserve dead code;
- narrate history better recorded in Git;
- drift away from the code they claim to explain.

### Errors and boundaries

- Fail early at boundaries with specific messages.
- Prefer narrow exception handling. Do not catch broad exceptions unless the boundary converts them
  into a deliberate error model.
- Do not hide import or packaging problems with `sys.path` mutation.
- Do not shell out with `os.system` or `subprocess(..., shell=True)` unless a project-specific
  exception is documented and tested.
- Keep environment-variable reads, filesystem discovery, and process-level behavior at the edge.

## Scripts

Committed scripts are reusable interface adapters. They should be glorified wrappers around
importable package behavior, and should not house domain logic.

A script may:

- parse command-line arguments;
- validate CLI-facing input;
- call one application/interface function;
- translate the returned result into an exit code, stdout, stderr, or a small file artifact.

A script should not:

- define business rules or domain algorithms;
- contain reusable transformation logic;
- define classes;
- mutate `sys.path` to make imports work;
- start work at import time;
- hide substantial behavior in private helper functions;
- become a second implementation path beside package code.

Python scripts under `scripts/` must follow this structure:

```python
import argparse
from collections.abc import Sequence


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    ...


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    ...
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Scripts must support `--help`. Importing a script must not run commands, start services, parse
process arguments, read large files, or print status.

If a script needs more than a thin wrapper, move the behavior into `src/` and test it there.

## Tests

Tests should be fast, independent, repeatable, self-validating, and timely.

- New behavior requires tests.
- Prefer behavior-focused tests over implementation-coupled tests.
- Organize tests by behavior and layer, not by assertion technique.
- Unit tests belong under the relevant domain/application/interface/infrastructure area.
- Property-based tests are a kind of unit or integration test. Put them beside the behavior they
  exercise and mark them with `pytest.mark.property` when selective runs are useful.
- Use integration tests for local component wiring: CLI-to-application, adapter-to-port,
  serialization boundaries, filesystem boundaries, and other seams that matter without requiring
  external services.
- Mark tests requiring network, credentials, service daemons, or non-local infrastructure as
  `external`; keep them out of the default loop until the project explicitly introduces and
  documents that infrastructure.
- Use smoke tests to guarantee modules import and scripts expose `--help`.
- Use architecture tests for repo-wide invariants: dependency direction, import-time discipline,
  script shape, and repository hygiene.
- Add regression tests for each repaired bug.
- Skips and xfails require explicit reasons.
- Mutation testing failures should either produce better tests or be explicitly justified.

A brittle test is a design signal. First ask whether the code has too many responsibilities, hidden
state, or an implicit dependency that should become explicit.

## Documentation

- Keep `README.md` operational: setup, commands, project-specific usage, and migration from this
  skeleton.
- Keep `docs/architecture.md` aligned with the actual dependency graph and import-linter contracts.
- Record non-obvious architecture decisions in docs rather than burying them in comments.
- For non-trivial implementation work, consider a short audit or design note before changing code:
  current behavior, intended behavior, risks, and acceptance criteria.

## CI/CD and maintenance automation

Continuous integration is part of the baseline discipline. Continuous deployment is not.

The default CI workflow does purpose-agnostic work:

- install the project from a clean checkout;
- run the same validation gate humans run locally;
- exercise the supported Python versions;
- verify that the package can be built;
- use least-privilege repository permissions.

Dependency maintenance should be automated enough to prevent silent drift, but not so automated that
it bypasses review. Dependabot updates should enter through normal pull/merge requests and pass the 
same quality gate as human-authored changes. Security checks should distinguish local, deterministic
static checks from dependency vulnerability audits that depend on external advisory data.

## Review discipline

- Keep changes small enough to review mechanically.
- Separate refactors from behavior changes when practical.
- State purpose, scope, non-scope, tests, and documentation impact in meaningful changes.
- Prefer incremental improvement over broad rewrites.
- Leave the repo cleaner and easier to understand than you found it.
