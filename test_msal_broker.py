#!/usr/bin/env python3
"""
Test script to check what dependencies msal[broker] should include
"""

import subprocess
import sys
import tempfile
import os

def test_msal_broker_deps():
    """Test what packages get installed with msal[broker]"""
    
    print("🔍 Testing what msal[broker] installs...")
    
    # Create a temporary virtual environment
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = os.path.join(temp_dir, "test_venv")
        
        # Create virtual environment
        print(f"📁 Creating test venv at {venv_path}")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        
        # Get pip path
        if os.name == 'nt':  # Windows
            pip_path = os.path.join(venv_path, "Scripts", "pip.exe")
            python_path = os.path.join(venv_path, "Scripts", "python.exe")
        else:  # Unix/Mac
            pip_path = os.path.join(venv_path, "bin", "pip")
            python_path = os.path.join(venv_path, "bin", "python")
        
        # Install msal[broker]
        print("📦 Installing msal[broker]...")
        result = subprocess.run([
            pip_path, "install", "msal[broker]==1.20.0"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Failed to install msal[broker]: {result.stderr}")
            return
        
        print("✅ Successfully installed msal[broker]")
        
        # List installed packages
        print("\n📋 Packages installed with msal[broker]:")
        result = subprocess.run([
            pip_path, "list", "--format=columns"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['msal', 'broker', 'azure', 'auth', 'microsoft']):
                    print(f"  📦 {line}")
        else:
            print(f"❌ Failed to list packages: {result.stderr}")
        
        # Check specific packages
        print("\n🔍 Checking for broker-related packages:")
        packages_to_check = [
            'msal',
            'pymsalruntime', 
            'msal-extensions',
            'azure-identity',
            'cryptography'
        ]
        
        for package in packages_to_check:
            result = subprocess.run([
                pip_path, "show", package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Extract version from output
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        print(f"  ✅ {package}: v{version}")
                        break
            else:
                print(f"  ❌ {package}: NOT FOUND")

if __name__ == "__main__":
    test_msal_broker_deps()