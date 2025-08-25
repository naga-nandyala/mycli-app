# MyCliApp Windows ZIP Package - Quick Start

## Overview

This guide helps you build and distribute MyCliApp as a standalone Windows ZIP package, similar to Azure CLI's installation approach.

## Prerequisites

- Python 3.8+
- Virtual environment (recommended)
- PowerShell (for build script)

## Building the ZIP Package

### Method 1: Using PowerShell Build Script (Recommended)

```powershell
# Navigate to project root
cd c:\dev_win\gitrepos_win\lrn_explore\pkg_related\pj1

# Build with default settings
.\installers\windows-zip\build.ps1

# Build with custom version and clean build
.\installers\windows-zip\build.ps1 -Version "1.0.1" -Clean
```

### Method 2: Manual Build

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install --upgrade pip pyinstaller
python -m pip install -e .[azure,broker]

# Build with PyInstaller
pyinstaller --clean .\installers\windows-zip\mycli.spec
```

## What Gets Created

The build process creates:

```text
installers\windows-zip\dist\
├── MyCliApp-1.0.0-Windows-x64.zip     # Final distribution ZIP
└── mycli\                             # Standalone executable folder
    ├── mycli.exe                      # Main executable
    └── [dependencies]                 # All required DLLs and files
```

## ZIP Package Contents

When users extract the ZIP file, they get:

```text
MyCliApp-Windows-x64\
├── install.bat                       # Installation verification script
├── README.md                         # User installation guide
└── mycli\                           # Application folder
    ├── mycli.exe                    # Main executable
    └── [all dependencies]          # Runtime files
```

## Distribution

1. **Upload the ZIP file** to your releases page or distribution server
2. **Users download and extract** to their preferred location
3. **Users run install.bat** to verify installation
4. **Users add to PATH** (optional) or use directly

## User Installation Experience

### For End Users

1. Download `MyCliApp-1.0.0-Windows-x64.zip`
2. Extract to desired location (e.g., `C:\MyCliApp`)
3. Run `install.bat` to verify
4. Add `C:\MyCliApp\mycli` to PATH (optional)

### Usage

```cmd
# Direct usage
C:\MyCliApp\mycli\mycli.exe --help

# If added to PATH
mycli --help
mycli auth login
```

## Features

- ✅ **No Python required** - Standalone executable
- ✅ **All dependencies included** - Azure SDK, MSAL, etc.
- ✅ **Windows optimized** - Native executable with version info
- ✅ **Small download size** - Optimized with UPX compression
- ✅ **Professional appearance** - Windows version information
- ✅ **Easy installation** - Simple extract and run

## Similar to Azure CLI

This approach mimics Azure CLI's Windows ZIP installation method:
- Standalone executable bundle
- No system modifications required
- User-controlled installation location
- Optional PATH integration

## Troubleshooting

### Build Issues

1. **PyInstaller not found**: Install with `pip install pyinstaller`
2. **Missing dependencies**: Run `pip install -e .[azure,broker]`
3. **Permission errors**: Run PowerShell as Administrator

### Runtime Issues

1. **Missing DLLs**: Ensure all dependencies are in the executable folder
2. **Azure auth fails**: Check if all MSAL/Azure modules are included
3. **Large file size**: Review excludes in mycli.spec

## Customization

### Change Version Info

Edit `installers\windows-zip\version_info.txt`:
- Update version numbers
- Change company/product names
- Modify descriptions

### Modify Build Settings

Edit `installers\windows-zip\mycli.spec`:
- Add/remove dependencies
- Change exclusions for size optimization
- Add application icon

### Custom Build Script

Modify `installers\windows-zip\build.ps1`:
- Add signing steps
- Include additional files
- Customize ZIP structure

## Next Steps

After mastering Windows ZIP distribution, you can expand to other Azure CLI-inspired methods:
- Windows MSI installer
- PowerShell module
- Chocolatey package
- Winget manifest

## File Sizes (Typical)

- Executable: ~15-25 MB (with Azure SDK)
- ZIP package: ~8-15 MB (with UPX compression)
- Uncompressed: ~40-60 MB (all dependencies)

These are similar to Azure CLI's distribution sizes.
