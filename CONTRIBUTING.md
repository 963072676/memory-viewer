# Contributing to Memory Viewer

Thank you for your interest in contributing!

## Development Setup

1. Fork the repository
2. Clone your fork
3. Install dependencies:
   ```bash
   # Backend
   cd backend && pip install -r requirements.txt
   
   # Frontend
   cd frontend && npm install
   ```

4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Style

- **Python**: Follow PEP 8, use `black` for formatting
- **TypeScript/Vue**: Follow Vue 3 style guide, use ESLint

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Describe your changes in the PR description
4. Request review from a maintainer

## Testing

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm run test

# Type checking
cd frontend && npm run type-check
```

## Commit Messages

Use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `refactor:` for code refactoring

## Reporting Issues

Please include:
- Memory Viewer version
- Steps to reproduce
- Expected vs actual behavior
- Browser/OS if applicable

## Questions?

Open an issue or join our discussions.
