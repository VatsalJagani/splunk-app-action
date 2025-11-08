# Contributing

Thank you for your interest in contributing to **splunk-app-action**! We welcome contributions from the community to help improve this GitHub Action. Please follow these guidelines to help us review and accept your contributions efficiently.

## Ways to Contribute

### Bug Reports
Found a bug? Help us fix it!

- **Search first** - Check [existing issues](https://github.com/VatsalJagani/splunk-app-action/issues) to avoid duplicates
- **Provide details** - Include:
  - Clear, descriptive title
  - Steps to reproduce the issue
  - Expected vs actual behavior
  - Workflow YAML snippet (if applicable)
  - Error messages or logs
  - Operating system and runner type (e.g., ubuntu-latest)

### Feature Requests
Have an idea for an improvement?

- **Search existing issues** to see if someone else has suggested it
- **Explain the motivation** - Why would this feature be useful?
- **Provide examples** - Show how the feature would be used
- **Consider scope** - Is this feature general enough to benefit many users?

### Documentation Improvements
Documentation is crucial! You can help by:

- Fixing typos or clarifying unclear sections
- Adding more examples
- Improving troubleshooting guides
- Translating documentation (if applicable)

### Code Contributions
Ready to submit code changes?

## Making a Pull Request

### Setup Your Development Environment

1. **Fork and clone** the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/splunk-app-action.git
   cd splunk-app-action
   ```

2. **Install dependencies**:
   ```bash
   make install
   ```

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/my-new-feature
   ```

### Development Workflow

1. **Make your changes** following the coding standards
2. **Run linting**:
   ```bash
   make lint
   ```
3. **Run tests**:
   ```bash
   make test
   ```
4. **Build and validate documentation**:
   ```bash
   make docs-check
   ```
5. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add feature: description of what you did"
   ```

### Submitting Your PR

1. **Push to your fork**:
   ```bash
   git push origin feature/my-new-feature
   ```

2. **Open a Pull Request** on GitHub with:
   - Clear title describing the change
   - Description of what was changed and why
   - Link to related issues (if applicable)
   - Screenshots or examples (if applicable)

3. **Respond to feedback** - Maintainers may request changes

## Coding Standards

- Follow the existing code style
- Write clear, descriptive comments for complex logic
- Add docstrings to all classes and functions
- Keep changes focused and minimal
- Ensure all linting and tests pass

## Testing

- Add tests for new functionality
- Ensure existing tests still pass
- Test your changes with real Splunk apps when possible

## Documentation

- Update documentation for any user-facing changes
- Update CHANGELOG.md with a description of your changes
- Keep README.md in sync with significant changes

## Project-Specific Guidelines

For detailed development environment setup, coding standards, and workflow details, please refer to the development documentation:

- `devtools/development.md` - Development environment and workflow
- `README.md` - Project overview and quick start
- `CLAUDE.md` - AI assistant guidelines (if using Claude/Copilot)

## Code of Conduct

Be respectful and constructive in all interactions. We aim to maintain a welcoming and inclusive community.

## Questions?

If you have questions about contributing, feel free to:
- Open a discussion on GitHub
- Comment on related issues
- Reach out to the maintainers

Thank you for contributing to splunk-app-action! 🎉
