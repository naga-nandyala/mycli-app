#!/usr/bin/env python3
"""
Create a macOS-specific portable bundle for mycli-app.
This script is designed to run in GitHub Actions and create packages suitable for Homebrew.
"""

import os
import sys
import shutil
import subprocess
import tarfile
import argparse
import tempfile
import json
import platform
from pathlib import Path


def run_command(cmd, cwd=None, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result


def get_macos_info():
    """Get macOS system information."""
    system_info = {
        "platform": platform.system(),
        "machine": platform.machine(),
        "release": platform.release(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    }

    # Get macOS version if available
    try:
        result = run_command(["sw_vers", "-productVersion"], check=False)
        if result.returncode == 0:
            system_info["macos_version"] = result.stdout.strip()
    except Exception:
        pass

    return system_info


def create_macos_venv_bundle(output_dir, python_version=None, arch=None, version=None):
    """Create a macOS-specific virtual environment bundle."""

    # Ensure we're on macOS
    if platform.system() != "Darwin":
        print("❌ Error: This script is designed for macOS only.")
        print(f"Current platform: {platform.system()}")
        print("Please run this script on macOS or use GitHub Actions with a macOS runner.")
        sys.exit(1)  # Get system info
    system_info = get_macos_info()
    print(f"Building for macOS {system_info.get('macos_version', 'unknown')}")
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

        print(f"Creating macOS bundle in: {bundle_path}")

        # Step 1: Create virtual environment
        python_exe = sys.executable if not python_version else f"python{python_version}"
        run_command([python_exe, "-m", "venv", str(bundle_path)])

        # macOS-specific paths
        venv_pip = bundle_path / "bin" / "pip"
        bin_dir = bundle_path / "bin"

        # Step 2: Upgrade pip and install wheel
        run_command([str(venv_pip), "install", "--upgrade", "pip", "wheel"])

        # Step 3: Install dependencies
        install_args = [str(venv_pip), "install", "--no-cache-dir"]

        # Install project dependencies from pyproject.toml
        project_root = Path(__file__).parent.parent.parent
        pyproject_file = project_root / "pyproject.toml"

        if pyproject_file.exists():
            print("Installing from pyproject.toml...")
            # Install the project with optional dependencies [azure,broker]
            print("Installing mycli-app package with [azure,broker] extras...")
            run_command([str(venv_pip), "install", "-e", f"{project_root}[azure,broker]"])
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
            run_command([str(venv_pip), "install", "-e", str(project_root)])

        # Log architecture info (platform-specific wheels are automatically chosen by pip on native systems)
        if arch == "arm64" or (arch is None and system_info["machine"] == "arm64"):
            print("Building for Apple Silicon (arm64) - using native wheels")
        elif arch == "x86_64" or (arch is None and system_info["machine"] == "x86_64"):
            print("Building for Intel (x86_64) - using native wheels")

        # Step 4: Create macOS-specific launcher script
        create_macos_launcher(bundle_path, bin_dir)

        # Step 5: Create application bundle metadata
        create_bundle_metadata(bundle_path, system_info, arch)

        # Step 6: Clean up unnecessary files
        cleanup_bundle(bundle_path)

        # Step 7: Create distribution packages
        create_distribution_packages(bundle_path, output_path, bundle_name, system_info, arch, version)

        print("\n✅ macOS bundle created successfully!")
        return bundle_path


def create_macos_launcher(bundle_path, bin_dir):
    """Create macOS-specific launcher script."""

    # Main launcher script
    launcher_content = """#!/bin/bash
# MyCLI macOS Launcher
# This script provides a portable way to run mycli on macOS

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$SCRIPT_DIR/python"

# Check if we're in the correct bundle structure
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: mycli bundle not found or corrupted"
    echo "Expected Python at: $VENV_PYTHON"
    exit 1
fi

# Set up environment
export PYTHONPATH="$BUNDLE_ROOT/lib/python*/site-packages:$PYTHONPATH"

# For Homebrew compatibility, check if we're being called via symlink
if [ -L "$0" ]; then
    # Called via Homebrew symlink, use the bundle's Python
    exec "$VENV_PYTHON" -m mycli_app "$@"
else
    # Called directly, use the bundle's Python
    exec "$VENV_PYTHON" -m mycli_app "$@"
fi
"""

    launcher_path = bin_dir / "mycli"
    with open(launcher_path, "w") as f:
        f.write(launcher_content)

    # Make executable
    os.chmod(launcher_path, 0o755)

    # Create a symlink for homebrew compatibility
    homebrew_launcher = bin_dir / "mycli-homebrew"
    if homebrew_launcher.exists():
        homebrew_launcher.unlink()
    homebrew_launcher.symlink_to("mycli")


def create_bundle_metadata(bundle_path, system_info, arch):
    """Create metadata for the macOS bundle."""

    # Determine architecture
    target_arch = arch or system_info["machine"]

    metadata = {
        "name": "mycli-macos-bundle",
        "version": "1.0.0",  # This should be dynamic based on your app version
        "description": "Portable macOS bundle for MyCLI application",
        "target_platform": "macOS",
        "target_architecture": target_arch,
        "macos_version": system_info.get("macos_version"),
        "python_version": system_info["python_version"],
        "build_date": subprocess.run(
            ["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True
        ).stdout.strip(),
        "homebrew_compatible": True,
        "bundle_structure": {
            "bin/": "Executables and launcher scripts",
            "lib/": "Python libraries and dependencies",
            "include/": "Header files (if needed)",
            "share/": "Shared resources",
            "pyvenv.cfg": "Virtual environment configuration",
        },
        "usage": {
            "direct": "./bin/mycli [command] [options]",
            "homebrew": "mycli [command] [options] (after brew install)",
        },
        "requirements": {
            "macos_min_version": "10.15",  # Catalina
            "architecture": target_arch,
            "dependencies_bundled": True,
        },
    }

    with open(bundle_path / "bundle_info.json", "w") as f:
        json.dump(metadata, f, indent=2)

    # Create a Homebrew-style info file
    homebrew_info = f"""# MyCLI - macOS Bundle

A portable command-line interface for Azure authentication and resource management.

## Bundle Information
- Version: {metadata['version']}
- Architecture: {target_arch}
- Python: {system_info['python_version']}
- macOS: {system_info.get('macos_version', 'unknown')}

## Installation
This bundle is designed to be installed via Homebrew:

```bash
brew install mycli
```

## Manual Usage
If using the bundle directly:

```bash
./bin/mycli login
./bin/mycli resource list
./bin/mycli --help
```

## Files
- `bin/mycli`: Main executable
- `bin/mycli-homebrew`: Homebrew-compatible symlink
- `lib/`: Python libraries and dependencies
- `bundle_info.json`: Bundle metadata
"""

    with open(bundle_path / "README.md", "w") as f:
        f.write(homebrew_info)


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
        "**/pip*",
        "**/easy_install*",
    ]

    for pattern in cleanup_patterns:
        for path in bundle_path.glob(pattern):
            if path.is_file():
                path.unlink()
                print(f"Removed file: {path.relative_to(bundle_path)}")
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"Removed directory: {path.relative_to(bundle_path)}")


def create_distribution_packages(bundle_path, output_path, bundle_name, system_info, arch, version=None):
    """Create various distribution packages for macOS."""

    target_arch = arch or system_info["machine"]
    # Use provided version or fall back to macOS version
    package_version = version or system_info.get("macos_version", "unknown")

    # Create tar.gz archive (most common for Homebrew)
    print("Creating tar.gz archive...")
    tar_name = f"{bundle_name}-{package_version}-{target_arch}.tar.gz"
    tar_path = output_path / tar_name

    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(bundle_path, arcname=bundle_name)

    # Get file size
    tar_size = tar_path.stat().st_size
    tar_size_mb = tar_size / (1024 * 1024)
    print(f"Created tar.gz: {tar_name} ({tar_size_mb:.1f} MB)")

    # Create SHA256 checksum for Homebrew
    print("Creating SHA256 checksum...")
    result = run_command(["shasum", "-a", "256", str(tar_path)])
    if result.returncode == 0:
        checksum = result.stdout.split()[0]
        checksum_file = output_path / f"{tar_name}.sha256"
        with open(checksum_file, "w") as f:
            f.write(f"{checksum}  {tar_name}\n")
        print(f"SHA256: {checksum}")

        # Create Homebrew formula template
        create_homebrew_formula_template(output_path, bundle_name, tar_name, checksum, system_info)

    # Create directory structure info
    create_structure_info(bundle_path, output_path, bundle_name)


def create_homebrew_formula_template(output_path, bundle_name, tar_name, sha256, system_info):
    """Create a Homebrew formula template."""

    formula_content = f"""# Homebrew Formula Template for MyCLI
# Save this as mycli.rb in your Homebrew tap

class Mycli < Formula
  desc "Command-line interface for Azure authentication and resource management"
  homepage "https://github.com/naga-nandyala/mycli-app"
  url "https://github.com/naga-nandyala/mycli-app/releases/download/v1.0.0/{tar_name}"
  sha256 "{sha256}"
  license "MIT"

  depends_on "python@3.12"
  depends_on arch: :{system_info['machine']}

  def install
    # Install the bundle
    libexec.install Dir["*"]
    
    # Create wrapper script
    (bin/"mycli").write <<~EOS
      #!/bin/bash
      exec "#{"{"}libexec{"}"}/bin/mycli" "$@"
    EOS
    
    chmod 0755, bin/"mycli"
  end

  test do
    assert_match "MyCliApp version", shell_output("#{bin}/mycli --version")
  end
end
"""

    formula_path = output_path / "mycli.rb"
    with open(formula_path, "w") as f:
        f.write(formula_content)

    print("Created Homebrew formula template: mycli.rb")


def create_structure_info(bundle_path, output_path, bundle_name):
    """Create bundle structure information."""

    structure_info = []

    def collect_structure(path, prefix=""):
        for item in sorted(path.iterdir()):
            if item.is_dir():
                structure_info.append(f"{prefix}{item.name}/")
                if len(structure_info) < 100:  # Limit output
                    collect_structure(item, prefix + "  ")
            else:
                size = item.stat().st_size
                structure_info.append(f"{prefix}{item.name} ({size} bytes)")

    collect_structure(bundle_path)

    structure_file = output_path / f"{bundle_name}-structure.txt"
    with open(structure_file, "w") as f:
        f.write("Bundle Structure:\n")
        f.write("=" * 50 + "\n")
        for line in structure_info:
            f.write(line + "\n")

    print(f"Created structure info: {bundle_name}-structure.txt")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Create macOS bundle for MyCLI")
    parser.add_argument("--output", "-o", default="./dist", help="Output directory for the bundle (default: ./dist)")
    parser.add_argument("--python-version", help="Python version to use (e.g., 3.11, 3.12)")
    parser.add_argument(
        "--arch", choices=["x86_64", "arm64"], help="Target architecture (default: current system architecture)"
    )
    parser.add_argument("--version", help="Package version for naming (e.g., 1.0.0)")

    args = parser.parse_args()

    print("🍎 Creating macOS bundle for MyCLI...")
    print(f"Output directory: {args.output}")
    print(f"Python version: {args.python_version or 'current'}")
    print(f"Architecture: {args.arch or 'current system'}")
    print(f"Package version: {args.version or 'auto-detect'}")
    print("-" * 50)

    try:
        bundle_path = create_macos_venv_bundle(args.output, args.python_version, args.arch, args.version)

        print("\n" + "=" * 50)
        print("🎉 SUCCESS! macOS bundle created.")
        print("\n📋 Files created:")
        output_path = Path(args.output)
        for file in output_path.glob("*"):
            if file.is_file():
                size = file.stat().st_size / (1024 * 1024)
                print(f"   {file.name} ({size:.1f} MB)")

        print("\n📋 Next steps for Homebrew:")
        print("1. Upload the .tar.gz file to GitHub releases")
        print("2. Update the Homebrew formula with the correct URL and SHA256")
        print("3. Submit to homebrew-core or create a custom tap")

        print("\n🧪 Testing locally:")
        print(f"   cd {bundle_path}")
        print("   ./bin/mycli --help")

    except Exception as e:
        print(f"\n❌ Error creating macOS bundle: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
