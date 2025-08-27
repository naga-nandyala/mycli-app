# Complete macOS Packaging Guide

A comprehensive guide to all macOS distribution formats supported by MyCliApp: ZIP, APP, DMG, PKG, and Homebrew.

## Overview of macOS Distribution Types

MyCliApp supports five distinct packaging formats, each optimized for different use cases and user preferences:

### Format Comparison

| Format | Installation Method | User Experience | System Integration | Target Audience |
|--------|-------------------|------------------|-------------------|-----------------|
| **ZIP** | Extract & run manually | Command-line focused | None (portable) | Developers, CI/CD, power users |
| **APP** | Drag to Applications | Native Mac app | Manual setup | Standard Mac users |
| **DMG** | Mount disk, drag & drop | Traditional Mac installer | Manual setup | General Mac users |
| **PKG** | Double-click installer | Professional wizard | Automatic setup | Enterprise, general users |
| **Homebrew** | `brew install mycli` | Command-line package manager | Automatic setup | CLI power users, developers |

## 1. ZIP Distribution (Cross-Platform)

### Description
Portable ZIP archive with embedded macOS Python runtime, similar to Azure CLI distribution but platform-specific.

### Features
- ✅ **Portable**: No installation required, runs from any directory
- ✅ **Platform-specific**: Optimized for macOS with embedded Python runtime
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
- **Development environments** (on macOS)
- **CI/CD pipelines** (macOS runners)
- **Docker containers** (macOS-based)
- **Testing multiple versions**
- **Users without admin privileges**

**Note**: Each platform requires its own ZIP build. This macOS ZIP only works on macOS systems.

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

## 5. Homebrew Distribution (Package Manager)

### Description
macOS package manager distribution that allows users to install MyCliApp with a simple `brew install` command.

### Features
- ✅ **Simplest installation**: Single command to install and update
- ✅ **Automatic dependency management**: Homebrew handles all dependencies
- ✅ **Version management**: Easy to upgrade, downgrade, or uninstall
- ✅ **System integration**: Automatically adds to PATH and manages symlinks
- ✅ **Popular with developers**: Standard tool for CLI software on macOS
- ✅ **Automatic updates**: Users can update with `brew upgrade mycli`

### Usage
```bash
# Install (once Homebrew formula is published)
brew install mycli

# Use immediately
mycli --help
mycli status

# Update to latest version
brew upgrade mycli

# Uninstall
brew uninstall mycli
```

### When to Use Homebrew
- **CLI-focused distribution** (perfect for command-line tools)
- **Developer audience** (most Mac developers use Homebrew)
- **Automatic updates** desired by users
- **Minimal installation friction** required
- **Integration with developer workflows**

### Homebrew Formula Requirements
To distribute via Homebrew, you need:

1. **Homebrew Formula**: Ruby script that defines how to install MyCliApp
2. **Source Archive**: Stable URL for source code (GitHub releases)
3. **Tap Repository**: Either official Homebrew or custom tap
4. **Build Instructions**: How Homebrew should build/install the package

### Example Homebrew Formula Structure
```ruby
class Mycli < Formula
  desc "CLI tool similar to Azure CLI for cloud management"
  homepage "https://github.com/naga-nandyala/mycli-app"
  url "https://github.com/naga-nandyala/mycli-app/archive/v1.0.0.tar.gz"
  sha256 "abc123..."
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
    bin.install_symlink libexec/"bin/mycli"
  end

  test do
    assert_match "MyCliApp", shell_output("#{bin}/mycli --version")
  end
end
```

### Creating Homebrew Distribution

#### Option 1: Official Homebrew (Recommended)
```bash
# 1. Create stable GitHub release
git tag v1.0.0
git push origin v1.0.0

# 2. Submit to Homebrew/homebrew-core
# Follow: https://docs.brew.sh/Formula-Cookbook
# Submit PR to: https://github.com/Homebrew/homebrew-core
```

#### Option 2: Custom Tap
```bash
# 1. Create your own tap repository
git clone https://github.com/naga-nandyala/homebrew-mycli
cd homebrew-mycli

# 2. Create formula file
mkdir -p Formula
cat > Formula/mycli.rb << EOF
# (Ruby formula content as shown above)
EOF

# 3. Users install from your tap
brew tap naga-nandyala/mycli
brew install naga-nandyala/mycli/mycli
```

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
1. **Homebrew** - `brew install mycli`, instant availability
2. **PKG** - "Just works", professional experience, automatic setup
3. **DMG** - Familiar Mac installation, manual PATH setup
4. **APP** - Native app experience, manual PATH setup
5. **ZIP** - Full control, manual everything

### For Different Audiences
- **General Mac Users**: Homebrew > PKG > DMG > APP > ZIP
- **Developers**: Homebrew > ZIP > APP > PKG > DMG  
- **Enterprise**: PKG > Homebrew > ZIP > DMG > APP
- **CI/CD**: ZIP > Homebrew > APP > PKG > DMG

### Installation Complexity
- **Zero setup**: Homebrew (`brew install mycli`)
- **Minimal setup**: PKG (automatic PATH, ready to use)
- **Some setup**: DMG/APP (drag and optionally add to PATH)
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

MyCliApp now supports **five comprehensive macOS distribution formats**:

- **🍺 Homebrew**: Simplest installation (`brew install mycli`)
- **🗜️ ZIP**: Portable, developer-friendly, CI/CD ready (macOS-specific build)
- **📱 APP**: Native Mac app with GUI integration  
- **💿 DMG**: Traditional Mac installer with visual appeal
- **📦 PKG**: Professional installer with automatic setup

**Recommendation**: Use **Homebrew for developer distribution** (easiest for CLI tools), **PKG for general/enterprise distribution** (most professional), and **ZIP for CI/CD** (most flexible).

**Important**: The ZIP format requires platform-specific builds. For cross-platform distribution, you need to build separate ZIPs on Windows, macOS, and Linux.

This gives you maximum flexibility to serve all types of Mac users and use cases! 🎉
