#!/usr/bin/env python3
"""
Test script to verify that Azure packages are available.
This script can be used to test the bundle creation process.
"""

import sys


def test_azure_imports():
    """Test if Azure packages can be imported."""
    missing_packages = []

    try:
        import azure.identity

        print(f"✅ azure-identity: {azure.identity.__version__}")
    except ImportError as e:
        missing_packages.append(f"azure-identity: {e}")

    try:
        import azure.core

        print(f"✅ azure-core: {azure.core.__version__}")
    except ImportError as e:
        missing_packages.append(f"azure-core: {e}")

    try:
        import azure.mgmt.core

        print(f"✅ azure-mgmt-core: {azure.mgmt.core.__version__}")
    except ImportError as e:
        missing_packages.append(f"azure-mgmt-core: {e}")

    try:
        import msal

        print(f"✅ msal: {msal.__version__}")
    except ImportError as e:
        missing_packages.append(f"msal: {e}")

    if missing_packages:
        print("\n❌ Missing packages:")
        for pkg in missing_packages:
            print(f"  - {pkg}")
        return False
    else:
        print("\n✅ All Azure packages are available!")
        return True


def test_mycli_azure_detection():
    """Test if mycli correctly detects Azure packages."""
    try:
        from mycli_app.cli import AZURE_AVAILABLE

        if AZURE_AVAILABLE:
            print("✅ mycli correctly detects Azure packages as available")
            return True
        else:
            print("❌ mycli incorrectly detects Azure packages as unavailable")
            return False
    except ImportError as e:
        print(f"❌ Could not import mycli_app.cli: {e}")
        return False


if __name__ == "__main__":
    print("🔍 Testing Azure package availability...")
    print("=" * 50)

    imports_ok = test_azure_imports()
    print()
    detection_ok = test_mycli_azure_detection()

    print("\n" + "=" * 50)
    if imports_ok and detection_ok:
        print("🎉 All Azure package tests passed!")
        sys.exit(0)
    else:
        print("❌ Some Azure package tests failed!")
        sys.exit(1)
