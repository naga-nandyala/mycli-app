# User Guide for MyCliApp

## Overview

MyCliApp is a command-line interface application that provides Azure-like functionality with comprehensive authentication options. This guide will help you get started and make the most of the application.

## Installation

### Quick Install
```bash
pip install mycli-app[azure]
```

### Installation Options
- **Basic**: `pip install mycli-app` (CLI only)
- **Azure**: `pip install mycli-app[azure]` (+ Azure authentication)
- **Broker**: `pip install mycli-app[broker]` (+ Windows Hello/Authenticator)
- **Development**: `pip install mycli-app[dev]` (+ dev tools)

## Getting Started

### 1. Check Installation
```bash
mycli --version
mycli status
```

### 2. Authenticate (Optional)
For Azure features, authenticate first:
```bash
mycli login
```

### 3. Explore Commands
```bash
mycli --help
mycli resource --help
mycli config --help
```

## Authentication Guide

### Browser Authentication (Default)
```bash
mycli login
```
- Opens your default web browser
- Sign in with your Azure credentials
- Works on all platforms

### Broker Authentication (Windows)
```bash
mycli login --use-broker
```
- Uses Windows Hello (face, fingerprint, PIN)
- Uses Microsoft Authenticator app
- More secure than browser authentication
- Windows only

### Device Code Flow
```bash
mycli login --use-device-code
```
- For remote/headless environments
- No browser required
- Follow the displayed instructions

### Tenant-Specific Login
```bash
mycli login --tenant "your-tenant-id"
```

### Check Authentication Status
```bash
mycli whoami          # Current user info
mycli account         # Account details
mycli broker          # Broker capabilities
```

### Logout
```bash
mycli logout
```

## Resource Management

### Create Resources
```bash
# Create a VM
mycli resource create --name "web-server-01" --type "vm" --location "eastus"

# Create storage
mycli resource create --name "backup-storage" --type "storage" --location "westus"

# Create database
mycli resource create --name "user-db" --type "database" --location "eastus"
```

### List Resources
```bash
# List all resources
mycli resource list

# Filter by location
mycli resource list --location "eastus"

# Filter by type
mycli resource list --type "vm"

# Combine filters
mycli resource list --location "eastus" --type "database"
```

### Delete Resources
```bash
# Delete with confirmation prompt
mycli resource delete "web-server-01"

# The command will ask for confirmation before deleting
```

## Configuration Management

### Set Configuration
```bash
# Set default location
mycli config set --key "default_location" --value "eastus"

# Set output format
mycli config set --key "output_format" --value "table"

# Set subscription
mycli config set --key "subscription" --value "my-subscription-123"
```

### View Configuration
```bash
# Show all configuration
mycli config show

# Show specific key
mycli config show --key "default_location"
```

## System Commands

### Status and Health
```bash
# Show system status
mycli status

# Show version
mycli --version

# Show help
mycli --help
```

### Cache Management
```bash
# Clear mycli authentication cache
mycli clear-cache

# Clear all cache including MSAL/Azure
mycli clear-cache --all
```

## Command Reference

### Global Options
- `--help`: Show help for any command
- `--version`: Show version information

### Authentication Commands
- `mycli login [options]`: Authenticate with Azure
- `mycli logout`: Sign out from Azure
- `mycli whoami`: Show current user
- `mycli account`: Show account information
- `mycli broker`: Show broker authentication info

### Resource Commands
- `mycli resource create [options]`: Create a new resource
- `mycli resource list [options]`: List resources
- `mycli resource delete <name>`: Delete a resource

### Configuration Commands
- `mycli config set --key <key> --value <value>`: Set configuration
- `mycli config show [--key <key>]`: Show configuration

### System Commands
- `mycli status`: Show system status
- `mycli clear-cache [--all]`: Clear authentication cache

## Advanced Usage

### Authentication Flows

1. **Standard Flow** (Browser):
   ```bash
   mycli login
   mycli whoami
   mycli resource list
   ```

2. **Secure Flow** (Broker on Windows):
   ```bash
   mycli login --use-broker
   mycli whoami
   mycli resource create --name "secure-vm" --type "vm"
   ```

3. **Remote Flow** (Device Code):
   ```bash
   mycli login --use-device-code
   # Follow the instructions to authenticate on another device
   ```

### Automation Examples

#### Batch Resource Creation
```bash
# Create multiple resources with a script
mycli resource create --name "web-01" --type "vm" --location "eastus"
mycli resource create --name "web-02" --type "vm" --location "eastus"
mycli resource create --name "web-storage" --type "storage" --location "eastus"
```

#### Configuration Setup
```bash
# Set up common configuration
mycli config set --key "default_location" --value "eastus"
mycli config set --key "output_format" --value "table"
mycli config set --key "subscription" --value "production-sub"
```

## Troubleshooting

### Common Issues

#### "Command not found: mycli"
```bash
# Check if installed
pip list | grep mycli

# Reinstall if needed
pip install mycli-app[azure]
```

#### Authentication Issues
```bash
# Check status
mycli status

# Clear cache and retry
mycli clear-cache --all
mycli login

# Try different authentication method
mycli login --use-device-code
```

#### Azure SDK Errors
```bash
# Install Azure extras
pip install mycli-app[azure]

# Verify installation
pip list | grep azure
```

### Getting Help

1. **In-app help**:
   ```bash
   mycli --help
   mycli command --help
   ```

2. **Check status**:
   ```bash
   mycli status
   ```

3. **Verify installation**:
   ```bash
   mycli --version
   pip list | grep mycli
   ```

## Best Practices

### Security
- Use broker authentication on Windows for enhanced security
- Regularly clear cache: `mycli clear-cache`
- Use tenant-specific login for multi-tenant environments
- Logout when switching between accounts: `mycli logout`

### Workflow
- Check status before starting: `mycli status`
- Authenticate once per session: `mycli login`
- Use filters to manage large resource lists: `mycli resource list --location eastus`
- Set common configuration to save time: `mycli config set`

### Organization
- Use consistent naming conventions for resources
- Group resources by location or purpose
- Regularly review and clean up unused resources

## Examples

### Complete Workflow Example
```bash
# 1. Check system
mycli status

# 2. Authenticate
mycli login

# 3. Set preferences
mycli config set --key "default_location" --value "eastus"

# 4. Create resources
mycli resource create --name "prod-web-01" --type "vm"
mycli resource create --name "prod-storage" --type "storage"

# 5. Verify
mycli resource list --location "eastus"

# 6. Cleanup (if needed)
mycli resource delete "prod-web-01"
```

### Multi-tenant Example
```bash
# Work with tenant A
mycli login --tenant "tenant-a-id"
mycli resource create --name "tenant-a-vm" --type "vm"

# Switch to tenant B
mycli logout
mycli login --tenant "tenant-b-id"
mycli resource create --name "tenant-b-vm" --type "vm"
```

## Configuration Files

### Location
- **Windows**: `%USERPROFILE%\.mycli\config.json`
- **macOS/Linux**: `~/.mycli/config.json`

### Content
The configuration file stores:
- Authentication status and user information
- Authentication method used
- Tenant information
- Broker capabilities (Windows)

**Note**: Actual credentials are managed by the Azure SDK and are not stored in plain text.

---

For more information, see the [README.md](README.md) and [INSTALL.md](INSTALL.md) files.
