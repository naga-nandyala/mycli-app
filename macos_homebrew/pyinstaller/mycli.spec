# mycli.spec - fully updated PyInstaller spec for mycli-app-naga
# Usage (macOS): pyinstaller mycli.spec
# Recommended: build in a clean venv with extras installed:
# pip install -e .[azure,broker]

import os
import importlib.util
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

# ---------------------------
# Project Paths Setup
# ---------------------------
PROJECT_ROOT = os.getcwd()
# Check if we need to adjust the root path
entry_script_check = os.path.join(PROJECT_ROOT, "src", "mycli_app", "cli.py")
if not os.path.exists(entry_script_check):
    # fallback if running from spec directory
    alt_root = os.path.abspath(os.path.join(PROJECT_ROOT, "..", ".."))
    candidate = os.path.join(alt_root, "src", "mycli_app", "cli.py")
    if os.path.exists(candidate):
        PROJECT_ROOT = alt_root

print(f"Project root: {PROJECT_ROOT}")

# Toggle Azure & Broker extras via environment variable
INCLUDE_AZURE = os.environ.get("MYCLI_WITH_AZURE", "1") == "1"

def can_import(module_name):
    """Check if a module can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False

# ---------------------------
# Hidden Imports
# ---------------------------
hiddenimports = []

if INCLUDE_AZURE:
    optional_modules = [
        # MSAL core modules
        "msal.application",
        "msal.oauth2cli", 
        "msal.token_cache",
        "msal.authority",
        "msal.client_credential",
        # Azure identity internals
        "azure.identity._credentials", 
        "azure.identity._internal",
        "azure.identity._internal.decorators",
        # Azure core essentials
        "azure.core.credentials",
        "azure.core.pipeline",
        "azure.core.pipeline.policies",
        # PyMSAL Runtime / broker support
        "pymsalruntime",
        "pymsalruntime.broker",
        "pymsalruntime.msalruntime",
        # Cryptography backends
        "cryptography.hazmat.backends.openssl",
        "cryptography.hazmat.bindings._rust",
    ]

    for mod in optional_modules:
        if can_import(mod):
            hiddenimports.append(mod)
        else:
            print(f"Warning: Optional module {mod} not found, skipping hidden import")

print(f"Hidden imports included ({len(hiddenimports)}): {hiddenimports}")

# ---------------------------
# Data Files
# ---------------------------
# Include any non-Python files your CLI needs
datas = []

# Try to collect package data files safely
try:
    package_datas = collect_data_files("mycli_app")
    datas.extend(package_datas)
    print(f"Collected {len(package_datas)} package data files")
except Exception as e:
    print(f"Warning: Could not collect mycli_app data files: {e}")

# Check for optional config files (don't fail if missing)
config_files = [
    ("src/mycli_app/config.yaml", "."),
    ("config.yaml", "."),
]

for src_path, dest_path in config_files:
    full_src = os.path.join(PROJECT_ROOT, src_path)
    if os.path.exists(full_src):
        datas.append((full_src, dest_path))
        print(f"Added config file: {src_path}")
        break  # Only add first found config
else:
    print("Note: No config.yaml found (this is optional)")

# ---------------------------
# Binaries
# ---------------------------
# Include compiled shared libraries
binaries = []

# Try to collect cryptography libraries (essential)
try:
    crypto_libs = collect_dynamic_libs("cryptography")
    binaries.extend(crypto_libs)
    print(f"Added {len(crypto_libs)} cryptography libraries")
except Exception as e:
    print(f"Warning: Could not collect cryptography libraries: {e}")

# Try to collect pymsalruntime libraries (optional)
try:
    if can_import("pymsalruntime"):
        msal_libs = collect_dynamic_libs("pymsalruntime")
        binaries.extend(msal_libs)
        print(f"Added {len(msal_libs)} pymsalruntime libraries")
    else:
        print("pymsalruntime not available, skipping binary collection")
except Exception as e:
    print(f"Warning: Could not collect pymsalruntime libraries: {e}")

# ---------------------------
# Entry Script & Paths
# ---------------------------
entry_script = os.path.join(PROJECT_ROOT, "src", "mycli_app", "cli.py")
if not os.path.exists(entry_script):
    raise FileNotFoundError(f"Cannot find entry script at {entry_script}")

pathex = [PROJECT_ROOT]

# ---------------------------
# PyInstaller Analysis
# ---------------------------
block_cipher = None

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

a = Analysis(
    [entry_script],
    pathex=pathex,
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="mycli",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="mycli",
)
