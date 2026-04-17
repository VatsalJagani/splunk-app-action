# splunk-app-action

GitHub Actions composite action for Splunk App/Add-on builds, app-inspect checks, and utilities. Runs Python from `src/` on Ubuntu runners.

## Commands

```bash
make                  # install + lint + test + docs-check
make lint             # codespell + ruff format + ruff check + basedpyright
make test             # uv run pytest
uv run pytest tests/path/to/test.py::Class::method -x -v
```

## Architecture

`action.yml` → `INPUT_*` env vars → `src/main.py`

**Three mutually exclusive build paths:**
1. **UCC**: `ucc_gen.build()` — runs `ucc-gen build` in repo copy
2. **Python deps**: `python_dependency_manager.install_dependencies()` — `pip install --target lib/`, cleans `.pyc`/`.dist-info`
3. **Standard**: `shutil.copytree()` only

**After build:** `app_build_generate.generate_build()` → App Inspect (3 parallel threads) → Utilities → Job summary

**App Inspect:** `SplunkAppInspect` (Splunkbase API) or `SplunkLocalAppInspect` (CLI). Results: `[0]=app, [1]=cloud, [2]=ssai`.

**Utilities:** `BaseUtility` subclasses detect changes via file hash, create PRs via `gat.Repo`. Idempotent — skips if `splunk_app_action_<hash>` branch already exists on remote.

## Key Non-Obvious Details

- `SavedPaths.repo_dir_path` is always `{cwd}/repodir` (hardcoded from action.yml checkout path)
- `AppInfo.publish()` must be called explicitly after construction; `set_build_number()` after build dir is ready
- App inspect threads set status in `finally` so outputs publish even on failure
- `python_dependency_manager` preserves `default/metadata/static/appserver/bin/local/lookups` when cleaning target dir
- `docs/source/CHANGELOG.md` is a symlink to root `CHANGELOG.md`

## Tests

```python
with setup_action_yml("integration_test_apps/valid_app", app_dir="valid_app", is_app_inspect_check="false"):
    main()
```

- `setup_action_yml()` in `tests/helper_test.py`: copies app → `temp_for_test/repodir/`, sets `INPUT_*` env vars, cleans up on exit
- `conftest.py` mocks `gat.set_env`, `gat.set_output`, `SplunkAppInspect._api_login`; adds `src/` to `sys.path`
- Expect failures: `pytest.raises(SystemExit)` with `code == 5`
- Permission tests: mask group-write bit (`stat.st_mode & ~0o020`) — varies by machine umask
- Never reuse app names across integration tests

## Python

- Python 3.12, `uv` only (never `pip`/`python`), zero lint errors
- `str | None` not `Optional`; `Generator` not `Iterator` for `@contextmanager`; absolute imports only
- `Callable` from `collections.abc`
- `CHANGELOG.md`: user-facing categories (Changed/Added/Fixed/etc.) + Developer & Internal Changes; feature format `**Name** - Description`; "Github" not "GitHub"
