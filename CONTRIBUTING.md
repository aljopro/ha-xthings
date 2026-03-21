# Contributing to Xthings (U-tec) Integration

Contributing to this project should be as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

## GitHub is used for everything

GitHub is used to host code, to track issues and feature requests, as well as accept pull requests.

## Getting started

```bash
# Fork and clone the repo
git clone https://github.com/<your-username>/ha-xthings.git
cd ha-xthings

# Install dev dependencies
scripts/setup

# Run the linter
scripts/lint
```

## Branch strategy

1. Fork the repo and create a branch from `main`:
   - `feature/<description>` for new features
   - `fix/<description>` for bug fixes
   - `chore/<description>` for maintenance
2. Make your changes in small, focused commits.
3. If you've changed something, update the documentation.
4. Make sure your code lints: `scripts/lint`
5. Test your changes (see [Testing](#testing) below).
6. Open a pull request against `main`.
7. Label your PR with the appropriate label (`enhancement`, `bug`, `breaking`, `documentation`, etc.) — this drives automatic release notes.

## Testing

### Unit tests

```bash
python3 -m pytest tests/test_unit.py -v
```

### Docker integration testing

Spin up a local Home Assistant instance with the component mounted:

```bash
docker compose up
```

This mounts `custom_components/` into the HA container. Config is in `docker/configuration.yaml`. After making changes, restart the container to pick them up.

### Local development

```bash
scripts/develop
```

This starts Home Assistant with `custom_components/` on `PYTHONPATH`, using a local `config/` directory.

## Code style

- We use **Ruff** for linting and formatting (configured in `.ruff.toml`).
- Run `scripts/lint` to auto-format and fix lint issues.
- CI runs `ruff check .` and `ruff format . --check` on every PR.
- Follow the patterns documented in `.instructions.md`, particularly:
  - Entity base class pattern (`entity.py`)
  - Coordinator pattern
  - API client exception hierarchy

## Releases

Releases are automated. When PRs are merged to `main`:

1. **Release Drafter** auto-updates a draft release with notes grouped by PR labels.
2. Version is auto-resolved from labels: `breaking` → major, `enhancement` → minor, `bug` → patch.
3. A maintainer triggers the "Release" workflow from GitHub Actions to publish.
4. The workflow bumps `manifest.json`, creates a tag, and publishes the GitHub release.
5. HACS picks up the new version automatically.

## Report bugs

GitHub issues are used to track bugs. Report a bug by [opening a new issue](https://github.com/aljopro/ha-xthings/issues/new/choose).

**Great bug reports** include:

- System Health details from Home Assistant
- Steps to reproduce (be specific!)
- What you expected vs. what actually happened
- Debug logs (enable via **Settings → System → Logs**, filter for `xthings`)

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
