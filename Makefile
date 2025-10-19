# Makefile for easy development workflows.
# See devtools/development.md for docs.
# Note GitHub Actions call uv directly, not this Makefile.

.DEFAULT_GOAL := default

.PHONY: default install lint test upgrade clean agent-rules

default: agent-rules install lint test docs-check

install:
	uv sync --all-extras

lint:
	uv run python devtools/lint.py

test:
	uv run pytest

upgrade:
	uv sync --upgrade --all-extras --dev

agent-rules: .cursorrules .clinerules .windsurfrules .github/copilot-instructions.md CLAUDE.md AGENTS.md

# Use .cursor/rules for sources of rules.
# Create agent instruction files for all major AI coding assistants from the source rules.

# Cursor rules file (standard location)
.cursorrules: .cursor/rules/general.mdc .cursor/rules/python.mdc
	cat .cursor/rules/general.mdc .cursor/rules/python.mdc > .cursorrules

# Claude/Cline rules file
.clinerules: .cursor/rules/general.mdc .cursor/rules/python.mdc
	cat .cursor/rules/general.mdc .cursor/rules/python.mdc > .clinerules

# Windsurf rules file
.windsurfrules: .cursor/rules/general.mdc .cursor/rules/python.mdc
	cat .cursor/rules/general.mdc .cursor/rules/python.mdc > .windsurfrules

# GitHub Copilot instructions (new standard location)
.github/copilot-instructions.md: .cursor/rules/general.mdc .cursor/rules/python.mdc
	cat .cursor/rules/general.mdc .cursor/rules/python.mdc > .github/copilot-instructions.md

# Legacy files (kept for backward compatibility)
CLAUDE.md: .cursor/rules/general.mdc .cursor/rules/python.mdc
	cat .cursor/rules/general.mdc .cursor/rules/python.mdc > CLAUDE.md

AGENTS.md: .cursor/rules/general.mdc .cursor/rules/python.mdc
	cat .cursor/rules/general.mdc .cursor/rules/python.mdc > AGENTS.md

clean:
	-rm -rf dist/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .mypy_cache/
	-rm -rf .ruff_cache/
	-rm -rf .venv/
	-rm -rf docs/build/
	-rm -rf src/splunk_app_action.egg-info
	-rm -rf src/utilities/logger/props.conf_temp
	-rm -rf temp_for_test
	-rm -rf CLAUDE.md AGENTS.md .cursorrules .clinerules .windsurfrules .github/copilot-instructions.md
	-find . -type d -name "__pycache__" -exec rm -rf {} +


.PHONY : docs-live
docs-live :
	rm -rf docs/build/
	sphinx-autobuild -b html --watch src/ docs/source/ docs/build/

.PHONY : docs-check
docs-check:
	rm -rf docs/build/
	uv sync --all-extras
	$(MAKE) -C docs html


.PHONY : create-tag
create-tag:
	./devtools/create_tag.sh
