# Architecture

This document records the intended internal dependency structure of the repository.

## Dependency direction

Default skeleton contract:

```text
interfaces | infrastructure
        ↓
application
        ↓
domain
```

The domain layer should not depend on application, infrastructure, or interface code. Application
code may depend on domain code. Infrastructure and interface adapters may depend inward, but should
not depend on each other unless the architecture is deliberately changed and documented.

## Internal modules

Replace this section with the project-specific package map.

| Module | Responsibility | May depend on | Must not depend on |
| --- | --- | --- | --- |
| `skeleton_package.domain` | Core entities, value objects, and domain rules. | Standard library. | Application, infrastructure, interfaces. |
| `skeleton_package.application` | Use cases and orchestration. | Domain. | Infrastructure and interfaces unless explicitly inverted. |
| `skeleton_package.infrastructure` | External adapters: files, APIs, persistence, frameworks. | Application, domain. | Interfaces. |
| `skeleton_package.interfaces` | CLI, HTTP, notebook, or user-facing adapters. | Application, domain. | Infrastructure unless explicitly documented. |

## Enforced architecture checks

The baseline enforces this document in two ways:

- `import-linter` checks the package-level dependency direction from `pyproject.toml`.
- `tests/architecture/` contains pytest guardrails for dependency direction, script entry-point
  structure, and common process/path hacks.

When the architecture changes, update this document, the import-linter contracts, and the
architecture tests in the same change.

## Architectural decisions

Record significant decisions here using a short ADR-style format:

- Context
- Decision
- Consequences
- Rejected alternatives
