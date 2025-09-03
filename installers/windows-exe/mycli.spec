# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MyCliApp Windows ZIP distribution
Similar to Azure CLI's ZIP package approach
"""

import sys
import os
from pathlib import Path

# Get the directory where this spec file is located
spec_dir = Path(SPECPATH).parent
project_root = spec_dir.parent  # Only go up one level, not two
src_path = project_root / 'src'
main_py = project_root / 'src' / 'mycli_app' / '__main__.py'

sys.path.insert(0, str(src_path))

block_cipher = None

a = Analysis(
    [str(main_py)],  # Entry point
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        # Include documentation files in the executable
        (str(project_root / 'README.md'), '.'),
        (str(project_root / 'LICENSE'), '.'),
        (str(project_root / 'CHANGELOG.md'), '.'),
    ],
    hiddenimports=[
        # Core application
        'mycli_app',
        'mycli_app.cli',
        'mycli_app.__main__',
        
        # CLI framework
        'click',
        'colorama',
        
        # Standard library modules that might be missed
        'json',
        'base64',
        'pathlib',
        'urllib3',
        'certifi',
        
        # Azure imports (optional but include for full functionality)
        'azure.identity',
        'azure.mgmt.core',
        'azure.core',
        'azure.core.exceptions',
        'azure.core.credentials',
        'msal',
        'msal.application',
        'requests',
        'cryptography',
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
        'PIL',
        'pygame',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'kivy',
        'tornado',
        'flask',
        'django',
        'sqlalchemy',
        'docutils',
        'pydoc',
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
    console=True,  # Console application (not GUI)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add 'mycli.ico' if you have an icon
    version_file=str(spec_dir / 'version_info.txt'),
)
