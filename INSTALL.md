# Installation Instructions for MyCliApp

## Quick Installation Guide

### Option 1: Install from Local Package (Current Setup)

1. **Navigate to the package directory**:
   ```bash
   cd "c:\dev_win\gitrepos_win\lrn_explore\pkg_related\pj1"
   ```

2. **Install the basic version**:
   ```bash
   pip install .
   ```

3. **Or install with Azure support**:
   ```bash
   pip install .[azure]
   ```

4. **Or install with enhanced broker authentication**:
   ```bash
   pip install .[broker]
   ```

5. **Or install for development**:
   ```bash
   pip install -e .[dev]
   ```

### Option 2: Install from Built Packages

1. **Navigate to the package directory**:
   ```bash
   cd "c:\dev_win\gitrepos_win\lrn_explore\pkg_related\pj1"
   ```

2. **Install from wheel file** (recommended):
   ```bash
   pip install dist/mycli_app-1.0.0-py3-none-any.whl
   ```

3. **Or install from source distribution**:
   ```bash
   pip install dist/mycli_app-1.0.0.tar.gz
   ```

4. **Install with Azure features**:
   ```bash
   pip install "dist/mycli_app-1.0.0-py3-none-any.whl[azure]"
   ```

### Option 3: Development Installation

For development and contributing:

1. **Clone/download the repository**
2. **Navigate to the project directory**
3. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # macOS/Linux
   ```

4. **Install in development mode**:
   ```bash
   pip install -e .[dev]
   ```

## Installation Options

| Installation Command | Features Included |
|---------------------|-------------------|
| `pip install .` | Basic CLI functionality |
| `pip install .[azure]` | + Azure authentication |
| `pip install .[broker]` | + Enhanced Windows authentication |
| `pip install .[dev]` | + Development tools (testing, linting) |

## Verification

After installation, verify it works:

```bash
# Check if mycli is installed
mycli --version

# Show help
mycli --help

# Check status
mycli status

# Test a command
mycli resource list
```

## Publishing to PyPI (Future)

When ready to publish to PyPI:

1. **Create accounts**:
   - Create an account on [PyPI](https://pypi.org/account/register/)
   - Create an account on [TestPyPI](https://test.pypi.org/account/register/) for testing

2. **Configure authentication**:
   ```bash
   # Configure for TestPyPI (for testing)
   twine configure
   ```

3. **Upload to TestPyPI first**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

4. **Test installation from TestPyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ mycli-app
   ```

5. **Upload to PyPI** (production):
   ```bash
   twine upload dist/*
   ```

6. **Once published, users can install with**:
   ```bash
   pip install mycli-app
   pip install mycli-app[azure]
   pip install mycli-app[broker]
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
