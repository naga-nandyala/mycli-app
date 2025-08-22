# MyCliApp

A modern Python CLI application similar to Azure CLI with comprehensive Azure authentication capabilities.

[![PyPI version](https://badge.fury.io/py/mycli-app.svg)](https://badge.fury.io/py/mycli-app)
[![Python Support](https://img.shields.io/pypi/pyversions/mycli-app.svg)](https://pypi.org/project/mycli-app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **🔐 Multiple Authentication Methods**: 
  - Interactive browser authentication
  - Broker-based authentication (Windows Hello, Microsoft Authenticator)
  - Device code flow for headless environments
  - Azure CLI credential fallback

- **📦 Resource Management**: Create, list, and delete resources (demo operations)
- **⚙️ Configuration Management**: Set and view configuration settings
- **🎨 Colorized Output**: Enhanced terminal output with colors and icons
- **🔄 Cross-platform**: Works on Windows, macOS, and Linux
- **💾 Persistent Authentication**: Saves authentication state between sessions
- **📊 Status Monitoring**: Check system status and health

## Installation

### Basic Installation (CLI only)
```bash
pip install mycli-app
```

### With Azure Authentication Support
```bash
pip install mycli-app[azure]
```

### With Enhanced Broker Authentication (Windows)
```bash
pip install mycli-app[broker]
```

### Development Installation
```bash
pip install mycli-app[dev]
```

## Quick Start

1. **Install the package**:
   ```bash
   pip install mycli-app[azure]
   ```

2. **Check status**:
   ```bash
   mycli status
   ```

3. **Login to Azure**:
   ```bash
   mycli login
   ```

4. **Start using commands**:
   ```bash
   mycli resource list
   mycli whoami
   ```

## Usage

### Authentication Commands

```bash
# Interactive browser login
mycli login

# Broker authentication (Windows Hello/Authenticator)
mycli login --use-broker

# Device code flow (for remote/headless scenarios)
mycli login --use-device-code

# Login with specific tenant
mycli login --tenant "your-tenant-id"

# Check authentication status
mycli whoami

# View account information
mycli account

# Check broker capabilities
mycli broker

# Logout
mycli logout
```

### Resource Management

```bash
# Create a resource
mycli resource create --name "my-vm" --location "eastus" --type "vm"

# List all resources
mycli resource list

# List resources by location
mycli resource list --location "eastus"

# List resources by type
mycli resource list --type "vm"

# Delete a resource (with confirmation)
mycli resource delete "my-vm"
```

### Configuration Management

```bash
# Set a configuration value
mycli config set --key "default_location" --value "westus"

# Show all configuration
mycli config show

# Show specific configuration key
mycli config show --key "default_location"
```

### System Commands

```bash
# Show system status
mycli status

# Show version
mycli --version

# Show help
mycli --help

# Clear authentication cache
mycli clear-cache

# Clear all cache including MSAL
mycli clear-cache --all
```

## Authentication Storage

Authentication information is stored in:
- **Windows**: `%USERPROFILE%\.mycli\config.json`
- **macOS/Linux**: `~/.mycli/config.json`

The stored information includes:
- Authentication status
- User information (user ID, display name)
- Tenant ID (if specified)
- Authentication method used
- Broker capabilities

**Note**: Actual credentials are managed securely by the Azure SDK and are not stored in plain text.

## Command Structure

```
mycli
├── resource
│   ├── create          # Create a new resource
│   ├── list            # List all resources
│   └── delete          # Delete a resource
├── config
│   ├── set             # Set configuration value
│   └── show            # Show configuration
├── login               # Authenticate with Azure
├── logout              # Sign out from Azure
├── whoami              # Show current user
├── account             # Show account information
├── broker              # Show broker capabilities
├── status              # Show system status
├── clear-cache         # Clear authentication cache
├── --help              # Show help
└── --version           # Show version
```

## Development

### Setting up Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/naga-nandyala/mycli-app.git
   cd mycli-app
   ```

2. **Install in development mode**:
   ```bash
   pip install -e .[dev]
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Format code**:
   ```bash
   black src/
   ```

5. **Type checking**:
   ```bash
   mypy src/
   ```

### Building and Publishing

1. **Build the package**:
   ```bash
   python -m build
   ```

2. **Upload to PyPI** (requires credentials):
   ```bash
   twine upload dist/*
   ```

## Configuration Options

The package supports multiple installation configurations:

| Installation | Command | Features |
|-------------|---------|----------|
| Basic | `pip install mycli-app` | Core CLI functionality |
| Azure | `pip install mycli-app[azure]` | + Azure authentication |
| Broker | `pip install mycli-app[broker]` | + Enhanced Windows authentication |
| Development | `pip install mycli-app[dev]` | + Testing and development tools |

## Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Optional**: Azure subscription for authentication features

### Core Dependencies
- `click>=8.0.0` - Command-line interface framework
- `colorama>=0.4.0` - Cross-platform colored terminal output

### Optional Dependencies
- `azure-identity>=1.12.0` - Azure authentication
- `azure-mgmt-core>=1.3.0` - Azure management
- `azure-core>=1.24.0` - Azure core functionality
- `msal>=1.20.0` - Microsoft Authentication Library

## Example Session

```bash
$ mycli status
📊 System Status:
  Service: Online
  Authentication: Not Authenticated (None)
  Azure SDK: Available
  Version: 1.0.0

$ mycli login
🔐 Starting Azure authentication...
✓ Successfully authenticated!
  User: your.email@domain.com

$ mycli resource create --name "test-vm" --type "vm"
✓ Creating vm resource...
  Name: test-vm
  Location: eastus
  Type: vm
✓ Resource 'test-vm' created successfully!

$ mycli resource list
📋 Listing resources...

Name            Type       Location   Status    
--------------------------------------------------
myvm-001        vm         eastus     running   
mystorage-001   storage    westus     active    
mydb-001        database   eastus     running   
test-vm         vm         eastus     running   

$ mycli logout
👋 Logging out...
✓ Successfully logged out!
```

## Error Handling

The application includes comprehensive error handling for:
- ❌ Missing Azure SDK packages
- ❌ Authentication failures  
- ❌ Network connectivity issues
- ❌ Invalid tenant IDs
- ❌ Permission issues
- ❌ Configuration problems

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](https://github.com/naga-nandyala/mycli-app#readme)
- 🐛 [Bug Reports](https://github.com/naga-nandyala/mycli-app/issues)
- 💬 [Discussions](https://github.com/naga-nandyala/mycli-app/discussions)

---

**Made with ❤️ for the CLI community**
