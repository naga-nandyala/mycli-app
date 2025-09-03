# PyInstaller spec file for building the mycli standalone binary
# Usage (run on macOS for each architecture):
#   pyinstaller mycli.spec
# Adjust hiddenimports if enabling Azure features.

import os
from PyInstaller.utils.hooks import collect_submodules

# Toggle to include azure dependencies (increases size)
INCLUDE_AZURE = True if os.environ.get("MYCLI_WITH_AZURE", "0") == "1" else False

hiddenimports = []
if INCLUDE_AZURE:
    azure_pkgs = [
        "azure.identity",
        "azure.core",
        "azure.mgmt.core",
        "msal",
    ]
    for pkg in azure_pkgs:
        hiddenimports.extend(collect_submodules(pkg))

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
