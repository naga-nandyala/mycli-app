#!/usr/bin/env python3
"""
Simple test script to demonstrate Windows bundle creation for MyCLI.
Run this script to create a Windows bundle for testing.
"""

import sys
import subprocess
import os
from pathlib import Path


def main():
    """Main test function."""
    print("🧪 Testing Windows Bundle Creation for MyCLI")
    print("=" * 50)

    # Check if we're on Windows
    if sys.platform != "win32":
        print("❌ This test must be run on Windows")
        print(f"Current platform: {sys.platform}")
        return 1

    # Get project root and script path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    bundle_script = script_dir / "create_windows_bundle.py"
    
    print(f"📁 Project root: {project_root}")
    print(f"📄 Bundle script: {bundle_script}")

 

    # Check if bundle script exists
    if not bundle_script.exists():
        print(f"❌ Bundle script not found: {bundle_script}")
        return 1

    # Check if virtual environment is activated
    print(f"{os.environ.get("VIRTUAL_ENV")}")
    if not os.environ.get("VIRTUAL_ENV"):
        print("⚠️  Warning: No virtual environment detected")
        print("💡 Recommendation: Activate .venv first:")
        print("   .venv\\Scripts\\activate.bat")
        print("")
   
   
   
    # Check if mycli is installed
    try:
        result = subprocess.run([sys.executable, "-c", "import mycli_app.cli"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ mycli_app not found. Install with:")
            print("   pip install -e .[azure,broker]")
            return 1
        else:
            print("✅ mycli_app is installed")
    except Exception as e:
        print(f"❌ Error checking mycli_app: {e}")
        return 1
    
    # Create test output directory
    test_output = project_root / "test_bundle_output"
    test_output.mkdir(exist_ok=True)

    print(f"📂 Test output directory: {test_output}")

    # Run the bundle creation script
    print("\n🚀 Running bundle creation script...")
    print("-" * 30)
     
    try:
        cmd = [sys.executable, str(bundle_script), "--output", str(test_output), "--version", "test-1.0.0"]

        print(f"Command: {' '.join(cmd)}")

        result = subprocess.run(cmd, cwd=project_root, text=True)

        if result.returncode == 0:
            print("\n✅ Bundle creation completed successfully!")

            # List created files
            print(f"\n📋 Files created in {test_output}:")
            for item in test_output.iterdir():
                if item.is_file():
                    size_mb = item.stat().st_size / (1024 * 1024)
                    print(f"   📄 {item.name} ({size_mb:.1f} MB)")
                elif item.is_dir():
                    print(f"   📁 {item.name}/")

            # Show next steps
            print("\n🎯 Next Steps:")
            print("1. Extract and test the ZIP bundle")
            print("2. Try running the bundled mycli:")
            print("   - Extract the ZIP file")
            print("   - Run: extracted_bundle\\Scripts\\mycli.bat --help")
            print("3. Test Chocolatey package (if desired)")
            print("4. Test Windows installer (if desired)")

        else:
            print(f"\n❌ Bundle creation failed with exit code: {result.returncode}")
            return 1

    except Exception as e:
        print(f"\n❌ Error running bundle script: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
