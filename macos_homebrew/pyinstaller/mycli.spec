# mycli.spec - fully updated PyInstaller spec for mycli-app-naga
# Usage (macOS): pyinstaller mycli.spec
# Recommended: build in a clean venv with extras installed:
# pip install -e .[azure,broker]

import os
import importlib.util
from PyInstaller.utils.hooks import collect_dynamic_libs, collect_data_files

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
datas = collect_data_files("mycli_app")  # collects all package data files
# Add custom files if needed
custom_datas = [
    ("src/mycli_app/config.yaml", "."),
    ("src/mycli_app/templates/*", "templates"),
]
datas.extend(custom_datas)

# ---------------------------
# Binaries
# ---------------------------
# Include compiled shared libraries
binaries = collect_dynamic_libs("cryptography") + collect_dynamic_libs("pymsalruntime")

# ---------------------------
# Entry Script & Paths
# ---------------------------
PROJECT_ROOT = os.getcwd()
entry_script = os.path.join(PROJECT_ROOT, "src", "mycli_app", "cli.py")
if not os.path.exists(entry_script):
    # fallback if running from spec directory
    alt_root = os.path.abspath(os.path.join(PROJECT_ROOT, "..", ".."))
    candidate = os.path.join(alt_root, "src", "mycli_app", "cli.py")
    if os.path.exists(candidate):
        PROJECT_ROOT = alt_root
        entry_script = candidate
    else:
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
