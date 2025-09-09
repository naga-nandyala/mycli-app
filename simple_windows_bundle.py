#!/usr/bin/env python3
"""
Simple Windows Bundle Creator for MyCLI
A minimal approach to create portable Windows bundles with just the essentials.
"""

import os
import sys
import subprocess
import zipfile
import tempfile
from pathlib import Path


def run_cmd(cmd):
    """Run a command and return success/failure."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result.returncode == 0


def create_simple_bundle(output_dir="./simple_bundle"):
    """Create a simple portable Windows bundle."""

    print("🪟 Creating Simple Windows Bundle...")

    # Ensure we're on Windows
    if os.name != "nt":
        print("❌ This script only works on Windows")
        return False

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        bundle_dir = Path(temp_dir) / "mycli-windows"
        print(f"Creating bundle in: {bundle_dir}")

        # Step 1: Create virtual environment
        if not run_cmd(f'python -m venv "{bundle_dir}"'):
            print("❌ Failed to create virtual environment")
            return False

        # Step 2: Install the application with Azure support
        venv_python = bundle_dir / "Scripts" / "python.exe"
        pip_cmd = f'"{venv_python}" -m pip'

        # Upgrade pip
        run_cmd(f"{pip_cmd} install --upgrade pip")

        # Install our app with Azure extras
        project_root = Path(__file__).parent
        if not run_cmd(f'{pip_cmd} install "{project_root}[azure,broker]"'):
            print("❌ Failed to install application")
            return False

        # Step 3: Create simple launcher
        create_simple_launcher(bundle_dir / "Scripts")

        # Step 4: Clean up unnecessary files to reduce bundle size
        cleanup_bundle(bundle_dir)

        # Step 5: Create ZIP distribution
        zip_path = output_path / "mycli-windows-portable.zip"
        print(f"Creating ZIP: {zip_path}")

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in bundle_dir.rglob("*"):
                if file_path.is_file():
                    arc_name = file_path.relative_to(bundle_dir)
                    zf.write(file_path, arc_name)

        zip_size = zip_path.stat().st_size / (1024 * 1024)
        print(f"✅ Created: {zip_path.name} ({zip_size:.1f} MB)")

        # Step 6: Create simple usage instructions
        create_usage_instructions(output_path)

        return True


def cleanup_bundle(bundle_dir):
    """Clean up unnecessary files to reduce bundle size (similar to complex script)."""
    import shutil

    print("🧹 Cleaning up bundle to reduce size...")

    files_removed = 0
    dirs_removed = 0
    bytes_saved = 0

    # Remove __pycache__ directories (biggest space saver)
    for pycache_dir in bundle_dir.rglob("__pycache__"):
        if pycache_dir.is_dir():
            # Calculate size before removal
            try:
                dir_size = sum(f.stat().st_size for f in pycache_dir.rglob("*") if f.is_file())
                bytes_saved += dir_size
                shutil.rmtree(pycache_dir)
                dirs_removed += 1
                print(f"Removed cache: {pycache_dir.relative_to(bundle_dir)}")
            except (PermissionError, OSError) as e:
                print(f"Could not remove {pycache_dir.relative_to(bundle_dir)}: {e}")

    # Remove unnecessary pip executables
    scripts_dir = bundle_dir / "Scripts"
    if scripts_dir.exists():
        for pip_exe in scripts_dir.glob("pip*.exe"):
            try:
                file_size = pip_exe.stat().st_size
                bytes_saved += file_size
                pip_exe.unlink()
                files_removed += 1
                print(f"Removed executable: {pip_exe.name}")
            except (PermissionError, OSError) as e:
                print(f"Could not remove {pip_exe.name}: {e}")

        # Remove easy_install executables
        for easy_install_exe in scripts_dir.glob("easy_install*.exe"):
            try:
                file_size = easy_install_exe.stat().st_size
                bytes_saved += file_size
                easy_install_exe.unlink()
                files_removed += 1
                print(f"Removed executable: {easy_install_exe.name}")
            except (PermissionError, OSError) as e:
                print(f"Could not remove {easy_install_exe.name}: {e}")

    # Remove test directories (be careful not to remove Azure test files)
    for test_dir in bundle_dir.rglob("test*"):
        if test_dir.is_dir() and "azure" not in str(test_dir).lower():
            try:
                dir_size = sum(f.stat().st_size for f in test_dir.rglob("*") if f.is_file())
                bytes_saved += dir_size
                shutil.rmtree(test_dir)
                dirs_removed += 1
                print(f"Removed test dir: {test_dir.relative_to(bundle_dir)}")
            except (PermissionError, OSError) as e:
                print(f"Could not remove {test_dir.relative_to(bundle_dir)}: {e}")

    # Remove .pyc and .pyo files
    for compiled_file in bundle_dir.rglob("*.py[co]"):
        try:
            file_size = compiled_file.stat().st_size
            bytes_saved += file_size
            compiled_file.unlink()
            files_removed += 1
        except (PermissionError, OSError):
            pass  # Skip files in use

    # Summary
    mb_saved = bytes_saved / (1024 * 1024)
    print(f"✅ Cleanup complete: Removed {dirs_removed} directories, {files_removed} files")
    print(f"💾 Space saved: {mb_saved:.1f} MB")


def create_simple_launcher(scripts_dir):
    """Create a simple, robust launcher script."""

    launcher_content = """@echo off
REM Simple MyCLI Launcher for Windows
REM Auto-detects bundle structure and runs the application

setlocal
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Find Python executable
if exist "%SCRIPT_DIR%\\python.exe" (
    set "PYTHON=%SCRIPT_DIR%\\python.exe"
) else (
    echo Error: Python interpreter not found in bundle
    pause
    exit /b 1
)

REM Run the application
"%PYTHON%" -c "from mycli_app.cli import main; main()" %*
"""

    launcher_path = scripts_dir / "mycli.bat"
    with open(launcher_path, "w", newline="\r\n") as f:
        f.write(launcher_content)

    print(f"✅ Created launcher: {launcher_path}")


def create_usage_instructions(output_path):
    """Create simple usage instructions."""

    instructions = """# MyCLI Windows Portable Bundle

## Quick Start

1. **Extract the ZIP file** to any directory on your Windows system
2. **Run the application** using one of these methods:

### Method 1: Direct execution
```cmd
cd mycli-windows
Scripts\\mycli.bat --help
Scripts\\mycli.bat login
```

### Method 2: Add to PATH (optional)
```cmd
REM Add the Scripts directory to your PATH
set PATH=%PATH%;C:\\path\\to\\mycli-windows\\Scripts

REM Now you can run from anywhere
mycli --help
mycli login
```

## What's Included

- ✅ Python interpreter (bundled)
- ✅ All Azure SDK dependencies 
- ✅ MyCLI application
- ✅ Simple launcher script
- ✅ Portable - no installation required

## Requirements

- Windows 10 or newer
- No Python installation required
- ~50-100MB disk space

## Troubleshooting

**"Python interpreter not found"**: Make sure you extracted the full ZIP contents

**"Module not found"**: The bundle may be incomplete - try re-extracting

**Azure login issues**: Make sure you have internet connection for authentication

## Distribution

This bundle can be:
- Shared via ZIP file
- Uploaded to file sharing services
- Distributed via network drives
- Added to software repositories

No installation or admin rights required!
"""

    readme_path = output_path / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(instructions)

    print(f"✅ Created instructions: {readme_path}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Create simple Windows bundle for MyCLI")
    parser.add_argument("--output", "-o", default="./simple_bundle", help="Output directory (default: ./simple_bundle)")

    args = parser.parse_args()

    if create_simple_bundle(args.output):
        print("\n🎉 SUCCESS! Simple bundle created.")
        print(f"\n📁 Files in {args.output}:")
        output_path = Path(args.output)
        for file_path in output_path.iterdir():
            if file_path.is_file():
                size = file_path.stat().st_size / (1024 * 1024)
                print(f"   📄 {file_path.name} ({size:.1f} MB)")

        print("\n🚀 Next steps:")
        print("1. Extract the ZIP file to test it")
        print("2. Run: extracted_folder\\Scripts\\mycli.bat --help")
        print("3. Share the ZIP file for distribution")
    else:
        print("\n❌ Failed to create bundle")
        return 1


if __name__ == "__main__":
    sys.exit(main())
