# MyCliApp

[![Homebrew Tap Test](https://github.com/naga-nandyala/mycli-app/actions/workflows/test-homebrew-tap.yml/badge.svg)](https://github.com/naga-nandyala/mycli-app/actions/workflows/test-homebrew-tap.yml)
[![Build macOS Binaries](https://github.com/naga-nandyala/mycli-app/actions/workflows/build-macos.yml/badge.svg)](https://github.com/naga-nandyala/mycli-app/actions/workflows/build-macos.yml)
[![Release Binaries](https://github.com/naga-nandyala/mycli-app/actions/workflows/release_binaries.yml/badge.svg)](https://github.com/naga-nandyala/mycli-app/actions/workflows/release_binaries.yml)

A professional CLI application inspired by Azure CLI with comprehensive Azure authentication capabilities and cross-platform distribution support.

## 📖 Documentation

For detailed information about this project, please refer to our comprehensive documentation:

- **[MyCliApp Functionality](MYCLI_FUNCTIONALITY.md)** - Complete overview of features, commands, authentication methods, and technical implementation
- **[macOS Packaging Approaches](MACOS_PACKAGING_APPROACHES.md)** - Comprehensive guide to all macOS distribution strategies including Homebrew, PyInstaller, App Bundles, PKG installers, and DMG creation

## ✨ Features

### 🔐 Advanced Authentication

- **Interactive Browser Authentication**: Default secure authentication flow
- **Windows Broker Authentication**: Native Windows Hello and Microsoft Authenticator support
- **macOS Broker Authentication**: Touch ID, Face ID, and Keychain integration with Microsoft Company Portal
- **Native MSAL Broker**: Direct MSAL broker integration with enhanced popup control
- **Device Code Flow**: Perfect for headless systems and remote servers
- **Azure CLI Integration**: Seamless integration with existing Azure CLI credentials
- **Intelligent Fallback**: Automatic fallback from broker to browser authentication
- **Token Caching**: Persistent authentication with secure token storage

### 📊 Resource Management

- **Resource Operations**: Create, list, and delete resources with type filtering
- **Location Support**: Multi-region resource deployment and management
- **Status Monitoring**: Real-time resource health and status checking
- **Batch Operations**: Efficient bulk resource management

### ⚙️ Configuration & Settings

- **Persistent Configuration**: User preferences stored securely
- **Environment Management**: Support for multiple Azure environments
- **Custom Settings**: Configurable output formats and default locations
- **Profile Management**: Multiple authentication profiles support

### 🎨 User Experience

- **Colored Terminal Output**: Beautiful, readable command output
- **Progress Indicators**: Real-time feedback for long-running operations
- **Error Handling**: Comprehensive error messages and troubleshooting tips
- **Help System**: Detailed documentation and command assistance

### 📦 Professional Distribution

- **Cross-Platform Support**: Windows, macOS (Intel & Apple Silicon), Linux
- **Multiple Installation Methods**: Package managers, binary downloads, source installation
- **Automatic Updates**: Seamless update experience via package managers
- **Code Signing**: Signed binaries for enhanced security

## 📥 Installation

### 🍺 macOS via Homebrew (Recommended)

```bash
# Install using our custom Homebrew tap
brew install naga-nandyala/mycli-app/mycli-app

# Verify installation
mycli --version

# Update to latest version
brew upgrade naga-nandyala/mycli-app/mycli-app
```

### 🐍 Python Package (PyPI)

```bash
# Basic installation
pip install mycli-app-naga

# With Azure SDK support
pip install mycli-app-naga[azure]

# With full broker authentication support (Windows/macOS)
pip install mycli-app-naga[broker]

# Development installation with all extras
pip install mycli-app-naga[dev]
```

### 🔧 From Source

```bash
# Clone the repository
git clone https://github.com/naga-nandyala/mycli-app.git
cd mycli-app

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .[azure,broker]

# Verify installation
mycli --version
```

### 📦 Binary Releases (Pre-built)

Download platform-specific binaries from [GitHub Releases](https://github.com/naga-nandyala/mycli-app/releases):

#### Windows Binary

- **Standalone EXE**: `mycli-app-windows-x64.zip` (~15MB)
  - Extract and run directly, no Python required
  - Includes all Azure SDK dependencies
  - Professional Windows executable with version info

#### macOS Binary

- **Intel (x86_64)**: `mycli-1.0.0-macos-x86_64.tar.gz`
- **Apple Silicon (ARM64)**: `mycli-1.0.0-macos-arm64.tar.gz`
- **Features**:
  - Code-signed binaries (no "untrusted developer" warnings)
  - Embedded Python runtime and all dependencies
  - Single executable file (~50MB)

#### Binary Installation Steps

```bash
# Download and extract (example for macOS ARM64)
curl -L -o mycli-macos-arm64.tar.gz \
  https://github.com/naga-nandyala/mycli-app/releases/latest/download/mycli-1.0.0-macos-arm64.tar.gz

# Extract
tar -xzf mycli-macos-arm64.tar.gz

# Make executable and test
chmod +x mycli
./mycli --version

# Optional: Move to PATH
sudo mv mycli /usr/local/bin/
```

### 🖥️ Windows Specific Options

#### PowerShell (Future)

```powershell
# Via PowerShell Gallery (planned)
Install-Module -Name MyCliApp
```

#### Chocolatey (Future)

```powershell
# Via Chocolatey (planned)
choco install mycli-app
```

#### WinGet (Future)

```powershell
# Via Windows Package Manager (planned)
winget install naga-nandyala.mycli-app
```

## 🚀 Quick Start

### First Run

```bash
# Check installation
mycli --version

# View system status
mycli status

# Get help
mycli --help
```

### macOS Broker Authentication

The CLI now provides enhanced native broker authentication support for macOS with the following features:

#### Features

- **Touch ID Integration**: Use Touch ID for secure authentication
- **Face ID Support**: Face ID authentication on supported Macs
- **Keychain Integration**: Secure credential storage in macOS Keychain
- **Company Portal Integration**: Enhanced enterprise features via Microsoft Company Portal
- **Fallback Handling**: Intelligent fallback to browser authentication when needed

#### Setup Requirements

```bash
# Install MSAL with broker support
pip install "msal[broker]>=1.20,<2"

# Install Microsoft Company Portal (recommended)
# Download from Mac App Store: Microsoft Company Portal

# Enable Touch ID/Face ID
# System Preferences > Touch ID & Password
```

#### Usage Examples

```bash
# Use broker authentication with fallback
mycli login --use-broker

# Force native broker only (fail if not available)
mycli login --force-broker

# Check broker capabilities
mycli broker

# Clear broker cache if needed
mycli clear-cache --all
```

### Authentication

```bash
# Login with default browser authentication
mycli login

# Login with specific tenant
mycli login --tenant your-tenant-id

# Login with Windows Hello/Authenticator (Windows) or Touch ID/Keychain (macOS)
mycli login --use-broker

# Force native broker authentication only (no browser fallback)
mycli login --force-broker

# Login with device code (headless systems)
mycli login --use-device-code

# Check authentication status
mycli whoami

# View account details
mycli account

# Logout
mycli logout
```

### Resource Management

```bash
# Create a virtual machine
mycli resource create --name myvm-001 --type vm --location eastus

# Create a storage account
mycli resource create --name mystorage-001 --type storage --location westus

# List all resources
mycli resource list

# Filter resources by location
mycli resource list --location eastus

# Filter resources by type
mycli resource list --type vm

# Delete a resource
mycli resource delete myvm-001
```

### Configuration

```bash
# Set default location
mycli config set --key default_location --value eastus

# Set output format
mycli config set --key output_format --value table

# View current configuration
mycli config show

# View specific setting
mycli config show --key default_location
```

### Authentication Methods Comparison

| Method | Use Case | Platform | Security | Setup |
|--------|----------|----------|----------|-------|
| Browser | Default, interactive use | All | High | None |
| Broker (Windows) | Enterprise, SSO | Windows | Highest | Windows Hello/Authenticator |
| Broker (macOS) | Touch ID, Keychain | macOS | Highest | Touch ID/Company Portal |
| Force Broker | Native-only authentication | Windows/macOS | Highest | Complete broker setup |
| Device Code | Headless, remote servers | All | High | None |
| Azure CLI | Development, existing setup | All | High | Azure CLI required |

## 📚 Command Reference

### Authentication Commands

| Command | Description | Options |
|---------|-------------|---------|
| `mycli login` | Authenticate with Azure | `--tenant`, `--use-broker`, `--use-device-code`, `--force-broker` |
| `mycli logout` | Sign out and clear credentials | None |
| `mycli whoami` | Show current user information | None |
| `mycli account` | Display account details | None |
| `mycli broker` | Show broker capabilities | None |
| `mycli clear-cache` | Clear authentication cache | `--all` |

### Resource Commands

| Command | Description | Options |
|---------|-------------|---------|
| `mycli resource create` | Create a new resource | `--name`, `--type`, `--location` |
| `mycli resource list` | List resources | `--location`, `--type` |
| `mycli resource delete` | Delete a resource | `<resource-name>` |

### Configuration Commands

| Command | Description | Options |
|---------|-------------|---------|
| `mycli config set` | Set configuration value | `--key`, `--value` |
| `mycli config show` | Display configuration | `--key` |

### System Commands

| Command | Description | Options |
|---------|-------------|---------|
| `mycli status` | Show system status | None |
| `mycli --version` | Display version information | None |
| `mycli --help` | Show help information | None |

## 🔧 Building from Source

### 🖥️ Windows Builds

#### Standalone EXE (PyInstaller)

```powershell
# Navigate to project root
cd mycli-app

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install build dependencies
python -m pip install --upgrade pip pyinstaller
python -m pip install -e .[azure,broker]

# Build standalone executable
pyinstaller --clean --distpath .\installers\windows-exe\dist .\installers\windows-exe\mycli.spec

# Build with automated script
.\installers\windows-exe\build.ps1 -Version "1.0.1" -Clean
```

#### Windows Installer (MSI)

```powershell
# Install WiX Toolset
# Build MSI installer (future feature)
```

### 🍎 macOS Builds

#### Universal Binary

```bash
# Install dependencies
brew install python@3.12 create-dmg

# Build all distributions
./packaging/macos/build_macos.sh

# Build specific type
./packaging/macos/build_macos.sh zip    # ZIP only
./packaging/macos/build_macos.sh app    # App bundle only
./packaging/macos/build_macos.sh dmg    # DMG only
```

#### Homebrew Formula

```bash
# Test formula locally
brew install --build-from-source ./mycli-app.rb

# Update formula (automated via GitHub Actions)
```

### 🐧 Linux Builds

```bash
# Build ZIP package
python3.12 packaging/standalone_zip/build_zip.py

# Build AppImage (future)
# Build Snap package (future)
# Build Flatpak (future)
```

### 📦 Distribution Artifacts

| Platform | Type | Size | Features |
|----------|------|------|----------|
| Windows | Standalone EXE | ~15MB | No Python required, version info |
| Windows | ZIP Package | ~25MB | Portable, all dependencies |
| macOS | Signed Binary | ~50MB | Code-signed, universal binary |
| macOS | DMG Installer | ~55MB | Easy installation, app bundle |
| Linux | ZIP Package | ~45MB | Portable, all dependencies |

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/naga-nandyala/mycli-app.git
cd mycli-app

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e .[dev,azure,broker]

# Install pre-commit hooks (optional)
pre-commit install
```

### Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "flake8>=4.0.0",
    "mypy>=0.990",
    "setuptools>=45.0.0",
    "wheel>=0.36.0",
    "twine>=4.0.0",
]
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=mycli_app --cov-report=html

# Run specific test
pytest tests/test_auth.py::test_login

# Run linting
flake8 src/
black --check src/
mypy src/
```

### Project Structure

```text
mycli-app/
├── src/mycli_app/           # Main application code
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Entry point for python -m
│   ├── cli.py              # CLI commands and logic
│   └── config.yaml         # Default configuration
├── installers/             # Build scripts and specifications
│   └── windows-exe/        # Windows executable builds
├── macos_homebrew/         # macOS packaging
├── tests/                  # Test suite
├── .github/                # GitHub Actions workflows
├── pyproject.toml          # Project configuration
├── requirements.txt        # Core dependencies
└── README.md              # This file
```

### Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **Docstrings**: Google-style docstrings
- **Type Hints**: Use type hints for function signatures
- **Testing**: Write tests for new features
- **Commits**: Use conventional commit messages

## 📋 Requirements

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8+ | 3.11+ |
| **OS** | Windows 7+, macOS 10.14+, Ubuntu 18.04+ | Windows 10+, macOS 12+, Ubuntu 20.04+ |
| **Memory** | 512MB RAM | 1GB RAM |
| **Disk** | 100MB | 200MB |
| **Network** | Internet connection for authentication | High-speed internet |

### Core Dependencies

```text
click>=8.0.0              # CLI framework
colorama>=0.4.0           # Cross-platform colored output
```

### Optional Dependencies

```text
# Azure SDK Integration
azure-identity>=1.12.0    # Azure authentication
azure-mgmt-core>=1.3.0    # Azure management SDK
azure-core>=1.24.0        # Azure core library
msal>=1.20.0              # Microsoft Authentication Library

# Broker Authentication (Windows/macOS)
msal[broker]>=1.20.0,<2   # MSAL with broker support
```

### Platform-Specific Requirements

#### Windows Platforms

- **Broker Authentication**: Windows 10+ with Windows Hello or Microsoft Authenticator
- **Code Signing**: Windows SDK (for development builds)

#### macOS Platforms

- **Broker Authentication**: Touch ID, Face ID, Keychain integration
- **Company Portal**: Microsoft Company Portal app (App Store) for enhanced broker features
- **Code Signing**: Xcode Command Line Tools
- **Homebrew**: For package management
- **Universal Binary**: Supports both Intel and Apple Silicon

#### Linux Platforms

- **Dependencies**: `python3-dev`, `libffi-dev`, `libssl-dev`
- **Package Managers**: apt, yum, pacman support planned

## 🔍 Troubleshooting

### Common Issues

#### Authentication Problems

**Issue**: `Authentication failed` error

**Solutions**:

```bash
# Clear authentication cache
mycli clear-cache --all

# Try different authentication method
mycli login --use-device-code

# Check Azure SDK installation
python -c "import azure.identity; print('Azure SDK OK')"
```

**Issue**: Broker authentication not working

**Solutions**:

```bash
# Check broker capabilities
mycli broker

# Install broker support (Windows/macOS)
pip install "msal[broker]>=1.20,<2"

# Try force broker authentication
mycli login --force-broker

# macOS specific: Install Company Portal
# Download from Mac App Store: Microsoft Company Portal

# macOS specific: Enable Touch ID
# System Preferences > Touch ID & Password

# Check keychain access (macOS)
security find-generic-password -s "Microsoft MSAL"
```

#### Installation Issues

**Issue**: `Package not found` error

**Solutions**:

```bash
# Update pip
python -m pip install --upgrade pip

# Install with specific index
pip install -i https://pypi.org/simple/ mycli-app-naga

# Install from source
pip install git+https://github.com/naga-nandyala/mycli-app.git
```

**Issue**: Binary won't run on macOS

**Solutions**:

```bash
# Check if binary is signed
codesign --verify --verbose mycli

# Allow unsigned binary (if needed)
xattr -d com.apple.quarantine mycli

# Check for broker authentication support
mycli broker

# If broker issues, try alternative methods
mycli login --use-device-code

# Download from official releases
# Use Homebrew installation instead
```

#### Runtime Issues

**Issue**: `Command not found: mycli`

**Solutions**:

```bash
# Check if installed correctly
pip list | grep mycli

# Add to PATH (if installed with --user)
export PATH="$HOME/.local/bin:$PATH"

# Reinstall package
pip uninstall mycli-app-naga
pip install mycli-app-naga
```

### Debug Mode

```bash
# Enable verbose logging
export MYCLI_DEBUG=1
mycli status

# Check configuration
mycli config show

# Verify dependencies
python -c "
import sys
print('Python:', sys.version)
import mycli_app
print('MyCliApp:', mycli_app.__version__)
try:
    import azure.identity
    print('Azure SDK: Available')
except ImportError:
    print('Azure SDK: Not available')
"
```

### Getting Help

1. **Documentation**: Check this README and [GitHub Wiki](https://github.com/naga-nandyala/mycli-app/wiki)
2. **Issues**: Search or create issues on [GitHub Issues](https://github.com/naga-nandyala/mycli-app/issues)
3. **Discussions**: Join conversations on [GitHub Discussions](https://github.com/naga-nandyala/mycli-app/discussions)
4. **Support**: Email support at [your.email@example.com](mailto:your.email@example.com)

### Reporting Bugs

When reporting issues, please include:

- **Environment**: OS, Python version, installation method
- **Command**: Full command that failed
- **Error**: Complete error message
- **Debug**: Output with `MYCLI_DEBUG=1`
- **Context**: What you were trying to accomplish

## 🔄 CI/CD Pipeline

### Automated Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **Homebrew Tap Test** | Push, PR | Test Homebrew formula |
| **Build macOS Binaries** | Release | Build signed macOS binaries |
| **Release Binaries** | Manual/Release | Build all platform binaries |
| **Update Homebrew Formula** | Release | Auto-update Homebrew tap |

### GitHub Actions Features

- **Multi-platform builds**: Windows, macOS (Intel + ARM64), Linux
- **Code signing**: Automated binary signing for macOS
- **Dependency caching**: Fast builds with pip/Homebrew caching
- **Automated testing**: Unit tests and integration tests
- **Release automation**: Automatic GitHub releases with assets
- **Homebrew integration**: Auto-update formula on releases

### Security & Quality

- **Code scanning**: CodeQL analysis for security vulnerabilities
- **Dependency updates**: Dependabot for automatic dependency updates
- **Secrets management**: Secure token storage for cross-repo operations
- **Branch protection**: Required reviews and status checks

## 📊 Project Status

### Current Version: 1.0.0

### ✅ Completed Features

- ✅ **Core CLI Framework**: Complete command structure
- ✅ **Azure Authentication**: All authentication methods implemented
- ✅ **Cross-platform Support**: Windows, macOS, Linux
- ✅ **Package Distribution**: Homebrew, PyPI, GitHub Releases
- ✅ **Binary Builds**: Standalone executables for all platforms
- ✅ **CI/CD Pipeline**: Automated builds and releases
- ✅ **Documentation**: Comprehensive README and guides

### 🚧 In Development

- 🚧 **Windows Installers**: MSI, NSIS, WinGet packages
- 🚧 **Linux Packages**: AppImage, Snap, Flatpak
- 🚧 **PowerShell Module**: Native PowerShell integration
- 🚧 **Configuration Management**: Advanced config features
- 🚧 **Plugin System**: Extensible command architecture

### 🔮 Planned Features

- 🔮 **Azure Resource Management**: Real Azure API integration
- 🔮 **Multi-tenant Support**: Enterprise tenant management
- 🔮 **Web Interface**: Optional web dashboard
- 🔮 **Shell Completion**: Bash, Zsh, PowerShell completion
- 🔮 **Telemetry**: Optional usage analytics

### Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed version history and changes.

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Ways to Contribute

- 🐛 **Bug Reports**: Report issues on GitHub Issues
- 💡 **Feature Requests**: Suggest new features and improvements
- 📝 **Documentation**: Improve docs, guides, and examples
- 🧪 **Testing**: Test on different platforms and environments
- 💻 **Code Contributions**: Submit pull requests with fixes and features

### Contribution Guidelines

1. **Search** existing issues and PRs before creating new ones
2. **Follow** our code style and conventions (Black, PEP 8)
3. **Write** tests for new features and bug fixes
4. **Update** documentation for user-facing changes
5. **Use** conventional commit messages
6. **Be** respectful and constructive in discussions

### Development Workflow

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR-USERNAME/mycli-app.git
cd mycli-app

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install development dependencies
pip install -e .[dev,azure,broker]

# 4. Create feature branch
git checkout -b feature/your-feature-name

# 5. Make changes and test
pytest
black src/
flake8 src/

# 6. Commit and push
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name

# 7. Create Pull Request
```

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

- ✅ **Commercial use** - Use in commercial projects
- ✅ **Modification** - Modify and adapt the code
- ✅ **Distribution** - Distribute original or modified versions
- ✅ **Private use** - Use privately without restrictions
- ❌ **Liability** - No warranty or liability
- ❌ **Trademark** - Does not grant trademark rights

## 🙏 Acknowledgments

### Technologies

- **[Click](https://click.palletsprojects.com/)** - Excellent CLI framework
- **[Azure SDK](https://azure.microsoft.com/en-us/downloads/)** - Microsoft Azure integration
- **[MSAL](https://github.com/AzureAD/microsoft-authentication-library-for-python)** - Microsoft Authentication Library
- **[PyInstaller](https://pyinstaller.org/)** - Python to executable conversion
- **[Colorama](https://pypi.org/project/colorama/)** - Cross-platform colored output

### Inspiration

- **[Azure CLI](https://github.com/Azure/azure-cli)** - Command structure and authentication patterns
- **[AWS CLI](https://github.com/aws/aws-cli)** - CLI design principles
- **[GitHub CLI](https://github.com/cli/cli)** - User experience patterns

### Community

- **Contributors**: Thanks to all who have contributed code, bug reports, and feedback
- **Testers**: Beta testers across different platforms and environments
- **Reviewers**: Code reviewers who help maintain quality standards

## 📞 Support & Contact

### Support Resources

- 📖 **Documentation**: [GitHub Wiki](https://github.com/naga-nandyala/mycli-app/wiki)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/naga-nandyala/mycli-app/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/naga-nandyala/mycli-app/discussions)
- 📧 **Email**: [your.email@example.com](mailto:your.email@example.com)

### Project Community

- 🌟 **Star** the project if you find it useful
- 👀 **Watch** for updates and releases
- 🔄 **Share** with others who might benefit
- 🤝 **Contribute** to make it even better

### Social Media

- **GitHub**: [@naga-nandyala](https://github.com/naga-nandyala)
- **LinkedIn**: [Your LinkedIn Profile](https://linkedin.com/in/your-profile)
- **Twitter**: [@your-twitter](https://twitter.com/your-twitter)

---

**Made with ❤️ by [Your Name](https://github.com/naga-nandyala)**

Building developer tools that make Azure management easier and more enjoyable

[![GitHub stars](https://img.shields.io/github/stars/naga-nandyala/mycli-app?style=social)](https://github.com/naga-nandyala/mycli-app/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/naga-nandyala/mycli-app?style=social)](https://github.com/naga-nandyala/mycli-app/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/naga-nandyala/mycli-app?style=social)](https://github.com/naga-nandyala/mycli-app/watchers)
