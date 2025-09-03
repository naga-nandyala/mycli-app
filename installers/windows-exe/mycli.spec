# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MyCliApp Windows ZIP distribution
Similar to Azure CLI's ZIP package approach
Package should be installed with extras: pip install -e .[azure,broker]
"""

import sys
import os
import importlib.util
from pathlib import Path

# Get the directory where this spec file is located
spec_dir = Path(SPECPATH).parent
project_root = spec_dir.parent  # installers -> pj1 (only one level up)
src_path = project_root / 'src'
main_py = project_root / 'src' / 'mycli_app' / '__main__.py'

print(f"Spec dir: {spec_dir}")
print(f"Project root: {project_root}")
print(f"Source path: {src_path}")
print(f"Main entry: {main_py}")
print(f"Main entry exists: {main_py.exists()}")

sys.path.insert(0, str(src_path))

# Toggle to include azure dependencies (increases size)
INCLUDE_AZURE = True if os.environ.get("MYCLI_WITH_AZURE", "0") == "1" else False

def can_import(module_name):
    """Check if a module can be imported"""
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, ValueError, ModuleNotFoundError):
        return False

# Base hidden imports
hiddenimports = [
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
]

# Add Azure imports if available and enabled
if INCLUDE_AZURE:
    potential_azure_imports = [
        # Core Azure packages
        'azure.identity',
        'azure.identity._credentials', 
        'azure.identity._internal',
        'azure.identity._internal.decorators',
        'azure.mgmt.core',
        'azure.core',
        'azure.core.exceptions',
        'azure.core.credentials',
        'azure.core.pipeline',
        'azure.core.pipeline.policies',
        # MSAL packages
        'msal',
        'msal.application',
        'msal.oauth2cli', 
        'msal.token_cache',
        'msal.authority',
        'msal.client_credential',
        # PyMSAL Runtime (broker support)
        'pymsalruntime',
        'pymsalruntime.broker',
        'pymsalruntime.msalruntime',
        # Supporting packages
        'requests',
        'cryptography',
        'cryptography.hazmat.backends.openssl',
        'cryptography.hazmat.bindings._rust',
    ]
    
    available_azure_imports = []
    for module in potential_azure_imports:
        if can_import(module):
            available_azure_imports.append(module)
        else:
            print(f"Warning: Module {module} not available, skipping hidden import")
    
    hiddenimports.extend(available_azure_imports)
    print(f"Adding {len(available_azure_imports)} available Azure-specific hidden imports")
    if available_azure_imports:
        print(f"Available Azure imports: {available_azure_imports}")
    else:
        print("Warning: No Azure modules found! Package may not be installed with extras.")

block_cipher = None

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
    hiddenimports=hiddenimports,
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
