"""Build a self-contained ZIP distribution for MyCliApp (fresh approach).

This script creates a portable ZIP similar in style to the Azure CLI
ZIP distribution: it bundles a minimal Python virtual environment with
all required packages plus handy launcher scripts so end users do NOT
need a pre-installed Python runtime.

Resulting structure inside the produced ZIP (example):

  MyCliApp-1.0.0-windows-x64/
    bin/
      mycli.cmd         (Windows launcher)
      mycli.sh          (POSIX launcher)
    python/             (embedded venv: Scripts/ or bin/, Lib/, site-packages/ ...)
    README-ZIP.md
    LICENSE
    CHANGELOG.md

Usage (builder):
  python packaging/standalone_zip/build_zip.py [--extras azure,broker] [--version 1.2.3] [--output dist_zip]

End-user usage after extraction:
  Windows:   bin\mycli.cmd --version
  Linux/mac: bin/mycli.sh --version

Notes:
  * Build on each target platform you want to distribute (Python venvs
    are not guaranteed cross-platform). Build once on Windows for a
    Windows ZIP, once on Linux for a Linux ZIP, etc.
  * This avoids PyInstaller; instead it ships a real Python runtime.
  * You can prune additional packages or __pycache__ if you need a
    smaller footprint (basic pruning included).
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
import textwrap
import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "dist_zip"


def run(cmd: list[str], cwd: Path | None = None, env: dict | None = None) -> None:
    """Run a command, raising a clearer error on failure."""
    print(f"[run] {' '.join(cmd)}")
    try:
        subprocess.check_call(cmd, cwd=str(cwd) if cwd else None, env=env)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Command failed (exit {e.returncode}): {' '.join(cmd)}") from e


def detect_version(explicit: str | None) -> str:
    if explicit:
        return explicit
    # Import version dynamically from package
    sys.path.insert(0, str(SRC_DIR))
    try:
        from mycli_app import __version__ as init_version  # type: ignore

        return init_version
    except Exception:
        # Fallback: try cli module
        try:
            from mycli_app.cli import __version__ as cli_version  # type: ignore

            return cli_version
        except Exception:
            return "0.0.0"


def current_platform_tag() -> str:
    system = platform.system().lower()
    arch = platform.machine().lower()
    # Normalize arch
    if arch in ("amd64", "x86_64"):
        arch = "x64"
    elif arch.startswith("arm64") or arch.startswith("aarch64"):
        arch = "arm64"
    return f"{system}-{arch}"


def create_venv(venv_dir: Path) -> None:
    import venv

    builder = venv.EnvBuilder(with_pip=True, clear=True, upgrade_deps=False)
    builder.create(str(venv_dir))


def pip_install(venv_dir: Path, requirements: list[str], *, upgrade: bool = False) -> None:
    """Install packages into the venv using 'python -m pip' for robustness.

    Some Windows environments block self-upgrade via the pip.exe shim; using
    'python -m pip' avoids stale entry point issues.
    """
    python_exe = venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
    cmd = [str(python_exe), "-m", "pip", "install", "--no-input", "--no-cache-dir"]
    if upgrade:
        cmd.append("--upgrade")
    cmd += requirements
    run(cmd)


def prune_site_packages(venv_dir: Path) -> None:
    site_packages = None
    if os.name == "nt":
        site_packages = venv_dir / "Lib" / "site-packages"
    else:
        # Find site-packages (typical: lib/pythonX.Y/site-packages)
        for p in (venv_dir / "lib").glob("python*/site-packages"):
            site_packages = p
            break
    if not site_packages or not site_packages.exists():
        print("[warn] site-packages not found for pruning")
        return

    removed = 0
    for root, dirs, files in os.walk(site_packages):
        for d in list(dirs):
            if d.lower() in {"tests", "test", "__pycache__"}:
                full = Path(root) / d
                try:
                    shutil.rmtree(full, ignore_errors=True)
                    removed += 1
                except Exception:
                    pass
    print(f"[info] Pruning complete. Removed {removed} test/cache directories.")


def write_launchers(dist_root: Path, venv_dir: Path) -> None:
    bin_dir = dist_root / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    if os.name == "nt":
        python_rel = "..\\python\\Scripts\\python.exe"
        content_cmd = (
            textwrap.dedent(
                f"""@echo off
            set DIR=%~dp0
            set PY={python_rel}
            "%~dp0{python_rel}" -m mycli_app.cli %*
            """  # noqa: E501
            ).strip()
            + "\n"
        )
        (bin_dir / "mycli.cmd").write_text(content_cmd, encoding="utf-8")

    # POSIX launcher (can still be useful for WSL or packaging reproducibility)
    python_rel_unix = "../python/bin/python"
    # NOTE: The variable BASH_SOURCE is part of bash, not Python; ignore name warnings.  # noqa: ERA001
    content_sh = (
        textwrap.dedent(
            f"""#!/usr/bin/env bash
        # Portable launcher for MyCliApp (POSIX)
    SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" >/dev/null 2>&1 && pwd )"
        PY="$SCRIPT_DIR/{python_rel_unix}"
        exec "$PY" -m mycli_app.cli "$@"
        """
        ).strip()
        + "\n"
    )
    sh_file = bin_dir / "mycli.sh"
    sh_file.write_text(content_sh, encoding="utf-8")
    try:
        sh_file.chmod(0o755)
    except Exception:
        pass


def write_zip_readme(dist_root: Path, version: str) -> None:
    readme_path = dist_root / "README-ZIP.md"
    content = f"""# MyCliApp Portable ZIP

Version: {version}

This is a self-contained distribution of MyCliApp including a private
Python runtime (virtual environment). No system-level installation is
required; just extract and run.

## Quick Start (Windows)
```powershell
bin\mycli.cmd --version
bin\mycli.cmd status
bin\mycli.cmd login
```

## Quick Start (Linux / macOS)
```bash
chmod +x bin/mycli.sh
bin/mycli.sh --version
bin/mycli.sh status
```

## Adding to PATH (optional)
Add the `bin` directory to your PATH to invoke `mycli` from anywhere.

## Upgrading
Download a newer ZIP and replace this directory.

## Notes
* Built on: {platform.platform()}
* Invocation uses an internal venv in `python/`.
* Do not move files within the directory structure; launchers use
  relative paths.

## License
See `LICENSE`.
"""
    readme_path.write_text(content, encoding="utf-8")


def copy_metadata(dist_root: Path) -> None:
    for fname in ["LICENSE", "CHANGELOG.md", "README.md"]:
        src = PROJECT_ROOT / fname
        if src.exists():
            shutil.copy2(src, dist_root / fname)


def relocate_venv(venv_dir: Path, dist_root: Path) -> None:
    # Keep venv under python/ for clarity
    target = dist_root / "python"
    if target.exists():
        shutil.rmtree(target)
    shutil.move(str(venv_dir), str(target))


def make_zip(folder: Path, output_dir: Path, version: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_name = f"MyCliApp-{version}-{current_platform_tag()}"
    zip_base = output_dir / zip_name
    if zip_base.with_suffix(".zip").exists():
        zip_base.with_suffix(".zip").unlink()
    shutil.make_archive(str(zip_base), "zip", root_dir=folder.parent, base_dir=folder.name)
    return zip_base.with_suffix(".zip")


def verify_install(venv_dir: Path) -> None:
    """Verify that core modules import correctly inside venv."""
    python_exe = venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
    code = "import mycli_app, mycli_app.cli, click, colorama; print('VERIFICATION_OK:'+getattr(mycli_app,'__version__','unknown'))"
    run([str(python_exe), "-c", code])


def build(extras: list[str], version: str, output_dir: Path, skip_prune: bool, upgrade_tools: bool) -> Path:
    build_root = PROJECT_ROOT / ".build_zip_tmp"
    if build_root.exists():
        shutil.rmtree(build_root)
    build_root.mkdir(parents=True)

    venv_dir = build_root / "venv"
    print("[info] Creating virtual environment...")
    create_venv(venv_dir)

    if upgrade_tools:
        print("[info] Upgrading build tooling (pip/setuptools/wheel)...")
        pip_install(venv_dir, ["pip", "setuptools", "wheel"], upgrade=True)
    else:
        print("[info] Skipping pip tooling upgrade (use --upgrade-tools to enable)")

    extras_part = f"[{','.join(extras)}]" if extras else ""
    print(f"[info] Installing project with extras: {extras if extras else 'none'}")
    # Always install the project in non-editable mode so it is self-contained
    pip_install(venv_dir, [f".{extras_part}" if extras_part else "."])

    print("[info] Verifying installation inside venv...")
    verify_install(venv_dir)

    if not skip_prune:
        print("[info] Pruning unnecessary files...")
        prune_site_packages(venv_dir)

    dist_root = build_root / f"MyCliApp-{version}-{current_platform_tag()}"
    dist_root.mkdir(parents=True)

    relocate_venv(venv_dir, dist_root)
    write_launchers(dist_root, dist_root / "python")
    write_zip_readme(dist_root, version)
    copy_metadata(dist_root)

    final_zip = make_zip(dist_root, output_dir, version)
    print(f"[success] Created ZIP: {final_zip}")

    # Clean temp working tree leaving only final zip
    shutil.rmtree(build_root)
    return final_zip


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build portable ZIP for MyCliApp")
    p.add_argument("--extras", default="azure,broker", help="Comma-separated extras to include (empty for none)")
    p.add_argument("--version", help="Override version (otherwise read from package)")
    p.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR), help="Output directory for final ZIP")
    p.add_argument("--skip-prune", action="store_true", help="Skip pruning tests/__pycache__ from site-packages")
    p.add_argument("--upgrade-tools", action="store_true", help="Upgrade pip/setuptools/wheel within venv first")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    version = detect_version(args.version)
    extras = [e.strip() for e in args.extras.split(",") if e.strip()] if args.extras else []
    output_dir = Path(args.output)
    print(
        json.dumps(
            {
                "version": version,
                "extras": extras,
                "output": str(output_dir),
                "platform": current_platform_tag(),
            },
            indent=2,
        )
    )
    build(extras, version, output_dir, args.skip_prune, args.upgrade_tools)


if __name__ == "__main__":  # pragma: no cover
    main()
