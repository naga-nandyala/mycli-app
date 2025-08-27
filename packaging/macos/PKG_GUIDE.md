# Complete macOS Packaging Guide

A comprehensive guide to all macOS distribution formats supported by MyCliApp: ZIP, APP, DMG, and PKG.

## Overview of macOS Distribution Types

MyCliApp supports four distinct packaging formats, each optimized for different use cases and user preferences:

### Format Comparison

| Format | Installation Method | User Experience | System Integration | Target Audience |
|--------|-------------------|------------------|-------------------|-----------------|
| **ZIP** | Extract & run manually | Command-line focused | None (portable) | Developers, CI/CD, power users |
| **APP** | Drag to Applications | Native Mac app | Manual setup | Standard Mac users |
| **DMG** | Mount disk, drag & drop | Traditional Mac installer | Manual setup | General Mac users |
| **PKG** | Double-click installer | Professional wizard | Automatic setup | Enterprise, general users |

## 1. ZIP Distribution (Cross-Platform)

### Description
Portable ZIP archive with embedded Python runtime, similar to Azure CLI distribution.

### Features
- ✅ **Portable**: No installation required, runs from any directory
- ✅ **Cross-platform**: Same format works on macOS, Linux, Windows
- ✅ **CI/CD friendly**: Perfect for automated environments
- ✅ **No admin rights**: Runs in user space
- ✅ **Multiple versions**: Can run different versions side-by-side

### Usage
```bash
# Extract and run
unzip MyCliApp-1.0.0-darwin-x64.zip
cd MyCliApp-1.0.0-darwin-x64/
./bin/mycli.sh --help

# Make globally available (optional)
echo 'export PATH="$PWD/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
mycli --help
```

### When to Use
- **Development environments**
- **CI/CD pipelines** 
- **Docker containers**
- **Testing multiple versions**
- **Users without admin privileges**

### Output Structure
```text
MyCliApp-1.0.0-darwin-x64/
├── bin/
│   ├── mycli.sh              # Main launcher script
│   └── mycli.cmd             # Windows compatibility
├── python/                   # Embedded Python runtime
│   ├── bin/python3.12
│   └── lib/python3.12/
└── lib/
    └── mycli_app/           # Application code
```

## 2. APP Bundle (Native macOS)

### Description
Native macOS application bundle (.app) that integrates seamlessly with the Mac desktop environment.

### Features
- ✅ **Native macOS integration**: Appears in Applications, Launchpad, Spotlight
- ✅ **Double-click to run**: Opens terminal with CLI ready
- ✅ **Proper app metadata**: Version info, icons, bundle identifier
- ✅ **Embedded runtime**: No system Python dependency
- ✅ **Gatekeeper compatible**: Can be code-signed for distribution

### Usage
```bash
# Install
cp -r MyCliApp.app /Applications/

# Run from GUI
open /Applications/MyCliApp.app

# Run from command line
/Applications/MyCliApp.app/Contents/MacOS/MyCliApp --help

# Add to PATH (optional)
echo 'export PATH="/Applications/MyCliApp.app/Contents/MacOS:$PATH"' >> ~/.zshrc
source ~/.zshrc
MyCliApp --help
```

### When to Use
- **Standard Mac application distribution**
- **Users who prefer GUI interaction**
- **Integration with macOS ecosystem**
- **Code signing and notarization**

### Bundle Structure
```text
MyCliApp.app/
├── Contents/
│   ├── Info.plist           # App metadata
│   ├── MacOS/
│   │   └── MyCliApp         # Main executable launcher
│   ├── Resources/           # Icons, docs, etc.
│   └── Frameworks/
│       └── Python/          # Embedded Python runtime
```

## 3. DMG Installer (Disk Image)

### Description
Traditional macOS disk image installer that provides drag-and-drop installation experience.

### Features
- ✅ **Familiar Mac experience**: Standard "drag to Applications" interface
- ✅ **Visual presentation**: Custom background, icons, and layout
- ✅ **Compressed distribution**: Efficient file size with compression
- ✅ **Mountable image**: Appears as virtual disk on desktop
- ✅ **Professional appearance**: Looks like commercial Mac software

### Usage
```bash
# Install
open MyCliApp-1.0.0-darwin-x64.dmg
# Drag MyCliApp.app to Applications folder in the DMG window
# Eject the DMG

# Run the installed app
open /Applications/MyCliApp.app

# Add to PATH for CLI access (manual)
echo 'export PATH="/Applications/MyCliApp.app/Contents/MacOS:$PATH"' >> ~/.zshrc
source ~/.zshrc
MyCliApp --help
```

### When to Use DMG
- **Traditional Mac software distribution**
- **Professional software appearance**
- **Users familiar with Mac software installation**
- **When you want custom installer presentation**

### DMG Contents
- MyCliApp.app (the application bundle)
- Applications symlink (for easy drag-and-drop)
- Optional: README, license files, custom background

## 4. PKG Installer (Professional Package)

### Description
Apple's native installer package format providing guided installation with system integration.

### Features
- ✅ **Professional installer wizard**: Welcome, license, progress, completion screens
- ✅ **Automatic system integration**: Sets up PATH, permissions, locations
- ✅ **Command-line availability**: Installs `mycli` command globally
- ✅ **Enterprise deployment**: MDM support, silent installation
- ✅ **Proper uninstall support**: System-level installation tracking
- ✅ **Pre/post install scripts**: Custom installation logic

### What Our PKG Does
1. **Shows welcome screen** with app description and version
2. **Displays license agreement** (MIT License)
3. **Installs MyCliApp.app** to `/Applications/`
4. **Creates CLI symlink** at `/usr/local/bin/mycli`
5. **Configures PATH** automatically in shell RC files
6. **Removes quarantine** attributes for seamless operation
7. **Shows completion** with usage instructions

### Usage
```bash
# Install (double-click or command line)
open MyCliApp-1.0.0-darwin-x64.pkg
# Follow the installation wizard

# Immediately available after installation
mycli --help
mycli status

# App also available in Applications
open -a MyCliApp
```

### When to Use PKG
- **Professional/enterprise software**
- **Users who prefer guided installation**
- **Automatic system integration required**
- **Mass deployment scenarios**
- **Software requiring admin privileges**

### PKG Installation Process
1. User double-clicks PKG file
2. macOS Installer.app opens
3. Welcome screen with app info
4. License agreement display
5. Installation location selection
6. Admin password prompt
7. Installation with progress bar
8. Completion screen with instructions

## Building All Package Types

### Build Commands
```bash
# Build all formats
./packaging/macos/build_macos.sh all 1.0.0

# Build specific formats
./packaging/macos/build_macos.sh zip 1.0.0    # Portable ZIP
./packaging/macos/build_macos.sh app 1.0.0    # App Bundle
./packaging/macos/build_macos.sh dmg 1.0.0    # Disk Image
./packaging/macos/build_macos.sh pkg 1.0.0    # PKG Installer

# Python direct usage
python packaging/macos/build_macos.py --type all --version 1.0.0
```

### Output Files
```text
dist_macos/
├── MyCliApp-1.0.0-darwin-x64.zip      # ZIP Distribution
├── MyCliApp.app/                       # App Bundle
├── MyCliApp-1.0.0-darwin-x64.dmg      # DMG Installer
└── MyCliApp-1.0.0-darwin-x64.pkg      # PKG Installer
```

## Choosing the Right Format

### For End Users (Easiest → Most Advanced)
1. **PKG** - "Just works", professional experience, automatic setup
2. **DMG** - Familiar Mac installation, manual PATH setup
3. **APP** - Native app experience, manual PATH setup
4. **ZIP** - Full control, manual everything

### For Different Audiences
- **General Mac Users**: PKG > DMG > APP > ZIP
- **Developers**: ZIP > APP > PKG > DMG  
- **Enterprise**: PKG > ZIP > DMG > APP
- **CI/CD**: ZIP > APP > PKG > DMG

### Installation Complexity
- **Zero setup**: PKG (automatic PATH, ready to use)
- **Minimal setup**: DMG/APP (drag and optionally add to PATH)
- **Manual setup**: ZIP (extract, make executable, add to PATH)

## Testing on Windows/WSL2

Since you're developing on Windows, here's how to test the packaging system:

### Syntax Validation (Windows)
```powershell
# Test all packaging functions
python -c "
import sys
sys.path.append('packaging/macos')
from build_macos import create_app_bundle, create_dmg, create_pkg
print('✅ All packaging functions loaded')
"

# Test argument parsing for all types
python packaging/macos/build_macos.py --help
```

### Mock Structure Testing (WSL2)
```bash
# In WSL2 - test Unix-like aspects
cd /mnt/c/dev_win/gitrepos_win/lrn_explore/pkg_related/pj1

# Test shell script
bash -n packaging/macos/build_macos.sh

# Test plist generation
python3 -c "
import plistlib
from packaging.macos.build_macos import create_info_plist
plist = create_info_plist('1.0.0', 'MyCliApp')
print('✅ Info.plist creation works')
print('Bundle ID:', plist['CFBundleIdentifier'])
"
```

### GitHub Actions Testing
```bash
# Trigger remote macOS build
git tag v1.0.0-test
git push origin v1.0.0-test

# Or manually trigger workflow in GitHub Actions tab
```

## Summary

MyCliApp now supports **four comprehensive macOS distribution formats**:

- **🗜️ ZIP**: Portable, developer-friendly, CI/CD ready
- **📱 APP**: Native Mac app with GUI integration  
- **💿 DMG**: Traditional Mac installer with visual appeal
- **📦 PKG**: Professional installer with automatic setup

**Recommendation**: Use **PKG for general distribution** (easiest for users) and **ZIP for developers/CI** (most flexible). The others serve specific use cases and user preferences.

This gives you maximum flexibility to serve all types of Mac users! 🎉
