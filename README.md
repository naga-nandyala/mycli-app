# MyCliApp

A simple CLI application similar to Azure CLI with Azure authentication capabilities.

## Features

- 🔐 Azure authentication with multiple methods (browser, device code, broker)
- 🌟 Windows Hello and Microsoft Authenticator support
- 📊 Resource management commands
- ⚙️ Configuration management
- 🎨 Colored terminal output
- 📦 Cross-platform support

## Installation

### From PyPI (when published)
```bash
pip install mycli-app-naga
```

### From Source
```bash
git clone https://github.com/naga-nandyala/mycli-app.git
cd mycli-app
pip install -e .
```

## Quick Start

```bash
# Check version
mycli --version

# Show status
mycli status

# Authenticate with Azure
mycli login

# List resources
mycli resource list

# Get help
mycli --help
```

## Authentication Methods

- **Browser Authentication**: Default method
- **Device Code Flow**: For headless systems
- **Broker Authentication**: Windows Hello, Microsoft Authenticator
- **Azure CLI Integration**: Uses existing Azure CLI credentials

## Distribution Packages

MyCliApp is available in multiple distribution formats for different platforms:

### Windows
- **Standalone ZIP**: `MyCliApp-{version}-windows-x64.zip`
- **Windows Installer**: `MyCliApp-{version}-windows-x64.exe` *(coming soon)*

### macOS
- **Standalone ZIP**: `MyCliApp-{version}-darwin-x64.zip`
- **App Bundle**: `MyCliApp.app` (native macOS application)
- **DMG Installer**: `MyCliApp-{version}-darwin-x64.dmg`

### Linux
- **Standalone ZIP**: `MyCliApp-{version}-linux-x64.zip`

All standalone ZIP packages include:
- Embedded Python runtime (no system Python required)
- All dependencies included
- Cross-platform launcher scripts

### Quick Installation

**Windows:**
```powershell
# Download and extract ZIP
Expand-Archive MyCliApp-1.0.0-windows-x64.zip
cd MyCliApp-1.0.0-windows-x64
.\bin\mycli.cmd --version
```

**macOS:**
```bash
# From ZIP
unzip MyCliApp-1.0.0-darwin-x64.zip
cd MyCliApp-1.0.0-darwin-x64
chmod +x bin/mycli.sh
./bin/mycli.sh --version

# From App Bundle
cp -R MyCliApp.app /Applications/
/Applications/MyCliApp.app/Contents/MacOS/MyCliApp --version

# From DMG - just double-click and drag to Applications
```

**Linux:**
```bash
unzip MyCliApp-1.0.0-linux-x64.zip
cd MyCliApp-1.0.0-linux-x64
chmod +x bin/mycli.sh
./bin/mycli.sh --version
```

## Building Distributions

### Windows
```powershell
python packaging/standalone_zip/build_zip.py
```

### macOS
```bash
# Install dependencies
brew install python@3.12 create-dmg

# Build all distributions (ZIP, APP, DMG)
./packaging/macos/build_macos.sh

# Or build specific type
./packaging/macos/build_macos.sh zip    # ZIP only
./packaging/macos/build_macos.sh app    # App bundle only
./packaging/macos/build_macos.sh dmg    # DMG only
```

### Linux
```bash
python3.12 packaging/standalone_zip/build_zip.py
```

For detailed instructions, see:
- [Windows Packaging Guide](packaging/standalone_zip/README.md)
- [macOS Packaging Guide](packaging/macos/README.md)
- [macOS Quick Start](packaging/macos/QUICK_START.md)

## Requirements

- Python 3.8+
- Windows (for broker authentication features)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Development

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
