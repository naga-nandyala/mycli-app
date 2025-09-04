#!/usr/bin/env python3
"""Test script to verify macOS broker authentication support."""

import sys
import os
import platform


# Mock platform functions for testing
def mock_get_broker_info():
    """Get information about available broker authentication methods."""
    broker_info = {
        "windows_hello_available": False,
        "authenticator_app_available": False,
        "keychain_available": False,
        "touch_id_available": False,
        "platform_support": False,
        "recommendations": [],
    }

    # Check if we're on Windows (primary platform for broker support)
    if os.name == "nt":
        broker_info["platform_support"] = True
        broker_info["recommendations"].append("Windows Hello for Business")
        broker_info["recommendations"].append("Microsoft Authenticator app")
        broker_info["windows_hello_available"] = True  # Assume available on Windows
        broker_info["authenticator_app_available"] = True  # Assume available
    elif platform.system() == "Darwin":  # macOS
        broker_info["platform_support"] = True
        broker_info["recommendations"].append("macOS Keychain")
        broker_info["recommendations"].append("Touch ID / Face ID")
        broker_info["recommendations"].append("Microsoft Authenticator app")
        broker_info["keychain_available"] = True  # Assume available on macOS
        broker_info["touch_id_available"] = True  # Assume available on modern Macs
        broker_info["authenticator_app_available"] = True  # Assume available
    else:
        broker_info["recommendations"].append("Use device code flow for other platforms")

    return broker_info


def test_platforms():
    """Test broker support detection for different platforms."""
    print("=== Testing Platform Detection ===")

    # Current platform
    print(f"\nCurrent Platform:")
    print(f"  os.name: {os.name}")
    print(f"  platform.system(): {platform.system()}")
    broker_info = mock_get_broker_info()
    print("  Broker info:")
    for key, value in broker_info.items():
        print(f"    {key}: {value}")

    # Mock macOS
    print(f"\nSimulated macOS:")
    original_system = platform.system
    original_os_name = os.name

    try:
        # Mock macOS environment
        platform.system = lambda: "Darwin"
        os.name = "posix"

        broker_info = mock_get_broker_info()
        print("  Broker info:")
        for key, value in broker_info.items():
            print(f"    {key}: {value}")

    finally:
        # Restore original values
        platform.system = original_system
        os.name = original_os_name

    # Mock Linux
    print(f"\nSimulated Linux:")
    try:
        # Mock Linux environment
        platform.system = lambda: "Linux"
        os.name = "posix"

        broker_info = mock_get_broker_info()
        print("  Broker info:")
        for key, value in broker_info.items():
            print(f"    {key}: {value}")

    finally:
        # Restore original values
        platform.system = original_system
        os.name = original_os_name


if __name__ == "__main__":
    test_platforms()
