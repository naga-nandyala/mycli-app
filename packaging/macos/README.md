# macOS Distribution Builder for MyCliApp

Build professional macOS distributions including ZIP, APP, DMG, PKG formats, plus Homebrew support.

## Quick Start

### Prerequisites (One-time Setup)

```bash
# On macOS - Install required tools
brew install python@3.12 create-dmg

# On Windows/WSL2 - Use GitHub Actions (see CI/CD section below)
```

### Build Commands

```bash
# Build all distribution types
./packaging/macos/build_macos.sh all 1.0.0

# Build specific types
./packaging/macos/build_macos.sh zip 1.0.0    # Portable ZIP
./packaging/macos/build_macos.sh app 1.0.0    # macOS App Bundle  
./packaging/macos/build_macos.sh dmg 1.0.0    # Disk Image Installer
./packaging/macos/build_macos.sh pkg 1.0.0    # Professional Installer (recommended)

# Or use Python directly
python packaging/macos/build_macos.py --type pkg --version 1.0.0
```

## Distribution Types

| Format | Description | Use Case | Installation |
|--------|-------------|----------|--------------|
| **ZIP** | Portable archive (macOS-specific) | Developers/CI | Extract and run |
| **APP** | macOS app bundle | Standard apps | Drag to Applications |
| **DMG** | Disk image | Traditional Mac | Mount and copy |
| **PKG** | Native installer | Professional/Enterprise | Double-click to install |
| **Homebrew** | Package manager | CLI tools | `brew install mycli` |

**Recommended:** Use Homebrew for CLI distribution, PKG for enterprise (see `MACOS_PACKAGING_GUIDE.md` for comprehensive details on all formats).

## Cross-Platform Development

### Building on Windows/WSL2

Since macOS builds require macOS, use GitHub Actions:

1. **Test locally** (syntax validation):

   ```powershell
   python -m py_compile packaging\macos\build_macos.py
   python -c "from packaging.macos.build_macos import create_info_plist; print('✅ OK')"
   ```

2. **Build via GitHub Actions** (actual macOS builds):

   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   # Check Actions tab for build results
   ```

### Coordinating Multi-Platform Builds

```bash
# Windows (local)
python packaging/standalone_zip/build_zip.py --version 1.0.0

# macOS (via CI/CD or remote Mac)
./packaging/macos/build_macos.sh all 1.0.0
```

## Output Structure

```text
dist_macos/
├── MyCliApp-1.0.0-darwin-x64.zip      # Portable ZIP
├── MyCliApp.app/                       # macOS App Bundle
├── MyCliApp-1.0.0-darwin-x64.dmg      # Disk Image
└── MyCliApp-1.0.0-darwin-x64.pkg      # Professional Installer
```

## Usage After Installation

### PKG Installer

```bash
# Automatically available after PKG installation
mycli --help
mycli status
```

### Other Formats

```bash
# App Bundle
/Applications/MyCliApp.app/Contents/MacOS/MyCliApp --help

# ZIP Extract
cd MyCliApp-1.0.0-darwin-x64/
./bin/mycli.sh --help
```

## System Requirements

- **macOS 10.14+** (for building)
- **Python 3.8+** (preferably Python 3.12+)
- **Xcode Command Line Tools** (for some dependencies)

## Troubleshooting

### "App can't be opened" Error

```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /Applications/MyCliApp.app
```

### Testing on Windows

```powershell
# Syntax validation
python -m py_compile packaging\macos\build_macos.py

# Mock testing
python -c "
import sys; sys.path.append('.')
from packaging.macos.build_macos import detect_version
print('Version detection works:', detect_version('1.0.0'))
"
```

### CI/CD Setup

- Workflow: `.github/workflows/build-macos.yml`
- Triggers: Tags, manual dispatch
- Artifacts: All distribution types uploaded

## Development Notes

- **PKG Creation**: Uses `pkgbuild` and `productbuild` (macOS native tools)
- **DMG Creation**: Uses `create-dmg` (install via Homebrew)
- **App Bundle**: Custom Python script with proper Info.plist
- **ZIP**: Reuses existing `packaging/standalone_zip/build_zip.py`

The PKG installer provides the most professional user experience and is recommended for general distribution!
