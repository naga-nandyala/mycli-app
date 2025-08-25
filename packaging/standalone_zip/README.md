# Standalone ZIP Packaging

Self-contained (portable) ZIP build for `MyCliApp` that bundles a minimal
Python virtual environment plus launcher scripts. This replaces / ignores the
legacy `installers/windows-exe` flow.

## Output Structure (inside produced ZIP)

```text
MyCliApp-<version>-<platform>/
  bin/
    mycli.cmd        (Windows launcher)
    mycli.sh         (POSIX launcher)
  python/            (embedded virtual environment: Scripts|bin, Lib, site-packages ...)
  README-ZIP.md      (auto-generated end‑user quick start)
  LICENSE            (copied if present)
  CHANGELOG.md       (copied if present)
  README.md          (project root README copied)
```
ZIP filename pattern: `MyCliApp-<version>-<os>-<arch>.zip` (e.g. `MyCliApp-1.2.3-windows-x64.zip`).


## Build Prerequisites

* Python 3.12+ (same version you want embedded). Build separately on each target
  OS (Windows vs Linux vs macOS) — the virtual environment is not cross‑platform.
* Project root installable via `pip install .` (PEP 517/518). Extras declared in `pyproject.toml` if you plan to include them.

## Basic Build Command

```powershell
python packaging/standalone_zip/build_zip.py
```

This uses defaults:

* extras: `azure,broker` (see `--extras` to override or supply empty)
* output dir: `dist_zip/`
* version: auto-detected from `mycli_app.__version__` (or `0.0.0` fallback)
* pruning: enabled (removes tests/, __pycache__ from site-packages)
* tooling upgrade: skipped (unless `--upgrade-tools` specified)

## Common Options

```text
--extras azure,broker   Comma-separated extras to include; use "" or omit to include none.
--version 1.4.0         Override detected version.
--output dist_custom    Destination directory for final ZIP.
--skip-prune            Keep tests/__pycache__ (disables pruning step).
--upgrade-tools         Upgrade pip/setuptools/wheel inside the temp venv first.
```

Examples:

```powershell
# Build with default extras
python packaging/standalone_zip/build_zip.py

# Build without extras
python packaging/standalone_zip/build_zip.py --extras ""

# Build specifying version and custom output directory
python packaging/standalone_zip/build_zip.py --version 1.4.0 --output artifacts

# Build keeping tests and upgrading pip tooling
python packaging/standalone_zip/build_zip.py --skip-prune --upgrade-tools
```

## End-User Usage After Extraction

Windows (PowerShell / CMD):

```powershell
bin\mycli.cmd --version
bin\mycli.cmd status
```

Linux / macOS:

```bash
chmod +x bin/mycli.sh  # first time only if not preserved
bin/mycli.sh --version
bin/mycli.sh status
```

You may add the `bin` directory to PATH for convenience.

## How It Works (High Level)

1. Creates a temporary venv (`.build_zip_tmp/venv`).
2. Optionally upgrades build tooling.
3. Installs the project (non‑editable) plus requested extras.
4. Verifies imports (`mycli_app`, `click`, etc.).
5. Prunes test/__pycache__ unless disabled.
6. Relocates venv to `python/` under a staging folder.
7. Writes launcher scripts + `README-ZIP.md`.
8. Copies metadata files.
9. Archives the staging folder into the final ZIP and removes temp build dir.

## Regenerating / Upgrading

To upgrade the distribution, rebuild on the target platform with a newer
project version and replace the extracted folder (or distribute the new ZIP).

## Troubleshooting

* If imports fail during verification, ensure extras names are correct and
  that `pyproject.toml` defines them.
* Use `--upgrade-tools` if installation fails due to outdated pip/wheel.
* Use `--skip-prune` while debugging to keep full package contents.

## See Also

Inline docstring at top of `build_zip.py` for additional context.

---
This README reflects the behavior of `build_zip.py` as of the current commit.
