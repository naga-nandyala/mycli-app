#!/usr/bin/env python3
"""
Create a Windows-specific portable bundle for mycli-app.
This script is designed to run on Windows and create packages suitable for distribution.
Similar to the macOS bundling approach but adapted for Windows specifics.
"""

import os
import sys
import shutil
import subprocess
import zipfile
import argparse
import tempfile
import json
import platform
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    # Don't use shell=True for list commands to avoid path issues
    use_shell = not isinstance(cmd, list)
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False, shell=use_shell)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error output: {result.stderr}")
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def run_command_with_env(cmd, env_vars, cwd=None, check=True):
    """Run a command with custom environment variables."""
    print(f"Running with custom env: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    # Don't use shell=True for list commands to avoid path issues
    use_shell = not isinstance(cmd, list)
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False, env=env_vars, shell=use_shell)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error output: {result.stderr}")
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
    return result


def get_windows_info():
    """Get Windows system information."""
    import winreg

    system_info = {
        "platform": platform.system(),
        "machine": platform.machine(),
        "release": platform.release(),
        "version": platform.version(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }

    # Get Windows version details
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
            try:
                system_info["windows_version"] = winreg.QueryValueEx(key, "DisplayVersion")[0]
            except FileNotFoundError:
                system_info["windows_version"] = winreg.QueryValueEx(key, "ReleaseId")[0]

            system_info["windows_build"] = winreg.QueryValueEx(key, "CurrentBuild")[0]
            system_info["windows_product"] = winreg.QueryValueEx(key, "ProductName")[0]
    except Exception as e:
        print(f"Warning: Could not get detailed Windows version info: {e}")
        system_info["windows_version"] = platform.version()

    return system_info


def create_windows_venv_bundle(output_dir, python_version=None, arch=None, version=None):
    """Create a Windows-specific virtual environment bundle."""

    # Ensure we're on Windows
    if platform.system() != "Windows":
        print("❌ Error: This script is designed for Windows only.")
        print(f"Current platform: {platform.system()}")
        print("Please run this script on Windows.")
        sys.exit(1)

    # Get system info
    system_info = get_windows_info()
    print(f"Building for {system_info['windows_product']}")
    print(f"Version: {system_info['windows_version']} (Build {system_info['windows_build']})")
    print(f"Architecture: {system_info['machine']}")
    print(f"Python version: {system_info['python_version']}")

    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Create temporary directory for building
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        bundle_name = f"mycli-{system_info['machine']}"
        bundle_path = temp_path / bundle_name

        print(f"Creating Windows bundle in: {bundle_path}")

        # Step 1: Create virtual environment
        python_exe = sys.executable if not python_version else f"python{python_version}"
        run_command([python_exe, "-m", "venv", str(bundle_path)])

        # Windows-specific paths - resolve to avoid short name issues
        venv_python = bundle_path / "Scripts" / "python.exe"
        scripts_dir = bundle_path / "Scripts"

        # Resolve the actual path to avoid Windows short name issues
        venv_python_resolved = venv_python.resolve()
        if not venv_python_resolved.exists():
            raise Exception(f"Virtual environment Python not found at {venv_python_resolved}")

        print(f"Virtual environment Python: {venv_python_resolved}")

        # Use python -m pip for better reliability with resolved path
        pip_cmd = [str(venv_python_resolved), "-m", "pip"]

        # Set environment variables for Windows builds
        env_vars = os.environ.copy()
        target_arch = arch or system_info["machine"]
        print(f"Building for architecture: {target_arch}")

        # Step 2: Upgrade pip and install wheel
        run_command_with_env(pip_cmd + ["install", "--upgrade", "pip", "wheel"], env_vars)

        # Step 3: Install dependencies
        install_args = pip_cmd + ["install", "--no-cache-dir"]

        # Install project dependencies from pyproject.toml
        project_root = Path(__file__).parent.parent.parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            print("Installing from pyproject.toml...")
            # First install the Azure dependencies explicitly
            print("Installing Azure dependencies explicitly...")
            azure_dependencies = [
                "azure-identity>=1.12.0",
                "azure-mgmt-core>=1.3.0",
                "azure-core>=1.24.0",
                "msal[broker]>=1.20.0,<2",
            ]
            run_command_with_env(install_args + azure_dependencies, env_vars)

            # Force reinstall azure-core to ensure all submodules are present
            print("Force reinstalling azure-core to ensure completeness...")
            force_reinstall_args = pip_cmd + ["install", "--force-reinstall", "--no-deps"]
            run_command_with_env(force_reinstall_args + ["azure-core>=1.24.0"], env_vars)

            # Then reinstall dependencies for azure-core
            azure_core_args = pip_cmd + ["install"]
            run_command_with_env(azure_core_args + ["azure-core>=1.24.0"], env_vars)

            # Then install the project with optional dependencies [azure,broker]
            print("Installing mycli-app package with [azure,broker] extras...")
            project_install_args = pip_cmd + ["install"]
            run_command_with_env(project_install_args + [f"{project_root}[azure,broker]"], env_vars)

            # List installed packages for debugging
            print("\nInstalled packages:")
            run_command(pip_cmd + ["list"], check=False)

            # Check for Azure packages specifically
            print("\nChecking for Azure packages:")
            azure_check = run_command(pip_cmd + ["show", "azure-core"], check=False)
            if azure_check.returncode == 0:
                print("azure-core is installed")
            else:
                print("azure-core is NOT installed")

            azure_identity_check = run_command(pip_cmd + ["show", "azure-identity"], check=False)
            if azure_identity_check.returncode == 0:
                print("azure-identity is installed")
            else:
                print("azure-identity is NOT installed")
        else:
            # Fallback: Install basic dependencies manually
            print("Installing basic dependencies...")
            dependencies = [
                "click>=8.0.0",
                "colorama>=0.4.0",
                "azure-identity>=1.12.0",
                "azure-mgmt-core>=1.3.0",
                "azure-core>=1.24.0",
                "msal[broker]>=1.20.0,<2",
            ]
            run_command(install_args + dependencies)

            # Install the package itself
            print("Installing mycli-app package...")
            run_command_with_env(pip_cmd + ["install", str(project_root)], env_vars)

        # Step 4: Create Windows-specific launcher scripts
        create_windows_launcher(bundle_path, scripts_dir)

        # Step 5: Create application bundle metadata
        create_bundle_metadata(bundle_path, system_info, arch)

        # Step 6: Clean up unnecessary files
        cleanup_bundle(bundle_path)

        # Step 6.5: Verify bundle functionality before distribution
        verify_bundle_functionality(bundle_path)

        # Step 7: Create distribution packages
        create_distribution_packages(bundle_path, output_path, bundle_name, system_info, arch, version)

        print("\n✅ Windows bundle created successfully!")
        return bundle_path


def create_windows_launcher(bundle_path, scripts_dir):
    """Create Windows-specific launcher scripts."""
    print("Setting up launcher...")

    # Check if pip created a console script during installation
    pip_generated_script = scripts_dir / "mycli.exe"

    if pip_generated_script.exists():
        print("Found pip-generated console script (.exe), creating portable version...")

        # Create a batch file wrapper for better path handling
        portable_bat_content = """@echo off
setlocal EnableDelayedExpansion

REM MyCLI Portable Console Script for Windows
REM Auto-generated to replace pip's hardcoded-path version

REM Get the directory containing this script
set "SCRIPT_DIR=%~dp0"

REM Remove trailing backslash
if "%SCRIPT_DIR:~-1%"=="\\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

REM Look for Python interpreter - handle different installation patterns
set "BUNDLE_PYTHON="

REM Method 1: Same directory (direct bundle use)
if exist "%SCRIPT_DIR%\\python.exe" (
    set "BUNDLE_PYTHON=%SCRIPT_DIR%\\python.exe"
    goto :found_python
)

REM Method 2: Check if we're in a standard bundle structure
if exist "%SCRIPT_DIR%\\..\\Scripts\\python.exe" (
    set "BUNDLE_PYTHON=%SCRIPT_DIR%\\..\\Scripts\\python.exe"
    goto :found_python
)

REM Method 3: Look for bundle structure patterns
for %%P in (
    "%SCRIPT_DIR%\\..\\..\\Scripts\\python.exe"
    "%SCRIPT_DIR%\\python.exe"
    "%SCRIPT_DIR%\\..\\python.exe"
) do (
    if exist "%%P" (
        set "BUNDLE_PYTHON=%%P"
        goto :found_python
    )
)

:found_python
REM If we still can't find Python, provide comprehensive debugging
if "%BUNDLE_PYTHON%"=="" (
    echo Error: Bundle Python interpreter not found >&2
    echo Debug: Comprehensive directory listing: >&2
    echo Debug: Current working directory: >&2
    cd >&2
    echo Debug: Script directory ^(%SCRIPT_DIR%^): >&2
    dir "%SCRIPT_DIR%" >&2 2>nul || echo Could not list %SCRIPT_DIR% >&2
    echo Debug: Parent directory: >&2
    dir "%SCRIPT_DIR%\\.." >&2 2>nul || echo Could not list parent >&2
    echo Debug: Grandparent directory: >&2
    dir "%SCRIPT_DIR%\\..\\.." >&2 2>nul || echo Could not list grandparent >&2
    exit /b 1
)

if not exist "%BUNDLE_PYTHON%" (
    echo Error: Bundle Python interpreter not found at %BUNDLE_PYTHON% >&2
    exit /b 1
)

REM Execute the main CLI function with debug information
"%BUNDLE_PYTHON%" -c "import sys; import os; print('Debug: Python executable:', sys.executable, file=sys.stderr); print('Debug: Python path:', sys.path, file=sys.stderr); [print(f'Debug: Found site-packages at: {path}', file=sys.stderr) for path in sys.path if 'site-packages' in path]; [print(f'Debug: Azure packages found at: {os.path.join(path, \"azure\")}', file=sys.stderr) if os.path.exists(os.path.join(path, 'azure')) else print(f'Debug: No azure packages at: {os.path.join(path, \"azure\")}', file=sys.stderr) for path in sys.path if 'site-packages' in path]; exec('try:\\n    import azure.identity; print(f\"Debug: azure.identity imported successfully from {azure.identity.__file__}\", file=sys.stderr)\\nexcept ImportError as e:\\n    print(f\"Debug: azure.identity import failed: {e}\", file=sys.stderr)'); exec('try:\\n    import azure.core; print(f\"Debug: azure.core imported successfully from {azure.core.__file__}\", file=sys.stderr)\\nexcept ImportError as e:\\n    print(f\"Debug: azure.core import failed: {e}\", file=sys.stderr)'); from mycli_app.cli import main; sys.exit(main())" %*
"""

        # Write the portable batch script
        portable_bat_path = scripts_dir / "mycli.bat"
        with open(portable_bat_path, "w", newline="\r\n") as f:
            f.write(portable_bat_content)

        print("  Created portable console script (.bat)")

        # Also create PowerShell version for flexibility
        ps_launcher_content = """# MyCLI Windows PowerShell Launcher
param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Get the directory containing this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ScriptDir "python.exe"

# Look for Python interpreter - handle different installation patterns
$BundlePython = $null

# Method 1: Same directory (direct bundle use)
if (Test-Path (Join-Path $ScriptDir "python.exe")) {
    $BundlePython = Join-Path $ScriptDir "python.exe"
}
# Method 2: Check if we're in a standard bundle structure
elseif (Test-Path (Join-Path $ScriptDir ".." "Scripts" "python.exe")) {
    $BundlePython = Join-Path $ScriptDir ".." "Scripts" "python.exe"
}
# Method 3: Look for bundle structure patterns
else {
    $PossiblePaths = @(
        (Join-Path $ScriptDir ".." ".." "Scripts" "python.exe"),
        (Join-Path $ScriptDir "python.exe"),
        (Join-Path $ScriptDir ".." "python.exe")
    )
    foreach ($Path in $PossiblePaths) {
        if (Test-Path $Path) {
            $BundlePython = $Path
            break
        }
    }
}

# If we still can't find Python, provide comprehensive debugging
if (-not $BundlePython) {
    Write-Error "Error: Bundle Python interpreter not found"
    Write-Error "Debug: Current working directory: $(Get-Location)"
    Write-Error "Debug: Script directory: $ScriptDir"
    if (Test-Path $ScriptDir) {
        Write-Error "Debug: Script directory contents:"
        Get-ChildItem $ScriptDir | ForEach-Object { Write-Error "  $_" }
    }
    exit 1
}

if (-not (Test-Path $BundlePython)) {
    Write-Error "Error: Bundle Python interpreter not found at $BundlePython"
    exit 1
}

# Execute the main CLI function with debug information
$PythonScript = @"
import sys
import os

# Debug: Print Python path information
print('Debug: Python executable:', sys.executable, file=sys.stderr)
print('Debug: Python path:', sys.path, file=sys.stderr)

# Debug: Try to find site-packages
for path in sys.path:
    if 'site-packages' in path:
        print(f'Debug: Found site-packages at: {path}', file=sys.stderr)
        # Check if azure packages exist
        azure_path = os.path.join(path, 'azure')
        if os.path.exists(azure_path):
            print(f'Debug: Azure packages found at: {azure_path}', file=sys.stderr)
        else:
            print(f'Debug: No azure packages at: {azure_path}', file=sys.stderr)

# Debug: Test Azure imports before running main
try:
    import azure.identity
    print(f'Debug: azure.identity imported successfully from {azure.identity.__file__}', file=sys.stderr)
except ImportError as e:
    print(f'Debug: azure.identity import failed: {e}', file=sys.stderr)

try:
    import azure.core
    print(f'Debug: azure.core imported successfully from {azure.core.__file__}', file=sys.stderr)
except ImportError as e:
    print(f'Debug: azure.core import failed: {e}', file=sys.stderr)

from mycli_app.cli import main
if __name__ == '__main__':
    sys.exit(main())
"@

& $BundlePython -c $PythonScript @Arguments
"""

        ps_launcher_path = scripts_dir / "mycli.ps1"
        with open(ps_launcher_path, "w", newline="\r\n", encoding="utf-8") as f:
            f.write(ps_launcher_content)

        print("  Created portable PowerShell script (.ps1)")
        return

    print("No pip-generated console script found, creating custom launcher...")

    # Main launcher batch script (fallback if console scripts don't work)
    launcher_content = """@echo off
setlocal EnableDelayedExpansion

REM MyCLI Windows Launcher
REM This script provides a portable way to run mycli on Windows

REM Get the directory containing this script
set "SCRIPT_DIR=%~dp0"
if "%SCRIPT_DIR:~-1%"=="\\" set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

set "BUNDLE_ROOT=%SCRIPT_DIR%\\.."
set "VENV_PYTHON=%SCRIPT_DIR%\\python.exe"

REM Check if we're in the correct bundle structure
if not exist "%VENV_PYTHON%" (
    echo Error: mycli bundle not found or corrupted >&2
    echo Expected Python at: %VENV_PYTHON% >&2
    exit /b 1
)

REM Set up environment
for /f "delims=" %%i in ('dir /b /s "%BUNDLE_ROOT%\\Lib\\site-packages" 2^>nul ^| findstr /i site-packages ^| head -1') do set "PYTHON_SITEPKG=%%i"
if defined PYTHON_SITEPKG (
    set "PYTHONPATH=%PYTHON_SITEPKG%;%PYTHONPATH%"
)

REM Alternative method: try to use the venv activation if available
set "VENV_ACTIVATE=%BUNDLE_ROOT%\\Scripts\\activate.bat"
if exist "%VENV_ACTIVATE%" (
    call "%VENV_ACTIVATE%"
)

REM Try to run the application with proper error handling
"%VENV_PYTHON%" -c "import mycli_app.cli" 2>nul
if %errorlevel% neq 0 (
    echo Error: Could not import mycli_app.cli module >&2
    echo Bundle structure may be incomplete >&2
    echo Python path: %PYTHONPATH% >&2
    echo Site packages: %PYTHON_SITEPKG% >&2
    exit /b 1
)

REM Execute the main CLI function
"%VENV_PYTHON%" -c "import sys; import os; print('Debug: Python executable:', sys.executable, file=sys.stderr); print('Debug: Python path:', sys.path, file=sys.stderr); [print(f'Debug: Found site-packages at: {path}', file=sys.stderr) for path in sys.path if 'site-packages' in path]; [print(f'Debug: Azure packages found at: {os.path.join(path, \"azure\")}', file=sys.stderr) if os.path.exists(os.path.join(path, 'azure')) else print(f'Debug: No azure packages at: {os.path.join(path, \"azure\")}', file=sys.stderr) for path in sys.path if 'site-packages' in path]; exec('try:\\n    import azure.identity; print(f\"Debug: azure.identity imported successfully from {azure.identity.__file__}\", file=sys.stderr)\\nexcept ImportError as e:\\n    print(f\"Debug: azure.identity import failed: {e}\", file=sys.stderr)'); exec('try:\\n    import azure.core; print(f\"Debug: azure.core imported successfully from {azure.core.__file__}\", file=sys.stderr)\\nexcept ImportError as e:\\n    print(f\"Debug: azure.core import failed: {e}\", file=sys.stderr)'); from mycli_app.cli import main; main()" %*
"""

    launcher_path = scripts_dir / "mycli.bat"
    with open(launcher_path, "w", newline="\r\n") as f:
        f.write(launcher_content)

    # Create PowerShell launcher as well
    ps_launcher_content = """# MyCLI Windows PowerShell Launcher
param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Get the directory containing this script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BundleRoot = Split-Path -Parent $ScriptDir
$VenvPython = Join-Path $ScriptDir "python.exe"

# Check if we're in the correct bundle structure
if (-not (Test-Path $VenvPython)) {
    Write-Error "Error: mycli bundle not found or corrupted"
    Write-Error "Expected Python at: $VenvPython"
    exit 1
}

# Set up environment
$PythonSitePkg = Get-ChildItem -Path "$BundleRoot\\Lib" -Recurse -Directory -Name "site-packages" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($PythonSitePkg) {
    $env:PYTHONPATH = "$BundleRoot\\Lib\\$PythonSitePkg;$env:PYTHONPATH"
}

# Execute the main CLI function
$PythonScript = @"
import sys
import os

# Debug: Print Python path information
print('Debug: Python executable:', sys.executable, file=sys.stderr)
print('Debug: Python path:', sys.path, file=sys.stderr)

# Debug: Try to find site-packages
for path in sys.path:
    if 'site-packages' in path:
        print(f'Debug: Found site-packages at: {path}', file=sys.stderr)
        # Check if azure packages exist
        azure_path = os.path.join(path, 'azure')
        if os.path.exists(azure_path):
            print(f'Debug: Azure packages found at: {azure_path}', file=sys.stderr)
        else:
            print(f'Debug: No azure packages at: {azure_path}', file=sys.stderr)

# Debug: Test Azure imports before running main
try:
    import azure.identity
    print(f'Debug: azure.identity imported successfully from {azure.identity.__file__}', file=sys.stderr)
except ImportError as e:
    print(f'Debug: azure.identity import failed: {e}', file=sys.stderr)

try:
    import azure.core
    print(f'Debug: azure.core imported successfully from {azure.core.__file__}', file=sys.stderr)
except ImportError as e:
    print(f'Debug: azure.core import failed: {e}', file=sys.stderr)

from mycli_app.cli import main
if __name__ == '__main__':
    sys.exit(main())
"@

& $VenvPython -c $PythonScript @Arguments
"""

    ps_launcher_path = scripts_dir / "mycli.ps1"
    with open(ps_launcher_path, "w", newline="\r\n", encoding="utf-8") as f:
        f.write(ps_launcher_content)

    print("Custom batch and PowerShell launchers created")


def create_bundle_metadata(bundle_path, system_info, arch):
    """Create metadata for the Windows bundle."""

    # Determine architecture
    target_arch = arch or system_info["machine"]

    metadata = {
        "name": "mycli-windows-bundle",
        "version": "1.0.0",  # This should be dynamic based on your app version
        "description": "Portable Windows bundle for MyCLI application",
        "target_platform": "Windows",
        "target_architecture": target_arch,
        "windows_version": system_info.get("windows_version"),
        "windows_build": system_info.get("windows_build"),
        "windows_product": system_info.get("windows_product"),
        "python_version": system_info["python_version"],
        "build_date": subprocess.run(
            ["powershell", "-Command", "Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ'"],
            capture_output=True,
            text=True,
            shell=True,
        ).stdout.strip(),
        "bundle_structure": {
            "Scripts/": "Executables and launcher scripts",
            "Lib/": "Python libraries and dependencies",
            "Include/": "Header files (if needed)",
            "share/": "Shared resources (if any)",
            "pyvenv.cfg": "Virtual environment configuration",
        },
        "usage": {
            "batch": ".\\Scripts\\mycli.bat [command] [options]",
            "powershell": ".\\Scripts\\mycli.ps1 [command] [options]",
            "executable": ".\\Scripts\\mycli.exe [command] [options] (if available)",
        },
        "requirements": {
            "windows_min_version": "Windows 10",
            "architecture": target_arch,
            "dependencies_bundled": True,
        },
    }

    with open(bundle_path / "bundle_info.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Create a Windows-style info file
    windows_info = f"""# MyCLI - Windows Bundle

A portable command-line interface for Azure authentication and resource management.

## Bundle Information
- Version: {metadata['version']}
- Architecture: {target_arch}
- Python: {system_info['python_version']}
- Windows: {system_info.get('windows_product', 'unknown')} {system_info.get('windows_version', '')}

## Installation
Extract the bundle to your desired location and use directly:

```cmd
mycli-bundle\\Scripts\\mycli.bat login
mycli-bundle\\Scripts\\mycli.bat resource list
mycli-bundle\\Scripts\\mycli.bat --help
```

Or in PowerShell:

```powershell
.\\mycli-bundle\\Scripts\\mycli.ps1 login
.\\mycli-bundle\\Scripts\\mycli.ps1 resource list
.\\mycli-bundle\\Scripts\\mycli.ps1 --help
```

## Adding to PATH
To use `mycli` from anywhere, add the Scripts directory to your PATH:

```cmd
set PATH=%PATH%;C:\\path\\to\\mycli-bundle\\Scripts
```

Or permanently via System Properties > Environment Variables.

## Files
- `Scripts/mycli.bat`: Batch launcher script
- `Scripts/mycli.ps1`: PowerShell launcher script
- `Scripts/mycli.exe`: Direct executable (if available)
- `Lib/`: Python libraries and dependencies
- `bundle_info.json`: Bundle metadata
"""

    with open(bundle_path / "README.md", "w", encoding="utf-8") as f:
        f.write(windows_info)


def cleanup_bundle(bundle_path):
    """Clean up unnecessary files from the bundle."""

    print("Cleaning up bundle...")

    # Remove common unnecessary files
    cleanup_patterns = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/test*",
        "**/tests*",
        "**/.git*",
        "**/.*",
        "**/Scripts/pip.exe",
        "**/Scripts/pip[0-9]*.exe",
        "**/Scripts/easy_install*.exe",
    ]

    for pattern in cleanup_patterns:
        for path in bundle_path.glob(pattern):
            # Extra safety: don't remove anything in azure packages
            if "azure" in str(path):
                continue
            if path.is_file():
                try:
                    path.unlink()
                    print(f"Removed file: {path.relative_to(bundle_path)}")
                except PermissionError:
                    print(f"Could not remove file (in use): {path.relative_to(bundle_path)}")
            elif path.is_dir():
                try:
                    shutil.rmtree(path)
                    print(f"Removed directory: {path.relative_to(bundle_path)}")
                except PermissionError:
                    print(f"Could not remove directory (in use): {path.relative_to(bundle_path)}")


def verify_bundle_functionality(bundle_path):
    """Verify that the bundle works correctly before distribution."""

    print("🔍 Verifying bundle functionality...")

    # Find the mycli launcher
    mycli_bat = bundle_path / "Scripts" / "mycli.bat"
    mycli_exe = bundle_path / "Scripts" / "mycli.exe"
    python_path = bundle_path / "Scripts" / "python.exe"

    # Determine which launcher to use
    launcher_to_test = None
    if mycli_exe.exists():
        launcher_to_test = str(mycli_exe)
        print(f"  Using executable launcher: {mycli_exe}")
    elif mycli_bat.exists():
        launcher_to_test = str(mycli_bat)
        print(f"  Using batch launcher: {mycli_bat}")
    else:
        raise Exception(f"No launcher found in {bundle_path / 'Scripts'}")

    if not python_path.exists():
        raise Exception(f"Python executable not found at {python_path}")

    # Test Azure dependencies are available
    print("  Testing Azure dependencies...")
    try:
        azure_check_script = """
import sys
import subprocess

# Check if specific packages from pyproject.toml are installed
required_packages = [
    "azure-identity>=1.12.0",
    "azure-mgmt-core>=1.3.0", 
    "azure-core>=1.24.0",
    "msal>=1.20.0"
]

print("\\n=== Checking Required Azure Packages ===")
missing_packages = []

for package_spec in required_packages:
    package_name = package_spec.split(">=")[0].split("[")[0]
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", package_name], 
                              capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            # Extract version from pip show output
            for line in result.stdout.split("\\n"):
                if line.startswith("Version:"):
                    version = line.split(":")[1].strip()
                    print(f"✅ {package_name}: {version}")
                    break
        else:
            print(f"❌ {package_name}: NOT INSTALLED")
            missing_packages.append(package_name)
    except Exception as e:
        print(f"❌ {package_name}: Error checking - {e}")
        missing_packages.append(package_name)

# Test basic imports
print("\\n=== Testing Basic Azure Imports ===")
try:
    import azure.identity
    print(f"✅ azure.identity imported - version: {azure.identity.__version__}")
except ImportError as e:
    print(f"❌ azure.identity import failed: {e}")
    missing_packages.append("azure-identity")

try:
    import azure.mgmt.core
    print(f"✅ azure.mgmt.core imported - version: {azure.mgmt.core.__version__}")
except ImportError as e:
    print(f"❌ azure.mgmt.core import failed: {e}")
    missing_packages.append("azure-mgmt-core")

try:
    import azure.core
    print(f"✅ azure.core imported - version: {azure.core.__version__}")
except ImportError as e:
    print(f"❌ azure.core import failed: {e}")
    missing_packages.append("azure-core")

try:
    import msal
    print(f"✅ msal imported - version: {msal.__version__}")
except ImportError as e:
    print(f"❌ msal import failed: {e}")
    missing_packages.append("msal")

if missing_packages:
    print(f"\\n❌ Missing packages: {', '.join(missing_packages)}")
    print("AZURE_AVAILABLE=False")
    sys.exit(1)
else:
    print("\\n✅ All required Azure packages are installed and importable")
    print("AZURE_AVAILABLE=True")
"""
        result = subprocess.run(
            [str(python_path), "-c", azure_check_script],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
            shell=True,
        )

        azure_output = result.stdout.strip()
        print("  ✅ Azure dependencies check:")
        for line in azure_output.split("\n"):
            print(f"    {line}")

        if "AZURE_AVAILABLE=False" in azure_output:
            raise Exception("Azure dependencies are missing from the bundle")

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Azure dependencies check failed with exit code {e.returncode}")
        print(f"  ❌ stdout: {e.stdout}")
        print(f"  ❌ stderr: {e.stderr}")
        raise Exception(f"Azure dependencies check failed: {e}")
    except subprocess.TimeoutExpired:
        print("  ❌ Azure dependencies check timed out")
        raise Exception("Azure dependencies check timed out")

    # Test version command
    print("  Testing version command...")
    try:
        result = subprocess.run(
            [launcher_to_test, "--version"], capture_output=True, text=True, timeout=60, check=True, shell=True
        )

        version_output = result.stdout.strip()
        print(f"  ✅ Version output: {version_output}")

        # Verify the output contains expected content
        if "MyCliApp version" not in version_output:
            print("  ⚠️  Warning: Version output doesn't contain 'MyCliApp version'")
            print(f"  ⚠️  Actual output: '{version_output}'")

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Version command failed with exit code {e.returncode}")
        print(f"  ❌ stdout: {e.stdout}")
        print(f"  ❌ stderr: {e.stderr}")
        raise Exception(f"Version command failed: {e}")
    except subprocess.TimeoutExpired:
        print("  ❌ Version command timed out")
        raise Exception("Version command timed out")

    # Test help command
    print("  Testing help command...")
    try:
        result = subprocess.run(
            [launcher_to_test, "--help"], capture_output=True, text=True, timeout=60, check=True, shell=True
        )

        help_output = result.stdout.strip()
        print(f"  ✅ Help command succeeded (output length: {len(help_output)} chars)")

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Help command failed with exit code {e.returncode}")
        print(f"  ❌ stdout: {e.stdout}")
        print(f"  ❌ stderr: {e.stderr}")
        raise Exception(f"Help command failed: {e}")
    except subprocess.TimeoutExpired:
        print("  ❌ Help command timed out")
        raise Exception("Help command timed out")

    # Test Azure authentication availability check
    print("  Testing Azure authentication availability...")
    try:
        result = subprocess.run(
            [launcher_to_test, "status"], capture_output=True, text=True, timeout=60, check=True, shell=True
        )

        status_output = result.stdout.strip()
        print("  ✅ Status command succeeded")

        # Check if Azure SDK is reported as available
        if "Azure SDK: Available" in status_output:
            print("  ✅ Azure SDK reported as available in status")
        elif "Azure SDK: Not Available" in status_output:
            print("  ❌ Azure SDK reported as NOT available in status")
            print(f"  ❌ Status output: {status_output}")
            raise Exception("Azure SDK not detected by application status command")
        else:
            print("  ⚠️  Could not determine Azure SDK status from output")
            print(f"  ⚠️  Status output: {status_output}")

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Status command failed with exit code {e.returncode}")
        print(f"  ❌ stdout: {e.stdout}")
        print(f"  ❌ stderr: {e.stderr}")
        raise Exception(f"Status command failed: {e}")
    except subprocess.TimeoutExpired:
        print("  ❌ Status command timed out")
        raise Exception("Status command timed out")

    # Test the actual Azure import issue that's causing the CLI to fail
    print("  Testing Azure imports in CLI context...")
    try:
        azure_cli_test_script = """
import sys
import os

# Test the same imports that mycli_app.cli would use
print("\\n=== Testing CLI Azure Import Context ===")

# Add the bundle's site-packages to sys.path if needed
import site
print(f"Site packages dirs: {site.getsitepackages()}")

try:
    # Test the exact imports that mycli_app.cli uses
    from mycli_app.cli import AZURE_AVAILABLE
    print(f"✅ AZURE_AVAILABLE from CLI: {AZURE_AVAILABLE}")
    
    if AZURE_AVAILABLE:
        print("✅ Azure packages detected by CLI module")
    else:
        print("❌ Azure packages NOT detected by CLI module")
        # Try to understand why
        try:
            import azure.identity
            print("  - azure.identity is importable directly")
        except ImportError as e:
            print(f"  - azure.identity import fails: {e}")
        
        try:
            import azure.core  
            print("  - azure.core is importable directly")
        except ImportError as e:
            print(f"  - azure.core import fails: {e}")
        
        try:
            import azure.mgmt.core
            print("  - azure.mgmt.core is importable directly") 
        except ImportError as e:
            print(f"  - azure.mgmt.core import fails: {e}")
            
        try:
            import msal
            print("  - msal is importable directly")
        except ImportError as e:
            print(f"  - msal import fails: {e}")
        
except ImportError as e:
    print(f"❌ Failed to import from mycli_app.cli: {e}")
    sys.exit(1)
"""

        result = subprocess.run(
            [str(python_path), "-c", azure_cli_test_script],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
            shell=True,
        )

        cli_test_output = result.stdout.strip()
        print("  ✅ CLI Azure context test:")
        for line in cli_test_output.split("\n"):
            print(f"    {line}")

        if "AZURE_AVAILABLE from CLI: False" in cli_test_output:
            print("  ❌ CLI module reports Azure as NOT available")
            raise Exception("CLI module cannot detect Azure packages even though they're installed")
        elif "AZURE_AVAILABLE from CLI: True" in cli_test_output:
            print("  ✅ CLI module reports Azure as available")

    except subprocess.CalledProcessError as e:
        print(f"  ❌ CLI Azure context test failed with exit code {e.returncode}")
        print(f"  ❌ stdout: {e.stdout}")
        print(f"  ❌ stderr: {e.stderr}")
        raise Exception(f"CLI Azure context test failed: {e}")
    except subprocess.TimeoutExpired:
        print("  ❌ CLI Azure context test timed out")
        raise Exception("CLI Azure context test timed out")

    print("  ✅ Bundle verification completed successfully!")


def create_distribution_packages(bundle_path, output_path, bundle_name, system_info, arch, version=None):
    """Create various distribution packages for Windows."""

    target_arch = arch or system_info["machine"]
    # Use provided version or fall back to Windows version
    package_version = version or system_info.get("windows_version", "unknown")

    # Create ZIP archive
    print("Creating ZIP archive...")
    zip_name = f"{bundle_name}-{package_version}-{target_arch}.zip"
    zip_path = output_path / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zip_file:
        for file_path in bundle_path.rglob("*"):
            if file_path.is_file():
                arcname = str(file_path.relative_to(bundle_path.parent))
                zip_file.write(file_path, arcname)

    # Get file size
    zip_size = zip_path.stat().st_size
    zip_size_mb = zip_size / (1024 * 1024)
    print(f"Created ZIP: {zip_name} ({zip_size_mb:.1f} MB)")

    # Create SHA256 checksum
    print("Creating SHA256 checksum...")
    try:
        result = run_command(
            [
                "powershell",
                "-Command",
                f"Get-FileHash -Path '{zip_path}' -Algorithm SHA256 | Select-Object -ExpandProperty Hash",
            ]
        )
        if result.returncode == 0:
            checksum = result.stdout.strip().lower()
            checksum_file = output_path / f"{zip_name}.sha256"
            with open(checksum_file, "w") as f:
                f.write(f"{checksum}  {zip_name}\n")
            print(f"SHA256: {checksum}")

            # Create Chocolatey package template
            create_chocolatey_package_template(output_path, bundle_name, zip_name, checksum, system_info)
    except Exception as e:
        print(f"Warning: Could not create checksum: {e}")

    # Create Windows installer template
    create_installer_template(output_path, bundle_name, system_info)

    # Create directory structure info
    create_structure_info(bundle_path, output_path, bundle_name)


def create_chocolatey_package_template(output_path, bundle_name, zip_name, sha256, system_info):
    """Create a Chocolatey package template."""

    # Create chocolatey directory structure
    choco_dir = output_path / "chocolatey"
    choco_dir.mkdir(exist_ok=True)
    tools_dir = choco_dir / "tools"
    tools_dir.mkdir(exist_ok=True)

    # Create nuspec file
    nuspec_content = """<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd">
  <metadata>
    <id>mycli</id>
    <version>1.0.0</version>
    <packageSourceUrl>https://github.com/naga-nandyala/mycli-app</packageSourceUrl>
    <owners>Your Name</owners>
    <title>MyCLI</title>
    <authors>Your Name</authors>
    <projectUrl>https://github.com/naga-nandyala/mycli-app</projectUrl>
    <copyright>2024 Your Name</copyright>
    <licenseUrl>https://github.com/naga-nandyala/mycli-app/blob/main/LICENSE</licenseUrl>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <projectSourceUrl>https://github.com/naga-nandyala/mycli-app</projectSourceUrl>
    <docsUrl>https://github.com/naga-nandyala/mycli-app#readme</docsUrl>
    <bugTrackerUrl>https://github.com/naga-nandyala/mycli-app/issues</bugTrackerUrl>
    <tags>cli azure authentication command-line tool</tags>
    <summary>Command-line interface for Azure authentication and resource management</summary>
    <description>MyCLI is a portable command-line interface for Azure authentication and resource management, similar to Azure CLI but with enhanced broker authentication support.</description>
    <releaseNotes>Initial release</releaseNotes>
    <dependencies>
      <dependency id="chocolatey-core.extension" version="1.1.0" />
    </dependencies>
  </metadata>
  <files>
    <file src="tools\\**" target="tools" />
  </files>
</package>"""

    with open(choco_dir / "mycli.nuspec", "w", encoding="utf-8") as f:
        f.write(nuspec_content)

    # Create chocolateyinstall.ps1
    install_script = f"""$ErrorActionPreference = 'Stop'

$packageName = 'mycli'
$url = 'https://github.com/naga-nandyala/mycli-app/releases/download/v1.0.0/{zip_name}'
$checksum = '{sha256}'
$checksumType = 'sha256'
$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$installDir = Join-Path $toolsDir 'mycli'

# Download and extract the bundle
$packageArgs = @{{
    packageName    = $packageName
    unzipLocation  = $toolsDir
    url            = $url
    checksum       = $checksum
    checksumType   = $checksumType
}}

Install-ChocolateyZipPackage @packageArgs

# Create shim for the executable
$shimArgs = @{{
    Path = Join-Path $installDir 'Scripts\\mycli.bat'
    Name = 'mycli'
}}

Install-BinFile @shimArgs

Write-Host "MyCLI has been installed successfully!"
Write-Host "You can now use 'mycli' command from anywhere in your command prompt or PowerShell."
"""

    with open(tools_dir / "chocolateyinstall.ps1", "w", encoding="utf-8") as f:
        f.write(install_script)

    # Create chocolateyuninstall.ps1
    uninstall_script = """$ErrorActionPreference = 'Stop'

$packageName = 'mycli'

# Remove the shim
Uninstall-BinFile -Name 'mycli'

Write-Host "MyCLI has been uninstalled successfully!"
"""

    with open(tools_dir / "chocolateyuninstall.ps1", "w", encoding="utf-8") as f:
        f.write(uninstall_script)

    print("Created Chocolatey package template in chocolatey/")


def create_installer_template(output_path, bundle_name, system_info):
    """Create a Windows installer template using Inno Setup."""

    installer_content = f"""[Setup]
AppName=MyCLI
AppVersion=1.0.0
AppPublisher=Your Name
AppPublisherURL=https://github.com/naga-nandyala/mycli-app
AppSupportURL=https://github.com/naga-nandyala/mycli-app/issues
AppUpdatesURL=https://github.com/naga-nandyala/mycli-app/releases
DefaultDirName={{autopf}}\\MyCLI
DefaultGroupName=MyCLI
AllowNoIcons=yes
LicenseFile=LICENSE
OutputDir=installer
OutputBaseFilename=MyCLI-Setup-{system_info.get('machine', 'x64')}
SetupIconFile=mycli.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed={system_info.get('machine', 'x64')}
ArchitecturesInstallIn64BitMode={system_info.get('machine', 'x64')}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "addtopath"; Description: "Add MyCLI to PATH environment variable"; GroupDescription: "Environment:"

[Files]
Source: "{bundle_name}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{group}}\\MyCLI Command Prompt"; Filename: "{{cmd}}"; Parameters: "/k ""{{app}}\\Scripts\\mycli.bat"" --help"; WorkingDir: "{{app}}"; Comment: "MyCLI Command Line Interface"
Name: "{{commondesktop}}\\MyCLI Command Prompt"; Filename: "{{cmd}}"; Parameters: "/k ""{{app}}\\Scripts\\mycli.bat"" --help"; WorkingDir: "{{app}}"; Tasks: desktopicon; Comment: "MyCLI Command Line Interface"

[Run]
Filename: "{{app}}\\Scripts\\mycli.bat"; Parameters: "--version"; WorkingDir: "{{app}}"; Flags: postinstall runasoriginaluser; Description: "Verify installation"

[Registry]
Root: HKLM; Subkey: "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{{olddata}};{{app}}\\Scripts"; Tasks: addtopath; Check: not IsPathInEnvironment('{{app}}\\Scripts')

[Code]
function IsPathInEnvironment(Path: string): Boolean;
var
  EnvironmentPath: string;
begin
  Result := False;
  if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment', 'Path', EnvironmentPath) then
  begin
    Result := Pos(UpperCase(Path), UpperCase(EnvironmentPath)) > 0;
  end;
end;
"""

    installer_path = output_path / "mycli-installer.iss"
    with open(installer_path, "w", encoding="utf-8") as f:
        f.write(installer_content)

    print("Created Inno Setup installer template: mycli-installer.iss")


def create_structure_info(bundle_path, output_path, bundle_name):
    """Create bundle structure information."""

    structure_info = []

    def collect_structure(path, prefix=""):
        try:
            for item in sorted(path.iterdir()):
                if item.is_dir():
                    structure_info.append(f"{prefix}{item.name}/")
                    if len(structure_info) < 100:  # Limit output
                        collect_structure(item, prefix + "  ")
                else:
                    size = item.stat().st_size
                    structure_info.append(f"{prefix}{item.name} ({size} bytes)")
        except PermissionError:
            structure_info.append(f"{prefix}[Access Denied]")

    collect_structure(bundle_path)

    structure_file = output_path / f"{bundle_name}-structure.txt"
    with open(structure_file, "w", encoding="utf-8") as f:
        f.write("Bundle Structure:\n")
        f.write("=" * 50 + "\n")
        for line in structure_info:
            f.write(line + "\n")

    print(f"Created structure info: {bundle_name}-structure.txt")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Create Windows bundle for MyCLI")
    parser.add_argument("--output", "-o", default="./dist", help="Output directory for the bundle (default: ./dist)")
    parser.add_argument("--python-version", help="Python version to use (e.g., 3.11, 3.12)")
    parser.add_argument(
        "--arch", choices=["x86", "AMD64", "ARM64"], help="Target architecture (default: current system architecture)"
    )
    parser.add_argument("--version", help="Package version for naming (e.g., 1.0.0)")

    args = parser.parse_args()

    print("🪟 Creating Windows bundle for MyCLI...")
    print(f"Output directory: {args.output}")
    print(f"Python version: {args.python_version or 'current'}")
    print(f"Architecture: {args.arch or 'current system'}")
    print(f"Package version: {args.version or 'auto-detect'}")
    print("-" * 50)

    try:
        bundle_path = create_windows_venv_bundle(args.output, args.python_version, args.arch, args.version)
        exit(1)
        print("\n" + "=" * 50)
        print("🎉 SUCCESS! Windows bundle created.")
        print("\n📋 Files created:")
        output_path = Path(args.output)
        for file in output_path.glob("*"):
            if file.is_file():
                size = file.stat().st_size / (1024 * 1024)
                print(f"   {file.name} ({size:.1f} MB)")

        print("\n📋 Next steps for distribution:")
        print("1. Upload the .zip file to GitHub releases")
        print("2. Update the Chocolatey package with the correct URL and SHA256")
        print("3. Build the Inno Setup installer if needed")
        print("4. Submit to Chocolatey community repository")

        print("\n🧪 Testing locally:")
        print(f"   cd {bundle_path}")
        print("   .\\Scripts\\mycli.bat --help")
        print("   .\\Scripts\\mycli.ps1 --help")

    except Exception as e:
        print(f"\n❌ Error creating Windows bundle: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
