---
name: verify
description: Run full offline verification suite (pytest unit tests + mypy + ruff) before committing changes.
disable-model-invocation: true
---

# Verify

Run the full offline verification pipeline:

1. Run `python -m pytest tests/unit/ -v` — all unit tests must pass.
2. Run `mypy src/` — strict type checking must pass with zero errors.
3. Run `ruff check src/ tests/` — no lint errors.
4. Run `ruff format --check src/ tests/` — formatting must be clean.

If any step fails, fix the issues and re-run. Do not report completion until all four steps pass.
