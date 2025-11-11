---
description: General Guidelines
globs: 
alwaysApply: true
---
# Assistant Rules

**Your fundamental responsibility:** Be a senior engineer - clear, factual, systematic, and make wise use of the user's attention.

- Be concise. State answers directly or do what is asked without extra commentary.
- If unclear, propose options and ask for confirmation.
- Suggest better approaches when applicable, but avoid praise, encouragement, or banter.
- Avoid gratuitous enthusiasm. Instead of "I've meticulously improved the code!", say "Added types to all methods in `Foo` and fixed all linter errors."

# Coding Guidelines

## Comments

- Keep comments concise, clear, and production-ready.
- Use comments for subtle/confusing code or non-obvious intent.
- DON'T repeat what's obvious from names/types, add "Added this function" notes, use fancy headings like "===== TOOLS =====", number steps, or use emojis/unicode in code.
- Emojis OK in output if consistent: ✔︎✘ for success/failure, ∆‼︎ for warnings/errors.

---
description: Python Coding Guidelines
globs: *.py,pyproject.toml
alwaysApply: false
---
# Python Guidelines

## Project Setup

- Python 3.12 only. Use modern practices, full type annotations, and generics.
- Read `pyproject.toml` and `Makefile` to understand project setup.
- ALWAYS use `uv` for dependencies (`uv sync`, `uv run`, `uv add`). Never use `pip` or `python` directly.
- Shortcuts: `make install`, `make lint`, `make test`, `make docs-check`, `make` (runs all).
- Run `make lint` and `make test` after code changes. Run `make docs-check` after Doc changes. Zero errors/warnings required before completion.

## Development Practices

- Resolve basedpyright errors. Use `# pyright: ignore` only when justified.
- Never change existing comments, pydocs, or log statements unless fixing the issue or explicitly asked.
- Use absolute imports: `from toplevel_pkg.module import ...` (not relative `.module`).
- Import from correct modules: `Callable` from `collections.abc`, `@override` from `typing_extensions`.
- Use `Path` instead of strings. Use `Path(file).read_text()` instead of `open()`.
- ALWAYS use `@override` for method overrides.

## Linting & Type Checking

Tools: codespell (auto-fix typos), ruff (lint/format), basedpyright (type check). All run via `make lint`.

Test files: Fix test logic first, then linting. Use file-level ignores for common test issues:
- File level: `# pyright: reportUnusedVariable=false`
- Line level: `# pyright: ignore[reportMissingImports]`

## Documentation & README

Use Sphinx with MyST Markdown. Keep README aligned with user-facing behavior.

**When to update:**
- Docs (`docs/source`): behavior, inputs/outputs, config, env vars, versions, CLI, defaults, migrations
- README: quickstart, versions, badges, examples, config summary
- Always run `make docs-check` and ensure CHANGELOG updated

## Changelog (Keep a Changelog)

Update `CHANGELOG.md` for all user-facing changes (behavior, inputs/outputs, config, logging, docs).

**Categories:**
- **Upgrade Notes** - Breaking changes, migration guidance, what's new
- **Changed/Added/Removed/Fixed/Deprecated/Security** - User-facing behavior only
- **Developer & Internal Changes** - Implementation, dependencies, tests, tooling

**Formatting:**
- Feature titles: `**Feature Name** - Brief one-line description`
- Sub-bullets: 2-space indent with user-benefit details
- Use "Github" not "GitHub" for consistency
- Developer section: Single-line summaries with key metrics (e.g., "~200 lines eliminated")

**Critical:** Primary sections focus on "what changed for the user" not "how it was implemented". Avoid class names, architecture details. Developer section is extremely concise - outcome/impact only, not implementation steps.

## Testing

- Longer tests: `tests/test_somename.py`
- Simple tests: Inline in source below `## Tests` (no pytest imports)
- NO trivial tests, throwaway files, or `if __name__ == "__main__"`
- Assertions: No redundant docs (`assert x == 5` not `assert x == 5, "x should be 5"`)
- Use `raise AssertionError("msg")` not `assert False`
- Add/update tests for new functionality and user-facing behavior changes
- Full test suite must pass before completion

## Integration Tests (GitHub Actions)

**CRITICAL for this project:** Always add/update integration tests when changing user-facing GitHub Action behavior.

- Prefer reusable workflow (`.github/workflows/reusable-integration-test.yml`) over custom jobs
- Use helper scripts (`.github/scripts/validate-*.sh`) for validation patterns
- **NEVER reuse app names** across tests - causes artifact conflicts. Clone and rename app ID in `app.conf`

## Types & Annotations

- Modern syntax: `str | None` not `Optional[str]`, `dict[str]` not `Dict[str]`, `list[str]` not `List[str]`
- Never use/import `Optional` for new code
- Use `StrEnum` when appropriate
- Exception: Use `lower_snake_case` for string enum values matching actual value

## Docstrings

- Concise, triple-quoted on own lines
- Use backticks for variables/code, plain fences for code blocks
- Explain "why", not obvious details from names/types
- NO obvious/repetitive docstrings
- Public exports SHOULD have docstrings; internal code only if non-obvious
- Example:
  ```python
  def check_if_url(text: str) -> ParseResult | None:
      """
      Check if string is URL and return `urlparse.ParseResult`.
      Returns None for Paths for easy interchangeable use.
      """
  ```

## Clean Code

- Avoid trivial wrapper functions
- Use `# pyright: ignore[reportUnusedParameter]` for required but unused params
- Mention backward compatibility breaks; don't add compat code unless user confirms

## Multi-line Strings

Use `dedent()` for readability:
```python
from textwrap import dedent
content = dedent("""
    # Title
    Text.
    """).strip()
```
