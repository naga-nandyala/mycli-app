# MyCliApp

A simple Python CLI application similar to Azure CLI with Azure authentication capabilities.

## Features

- **Resource Management**: Create, list, and delete resources (dummy operations)
- **Configuration Management**: Set and view configuration settings
- **Azure Authentication**: Real Azure authentication using Azure SDK with multiple authentication methods
- **Broker Authentication**: Enhanced security through Windows Hello and Microsoft Authenticator
- **Device Code Flow**: Authentication for environments without browser access
- **Status Monitoring**: Check system status and health
- **Colorized Output**: Enhanced terminal output with colors and icons
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Persistent Authentication**: Saves authentication state between sessions

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Azure Authentication Setup

The application now supports real Azure authentication through the Azure SDK. To use Azure authentication features:

1. Ensure you have the Azure packages installed (included in requirements.txt):
   - azure-identity
   - azure-mgmt-core
   - azure-core
   - msal

2. You can authenticate using:
   - **Interactive Browser Login**: Default method, opens a browser for authentication
   - **Broker Authentication**: Enhanced security using Windows Hello or Microsoft Authenticator (Windows)
   - **Device Code Flow**: For environments without browser access or remote scenarios
   - **Azure CLI**: If you're already authenticated with Azure CLI

## Usage

### Basic Commands

```bash
# Show help
python mycli.py --help

# Show version
python mycli.py --version

# Show status (includes authentication status)
python mycli.py status
```

### Authentication Commands

```bash
# Login to Azure (opens browser)
python mycli.py login

# Login with broker authentication (Windows Hello/Authenticator)
python mycli.py login --use-broker

# Login with device code flow (for remote/headless scenarios)
python mycli.py login --use-device-code

# Login with specific tenant
python mycli.py login --tenant "your-tenant-id"

# Check broker authentication capabilities
python mycli.py broker

# Check who you're logged in as
python mycli.py whoami

# View account information
python mycli.py account

# Logout from Azure
python mycli.py logout
```

### Resource Management

```bash
# Create a resource
python mycli.py resource create --name "my-vm" --location "eastus" --type "vm"

# List all resources
python mycli.py resource list

# List resources by location
python mycli.py resource list --location "eastus"

# List resources by type
python mycli.py resource list --type "vm"

# Delete a resource (with confirmation)
python mycli.py resource delete "my-vm"
```

### Configuration Management

```bash
# Set a configuration value
python mycli.py config set --key "default_location" --value "westus"

# Show all configuration
python mycli.py config show

# Show specific configuration key
python mycli.py config show --key "default_location"
```

## Installation as Package

To install this as a system-wide command:

```bash
pip install -e .
```

After installation, you can use the `mycli` command directly:

```bash
mycli --help
mycli login
mycli resource list
mycli status
```

## Authentication Storage

Authentication information is stored in:
- **Windows**: `%USERPROFILE%\.mycli\config.json`
- **macOS/Linux**: `~/.mycli/config.json`

The stored information includes:
- Authentication status
- User information (user ID, display name)
- Tenant ID (if specified)
- Authentication method used (browser, broker, device_code, cli)
- Broker capabilities (for broker authentication)

**Note**: Credentials are managed by the Azure SDK and are not stored directly in the config file.

## Command Structure

The CLI follows a hierarchical command structure similar to Azure CLI:

```
mycli
├── resource
│   ├── create
│   ├── list
│   └── delete
├── config
│   ├── set
│   └── show
├── login
├── logout
├── whoami
├── account
├── status
├── --help
└── --version
```

## Example Session with Azure Authentication

```bash
$ python mycli.py status
📊 System Status:
  Service: Online
  Authentication: Not Authenticated (None)
  Azure SDK: Available
  Version: 1.0.0

$ python mycli.py login
🔐 Starting Azure authentication...
✓ Successfully authenticated!
  User: your.email@domain.com

$ python mycli.py whoami
Current Authentication:
  User: your.email@domain.com
  Display Name: Your Name
  Tenant: common
  Status: Authenticated
  Azure SDK: Available

$ python mycli.py resource create --name "test-vm" --type "vm"
✓ Creating vm resource...
  Name: test-vm
  Location: eastus
  Type: vm
✓ Resource 'test-vm' created successfully!

$ python mycli.py logout
� Logging out...
✓ Successfully logged out!
💡 Note: You may need to clear your browser cache for complete logout.
```

## Dependencies

- **click**: For building the command-line interface
- **colorama**: For cross-platform colored terminal output
- **azure-identity**: For Azure authentication
- **azure-mgmt-core**: For Azure management operations
- **azure-core**: Core Azure SDK functionality
- **msal**: Microsoft Authentication Library

## Error Handling

The application includes comprehensive error handling for:
- Missing Azure SDK packages
- Authentication failures
- Network connectivity issues
- Invalid tenant IDs
- Permission issues

## License

MIT License
