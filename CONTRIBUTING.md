# Contributing to Mr. F

First off, thank you for considering contributing to Mr. F! It's people like you that make Mr. F such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed and what behavior you expected**
* **Include logs if possible**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title**
* **Provide a detailed description of the suggested enhancement**
* **Explain why this enhancement would be useful**
* **List some examples of how this enhancement would be used**

### Pull Requests

* Fill in the required template
* Follow the Python style guide (PEP 8)
* Include tests for new features
* Update documentation as needed
* Ensure all tests pass

## Development Setup

### Prerequisites

* Python 3.11+
* Git
* OpenRouter API key (or other LLM provider)

### Setting Up Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/mr._F.git
cd mr._F

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (if any)
pip install -r requirements.txt  # When we have requirements

# Set up environment variables
export OPENROUTER_API_KEY=your-api-key
export OPENROUTER_MODEL=openrouter/free
```

### Running Tests

```bash
# Run the test suite
cd workspace
python tests.py

# Run evaluator tests
python core/evaluator.py
```

### Running Evolution

```bash
# Run a single evolution step
python core/runner.py

# Check results
cat runs/latest/result.json
cat core/JOURNAL.md
```

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Python Styleguide

* Follow PEP 8
* Use 4 spaces for indentation
* Limit lines to 100 characters
* Use docstrings for functions and classes
* Write meaningful variable names

### Documentation Styleguide

* Use Markdown for documentation files
* Reference other documentation where appropriate
* Keep examples up-to-date
* Use clear, concise language

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Something isn't working correctly
* `enhancement` - New feature request
* `documentation` - Documentation improvements
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `question` - Further information is requested

### Architecture Decisions

When making significant architectural changes:

1. Create an Architecture Decision Record (ADR)
2. Discuss in a GitHub issue first
3. Get feedback from maintainers
4. Document the decision in docs/architecture/

### Testing Philosophy

* Tests must pass before any change is accepted
* Test coverage should not decrease
* Write tests before adding features (TDD when possible)
* Tests should be fast and deterministic

### Memory and Learning

* All evolution sessions are logged to `memory/journal.jsonl`
* Failures are tracked in `memory/failures.json`
* Successes are synthesized in `memory/summaries.json`
* Never delete journal entries - they are the memory of the system

### Safety First

* Never compromise safety constraints
* Always validate syntax before applying changes
* Always run tests before accepting changes
* Revert immediately on any regression

## Questions?

Feel free to open an issue with the "question" label if you have any questions about contributing!

---

Thank you for contributing to Mr. F! 🚀
