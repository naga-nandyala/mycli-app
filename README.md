# MyCliApp

[![Homebrew Formula Test](https://github.com/naga-nandyala/mycli-app/actions/workflows/test-homebrew-formula.yml/badge.svg)](https://github.com/naga-nandyala/mycli-app/actions/workflows/test-homebrew-formula.yml)

A simple CLI application similar to Azure CLI with Azure authentication capabilities.

## Features

- 🔐 Azure authentication with multiple methods (browser, device code, broker)
- 🌟 Windows Hello and Microsoft Authenticator support
- 📊 Resource management commands
- ⚙️ Configuration management
- 🎨 Colored terminal output
- 📦 Cross-platform support

## Installation

### macOS via Homebrew (Recommended)

```bash
# Install using our Homebrew tap
brew install naga-nandyala/mycli-app/mycli-app

# Verify installation
mycli --version
```

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

### Binary Releases

Pre-built binaries are available for download from [GitHub Releases](https://github.com/naga-nandyala/mycli-app/releases):

- **Windows**: `mycli-app-windows-x64.zip`
- **macOS (Intel)**: `mycli-app-darwin-x64.zip`  
- **macOS (Apple Silicon)**: `mycli-app-darwin-arm64.zip`

Each binary includes an embedded Python runtime and all dependencies.

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
