# 📚 Python Packaging Tutorial: From Script to Professional Package

> **A Complete Guide to Transforming a Single Python Script into a Professional, Installable Package**

## 📖 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Initial Project State](#initial-project-state)
4. [Phase 1: Project Analysis](#phase-1-project-analysis)
5. [Phase 2: Modern Package Structure](#phase-2-modern-package-structure)
6. [Phase 3: Configuration Files](#phase-3-configuration-files)
7. [Phase 4: Documentation](#phase-4-documentation)
8. [Phase 5: Building the Package](#phase-5-building-the-package)
9. [Phase 6: Testing & Verification](#phase-6-testing--verification)
10. [Phase 7: Distribution](#phase-7-distribution)
11. [Key Concepts Explained](#key-concepts-explained)
12. [Common Pitfalls & Solutions](#common-pitfalls--solutions)
13. [Best Practices](#best-practices)
14. [Advanced Topics](#advanced-topics)
15. [Resources & References](#resources--references)

---

## Overview

This tutorial demonstrates how to transform a single Python CLI script (`mycli.py`) into a professional, installable Python package that users can install via `pip install`. We'll cover modern Python packaging standards, best practices, and common pitfalls.

### What You'll Learn

- ✅ Modern Python packaging with `pyproject.toml`
- ✅ Proper package structure using `src/` layout
- ✅ Entry points and command-line interfaces
- ✅ Optional dependencies and extras
- ✅ Building wheels and source distributions
- ✅ Professional documentation practices
- ✅ Distribution strategies

### What We Built

**Before:** Single file `mycli.py` (39,494 bytes)
**After:** Professional package installable via `pip install mycli-app[azure]`

---

## Prerequisites

### Required Knowledge
- Basic Python programming
- Understanding of virtual environments
- Familiarity with command-line interfaces
- Basic Git knowledge

### Required Tools
```bash
# Python 3.8+ (we used Python 3.12)
python --version

# Package management tools
pip install build wheel setuptools twine

# Optional: For publishing to PyPI
pip install twine
```

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv .venv

# Windows
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

# Verify environment
which python
python --version
```

---

## Initial Project State

### Starting Point
We began with a single-file CLI application:

```
mycli-app/
├── mycli.py              # 39,494 bytes - Main CLI application
├── requirements.txt      # Dependencies list
├── README.md            # Basic project info
└── BROKER_AUTH.md       # Authentication documentation
```

### Original `mycli.py` Structure
```python
# Original file contained:
# - Click-based CLI with multiple commands
# - Azure authentication logic
# - Resource management functions
# - Configuration management
# - Colorized output using colorama
# - Error handling and logging
```

### Dependencies Analysis
```txt
# requirements.txt
click>=8.0.0
colorama>=0.4.0
requests>=2.25.0
azure-identity>=1.12.0    # Optional Azure features
azure-mgmt-core>=1.3.0    # Optional Azure features
azure-core>=1.24.0        # Optional Azure features
msal>=1.20.0              # Optional authentication
```

---

## Phase 1: Project Analysis

### Step 1: Code Assessment

First, we analyzed the existing codebase to understand:

1. **Entry Points**: How users interact with the CLI
2. **Dependencies**: Core vs. optional requirements
3. **Functionality**: What the application does
4. **Structure**: How to organize the code

```python
# Key findings from mycli.py:
@click.group()
def cli():
    """MyCliApp - A comprehensive CLI tool for Azure resource management."""
    pass

# Main entry point
def main():
    cli()

if __name__ == "__main__":
    main()
```

### Step 2: Dependency Classification

We categorized dependencies into groups:

- **Core**: Required for basic functionality (`click`, `colorama`, `requests`)
- **Azure**: Optional Azure features (`azure-*` packages)
- **Broker**: Enhanced authentication (`msal[broker]`)
- **Development**: Testing and linting tools

### Step 3: User Experience Goals

Defined how users should interact with the final package:

```bash
# Installation options
pip install mycli-app                    # Basic CLI
pip install mycli-app[azure]            # With Azure features
pip install mycli-app[broker]           # With enhanced auth
pip install mycli-app[dev]              # Development tools

# Usage after installation
mycli --help
mycli status
mycli auth login
mycli resource list
```

---

## Phase 2: Modern Package Structure

### Step 1: The `src/` Layout

Modern Python packaging uses the `src/` layout to prevent common import issues:

```
src/
└── mycli_app/           # Package name (underscores, not hyphens)
    ├── __init__.py      # Package initialization
    ├── __main__.py      # Entry point for python -m mycli_app
    └── cli.py           # Main CLI logic (migrated from mycli.py)
```

**Why `src/` layout?**
- Prevents importing from source during development
- Forces proper installation testing
- Separates source from build artifacts
- Industry best practice since ~2018

### Step 2: Package Initialization (`__init__.py`)

```python
"""MyCliApp - A comprehensive CLI tool for Azure resource management."""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

# Import main CLI function for easy access
from .cli import cli, main

# Define what gets imported with "from mycli_app import *"
__all__ = ["cli", "main", "__version__"]
```

**Key Concepts:**
- `__version__`: Single source of truth for version
- `__all__`: Controls what gets imported with `import *`
- Relative imports: `from .cli import ...`

### Step 3: Module Entry Point (`__main__.py`)

```python
"""Entry point for running mycli_app as a module with python -m mycli_app"""

from .cli import main

if __name__ == "__main__":
    main()
```

**Purpose:**
- Enables `python -m mycli_app` execution
- Alternative to the `mycli` command
- Useful for debugging and development

### Step 4: Main CLI Module (`cli.py`)

This file contains the migrated logic from `mycli.py`:

```python
"""Main CLI application logic."""

import click
import colorama
# ... other imports

# Initialize colorama for cross-platform colored output
colorama.init()

@click.group()
def cli():
    """MyCliApp - A comprehensive CLI tool for Azure resource management."""
    pass

# ... all the original commands and functions

def main():
    """Main entry point for the CLI application."""
    cli()

if __name__ == "__main__":
    main()
```

**Migration Process:**
1. Copy all code from `mycli.py` to `cli.py`
2. Update imports if necessary
3. Ensure all functionality remains intact
4. Test that commands work correctly

---

## Phase 3: Configuration Files

### Step 1: Modern Packaging (`pyproject.toml`)

This is the modern standard for Python packaging, replacing `setup.py`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mycli-app"                    # Package name on PyPI (hyphens allowed)
version = "1.0.0"
description = "A comprehensive CLI tool for Azure resource management"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["cli", "azure", "cloud", "management"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

# Always installed dependencies
dependencies = [
    "click>=8.0.0",
    "colorama>=0.4.0",
    "requests>=2.25.0",
]

# Optional dependencies grouped by feature
[project.optional-dependencies]
azure = [
    "azure-identity>=1.12.0",
    "azure-mgmt-core>=1.3.0",
    "azure-core>=1.24.0",
    "msal>=1.20.0",
]
broker = [
    "msal[broker]>=1.20.0",
]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "flake8>=4.0.0",
    "mypy>=0.950",
]

# Entry points create console commands
[project.scripts]
mycli = "mycli_app.cli:cli"

[project.urls]
Homepage = "https://github.com/naga-nandyala/mycli-app"
Repository = "https://github.com/naga-nandyala/mycli-app"
Issues = "https://github.com/naga-nandyala/mycli-app/issues"
```

**Key Sections Explained:**

#### `[build-system]`
- Tells pip how to build your package
- `setuptools` is the most common build backend

#### `[project]`
- Core metadata about your package
- `name`: Must be unique on PyPI (hyphens become underscores in import)
- `classifiers`: Help users find your package

#### `dependencies`
- Always installed when someone installs your package
- Keep minimal - only include what's absolutely necessary

#### `[project.optional-dependencies]`
- Users choose what to install: `pip install mycli-app[azure]`
- Groups related functionality
- Reduces bloat for users who don't need all features

#### `[project.scripts]`
- Creates console commands
- `mycli = "mycli_app.cli:cli"` means:
  - Command name: `mycli`
  - Module: `mycli_app.cli`
  - Function: `cli`

### Step 2: Backward Compatibility (`setup.py`)

While `pyproject.toml` is modern, some tools still need `setup.py`:

```python
from setuptools import setup, find_packages

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
```

**Why Both Files?**
- `pyproject.toml`: Modern, declarative, preferred
- `setup.py`: Backward compatibility, some tools require it
- Together: Maximum compatibility

### Step 3: File Inclusion (`MANIFEST.in`)

Controls which files are included in the built package:

```
include README.md
include LICENSE
include CHANGELOG.md
include requirements.txt
recursive-include src/mycli_app *.py
global-exclude *.pyc
global-exclude __pycache__
global-exclude .DS_Store
global-exclude *.egg-info
```

**Commands Explained:**
- `include`: Include specific files
- `recursive-include`: Include files matching pattern in subdirectories
- `global-exclude`: Exclude files everywhere

---

## Phase 4: Documentation

### Professional Documentation Structure

Created comprehensive documentation for users and developers:

```
docs/
├── README.md          # Project overview, quick start
├── INSTALL.md         # Detailed installation instructions
├── USER_GUIDE.md      # Complete usage guide
├── CHANGELOG.md       # Version history
└── LICENSE           # MIT license
```

### Key Documentation Components

#### 1. README.md
```markdown
# MyCliApp

A comprehensive CLI tool for Azure resource management.

## Quick Start
```bash
pip install mycli-app[azure]
mycli --help
```

## Features
- Azure authentication
- Resource management
- Configuration management
- Cross-platform support
```

#### 2. INSTALL.md
```markdown
# Installation Guide

## Prerequisites
- Python 3.8+
- pip

## Installation Options

### Basic Installation
```bash
pip install mycli-app
```

### With Azure Features
```bash
pip install mycli-app[azure]
```

### Development Installation
```bash
git clone https://github.com/naga-nandyala/mycli-app.git
cd mycli-app
pip install -e .[dev]
```
```

#### 3. USER_GUIDE.md
Comprehensive usage documentation with examples for every command.

#### 4. CHANGELOG.md
```markdown
# Changelog

## [1.0.0] - 2025-08-22

### Added
- Initial release
- Azure authentication support
- Resource management commands
- Configuration management
- Cross-platform compatibility
```

### Documentation Best Practices

1. **User-Focused**: Write for your users, not yourself
2. **Examples**: Include working examples for every feature
3. **Installation**: Multiple installation methods
4. **Troubleshooting**: Common issues and solutions
5. **Contributing**: Guide for contributors

---

## Phase 5: Building the Package

### Step 1: Clean Previous Builds

```bash
# Remove old build artifacts
Remove-Item -Recurse -Force dist/, build/, src/*.egg-info/ -ErrorAction SilentlyContinue
```

### Step 2: Build Process

```bash
# Build both wheel and source distribution
python -m build
```

**What happens during build:**

1. **Reads Configuration**: Parses `pyproject.toml`
2. **Collects Files**: Uses `MANIFEST.in` rules
3. **Creates Metadata**: Package information
4. **Builds Wheel**: Pre-compiled package (`.whl`)
5. **Builds Source**: Source distribution (`.tar.gz`)

### Step 3: Build Outputs

```
dist/
├── mycli_app-1.0.0-py3-none-any.whl    # Wheel package
└── mycli_app-1.0.0.tar.gz              # Source distribution
```

**File Name Breakdown:**
- `mycli_app`: Package name (underscores)
- `1.0.0`: Version
- `py3`: Python 3 compatible
- `none`: No platform-specific code
- `any`: Works on any platform

### Step 4: Understanding Build Outputs

#### Wheel Package (`.whl`)
```bash
# Inspect wheel contents
python -m zipfile -l dist/mycli_app-1.0.0-py3-none-any.whl
```

**Advantages:**
- Fast installation (no compilation)
- Smaller download
- Works offline
- Platform-specific optimizations possible

#### Source Distribution (`.tar.gz`)
```bash
# Extract and inspect
tar -tf dist/mycli_app-1.0.0.tar.gz
```

**Advantages:**
- Can be built on any platform
- Source code inspection
- Custom build options
- Required for some package managers

---

## Phase 6: Testing & Verification

### Step 1: Installation Testing

```bash
# Test basic installation
pip install dist/mycli_app-1.0.0-py3-none-any.whl

# Verify installation
pip list | grep mycli

# Test command creation
which mycli
mycli --version
```

### Step 2: Functionality Testing

```bash
# Test core functionality
mycli --help
mycli status

# Test subcommands
mycli auth --help
mycli resource --help
mycli config --help
```

### Step 3: Optional Dependencies Testing

```bash
# Test Azure extras
pip install "dist/mycli_app-1.0.0-py3-none-any.whl[azure]"

# Verify Azure packages installed
pip list | grep azure

# Test Azure functionality
mycli auth login
```

### Step 4: Module Execution Testing

```bash
# Test python -m execution
python -m mycli_app --help
python -m mycli_app status
```

### Step 5: Uninstall Testing

```bash
# Clean uninstall
pip uninstall mycli-app -y

# Verify removal
mycli --version  # Should fail
which mycli      # Should not exist
```

---

## Phase 7: Distribution

### Distribution Options

#### Option 1: Direct File Sharing
```bash
# Share the wheel file
# Users install with:
pip install mycli_app-1.0.0-py3-none-any.whl
```

#### Option 2: GitHub Releases
1. Create a release on GitHub
2. Upload build artifacts
3. Users download and install

#### Option 3: PyPI Publishing (Recommended)

```bash
# Test on TestPyPI first
twine upload --repository testpypi dist/*

# Then publish to real PyPI
twine upload dist/*
```

**After PyPI publishing:**
```bash
# Users install with:
pip install mycli-app[azure]
```

### Installation Methods for Users

#### From Source Repository
```bash
git clone https://github.com/naga-nandyala/mycli-app.git
cd mycli-app
pip install .                    # Basic
pip install .[azure]            # With Azure
pip install .[broker,dev]       # Multiple extras
```

#### From Built Package
```bash
pip install mycli_app-1.0.0-py3-none-any.whl
pip install "mycli_app-1.0.0-py3-none-any.whl[azure]"
```

#### From PyPI
```bash
pip install mycli-app[azure]
```

---

## Key Concepts Explained

### Package vs. Module Names

- **Package Name** (for PyPI): `mycli-app` (hyphens allowed)
- **Module Name** (for imports): `mycli_app` (underscores only)
- **Command Name**: `mycli` (defined in entry points)

```python
# This creates the mapping:
[project.scripts]
mycli = "mycli_app.cli:cli"
#  ↑        ↑         ↑
# cmd   module.py  function
```

### Entry Points Magic

Entry points create executable commands:

```toml
[project.scripts]
mycli = "mycli_app.cli:cli"
```

**This means:**
1. When user types `mycli`
2. Python finds the `mycli_app` package
3. Imports the `cli` module
4. Calls the `cli()` function

### Optional Dependencies

```toml
[project.optional-dependencies]
azure = ["azure-identity>=1.12.0"]
```

**Installation:**
```bash
pip install mycli-app[azure]    # Installs mycli-app + azure deps
pip install mycli-app           # Installs mycli-app only
```

**Code Pattern:**
```python
try:
    from azure.identity import DefaultAzureCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

@click.command()
def azure_login():
    if not AZURE_AVAILABLE:
        click.echo("Install Azure extras: pip install mycli-app[azure]")
        return
    # ... azure code
```

### Semantic Versioning

Version: `1.0.0`
- **1**: Major version (breaking changes)
- **0**: Minor version (new features)
- **0**: Patch version (bug fixes)

**Update strategy:**
- Bug fix: `1.0.0` → `1.0.1`
- New feature: `1.0.1` → `1.1.0`
- Breaking change: `1.1.0` → `2.0.0`

---

## Common Pitfalls & Solutions

### 1. Import Errors

**Problem:**
```python
# This fails in installed package
from mycli import cli
```

**Solution:**
```python
# Use relative imports in package
from .cli import cli

# Or absolute imports with full package name
from mycli_app.cli import cli
```

### 2. Missing Files in Package

**Problem:** Built package missing important files

**Solution:** Update `MANIFEST.in`
```
include README.md
include LICENSE
recursive-include src/mycli_app *.py
```

### 3. Command Not Found

**Problem:** `mycli` command doesn't exist after installation

**Solutions:**
1. Check entry points in `pyproject.toml`
2. Verify installation: `pip list | grep mycli`
3. Check PATH: `echo $PATH`
4. Reinstall: `pip install --force-reinstall`

### 4. Dependency Conflicts

**Problem:** Package installation fails due to conflicts

**Solutions:**
1. Use virtual environments
2. Loosen version constraints: `click>=8.0.0` instead of `click==8.1.0`
3. Test with fresh environments

### 5. Cross-Platform Issues

**Problem:** Package works on Windows but not macOS/Linux

**Solutions:**
1. Use `pathlib` instead of `os.path`
2. Test on multiple platforms
3. Use `colorama.init()` for colored output
4. Avoid platform-specific dependencies in core

---

## Best Practices

### 1. Project Structure

```
✅ Good: src/ layout
src/
└── mypackage/
    ├── __init__.py
    └── module.py

❌ Bad: Flat layout
mypackage/
├── __init__.py
└── module.py
```

### 2. Dependencies

```toml
✅ Good: Minimal core, optional extras
dependencies = ["click>=8.0.0"]
[project.optional-dependencies]
azure = ["azure-identity>=1.12.0"]

❌ Bad: Everything required
dependencies = [
    "click>=8.0.0",
    "azure-identity>=1.12.0",  # Not everyone needs this
    "matplotlib>=3.0.0",       # Heavy dependency
]
```

### 3. Version Constraints

```toml
✅ Good: Compatible range
dependencies = ["click>=8.0.0,<9.0.0"]

❌ Bad: Too restrictive
dependencies = ["click==8.1.3"]

❌ Bad: Too loose
dependencies = ["click"]
```

### 4. Entry Points

```toml
✅ Good: Clear, descriptive names
[project.scripts]
mycli = "mycli_app.cli:cli"
myapp-admin = "mycli_app.admin:admin_cli"

❌ Bad: Generic names
[project.scripts]
cli = "mycli_app.cli:cli"
app = "mycli_app.cli:cli"
```

### 5. Documentation

```markdown
✅ Good: User-focused with examples
## Installation
```bash
pip install mycli-app[azure]
```

## Quick Start
```bash
mycli auth login
mycli resource list
```

❌ Bad: Developer-focused without examples
## Installation
Use pip to install the package.

## Usage
Run the CLI tool.
```

---

## Advanced Topics

### 1. Custom Build Backends

Instead of setuptools, you can use other build backends:

```toml
[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

### 2. Platform-Specific Dependencies

```toml
[project.optional-dependencies]
windows = [
    "pywin32>=227; sys_platform == 'win32'"
]
unix = [
    "termios>=1.0; sys_platform != 'win32'"
]
```

### 3. Console Scripts vs. GUI Scripts

```toml
[project.scripts]
mycli = "mycli_app.cli:cli"           # Console application

[project.gui-scripts]
mygui = "mycli_app.gui:main"          # GUI application (Windows)
```

### 4. Plugin Systems

```toml
[project.entry-points."mycli.plugins"]
auth = "mycli_plugins.auth:AuthPlugin"
deploy = "mycli_plugins.deploy:DeployPlugin"
```

### 5. Development Dependencies in pyproject.toml

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=22.0.0",
    "isort>=5.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
]
test = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
]
lint = [
    "black>=22.0.0",
    "isort>=5.0.0",
    "flake8>=5.0.0",
]
```

**Usage:**
```bash
pip install -e .[dev]      # All development tools
pip install -e .[test]     # Just testing
pip install -e .[lint]     # Just linting
```

---

## Resources & References

### Official Documentation
- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPA Build Documentation](https://build.pypa.io/)
- [Setuptools Documentation](https://setuptools.pypa.io/)
- [PEP 621 - pyproject.toml](https://peps.python.org/pep-0621/)

### Tools & Libraries
- [Click Documentation](https://click.palletsprojects.com/) - CLI framework
- [Colorama Documentation](https://pypi.org/project/colorama/) - Cross-platform colors
- [Twine Documentation](https://twine.readthedocs.io/) - Publishing to PyPI

### Best Practices
- [Python Application Layout](https://realpython.com/python-application-layouts/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

### Examples
- [Click Examples](https://github.com/pallets/click/tree/main/examples)
- [PyPA Sample Project](https://github.com/pypa/sampleproject)

---

## Summary

This tutorial covered the complete process of transforming a single Python script into a professional, installable package:

### ✅ What We Accomplished

1. **Modern Structure**: Adopted `src/` layout
2. **Professional Config**: Used `pyproject.toml` standard
3. **Flexible Installation**: Core + optional dependencies
4. **User Experience**: Easy `pip install mycli-app[azure]`
5. **Complete Documentation**: User guides and examples
6. **Distribution Ready**: Built wheel and source packages

### 🎯 Key Takeaways

- **Start Simple**: Core functionality with minimal dependencies
- **Plan for Growth**: Optional extras for advanced features
- **User First**: Design installation and usage for your users
- **Test Everything**: Installation, functionality, uninstallation
- **Document Well**: Your future self and users will thank you

### 🚀 Next Steps

1. **Publish to PyPI**: Share with the world
2. **Add CI/CD**: Automate testing and publishing
3. **Gather Feedback**: Listen to your users
4. **Iterate**: Improve based on real usage

You now have the knowledge to package any Python application professionally! 🎉

---

*This tutorial demonstrates real-world Python packaging using the `mycli-app` project as a case study. The techniques shown here apply to any Python CLI application or library.*
