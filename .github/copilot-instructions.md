# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---
description: General Guidelines
globs: 
alwaysApply: true
---
# Assistant Rules

Be a senior engineer — concise, factual, systematic. No praise, banter, or gratuitous enthusiasm. Propose options if unclear. Comments only for non-obvious intent.

## Architecture

**GitHub Actions composite action** (`action.yml`) for Splunk App/Add-on builds, inspection, and utilities. Runs Python from `src/` on Ubuntu runners.

**Pipeline** (`action.yml` → `src/main.py`):
1. **Paths & metadata** — `SavedPaths` + `AppInfo` from inputs/`app.conf`/`globalConfig.json`; `AppInfo.publish()` exports to GH Actions
2. **Build** — `ucc_gen.build()` (UCC add-ons) or `app_build_generate.generate_build()` (standard apps via tar); optional `python_dependency_manager` for pip deps
3. **AppInspect** — `SplunkAppInspect` (API, threaded: app/cloud/SSAI parallel) or `SplunkLocalAppInspect` (CLI); both extend `BaseAppInspect` ABC
4. **Utilities** — Optional utilities via `SplunkAppUtilities`; each extends `BaseUtility` ABC
5. **Job summary & annotations** — Published to GitHub Actions UI

**Key modules:** `src/helpers/saved_values.py` (paths, app info, `keep_working_dir_unchanged`), `src/helpers/splunk_config_parser.py` (custom `.conf` parser with `FILE_SECTION`), `src/app_inspect.py` (inspect ABCs), `src/utilities/base_utility.py` (`BaseUtility` ABC)

**Tests:** `conftest.py` globally mocks `gat.set_env`/`gat.set_output`/`SplunkAppInspect._api_login`. `sys.path` adds `src/` so tests import directly. Fixtures in `tests/test_app_repos/` and `tests/integration_test_apps/`.

## Commands

```bash
make                  # install + lint + test + docs-check
make lint             # codespell + ruff format + ruff check + basedpyright
make test             # uv run pytest
make docs-check       # Sphinx build, fail on warnings

uv run pytest tests/test_ucc_gen.py::TestUccGen::test_remove_executables_enabled -x -v
uv run basedpyright src/main.py
uv run ruff check src/main.py
```

---
description: Python Coding Guidelines
globs: *.py,pyproject.toml
alwaysApply: false
---
# Python Guidelines

- **Python 3.12 only.** Use `uv` exclusively (never `pip`/`python`). Run `make lint` + `make test` after changes; zero errors required.
- Modern types: `str | None` not `Optional`, `list[str]` not `List[str]`. Use `StrEnum`, `@override` (from `typing_extensions`), `Path` over strings.
- Absolute imports only. `Callable` from `collections.abc`.
- Resolve basedpyright errors; `# pyright: ignore` only when justified. Test files: fix logic first, use file-level ignores (`# pyright: reportUnusedVariable=false`).
- Never change existing comments/pydocs/log statements unless fixing the issue or explicitly asked.
- Docstrings: concise, explain "why" not "what". Public exports should have them; skip for obvious internals.
- Use `dedent()` for multi-line strings. Use `raise AssertionError("msg")` not `assert False`.

## Changelog

Update `CHANGELOG.md` for user-facing changes. Categories: **Upgrade Notes**, **Changed/Added/Removed/Fixed/Deprecated/Security** (user-facing only), **Developer & Internal Changes** (concise, outcome-only). Feature format: `**Name** - Description`. Use "Github" not "GitHub".

## Testing

- Tests in `tests/test_*.py`. No trivial tests, no `if __name__ == "__main__"`.
- Integration tests: use reusable workflow (`.github/workflows/reusable-integration-test.yml`). **Never reuse app names** across tests.
- Update docs (`docs/source`) + README for behavior changes. Run `make docs-check`.
