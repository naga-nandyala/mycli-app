# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Add the src directory to sys.path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

block_cipher = None

a = Analysis(
    ['../src/mycli_app/__main__.py'],  # Entry point
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        # Include documentation files
        ('../README.md', '.'),
        ('../LICENSE', '.'),
        ('../USER_GUIDE.md', '.'),
        ('../CHANGELOG.md', '.'),
    ],
    hiddenimports=[
        'mycli_app',
        'mycli_app.cli',
        'click',
        'colorama',
        'requests',
        # Azure imports (optional)
        'azure.identity',
        'azure.mgmt.core',
        'azure.core',
        'msal',
        # JSON and other modules that might be missed
        'json',
        'urllib3',
        'certifi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy',
        'pandas',
        'jupyter',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mycli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable (if UPX is available)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one: 'path/to/icon.ico'
    version_file='version_info.txt',  # Add version info
)
