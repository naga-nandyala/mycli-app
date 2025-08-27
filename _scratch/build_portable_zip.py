#!/usr/bin/env python3
"""
Azure CLI-style Portable ZIP Builder for MyCliApp

Creates a self-contained ZIP distribution similar to Azure CLI's approach:
- Bundles a complete Python environment with all dependencies
- Includes platform-specific launchers
- No external Python installation required
- Cross-platform compatible

The resulting ZIP contains:
  MyCliApp-{version}-{platform}/
    ├── bin/
    │   ├── mycli.cmd     (Windows)
    │   └── mycli         (Unix/Linux/macOS)
    ├── lib/
    │   └── python3.x/    (Complete Python environment)
    ├── README.txt
    └── LICENSE

Usage:
    python build_portable_zip.py
    python build_portable_zip.py --version 1.2.3 --include-azure
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path


def get_project_info():
    """Get project metadata from pyproject.toml and source code."""
    project_root = Path(__file__).parent

    # Try to get version from the source
    sys.path.insert(0, str(project_root / "src"))
    try:
        from mycli_app.cli import __version__

        version = __version__
    except ImportError:
        version = "1.0.0"

    # Try to get project name from pyproject.toml
    try:
        import tomllib

        with open(project_root / "pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
        app_name = pyproject["project"]["name"]
    except (ImportError, FileNotFoundError, KeyError):
        app_name = "mycli-app"

    return {"name": app_name, "version": version, "root": project_root}


def get_platform_info():
    """Get current platform information for naming."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize architecture names
    if machine in ("x86_64", "amd64"):
        arch = "x64"
    elif machine.startswith("arm") or machine.startswith("aarch"):
        arch = "arm64"
    else:
        arch = machine

    return f"{system}-{arch}"


def create_python_environment(target_dir: Path, include_azure: bool = False):
    """Create a portable Python environment with all dependencies."""
    print("Creating Python virtual environment...")

    # Create virtual environment
    venv.create(target_dir, with_pip=True, clear=True)

    # Get pip executable path
    if os.name == "nt":
        pip_exe = target_dir / "Scripts" / "pip.exe"
        python_exe = target_dir / "Scripts" / "python.exe"
    else:
        pip_exe = target_dir / "bin" / "pip"
        python_exe = target_dir / "bin" / "python"

    print("Installing dependencies...")

    # Upgrade pip first
    subprocess.run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True)

    # Install core dependencies
    core_deps = ["click>=8.0.0", "colorama>=0.4.0"]
    subprocess.run([str(pip_exe), "install"] + core_deps, check=True)

    # Install Azure dependencies if requested
    if include_azure:
        print("Installing Azure dependencies...")
        azure_deps = ["azure-identity>=1.12.0", "azure-mgmt-core>=1.3.0", "azure-core>=1.24.0", "msal>=1.20.0"]
        subprocess.run([str(pip_exe), "install"] + azure_deps, check=True)

    # Install the CLI app itself
    project_root = get_project_info()["root"]
    extras = "[azure,broker]" if include_azure else ""
    subprocess.run([str(pip_exe), "install", "-e", f"{project_root}{extras}"], check=True)

    return python_exe


def create_launchers(dist_dir: Path, python_path: Path):
    """Create platform-specific launcher scripts."""
    bin_dir = dist_dir / "bin"
    bin_dir.mkdir(exist_ok=True)

    if os.name == "nt":
        # Windows batch file launcher
        cmd_content = """@echo off
set SCRIPT_DIR=%~dp0
set PYTHON_DIR=%SCRIPT_DIR%..\\lib\\python
"%PYTHON_DIR%\\Scripts\\python.exe" -m mycli_app.cli %*
"""
        cmd_file = bin_dir / "mycli.cmd"
        cmd_file.write_text(cmd_content, encoding="utf-8")

        # Also create a .bat version
        bat_file = bin_dir / "mycli.bat"
        bat_file.write_text(cmd_content, encoding="utf-8")

    # Unix/Linux shell script launcher (works on Windows with WSL too)
    sh_content = """#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_DIR="$SCRIPT_DIR/../lib/python"
exec "$PYTHON_DIR/bin/python" -m mycli_app.cli "$@"
"""
    sh_file = bin_dir / "mycli"
    sh_file.write_text(sh_content, encoding="utf-8")
    try:
        sh_file.chmod(0o755)  # Make executable
    except OSError:
        pass  # Windows doesn't support chmod


def create_readme(dist_dir: Path, project_info: dict, platform_tag: str, include_azure: bool):
    """Create a README file for the distribution."""
    readme_content = f"""MyCliApp Portable Distribution
================================

Version: {project_info['version']}
Platform: {platform_tag}
Azure Support: {'Included' if include_azure else 'Not included'}

This is a self-contained distribution of MyCliApp that includes a complete
Python runtime. No separate Python installation is required.

Quick Start
-----------

Windows:
  bin\\mycli.cmd --version
  bin\\mycli.cmd status
  bin\\mycli.cmd login

Linux/macOS:
  ./bin/mycli --version
  ./bin/mycli status
  ./bin/mycli login

Adding to PATH
--------------
You can add the 'bin' directory to your system PATH to use 'mycli' from anywhere:

Windows:
  1. Add the full path to the 'bin' directory to your PATH environment variable
  2. Then use: mycli --version

Linux/macOS:
  1. Add this line to your ~/.bashrc or ~/.zshrc:
     export PATH="/path/to/MyCliApp/bin:$PATH"
  2. Then use: mycli --version

Features
--------
- Azure authentication (browser, device code, Windows Hello)
- Resource management commands  
- Configuration management
- Cross-platform compatibility
- No Python installation required

Support
-------
For help and documentation, visit:
https://github.com/naga-nandyala/mycli-app

Built on: {platform.platform()}
"""

    readme_file = dist_dir / "README.txt"
    readme_file.write_text(readme_content, encoding="utf-8")


def cleanup_environment(env_dir: Path):
    """Remove unnecessary files to reduce distribution size."""
    print("Cleaning up environment...")

    # Remove test directories and __pycache__
    for root, dirs, files in os.walk(env_dir):
        # Remove __pycache__ directories
        if "__pycache__" in dirs:
            pycache_path = Path(root) / "__pycache__"
            shutil.rmtree(pycache_path, ignore_errors=True)
            dirs.remove("__pycache__")

        # Remove test directories
        for test_dir in ["tests", "test"]:
            if test_dir in dirs:
                test_path = Path(root) / test_dir
                shutil.rmtree(test_path, ignore_errors=True)
                dirs.remove(test_dir)


def build_zip_distribution(version: str = None, include_azure: bool = False, output_dir: str = None):
    """Build the complete ZIP distribution."""
    project_info = get_project_info()
    if version:
        project_info["version"] = version

    platform_tag = get_platform_info()

    # Set up directories
    if output_dir:
        output_path = Path(output_dir)
    else:
        output_path = project_info["root"] / "dist"

    output_path.mkdir(exist_ok=True)

    dist_name = f"MyCliApp-{project_info['version']}-{platform_tag}"

    print(f"Building {dist_name}...")
    print(f"Azure support: {'Yes' if include_azure else 'No'}")

    # Create temporary build directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        dist_dir = temp_path / dist_name
        dist_dir.mkdir()

        # Create Python environment
        python_env = dist_dir / "lib" / "python"
        create_python_environment(python_env, include_azure)

        # Clean up environment
        cleanup_environment(python_env)

        # Create launchers
        create_launchers(dist_dir, python_env)

        # Create README
        create_readme(dist_dir, project_info, platform_tag, include_azure)

        # Copy license and other files
        for filename in ["LICENSE", "CHANGELOG.md"]:
            src_file = project_info["root"] / filename
            if src_file.exists():
                shutil.copy2(src_file, dist_dir / filename)

        # Create ZIP file
        zip_path = output_path / f"{dist_name}.zip"
        print(f"Creating ZIP file: {zip_path}")

        shutil.make_archive(str(zip_path.with_suffix("")), "zip", root_dir=str(temp_path), base_dir=dist_name)

        # Get file size
        zip_size_mb = zip_path.stat().st_size / (1024 * 1024)

        print(f"\nSuccess! Created {zip_path}")
        print(f"Size: {zip_size_mb:.1f} MB")
        print("\nTo test the distribution:")
        print(f"1. Extract {zip_path}")
        print(f"2. Run: {dist_name}/bin/mycli{'cmd' if os.name == 'nt' else ''} --version")

        return zip_path


def main():
    parser = argparse.ArgumentParser(description="Build Azure CLI-style portable ZIP distribution for MyCliApp")
    parser.add_argument("--version", help="Override version number")
    parser.add_argument("--include-azure", action="store_true", help="Include Azure authentication dependencies")
    parser.add_argument("--output-dir", help="Output directory for ZIP file (default: ./dist)")
    parser.add_argument("--info", action="store_true", help="Show project information and exit")

    args = parser.parse_args()

    if args.info:
        project_info = get_project_info()
        platform_tag = get_platform_info()
        info = {
            "project": project_info,
            "platform": platform_tag,
            "python": {"version": sys.version, "executable": sys.executable},
        }
        print(json.dumps(info, indent=2, default=str))
        return

    try:
        zip_path = build_zip_distribution(
            version=args.version, include_azure=args.include_azure, output_dir=args.output_dir
        )
        print(f"\nBuild completed successfully: {zip_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
