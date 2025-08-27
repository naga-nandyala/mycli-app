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

## Requirements

- Python 3.8+
- Windows (for broker authentication features)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Development

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.
