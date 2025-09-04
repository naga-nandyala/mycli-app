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
            # Use regular install instead of editable for bundling
            run_command([str(venv_pip), "install", f"{project_root}[azure,broker]"])
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
            # Use regular install instead of editable for bundling
            run_command([str(venv_pip), "install", str(project_root)])

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

        # Step 6.5: Verify bundle functionality before distribution
        verify_bundle_functionality(bundle_path)

        # Step 7: Create distribution packages
        create_distribution_packages(bundle_path, output_path, bundle_name, system_info, arch, version)

        print("\n✅ macOS bundle created successfully!")
        return bundle_path


def create_macos_launcher(bundle_path, bin_dir):
    """Create macOS-specific launcher script."""
    print("Setting up launcher...")

    # Check if pip created a console script during installation
    pip_generated_script = bin_dir / "mycli"
    if pip_generated_script.exists():
        print("Found pip-generated console script, creating portable version...")
        
        # Instead of fixing the pip script, create our own portable version
        # This avoids hardcoded paths entirely
        portable_script_content = """#!/bin/bash
# MyCLI Portable Console Script
# Auto-generated to replace pip's hardcoded-path version

# Get the directory containing this script (resolve symlinks carefully)
SCRIPT_PATH="${BASH_SOURCE[0]}"

# If this is a symlink (like from Homebrew), resolve it
if [ -L "$SCRIPT_PATH" ]; then
    SCRIPT_PATH="$(readlink -f "$SCRIPT_PATH" 2>/dev/null || realpath "$SCRIPT_PATH" 2>/dev/null || readlink "$SCRIPT_PATH")"
fi

SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

# Look for Python interpreter - handle both direct use and Homebrew installation
BUNDLE_PYTHON=""

# Method 1: Same directory (direct bundle use)
if [ -f "$SCRIPT_DIR/python" ]; then
    BUNDLE_PYTHON="$SCRIPT_DIR/python"

# Method 2: Check if we're in a Homebrew-style installation
elif [ -f "$SCRIPT_DIR/../bin/python" ]; then
    BUNDLE_PYTHON="$SCRIPT_DIR/../bin/python"

# Method 3: Look for bundle structure patterns
else
    # Check common bundle locations relative to where we are
    for python_path in \\
        "$SCRIPT_DIR/../../libexec/bin/python" \\
        "$SCRIPT_DIR/../libexec/bin/python" \\
        "$SCRIPT_DIR/python" \\
        "$SCRIPT_DIR/../python"; do
        
        if [ -f "$python_path" ]; then
            BUNDLE_PYTHON="$python_path"
            break
        fi
    done
fi

# If we still can't find Python, provide comprehensive debugging
if [ -z "$BUNDLE_PYTHON" ] || [ ! -f "$BUNDLE_PYTHON" ]; then
    echo "Error: Bundle Python interpreter not found" >&2
    echo "Debug: Comprehensive directory listing:" >&2
    echo "Debug: Current working directory:" >&2
    pwd >&2
    echo "Debug: Script directory ($SCRIPT_DIR):" >&2
    ls -la "$SCRIPT_DIR" >&2 || echo "Could not list $SCRIPT_DIR" >&2
    echo "Debug: Parent directory:" >&2
    ls -la "$(dirname "$SCRIPT_DIR")" >&2 || echo "Could not list parent" >&2
    echo "Debug: Grandparent directory:" >&2
    ls -la "$(dirname "$(dirname "$SCRIPT_DIR")")" >&2 || echo "Could not list grandparent" >&2
    exit 1
fi

# Execute the main CLI function
exec "$BUNDLE_PYTHON" -c "
import sys
from mycli_app.cli import main
if __name__ == '__main__':
    sys.exit(main())
" "$@"
"""
        
        # Write the portable script
        with open(pip_generated_script, 'w') as f:
            f.write(portable_script_content)
        
        print("  Created portable console script")
        
        # Make sure it's executable
        os.chmod(pip_generated_script, 0o755)

        # Create a symlink for homebrew compatibility
        homebrew_launcher = bin_dir / "mycli-homebrew"
        if homebrew_launcher.exists():
            homebrew_launcher.unlink()
        homebrew_launcher.symlink_to("mycli")

        print("Console script setup complete with portable wrapper")
        return

    print("No pip-generated console script found, creating custom launcher...")

    # Main launcher script (fallback if console scripts don't work)
    launcher_content = """#!/bin/bash
# MyCLI macOS Launcher
# This script provides a portable way to run mycli on macOS

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUNDLE_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$SCRIPT_DIR/python"

# Check if we're in the correct bundle structure
if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: mycli bundle not found or corrupted" >&2
    echo "Expected Python at: $VENV_PYTHON" >&2
    exit 1
fi

# Set up environment - expand the glob pattern correctly
PYTHON_SITEPKG=$(find "$BUNDLE_ROOT/lib" -name "site-packages" -type d 2>/dev/null | head -1)
if [ -n "$PYTHON_SITEPKG" ]; then
    export PYTHONPATH="$PYTHON_SITEPKG:$PYTHONPATH"
fi

# Alternative method: try to use the venv activation if available
VENV_ACTIVATE="$BUNDLE_ROOT/bin/activate"
if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
fi

# Try to run the application with proper error handling
if ! "$VENV_PYTHON" -c "import mycli_app.cli" 2>/dev/null; then
    echo "Error: Could not import mycli_app.cli module" >&2
    echo "Bundle structure may be incomplete" >&2
    echo "Python path: $PYTHONPATH" >&2
    echo "Site packages: $PYTHON_SITEPKG" >&2
    exit 1
fi

# For Homebrew compatibility, check if we're being called via symlink
if [ -L "$0" ]; then
    # Called via Homebrew symlink, use the bundle's Python with entry point
    exec "$VENV_PYTHON" -c "from mycli_app.cli import main; main()" "$@"
else
    # Called directly, use the bundle's Python with entry point
    exec "$VENV_PYTHON" -c "from mycli_app.cli import main; main()" "$@"
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

    print("Custom launcher created")


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


def verify_bundle_functionality(bundle_path):
    """Verify that the bundle works correctly before distribution."""

    print("🔍 Verifying bundle functionality...")

    # Find the mycli executable
    mycli_path = bundle_path / "bin" / "mycli"

    if not mycli_path.exists():
        raise Exception(f"mycli executable not found at {mycli_path}")

    # Make sure it's executable
    import stat

    current_mode = mycli_path.stat().st_mode
    mycli_path.chmod(current_mode | stat.S_IEXEC)

    # Test version command
    print("  Testing version command...")
    try:
        result = subprocess.run([str(mycli_path), "--version"], capture_output=True, text=True, timeout=30, check=True)

        version_output = result.stdout.strip()
        print(f"  ✅ Version output: {version_output}")

        # Verify the output contains expected content
        if "MyCliApp version" not in version_output:
            print(f"  ⚠️  Warning: Version output doesn't contain 'MyCliApp version'")
            print(f"  ⚠️  Actual output: '{version_output}'")
            # Don't fail here, just warn

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Version command failed with exit code {e.returncode}")
        print(f"  ❌ stdout: {e.stdout}")
        print(f"  ❌ stderr: {e.stderr}")
        raise Exception(f"Version command failed: {e}")
    except subprocess.TimeoutExpired:
        print(f"  ❌ Version command timed out")
        raise Exception("Version command timed out")

    # Test help command
    print("  Testing help command...")
    try:
        result = subprocess.run([str(mycli_path), "--help"], capture_output=True, text=True, timeout=30, check=True)

        help_output = result.stdout.strip()
        print(f"  ✅ Help command succeeded (output length: {len(help_output)} chars)")

    except subprocess.CalledProcessError as e:
        print(f"  ❌ Help command failed with exit code {e.returncode}")
        print(f"  ❌ stdout: {e.stdout}")
        print(f"  ❌ stderr: {e.stderr}")
        raise Exception(f"Help command failed: {e}")
    except subprocess.TimeoutExpired:
        print(f"  ❌ Help command timed out")
        raise Exception("Help command timed out")

    print("  ✅ Bundle verification completed successfully!")


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
