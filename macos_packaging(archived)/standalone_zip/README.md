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

### Platform-Specific Build Requirements

**Windows:**

```powershell
# Ensure Python 3.12+ and pip are available
python --version
pip --version
```

**Linux:**

```bash
# Install Python and development tools
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev python3-pip
# Or on RHEL/CentOS/Fedora:
# sudo dnf install python3.12 python3.12-devel python3-pip

# Verify installation
python3.12 --version
pip --version
```

**macOS:**

```bash
# Using Homebrew
brew install python@3.12
python3.12 --version
pip --version
```

## Basic Build Command

**Windows:**

```powershell
python packaging/standalone_zip/build_zip.py
```

**Linux:**

```bash
python3.12 packaging/standalone_zip/build_zip.py
```

**macOS:**

```bash
python3.12 packaging/standalone_zip/build_zip.py
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

## Cross-Platform Building

To create distributions for multiple platforms, build on each target platform:

### Building for Windows (on Windows)

```powershell
# Create Windows distribution
python packaging/standalone_zip/build_zip.py --version 1.0.0
# Output: MyCliApp-1.0.0-windows-x64.zip
```

### Building for Linux (on Linux)

```bash
# Create Linux distribution  
python3.12 packaging/standalone_zip/build_zip.py --version 1.0.0
# Output: MyCliApp-1.0.0-linux-x64.zip

# For different architectures, build on target hardware:
# ARM64: MyCliApp-1.0.0-linux-arm64.zip
# x86: MyCliApp-1.0.0-linux-x86.zip
```

### Building for macOS (on macOS)

```bash
# Create macOS distribution
python3.12 packaging/standalone_zip/build_zip.py --version 1.0.0
# Output: MyCliApp-1.0.0-darwin-x64.zip (Intel)
# Output: MyCliApp-1.0.0-darwin-arm64.zip (Apple Silicon)
```

### Using CI/CD for Multi-Platform Builds

You can automate this process using GitHub Actions or similar CI/CD systems to build on multiple platforms simultaneously.

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

### General Issues

* If imports fail during verification, ensure extras names are correct and
  that `pyproject.toml` defines them.
* Use `--upgrade-tools` if installation fails due to outdated pip/wheel.
* Use `--skip-prune` while debugging to keep full package contents.

### Linux-Specific Issues

**Python version conflicts:**

```bash
# If 'python' points to Python 2.x, use python3.12 explicitly
which python3.12
python3.12 --version

# Create alias for convenience
alias python=python3.12
```

**Missing development packages:**

```bash
# Ubuntu/Debian - install development headers
sudo apt install python3.12-dev build-essential

# RHEL/CentOS/Fedora
sudo dnf install python3.12-devel gcc
```

**Permission issues:**

```bash
# Ensure build directory is writable
chmod 755 packaging/standalone_zip/
ls -la packaging/standalone_zip/
```

**Virtual environment creation fails:**

```bash
# Ensure venv module is available
python3.12 -m venv --help

# If missing, install python3-venv
sudo apt install python3.12-venv  # Ubuntu/Debian
sudo dnf install python3-venv     # RHEL/Fedora
```

## See Also

Inline docstring at top of `build_zip.py` for additional context.

---
This README reflects the behavior of `build_zip.py` as of the current commit.
