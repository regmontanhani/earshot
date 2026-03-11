# Contributing to Earshot

Thanks for your interest in contributing to Earshot! This document outlines how to contribute and the standards we follow.

## Getting Started

1. **Fork the repository** - Click "Fork" on GitHub to create your own copy
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/earshot.git
   cd earshot
   ```
3. **Set up the development environment**
   ```bash
   ./setup.sh
   ```
4. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Making Changes

1. Make your changes in your feature branch
2. Test manually by running the app:
   ```bash
   ./run_app.sh          # Menu bar app
   ./earshot_run file.m4a  # CLI tool
   ```
3. Ensure your code follows the existing style

### Commit Guidelines

- Use clear, descriptive commit messages
- Keep commits focused on a single change
- Reference issues when applicable: `Fix #123: description`

### Pull Request Process

1. Push your branch to your fork
2. Open a Pull Request against `main`
3. Fill out the PR template with:
   - What the change does
   - How you tested it
   - Any breaking changes
4. Wait for review - PRs require approval before merging

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints for function signatures
- Keep functions focused and reasonably sized
- Document complex logic with comments

### Architecture Guidelines

- **Transcript format**: All modules work with the standard transcript dict:
  ```python
  {"text": "...", "segments": [{"start": 0.0, "end": 1.0, "text": "...", "speaker": "..."}]}
  ```
- **Threading**: Use daemon threads for background work, `rumps.notification()` for feedback
- **Settings**: Use `load_settings()` / `save_settings()` from `config.py`

### Testing Changes

No automated test suite exists yet. Please test manually:

- [ ] Menu bar app launches and shows icon
- [ ] File transcription works (try a short audio file)
- [ ] Live transcription works (if you have BlackHole set up)
- [ ] Settings changes persist across restarts

## Reporting Issues

When opening an issue, include:

- macOS version and chip (Intel vs Apple Silicon)
- Python version (`python3 --version`)
- Steps to reproduce the problem
- Error messages or logs (`/tmp/earshot.log`, `/tmp/earshot.error.log`)

## Feature Requests

We welcome feature ideas! Please:

- Check existing issues first to avoid duplicates
- Describe the use case, not just the solution
- Be open to discussion about implementation approaches

## Questions?

Open a Discussion or Issue if you need help getting started.
