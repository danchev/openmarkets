# Python 3.11 Minimum Implementation Plan

## Design overview

Raise the package minimum from Python 3.10 to 3.11 so every supported environment can use Pillow 13.0.0, which resolves the documentation imaging security finding. Keep package metadata, lint target, lockfile, and CI coverage aligned.

## Class diagram

No class or runtime type changes are involved.

## Entity relationship diagram

No data entities or relationships change.

## Implementation steps

1. Update `pyproject.toml` classifiers, `requires-python`, and Ruff target version.
2. Regenerate `uv.lock` with Pillow 13.0.0 and update vulnerable locked dependencies identified by the security audit.
3. Keep the CI Python matrix beginning at 3.11 and verify locked dependency resolution and the audit.

## Verification

Run `uv lock --check`, `uv sync --locked --all-groups --all-extras --python 3.11`, and `uv audit --locked`. Confirm no Python 3.10 support declaration or Pillow 12.3.0 resolution remains.
