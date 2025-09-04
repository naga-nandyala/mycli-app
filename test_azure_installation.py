#!/usr/bin/env python3
"""
Test script to debug Azure package installation issues.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    print(f"Return code: {result.returncode}")
    return result


def test_azure_installation():
    """Test Azure package installation in a temporary venv."""
    print("Testing Azure package installation...")

    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        test_venv = temp_path / "test_venv"

        print(f"Creating test venv in: {test_venv}")

        # Create virtual environment
        run_command([sys.executable, "-m", "venv", str(test_venv)])

        # Windows paths - always use python -m pip for reliability
        if sys.platform == "win32":
            venv_python = test_venv / "Scripts" / "python.exe"
        else:
            venv_python = test_venv / "bin" / "python"

        # Always use python -m pip for better reliability
        pip_cmd = [str(venv_python), "-m", "pip"]

        # Upgrade pip
        print("\nUpgrading pip...")
        run_command(pip_cmd + ["install", "--upgrade", "pip"])

        # Get project root
        project_root = Path(__file__).parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            print(f"\nInstalling from {pyproject_file}...")

            # First try installing Azure dependencies explicitly
            print("\nInstalling Azure dependencies explicitly...")
            azure_dependencies = [
                "azure-identity>=1.12.0",
                "azure-mgmt-core>=1.3.0",
                "azure-core>=1.24.0",
                "msal[broker]>=1.20.0,<2",
            ]
            run_command(pip_cmd + ["install", "-v"] + azure_dependencies)

            # Then install the project with extras
            print("\nInstalling project with [azure,broker] extras...")
            run_command(pip_cmd + ["install", "-v", f"{project_root}[azure,broker]"])

            # List installed packages
            print("\nInstalled packages:")
            run_command(pip_cmd + ["list"])

            # Check for Azure packages specifically
            print("\nChecking Azure packages:")
            for pkg in ["azure-core", "azure-identity", "azure-mgmt-core", "msal"]:
                result = run_command(pip_cmd + ["show", pkg], check=False)
                if result.returncode == 0:
                    print(f"✅ {pkg} is installed")
                else:
                    print(f"❌ {pkg} is NOT installed")

            # Test import
            print("\nTesting Azure imports:")
            test_script = """
try:
    import azure.identity
    import azure.core
    import azure.mgmt.core
    import msal
    print("✅ All Azure packages imported successfully")
    print(f"azure-identity: {azure.identity.__version__}")
    print(f"azure-core: {azure.core.__version__}")
    print(f"msal: {msal.__version__}")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import sys
    sys.exit(1)
"""
            result = run_command([str(venv_python), "-c", test_script], check=False)
            if result.returncode == 0:
                print("✅ Azure import test passed")
            else:
                print("❌ Azure import test failed")

        else:
            print(f"❌ pyproject.toml not found at {pyproject_file}")


if __name__ == "__main__":
    test_azure_installation()
