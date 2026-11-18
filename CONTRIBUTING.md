# Contributing to ORS Studio

Thank you for considering a contribution. ORS is an independent Operations Research learning and analysis tool. Correctness, clear assumptions, and maintainable code are more important than adding a large number of menu items.

## Before you start

- Read `AGENTS.md`, `.agents/rules/engineering-quality.md`, `docs/TAD.md`, and `docs/MODULE_IMPLEMENTATION_SCOPE.md`.
- Check existing issues before beginning a large change.
- Keep pull requests focused. Avoid unrelated refactors in solver changes.
- Never commit datasets, local SQLite databases, logs, virtual environments, API keys, credentials, or personal data.

## Development environment

- Windows x64 with Python 3.15.x is the supported release-build environment.
- Run `setup_windows.bat`, then `START_ORS.bat`.
- Install development dependencies with `python -m pip install -r requirements-dev.txt`.

## Required checks

```bash
python -m pytest -q
python -m compileall -q backend run_app.py
node --check frontend/js/app.js
node --check frontend/js/modules.js
node --check frontend/js/data-center.js
node --check frontend/js/batch.js
node --check frontend/js/history.js
node --check frontend/js/results.js
node --check frontend/js/api.js
```

## Solver contributions

- Define the exact model variant, input domain, assumptions, and limitations.
- Validate dimensions, finite values, bounds, probabilities, and infeasible cases.
- Add small deterministic tests with independently checkable expected results.
- Do not present a heuristic as an exact optimum.
- Do not compare models with different objectives as if they were equivalent.
- Update `docs/MODULE_IMPLEMENTATION_SCOPE.md` when scope changes.

## UI contributions

- Follow `design-system/ors-studio/MASTER.md` and the relevant page design spec.
- Prefer native semantic controls and accessible labels.
- Keep keyboard focus visible; support keyboard operation and reduced motion.
- Avoid generic dashboard templates, decorative gradients, emoji iconography, unnecessary cards, and animation that does not communicate state.
- Preserve existing element IDs and API contracts unless a coordinated refactor updates all references.

## Pull requests

Include the motivation, affected modules, tests run, screenshots for meaningful UI changes, and any changed assumptions or solver limitations. Do not claim Windows installer compatibility until the Windows workflow and clean-machine test pass.
