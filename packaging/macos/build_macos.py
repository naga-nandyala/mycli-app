#!/usr/bin/env python3
"""Build macOS distributions for MyCliApp.

This script creates macOS-native distributions:
1. Standalone ZIP (using existing build_zip.py but optimized for macOS)
2. macOS .app bundle with proper metadata
3. DMG installer (optional)

The .app bundle provides a native macOS experience while the ZIP provides
a simple command-line distribution similar to Azure CLI.

Requirements:
- macOS (for .app and DMG builds)
- Python 3.8+ (preferably 3.12+)
- create-dmg (for DMG creation): brew install create-dmg

Usage:
    python packaging/macos/build_macos.py [--type zip|app|dmg|pkg|all] [--version 1.0.0]

Output structure:
    dist_macos/
        MyCliApp-1.0.0-darwin-x64.zip      # Standalone ZIP
        MyCliApp.app/                       # macOS app bundle
        MyCliApp-1.0.0-darwin-x64.dmg      # DMG installer
        MyCliApp-1.0.0-darwin-x64.pkg      # macOS installer package
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
import json
import plistlib

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "dist_macos"
MACOS_DIR = PROJECT_ROOT / "packaging" / "macos"


def run(cmd: list[str], cwd: Path | None = None, env: dict | None = None, capture_output: bool = False) -> str | None:
    """Run a command, raising a clearer error on failure."""
    print(f"[run] {' '.join(cmd)}")
    try:
        if capture_output:
            result = subprocess.run(
                cmd, cwd=str(cwd) if cwd else None, env=env, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        else:
            subprocess.check_call(cmd, cwd=str(cwd) if cwd else None, env=env)
            return None
    except subprocess.CalledProcessError as e:
        if capture_output and e.stdout:
            print(f"STDOUT: {e.stdout}")
        if capture_output and e.stderr:
            print(f"STDERR: {e.stderr}")
        raise RuntimeError(f"Command failed (exit {e.returncode}): {' '.join(cmd)}") from e


def detect_version(explicit: str | None) -> str:
    """Detect version from the package."""
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
    """Get current platform tag for macOS."""
    system = platform.system().lower()
    if system != "darwin":
        raise RuntimeError("This script should only be run on macOS")

    arch = platform.machine().lower()
    # Normalize arch
    if arch in ("amd64", "x86_64"):
        arch = "x64"
    elif arch.startswith("arm64") or arch.startswith("aarch64"):
        arch = "arm64"
    return f"darwin-{arch}"


def check_macos():
    """Ensure we're running on macOS."""
    if platform.system() != "Darwin":
        raise RuntimeError("macOS distributions must be built on macOS")


def build_zip(version: str, output_dir: Path) -> Path:
    """Build standalone ZIP using existing build_zip.py script."""
    print("[info] Building standalone ZIP for macOS...")

    build_script = PROJECT_ROOT / "packaging" / "standalone_zip" / "build_zip.py"
    cmd = [
        sys.executable,
        str(build_script),
        "--extras",
        "azure,broker",
        "--version",
        version,
        "--output",
        str(output_dir),
    ]

    run(cmd, cwd=PROJECT_ROOT)

    # Find the generated ZIP
    zip_pattern = f"MyCliApp-{version}-{current_platform_tag()}.zip"
    zip_path = output_dir / zip_pattern

    if not zip_path.exists():
        raise RuntimeError(f"Expected ZIP not found: {zip_path}")

    print(f"[success] Created ZIP: {zip_path}")
    return zip_path


def create_app_bundle(version: str, output_dir: Path) -> Path:
    """Create a macOS .app bundle."""
    print("[info] Creating macOS .app bundle...")

    app_name = "MyCliApp"
    app_bundle = output_dir / f"{app_name}.app"

    # Remove existing app bundle
    if app_bundle.exists():
        shutil.rmtree(app_bundle)

    # Create app bundle structure
    contents_dir = app_bundle / "Contents"
    macos_dir = contents_dir / "MacOS"
    resources_dir = contents_dir / "Resources"
    frameworks_dir = contents_dir / "Frameworks"

    for dir_path in [contents_dir, macos_dir, resources_dir, frameworks_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # First build the ZIP to get the embedded Python environment
    temp_zip = build_zip(version, output_dir / ".temp")

    # Extract the ZIP to get the Python environment
    temp_extract_dir = output_dir / ".temp_extract"
    if temp_extract_dir.exists():
        shutil.rmtree(temp_extract_dir)

    shutil.unpack_archive(str(temp_zip), str(temp_extract_dir))

    # Find the extracted directory
    extracted_dirs = list(temp_extract_dir.glob("MyCliApp-*"))
    if not extracted_dirs:
        raise RuntimeError("Failed to find extracted directory")

    extracted_dir = extracted_dirs[0]

    # Copy Python environment to Frameworks
    python_src = extracted_dir / "python"
    python_dst = frameworks_dir / "Python"
    shutil.copytree(python_src, python_dst)

    # Create the main executable script
    executable_script = macos_dir / app_name
    script_content = textwrap.dedent(
        """#!/bin/bash
        # MyCliApp macOS launcher
        
        # Get the directory containing this script
        SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
        APP_DIR="$SCRIPT_DIR/.."
        
        # Set up Python path
        PYTHON_FRAMEWORK="$APP_DIR/Frameworks/Python"
        PYTHON_BIN="$PYTHON_FRAMEWORK/bin/python"
        
        # Set environment variables
        export PYTHONWARNINGS="ignore::RuntimeWarning"
        export PYTHONPATH="$PYTHON_FRAMEWORK/lib/python3.12/site-packages"
        
        # Check if we're running from terminal or GUI
        if [ -t 1 ]; then
            # Running from terminal - execute CLI directly
            exec "$PYTHON_BIN" -m mycli_app.cli "$@"
        else
            # Running from GUI - open terminal and run CLI
            osascript -e "tell application \\"Terminal\\" to do script \\"cd '$PWD' && '$PYTHON_BIN' -m mycli_app.cli; exit\\""
        fi
    """
    ).strip()

    executable_script.write_text(script_content)
    executable_script.chmod(0o755)

    # Create Info.plist
    info_plist = create_info_plist(version, app_name)
    plist_path = contents_dir / "Info.plist"
    with open(plist_path, "wb") as f:
        plistlib.dump(info_plist, f)

    # Create an icon (optional - you can add a proper .icns file later)
    create_default_icon(resources_dir)

    # Copy additional resources
    for file_name in ["LICENSE", "README.md", "CHANGELOG.md"]:
        src_file = PROJECT_ROOT / file_name
        if src_file.exists():
            shutil.copy2(src_file, resources_dir)

    # Create a README for the app bundle
    app_readme = resources_dir / "README-APP.md"
    readme_content = create_app_readme(version, app_name)
    app_readme.write_text(readme_content)

    # Clean up temporary files
    shutil.rmtree(output_dir / ".temp")
    shutil.rmtree(temp_extract_dir)

    print(f"[success] Created app bundle: {app_bundle}")
    return app_bundle


def create_info_plist(version: str, app_name: str) -> dict:
    """Create Info.plist content for the app bundle."""
    return {
        "CFBundleName": app_name,
        "CFBundleDisplayName": "MyCliApp",
        "CFBundleIdentifier": "com.example.mycliapp",
        "CFBundleVersion": version,
        "CFBundleShortVersionString": version,
        "CFBundleExecutable": app_name,
        "CFBundleIconFile": "AppIcon",
        "CFBundlePackageType": "APPL",
        "CFBundleSignature": "????",
        "CFBundleInfoDictionaryVersion": "6.0",
        "LSMinimumSystemVersion": "10.14",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "LSApplicationCategoryType": "public.app-category.developer-tools",
        "NSHumanReadableCopyright": "Copyright © 2025 MyCliApp. All rights reserved.",
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeExtensions": ["sh", "command"],
                "CFBundleTypeName": "Shell Script",
                "CFBundleTypeRole": "Viewer",
                "LSHandlerRank": "Alternate",
            }
        ],
        "LSEnvironment": {"PYTHONWARNINGS": "ignore::RuntimeWarning"},
    }


def create_default_icon(resources_dir: Path):
    """Create a simple default icon for the app."""
    # This creates a simple text-based icon
    # In a real project, you'd want to create a proper .icns file
    icon_script = resources_dir / "create_icon.py"
    icon_content = textwrap.dedent(
        """
        # This is a placeholder for icon creation
        # To create a proper icon:
        # 1. Create a 1024x1024 PNG image
        # 2. Use iconutil to convert to .icns:
        #    iconutil -c icns MyCliApp.iconset
        # 3. Place the resulting AppIcon.icns in Resources/
        
        print("Icon placeholder created")
    """
    ).strip()

    icon_script.write_text(icon_content)

    # Create a simple text file as placeholder
    icon_placeholder = resources_dir / "AppIcon.icns"
    icon_placeholder.write_text("# Placeholder icon file\n# Replace with actual .icns file")


def create_app_readme(version: str, app_name: str) -> str:
    """Create README content for the app bundle."""
    return textwrap.dedent(
        f"""
        # {app_name} macOS Application
        
        Version: {version}
        Platform: macOS
        
        ## About
        
        This is a native macOS application bundle for MyCliApp, a CLI tool similar to Azure CLI.
        
        ## Usage
        
        ### GUI Usage
        Double-click the {app_name}.app to open a terminal window with the CLI ready to use.
        
        ### Command Line Usage
        You can also run the CLI directly from the command line:
        
        ```bash
        # Navigate to the app bundle
        cd /Applications/{app_name}.app/Contents/MacOS
        ./{app_name} --help
        
        # Or add to PATH for system-wide access
        echo 'export PATH="/Applications/{app_name}.app/Contents/MacOS:$PATH"' >> ~/.zshrc
        source ~/.zshrc
        {app_name.lower()} --help
        ```
        
        ## Features
        
        - Native macOS application bundle
        - Embedded Python runtime (no system Python required)
        - Azure authentication support
        - Cross-platform compatibility
        
        ## Installation
        
        1. Copy {app_name}.app to /Applications/
        2. Right-click and select "Open" the first time (for unsigned apps)
        3. Use from Applications folder or add to PATH
        
        ## Troubleshooting
        
        ### "App can't be opened" error
        - Right-click the app and select "Open"
        - Or run: `xattr -d com.apple.quarantine /Applications/{app_name}.app`
        
        ### Python/permissions issues
        - Ensure the app has proper permissions in System Preferences > Security & Privacy
        
        ## Uninstalling
        
        Simply drag {app_name}.app to the Trash.
        
        ---
        Built on: {platform.platform()}
        Python Version: {platform.python_version()}
    """
    ).strip()


def create_dmg(app_bundle: Path, version: str, output_dir: Path) -> Path:
    """Create a DMG installer for the app bundle."""
    print(f"[info] Creating DMG installer...")

    # Check if create-dmg is available
    try:
        run(["which", "create-dmg"], capture_output=True)
    except RuntimeError:
        print(f"[warning] create-dmg not found. Install with: brew install create-dmg")
        print(f"[info] Skipping DMG creation")
        return None

    dmg_name = f"MyCliApp-{version}-{current_platform_tag()}.dmg"
    dmg_path = output_dir / dmg_name

    # Remove existing DMG
    if dmg_path.exists():
        dmg_path.unlink()

    # Create temporary directory for DMG contents
    dmg_temp = output_dir / ".dmg_temp"
    if dmg_temp.exists():
        shutil.rmtree(dmg_temp)
    dmg_temp.mkdir()

    # Copy app bundle to temp directory
    temp_app = dmg_temp / app_bundle.name
    shutil.copytree(app_bundle, temp_app)

    # Create Applications symlink
    applications_link = dmg_temp / "Applications"
    applications_link.symlink_to("/Applications")

    # Create DMG
    cmd = [
        "create-dmg",
        "--volname",
        f"MyCliApp {version}",
        "--volicon",
        (
            str(temp_app / "Contents" / "Resources" / "AppIcon.icns")
            if (temp_app / "Contents" / "Resources" / "AppIcon.icns").exists()
            else ""
        ),
        "--window-pos",
        "200",
        "120",
        "--window-size",
        "600",
        "300",
        "--icon-size",
        "100",
        "--icon",
        app_bundle.name,
        "175",
        "120",
        "--hide-extension",
        app_bundle.name,
        "--app-drop-link",
        "425",
        "120",
        str(dmg_path),
        str(dmg_temp),
    ]

    # Remove empty volicon argument if no icon exists
    cmd = [arg for arg in cmd if arg != ""]

    try:
        run(cmd, cwd=output_dir)
        print(f"[success] Created DMG: {dmg_path}")
    except RuntimeError as e:
        print(f"[warning] DMG creation failed: {e}")
        dmg_path = None
    finally:
        # Clean up
        if dmg_temp.exists():
            shutil.rmtree(dmg_temp)

    return dmg_path


def create_pkg(app_bundle: Path, version: str, output_dir: Path) -> Path:
    """Create a PKG installer for the app bundle."""
    print("[info] Creating PKG installer...")

    pkg_name = f"MyCliApp-{version}-{current_platform_tag()}.pkg"
    pkg_path = output_dir / pkg_name

    # Remove existing PKG
    if pkg_path.exists():
        pkg_path.unlink()

    # Create temporary directory for package building
    pkg_temp = output_dir / ".pkg_temp"
    if pkg_temp.exists():
        shutil.rmtree(pkg_temp)
    pkg_temp.mkdir()

    # Create package structure
    payload_dir = pkg_temp / "payload"
    scripts_dir = pkg_temp / "scripts"

    payload_dir.mkdir(parents=True)
    scripts_dir.mkdir(parents=True)

    # Copy app bundle to payload (will be installed to /Applications)
    app_payload = payload_dir / "Applications"
    app_payload.mkdir(parents=True)
    shutil.copytree(app_bundle, app_payload / app_bundle.name)

    # Create command-line symlink payload (will be installed to /usr/local/bin)
    bin_payload = payload_dir / "usr" / "local" / "bin"
    bin_payload.mkdir(parents=True)

    # Create a symlink script that will create the CLI symlink
    cli_symlink = bin_payload / "mycli"
    symlink_content = f"""#!/bin/bash
exec "/Applications/{app_bundle.name}/Contents/MacOS/MyCliApp" "$@"
"""
    cli_symlink.write_text(symlink_content)
    cli_symlink.chmod(0o755)

    # Create post-install script
    postinstall_script = scripts_dir / "postinstall"
    postinstall_content = textwrap.dedent(
        f"""#!/bin/bash
        # Post-installation script for MyCliApp
        
        echo "Setting up MyCliApp..."
        
        # Ensure proper permissions
        chmod 755 "/Applications/{app_bundle.name}/Contents/MacOS/MyCliApp"
        chmod 755 "/usr/local/bin/mycli"
        
        # Add to PATH if not already there (for new shells)
        SHELL_RC=""
        if [[ "${{SHELL}}" == *"zsh"* ]]; then
            SHELL_RC="$HOME/.zshrc"
        elif [[ "${{SHELL}}" == *"bash"* ]]; then
            SHELL_RC="$HOME/.bash_profile"
        fi
        
        if [[ -n "$SHELL_RC" && -f "$SHELL_RC" ]]; then
            if ! grep -q "/usr/local/bin" "$SHELL_RC"; then
                echo 'export PATH="/usr/local/bin:$PATH"' >> "$SHELL_RC"
            fi
        fi
        
        # Remove quarantine attribute
        xattr -dr com.apple.quarantine "/Applications/{app_bundle.name}" 2>/dev/null || true
        
        echo "MyCliApp installation completed successfully!"
        echo "You can now run 'mycli --help' from any terminal."
        
        exit 0
    """
    ).strip()

    postinstall_script.write_text(postinstall_content)
    postinstall_script.chmod(0o755)

    # Create Distribution.xml for installer configuration
    distribution_xml = pkg_temp / "Distribution.xml"
    distribution_content = f"""<?xml version="1.0" encoding="utf-8"?>
<installer-script minSpecVersion="1.000000">
    <title>MyCliApp {version}</title>
    <background file="background.png" alignment="topleft" scaling="proportional"/>
    <welcome file="welcome.html"/>
    <license file="license.html"/>
    <readme file="readme.html"/>
    <options customize="never" require-scripts="false" hostArchitectures="x86_64,arm64"/>
    <domains enable_anywhere="true" enable_currentUserHome="false" enable_localSystem="true"/>
    
    <pkg-ref id="com.example.mycliapp.pkg">
        <bundle-version>
            <bundle CFBundleShortVersionString="{version}" CFBundleVersion="{version}" id="com.example.mycliapp" path="Applications/MyCliApp.app"/>
        </bundle-version>
    </pkg-ref>
    
    <choices-outline>
        <line choice="com.example.mycliapp.pkg"/>
    </choices-outline>
    
    <choice id="com.example.mycliapp.pkg" title="MyCliApp">
        <pkg-ref id="com.example.mycliapp.pkg"/>
    </choice>
    
    <pkg-ref id="com.example.mycliapp.pkg" installKBytes="50000">MyCliApp.pkg</pkg-ref>
</installer-script>"""

    distribution_xml.write_text(distribution_content)

    # Create welcome message
    welcome_html = pkg_temp / "welcome.html"
    welcome_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to MyCliApp</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; }}
        h1 {{ color: #007AFF; }}
        .version {{ color: #666; font-style: italic; }}
    </style>
</head>
<body>
    <h1>Welcome to MyCliApp</h1>
    <p class="version">Version {version}</p>
    <p>This installer will install MyCliApp, a powerful CLI tool similar to Azure CLI.</p>
    <p><strong>What will be installed:</strong></p>
    <ul>
        <li>MyCliApp.app in Applications folder</li>
        <li>Command-line interface accessible as 'mycli'</li>
        <li>Automatic PATH configuration</li>
    </ul>
    <p>After installation, you can run <code>mycli --help</code> from any terminal.</p>
</body>
</html>"""

    welcome_html.write_text(welcome_content)

    # Create license file
    license_html = pkg_temp / "license.html"
    license_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>License Agreement</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 20px; }
        pre { background: #f5f5f5; padding: 15px; border-radius: 5px; overflow: auto; }
    </style>
</head>
<body>
    <h1>MIT License</h1>
    <pre>
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
    </pre>
</body>
</html>"""

    license_html.write_text(license_content)

    try:
        # First create the component package
        component_pkg = pkg_temp / "MyCliApp.pkg"

        run(
            [
                "pkgbuild",
                "--root",
                str(payload_dir),
                "--scripts",
                str(scripts_dir),
                "--identifier",
                "com.example.mycliapp.pkg",
                "--version",
                version,
                "--install-location",
                "/",
                str(component_pkg),
            ]
        )

        # Then create the product archive with distribution
        run(
            [
                "productbuild",
                "--distribution",
                str(distribution_xml),
                "--package-path",
                str(pkg_temp),
                "--resources",
                str(pkg_temp),
                str(pkg_path),
            ]
        )

        print(f"[success] Created PKG: {pkg_path}")

    except RuntimeError as e:
        print(f"[warning] PKG creation failed: {e}")
        pkg_path = None
    finally:
        # Clean up
        if pkg_temp.exists():
            shutil.rmtree(pkg_temp)

    return pkg_path


def build_macos_distributions(build_type: str, version: str, output_dir: Path):
    """Build specified macOS distributions."""
    check_macos()

    output_dir.mkdir(parents=True, exist_ok=True)

    results = {}

    if build_type in ["zip", "all"]:
        print(f"\n{'='*60}")
        print(f"Building Standalone ZIP")
        print(f"{'='*60}")
        try:
            zip_path = build_zip(version, output_dir)
            results["zip"] = zip_path
        except Exception as e:
            print(f"[error] ZIP build failed: {e}")
            results["zip"] = None

    if build_type in ["app", "all"]:
        print(f"\n{'='*60}")
        print(f"Building macOS App Bundle")
        print(f"{'='*60}")
        try:
            app_path = create_app_bundle(version, output_dir)
            results["app"] = app_path
        except Exception as e:
            print(f"[error] App bundle build failed: {e}")
            results["app"] = None

    if build_type in ["dmg", "all"]:
        print(f"\n{'='*60}")
        print(f"Building DMG Installer")
        print(f"{'='*60}")

        # DMG requires app bundle
        app_path = results.get("app")
        if not app_path and build_type == "dmg":
            print(f"[info] Building app bundle first for DMG...")
            try:
                app_path = create_app_bundle(version, output_dir)
                results["app"] = app_path
            except Exception as e:
                print(f"[error] App bundle build failed (required for DMG): {e}")
                results["dmg"] = None
                return results

        if app_path:
            try:
                dmg_path = create_dmg(app_path, version, output_dir)
                results["dmg"] = dmg_path
            except Exception as e:
                print(f"[error] DMG build failed: {e}")
                results["dmg"] = None

    if build_type in ["pkg", "all"]:
        print(f"\n{'='*60}")
        print("Building PKG Installer")
        print(f"{'='*60}")

        # PKG requires app bundle
        app_path = results.get("app")
        if not app_path and build_type == "pkg":
            print("[info] Building app bundle first for PKG...")
            try:
                app_path = create_app_bundle(version, output_dir)
                results["app"] = app_path
            except Exception as e:
                print(f"[error] App bundle build failed (required for PKG): {e}")
                results["pkg"] = None
                return results

        if app_path:
            try:
                pkg_path = create_pkg(app_path, version, output_dir)
                results["pkg"] = pkg_path
            except Exception as e:
                print(f"[error] PKG build failed: {e}")
                results["pkg"] = None

    return results


def print_summary(results: dict, version: str, platform_tag: str):
    """Print build summary."""
    print(f"\n{'='*60}")
    print(f"BUILD SUMMARY")
    print(f"{'='*60}")
    print(f"Version: {version}")
    print(f"Platform: {platform_tag}")
    print(f"Build Date: {run(['date'], capture_output=True)}")

    print(f"\nResults:")
    for build_type, path in results.items():
        if path:
            print(f"  ✅ {build_type.upper()}: {path}")
        else:
            print(f"  ❌ {build_type.upper()}: Failed")

    print(f"\nUsage Instructions:")

    if results.get("zip"):
        print(f"\n📦 Standalone ZIP:")
        print(f"  1. Extract the ZIP file")
        print(f"  2. Run: chmod +x bin/mycli.sh")
        print(f"  3. Use: bin/mycli.sh --help")

    if results.get("app"):
        print(f"\n🖥️  macOS App Bundle:")
        print(f"  1. Copy MyCliApp.app to /Applications/")
        print(f"  2. Right-click and 'Open' first time")
        print(f"  3. Double-click to use or add to PATH")

    if results.get("dmg"):
        print(f"\n💿 DMG Installer:")
        print(f"  1. Double-click the DMG file")
        print(f"  2. Drag MyCliApp to Applications folder")
        print(f"  3. Eject the DMG")

    if results.get("pkg"):
        print(f"\n📦 PKG Installer:")
        print(f"  1. Double-click the PKG file")
        print(f"  2. Follow the installation wizard")
        print(f"  3. Use 'mycli' from any terminal")

    print(f"\n💡 Tips:")
    print(f"  • For CLI usage: Add to PATH or use full path")
    print(f"  • For GUI usage: Use the .app bundle")
    print(f"  • PKG installer automatically adds to PATH")
    print(f"  • Both include embedded Python runtime")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build macOS distributions for MyCliApp")
    parser.add_argument(
        "--type", choices=["zip", "app", "dmg", "pkg", "all"], default="all", help="Type of distribution to build"
    )
    parser.add_argument("--version", help="Override version (otherwise auto-detected)")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    version = detect_version(args.version)
    output_dir = Path(args.output)
    platform_tag = current_platform_tag()

    print(f"MyCliApp macOS Distribution Builder")
    print(f"Version: {version}")
    print(f"Platform: {platform_tag}")
    print(f"Build Type: {args.type}")
    print(f"Output: {output_dir}")

    try:
        results = build_macos_distributions(args.type, version, output_dir)
        print_summary(results, version, platform_tag)

        # Check if any builds succeeded
        success_count = sum(1 for path in results.values() if path is not None)
        if success_count > 0:
            print(f"\n🎉 {success_count} distribution(s) built successfully!")
        else:
            print(f"\n❌ All builds failed!")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
