# AGENTS Guidelines

This repository follows these guidelines for contributions by AI agents or humans:

1. **Commit Messages**: Use [Conventional Commits](https://www.conventionalcommits.org/) format. Examples include:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for test-related changes
   - `chore:` for maintenance tasks

2. **Simplicity First**: Prefer simpler implementations over overly complex solutions.

3. **Run Tests**: Always run tests before committing to ensure functionality and catch regressions. Use `pytest --cov=whispr tests` for Python tests.

4. **Uniform Structure**: Maintain a consistent code structure across modules so files and packages are easy to navigate.

5. **Explain Why**: Add comments explaining *why* something is done if it is not obvious from code alone.

6. **Copyright Header**: Add the following header at the beginning of every new `.py` code file created as part of PR:

```
Copyright (c) 2025 Naren Yellavula & Cybrota contributors
Apache License, Version 2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
```
7. **Branch Names**: Use '_type_/_short_topic_' convention for new branches (e.g. feat/add-s3-backup).

8. **Architectural Decision Records (ADRs)**: For non-trivial design choices, add a short ADR (docs/adr/NNN-*.md) explaining context, the decision, and alternatives.

9. **Style & Formatting**: Use ruff linter to style the code.

10. **Security**: Run `bandit` to check if code is free from security issues
