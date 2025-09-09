# Windows Bundling for MyCLI

This directory contains scripts and tools for creating Windows-specific portable bundles for MyCLI, similar to the macOS bundling approach.

## Overview

The Windows bundling approach creates a self-contained virtual environment with all dependencies, similar to how the Azure CLI distributes their Windows packages. This approach provides:

- Portable installation without requiring Python pre-installation
- All Azure SDK dependencies bundled
- Multiple launcher options (batch, PowerShell, executable)
- Easy distribution via ZIP, Chocolatey, or Windows installer

## Files

- `create_windows_bundle.py` - Main bundling script
- `README.md` - This documentation

## Usage

### Prerequisites

1. **Windows System**: This script must be run on Windows
2. **Python 3.8+**: Python with pip installed
3. **Virtual Environment**: Create and activate a virtual environment in the project root
4. **Dependencies**: Install the project with Azure extras

### Setup

```cmd
# From project root
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e .[azure,broker]
```

### Running the Bundle Script

```cmd
# Basic usage
python windows_packaging\venv_bundling\create_windows_bundle.py

# Custom output directory
python windows_packaging\venv_bundling\create_windows_bundle.py --output dist\windows

# Specific architecture
python windows_packaging\venv_bundling\create_windows_bundle.py --arch AMD64

# Custom version
python windows_packaging\venv_bundling\create_windows_bundle.py --version 1.2.0
```

### Command Line Options

- `--output`, `-o`: Output directory for the bundle (default: `./dist`)
- `--python-version`: Python version to use (e.g., `3.11`, `3.12`)
- `--arch`: Target architecture (`x86`, `AMD64`, `ARM64`)
- `--version`: Package version for naming (e.g., `1.0.0`)

## What the Script Does

1. **Environment Validation**: Ensures running on Windows
2. **Virtual Environment Creation**: Creates isolated Python environment
3. **Dependency Installation**: Installs all Azure SDK dependencies
4. **Launcher Creation**: Creates multiple launcher types:
   - `mycli.bat` - Batch file launcher
   - `mycli.ps1` - PowerShell launcher  
   - `mycli.exe` - Direct executable (if pip creates one)
5. **Bundle Verification**: Tests the bundle functionality
6. **Distribution Packages**: Creates ZIP, Chocolatey template, installer template

## Output Structure

The script creates several output files:

```
dist/
├── mycli-AMD64-<version>-AMD64.zip          # Main distribution ZIP
├── mycli-AMD64-<version>-AMD64.zip.sha256   # Checksum file
├── chocolatey/                              # Chocolatey package template
│   ├── mycli.nuspec
│   └── tools/
│       ├── chocolateyinstall.ps1
│       └── chocolateyuninstall.ps1
├── mycli-installer.iss                      # Inno Setup installer template
└── mycli-AMD64-structure.txt                # Bundle structure info
```

## Bundle Structure

The created bundle has this structure:

```
mycli-AMD64/
├── bundle_info.json        # Bundle metadata
├── README.md              # Usage instructions
├── pyvenv.cfg             # Virtual environment config
├── Scripts/               # Executables and launchers
│   ├── python.exe         # Python interpreter
│   ├── mycli.bat          # Batch launcher
│   ├── mycli.ps1          # PowerShell launcher
│   └── mycli.exe          # Direct executable (if available)
├── Lib/                   # Python libraries
│   └── site-packages/     # All dependencies including Azure SDK
└── Include/               # Header files (if needed)
```

## Usage of Bundled Application

### Direct Usage

```cmd
# Extract the ZIP file
# Navigate to the bundle directory
cd mycli-AMD64

# Run using batch launcher
Scripts\mycli.bat --help
Scripts\mycli.bat login

# Run using PowerShell launcher
Scripts\mycli.ps1 --help
Scripts\mycli.ps1 login

# Run using direct executable (if available)
Scripts\mycli.exe --help
Scripts\mycli.exe login
```

### Adding to PATH

```cmd
# Add Scripts directory to PATH
set PATH=%PATH%;C:\path\to\mycli-AMD64\Scripts

# Now use from anywhere
mycli --help
mycli login
```

## Distribution Options

### 1. ZIP Distribution

The simplest distribution method. Users download and extract the ZIP file.

**Pros:**
- Simple to create and distribute
- Works immediately after extraction
- No installation required

**Cons:**
- Manual PATH setup
- No automatic updates
- User must manage file location

### 2. Chocolatey Package

Professional package management for Windows.

**Setup:**
1. Use the generated `chocolatey/` template
2. Update URLs and checksums in `chocolateyinstall.ps1`
3. Build with `choco pack`
4. Submit to Chocolatey community repository

**Pros:**
- Automatic PATH setup
- Easy installation with `choco install mycli`
- Integrated with Windows package management
- Automatic updates

**Cons:**
- Requires Chocolatey to be installed
- Review process for community repository

### 3. Windows Installer

Traditional Windows MSI installer using Inno Setup.

**Setup:**
1. Install Inno Setup
2. Use the generated `mycli-installer.iss` template
3. Compile the installer

**Pros:**
- Familiar Windows installation experience
- Automatic PATH setup
- Uninstall support via Control Panel
- No additional dependencies

**Cons:**
- Requires Inno Setup to build
- Larger file size
- More complex build process

## Comparison with Existing PyInstaller Approach

| Feature | Windows Bundle (This) | PyInstaller (Existing) |
|---------|----------------------|------------------------|
| **Distribution** | ZIP/Chocolatey/Installer | Single EXE |
| **Size** | ~50-100MB | ~30-50MB |
| **Startup Time** | Fast | Slower (extraction) |
| **Dependencies** | All bundled | Minimal |
| **Maintenance** | Easy updates | Rebuild required |
| **PATH Integration** | Multiple options | Manual |
| **Azure SDK** | Full SDK included | Limited subset |
| **Debugging** | Easy (full Python) | Difficult |

## Azure SDK Integration

The bundle includes full Azure SDK support:

- `azure-identity` - Authentication methods
- `azure-core` - Core functionality  
- `azure-mgmt-core` - Management APIs
- `msal[broker]` - Microsoft Authentication Library with broker support

The bundle is tested to ensure all Azure packages are properly installed and importable.

## Troubleshooting

### Bundle Creation Issues

1. **Missing Azure Packages**: Ensure project is installed with `[azure,broker]` extras
2. **Permission Errors**: Run as administrator if needed
3. **Path Issues**: Use absolute paths for output directories

### Bundle Usage Issues

1. **Import Errors**: Check if Azure packages are properly bundled
2. **Path Issues**: Ensure Scripts directory is in PATH
3. **Launcher Issues**: Try different launcher types (bat/ps1/exe)

### Common Error Messages

**"Azure SDK: Not Available"**
- Bundle may be missing Azure packages
- Check bundle_info.json for Azure package list
- Re-run bundling with verbose output

**"Bundle Python interpreter not found"**
- Bundle structure may be corrupted
- Check if python.exe exists in Scripts directory
- Verify bundle extraction was complete

## Performance Considerations

- **Bundle Size**: ~50-100MB depending on included packages
- **Startup Time**: ~1-2 seconds (similar to native Python)
- **Memory Usage**: Similar to running Python directly
- **Disk I/O**: Minimal after initial load

## Security Considerations

- Bundle includes full Python interpreter
- All dependencies are at versions specified in pyproject.toml
- SHA256 checksums provided for integrity verification
- No automatic update mechanism (manual security updates required)

## Future Enhancements

1. **Automatic Updates**: Implement update mechanism
2. **Digital Signing**: Code signing for Windows executables
3. **ARM64 Support**: Native ARM64 builds for newer Windows devices
4. **Size Optimization**: Remove unnecessary files to reduce bundle size
5. **Multi-Python Support**: Support for different Python versions

## Contributing

When making changes to the bundling script:

1. Test on different Windows versions (10, 11)
2. Test on different architectures (x86, AMD64, ARM64)
3. Verify Azure SDK functionality after bundling
4. Update documentation for any new features
5. Test all distribution methods (ZIP, Chocolatey, Installer)
