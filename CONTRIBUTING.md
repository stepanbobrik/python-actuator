<!--
SPDX-FileCopyrightText: 2026 Bobrik Stepan
SPDX-License-Identifier: MIT
-->

# Contributing

Contributions are welcome through pull requests.

## Development setup

The project uses Python 3.12 or newer and `uv`:

```bash
uv sync --all-groups
make check
```

## Pull requests

1. Fork the repository and create a focused branch.
2. Add or update tests and documentation with the change.
3. Run `make check` before opening the pull request.
4. Explain the motivation and compatibility impact in the pull request.

Do not include credentials, private keys, or unrelated formatting changes.

Commit messages should follow Conventional Commits, for example:

```text
feat: add redis health indicator
fix: return service unavailable for down checks
```
