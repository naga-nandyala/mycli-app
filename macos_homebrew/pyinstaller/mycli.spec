# PyInstaller spec file for building the mycli standalone binary
# Usage (run on macOS for each architecture):
#   pyinstaller mycli.spec
# Package should be installed with extras: pip install -e .[azure,broker]

import os
import importlib.util

# Toggle to include azure dependencies (increases size)
INCLUDE_AZURE = True if os.environ.get("MYCLI_WITH_AZURE", "0") == "1" else False

def can_import(module_name):
    """Check if a module can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False

hiddenimports = []
if INCLUDE_AZURE:
    # Only add hidden imports for modules that are actually available
    potential_imports = [
        # Core MSAL modules that might be dynamically imported
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
        # PyMSAL Runtime (broker support)
        "pymsalruntime",
        "pymsalruntime.broker",
        "pymsalruntime.msalruntime",
        # Cryptography backends
        "cryptography.hazmat.backends.openssl",
        "cryptography.hazmat.bindings._rust",
    ]
    
    available_imports = []
    for module in potential_imports:
        if can_import(module):
            available_imports.append(module)
        else:
            print(f"Warning: Module {module} not available, skipping hidden import")
    
    hiddenimports = available_imports
    print(f"Adding {len(hiddenimports)} available Azure-specific hidden imports")
    if hiddenimports:
        print(f"Available imports: {hiddenimports}")
    else:
        print("Warning: No Azure modules found! Package may not be installed with extras.")

block_cipher = None

"""Spec adjustments:
We cannot rely on __file__ (not injected by PyInstaller exec). Use current working
directory (expected repo root in CI). Fallback: ascend two levels if entry script
not found initially (covers invocation from spec directory).
"""
PROJECT_ROOT = os.getcwd()
entry_script = os.path.join(PROJECT_ROOT, 'src', 'mycli_app', 'cli.py')
if not os.path.exists(entry_script):
    # Try going two levels up (running from spec dir scenario)
    alt_root = os.path.abspath(os.path.join(PROJECT_ROOT, '..', '..'))
    candidate = os.path.join(alt_root, 'src', 'mycli_app', 'cli.py')
    if os.path.exists(candidate):
        PROJECT_ROOT = alt_root
        entry_script = candidate

pathex = [PROJECT_ROOT]

a = Analysis(
    [entry_script],
    pathex=pathex,
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
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
    name='mycli',
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
    name='mycli'
)
