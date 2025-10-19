# AI Agent Instructions

This directory contains the source instruction files for AI coding assistants.

## Structure

- `general.mdc` - General coding guidelines applicable to all languages
- `python.mdc` - Python-specific guidelines including project setup, testing, linting, and type-checking

## Generating Agent Instruction Files

The Makefile automatically generates instruction files for various AI coding assistants from these source files:

```shell
make agent-rules
```

This creates the following files (all git-ignored):

### Standard Locations
- `.cursorrules` - For Cursor (root directory)
- `.clinerules` - For Claude/Cline (root directory)  
- `.windsurfrules` - For Windsurf (root directory)
- `.github/copilot-instructions.md` - For GitHub Copilot (standard location)

### Legacy Files (kept for backward compatibility)
- `CLAUDE.md` - For Claude AI (root directory)
- `AGENTS.md` - For general agents (root directory)

## Modifying Instructions

To modify AI agent instructions:

1. Edit the source files in this directory (`general.mdc` and/or `python.mdc`)
2. Run `make agent-rules` to regenerate all instruction files
3. Test with your preferred AI assistant
4. Commit only the source files (the generated files are git-ignored)

## What's Included

The generated instruction files include:

- **General Coding Guidelines**: Comment style, code clarity, best practices
- **Python-Specific Guidelines**: Modern Python 3.12+ practices, type annotations
- **Project Setup**: How to use uv, Makefile shortcuts
- **Development Workflows**: 
  - `make install` - Install dependencies
  - `make lint` - Run linting with ruff and type checking with basedpyright
  - `make test` - Run tests with pytest
  - `make` - Run install, lint, and test in one command
- **Testing Guidelines**: Pytest usage, test organization, inline tests
- **Code Quality**: Type checking, linting rules, formatting standards
