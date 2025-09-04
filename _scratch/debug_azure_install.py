#!/usr/bin/env python3
"""
Debug script to test Azure package installation independently
This can be run on different macOS architectures to compare results
"""

import subprocess
import sys
import tempfile
import platform
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return the result"""
    print(f"🔧 Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        print(f"✅ Exit code: {result.returncode}")
        if result.stdout:
            print(f"📤 STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"📤 STDERR:\n{result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"📤 STDOUT:\n{e.stdout}")
        if e.stderr:
            print(f"📤 STDERR:\n{e.stderr}")
        if check:
            raise
        return e


def main():
    print("🔍 Azure Package Installation Debug Test")
    print(f"Platform: {platform.system()}")
    print(f"Architecture: {platform.machine()}")
    print(f"Python version: {sys.version}")
    print("-" * 50)

    # Create a temporary venv for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_venv"
        print(f"📁 Creating test venv in: {venv_path}")

        # Create venv
        run_command([sys.executable, "-m", "venv", str(venv_path)])

        # Get venv python
        if platform.system() == "Windows":
            venv_python = venv_path / "Scripts" / "python.exe"
        else:
            venv_python = venv_path / "bin" / "python"

        pip_cmd = [str(venv_python), "-m", "pip"]

        # Upgrade pip
        print("\n📦 Upgrading pip...")
        run_command(pip_cmd + ["install", "--upgrade", "pip"])

        # Show pip version
        print("\n📋 Pip version:")
        run_command(pip_cmd + ["--version"])

        # Test Azure package installation one by one
        azure_packages = [
            "azure-core>=1.24.0",
            "azure-identity>=1.12.0",
            "azure-mgmt-core>=1.3.0",
            "msal[broker]>=1.20.0,<2",
        ]

        for package in azure_packages:
            print(f"\n🧪 Testing installation of: {package}")
            run_command(pip_cmd + ["install", "--no-cache-dir", "-v", package], check=False)

            # Check if package was installed
            package_name = package.split(">=")[0].split("[")[0]
            check_result = run_command(pip_cmd + ["show", package_name], check=False)

            if check_result.returncode == 0:
                print(f"✅ {package_name} installation verified")
            else:
                print(f"❌ {package_name} installation failed")

        # List all installed packages
        print("\n📋 All installed packages:")
        run_command(pip_cmd + ["list"])

        # Test importing Azure modules
        print("\n🐍 Testing Azure imports:")
        import_tests = ["import azure.core", "import azure.identity", "import azure.mgmt.core", "import msal"]

        for import_test in import_tests:
            test_result = run_command([str(venv_python), "-c", import_test], check=False)
            if test_result.returncode == 0:
                print(f"✅ {import_test} - SUCCESS")
            else:
                print(f"❌ {import_test} - FAILED")


if __name__ == "__main__":
    main()
