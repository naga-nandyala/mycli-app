# Installation Instructions for MyCliApp

## 🚀 Quick Installation Guide (2025)

### Option 1: From PyPI (Recommended)

```bash
# Basic CLI functionality
pip install mycli-app

# With Azure authentication support
pip install mycli-app[azure]

# With enhanced Windows authentication (Windows Hello, Microsoft Authenticator)
pip install mycli-app[broker]

# For development
pip install mycli-app[dev]
```

### Option 2: From GitHub Releases

1. **Download the latest release**:
   - Go to [Releases](https://github.com/naga-nandyala/mycli-app/releases)
   - Download `MyCliApp-1.0.0-Standalone.zip` for Windows

2. **Windows Executable** (No Python required):
   ```powershell
   # Extract the ZIP file
   Expand-Archive MyCliApp-1.0.0-Standalone.zip
   
   # Run directly
   .\mycli.exe --help
   ```

3. **Python Wheel**:
   ```bash
   pip install mycli_app-1.0.0-py3-none-any.whl[azure]
   ```

### Option 3: From Source Repository

1. **Clone the repository**:
   ```bash
   git clone https://github.com/naga-nandyala/mycli-app.git
   cd mycli-app
   ```

2. **Install from source**:
   ```bash
   # Basic installation
   pip install .
   
   # With Azure support
   pip install .[azure]
   
   # With broker authentication
   pip install .[broker]
   
   # Development mode (editable install)
   pip install -e .[dev]
   ```

### Option 4: Modern Package Managers (2025)

#### WinGet (Windows)
```powershell
winget install YourCompany.MyCliApp
```

#### Chocolatey (Windows)
```powershell
choco install mycli-app
```

#### Homebrew (macOS) - Coming Soon
```bash
brew install mycli-app
```

## 📋 Installation Options Summary

| Installation Method | Command | Features Included | Platform |
|---------------------|---------|-------------------|----------|
| **PyPI Basic** | `pip install mycli-app` | Core CLI functionality | All |
| **PyPI Azure** | `pip install mycli-app[azure]` | + Azure authentication | All |
| **PyPI Broker** | `pip install mycli-app[broker]` | + Windows Hello/Authenticator | Windows |
| **PyPI Dev** | `pip install mycli-app[dev]` | + Development tools | All |
| **Windows EXE** | Download from releases | Standalone, no Python needed | Windows |
| **WinGet** | `winget install YourCompany.MyCliApp` | Native Windows package | Windows |
| **Chocolatey** | `choco install mycli-app` | Package manager | Windows |

## ✅ Verification

After installation, verify it works:

```bash
# Check if mycli is installed
mycli --version

# Show help
mycli --help

# Check system status
mycli status

# Test authentication status
mycli whoami
```

## 🌍 Virtual Environment (Recommended)

For the best experience, use a virtual environment:

```bash
# Create virtual environment
python -m venv mycli-env

# Activate (Windows)
mycli-env\Scripts\activate

# Activate (macOS/Linux)
source mycli-env/bin/activate

# Install mycli-app
pip install mycli-app[azure]

# Use the application
mycli --help
```

## 🔄 Updating

### From PyPI
```bash
# Update to latest version
pip install --upgrade mycli-app[azure]
```

### From WinGet
```powershell
winget upgrade YourCompany.MyCliApp
```

### From Chocolatey
```powershell
choco upgrade mycli-app
```

## 📦 Publishing to PyPI (For Maintainers)

### First-time Setup
1. **Create accounts**:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **Configure API tokens**:
   ```bash
   # Set up authentication
   pip install twine
   
   # Configure .pypirc file with API tokens
   ```

### Publishing Process
```bash
# 1. Clean previous builds
rm -rf dist/ build/ *.egg-info/

# 2. Build package
python -m build

# 3. Check package
twine check dist/*

# 4. Upload to TestPyPI first
twine upload --repository testpypi dist/*

# 5. Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ mycli-app[azure]

# 6. Upload to production PyPI
twine upload dist/*
```

### After Publishing
Users can install with:
```bash
pip install mycli-app[azure]
pip install mycli-app[broker]
pip install mycli-app[dev]
```

## Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **For Azure features**: Active Azure subscription (optional)

## Uninstalling

To uninstall:
```bash
pip uninstall mycli-app
```

## Troubleshooting

### Common Issues

1. **"Command not found: mycli"**
   - Ensure the package is installed: `pip list | grep mycli`
   - Check your PATH includes Python scripts directory

2. **Azure SDK errors**
   - Install Azure extras: `pip install mycli-app[azure]`
   - Verify Azure packages: `pip list | grep azure`

3. **Permission errors**
   - Try installing with `--user` flag: `pip install --user mycli-app`
   - Or use a virtual environment

### Getting Help

- Run `mycli --help` for command help
- Run `mycli status` to check system status
- Check the README.md for detailed usage instructions
