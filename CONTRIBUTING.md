# Contributing to Track360

Thank you for your interest in contributing to Track360! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if applicable**
- **Include your environment details** (OS, Python version, Django version)

### Suggesting Features

Feature suggestions are welcome! Please:

- **Use a clear and descriptive title**
- **Provide a detailed description of the proposed feature**
- **Explain why this feature would be useful**
- **Include mockups or examples if applicable**

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`
3. Make your changes
4. Write or update tests as needed
5. Update documentation as needed
6. Submit a pull request

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/Track360.git
cd Track360/Portable-Dashboard-Deploy
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide. Key points:

- **Indentation**: 4 spaces (no tabs)
- **Line length**: Maximum 79 characters for code, 72 for docstrings/comments
- **Imports**: Group in order (standard library, third-party, local)
- **Naming**:
  - `snake_case` for functions and variables
  - `PascalCase` for class names
  - `UPPER_CASE` for constants

### Django Best Practices

- Use Django's ORM instead of raw SQL when possible
- Follow Django's MVT (Model-View-Template) pattern
- Use Django's built-in security features
- Write database migrations for schema changes
- Use Django's translation framework for user-facing text

### Code Quality

```bash
# Run linter (if configured)
flake8 .

# Run tests
python manage.py test

# Check for security issues
python manage.py check --deploy
```

## Commit Messages

Write clear, concise commit messages that explain what changed and why:

### Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring (no feature change)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependencies

### Examples

```
feat: Add KPI rating submission feature

- Added KPIRating model
- Created rating submission form
- Implemented rating calculation logic

Closes #123
```

```
fix: Resolve dashboard loading issue with large datasets

The dashboard was timing out when loading projects with many resources.
Optimized the query to use select_related and prefetch_related.

Fixes #456
```

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest main:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run tests** and ensure they pass:
   ```bash
   python manage.py test
   ```

3. **Update documentation** if you changed functionality

4. **Update CHANGELOG.md** with your changes

### Submitting

1. **Push to your fork**:
   ```bash
   git push origin your-feature-branch
   ```

2. **Create a Pull Request** on GitHub

3. **Fill out the PR template** completely

4. **Link related issues** using keywords (Fixes #123, Closes #456)

### PR Review Process

- Maintainers will review your PR
- Address any requested changes
- Once approved, a maintainer will merge your PR
- After merging, you can delete your branch

### PR Guidelines

- **One feature per PR**: Keep PRs focused on a single feature or fix
- **Write tests**: Include tests for new features or bug fixes
- **Update docs**: Document new features and API changes
- **Keep it small**: Smaller PRs are easier to review and merge
- **Be responsive**: Respond to review comments promptly

## Testing

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test dashboard

# Run a specific test
python manage.py test dashboard.tests.test_models.ProjectModelTest
```

### Writing Tests

- Place tests in `tests/` directory or `tests.py` file
- Use Django's `TestCase` or `TransactionTestCase`
- Test models, views, forms, and business logic
- Aim for good test coverage
- Use descriptive test names

Example:

```python
from django.test import TestCase
from dashboard.models import Project

class ProjectModelTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            name="Test Project",
            status="active"
        )
    
    def test_project_creation(self):
        self.assertEqual(self.project.name, "Test Project")
        self.assertEqual(self.project.status, "active")
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions and classes
- Update inline comments for complex logic
- Create documentation files for major features

## Questions?

If you have questions:

1. Check the [README.md](README.md)
2. Search [existing issues](https://github.com/Kamranghafar92/Track360/issues)
3. Create a new issue with the "question" label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Track360!
