# MyCliApp

A simple Python CLI application similar to Azure CLI with dummy commands for demonstration purposes.

## Features

- **Resource Management**: Create, list, and delete resources (dummy operations)
- **Configuration Management**: Set and view configuration settings
- **Authentication**: Simulate login/logout operations
- **Status Monitoring**: Check system status and health
- **Colorized Output**: Enhanced terminal output with colors and icons
- **Cross-platform**: Works on Windows, macOS, and Linux

## Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Commands

```bash
# Show help
python mycli.py --help

# Show version
python mycli.py --version

# Show status
python mycli.py status
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

### Authentication

```bash
# Simulate login
python mycli.py login

# Simulate logout
python mycli.py logout
```

## Installation as Package

To install this as a system-wide command:

```bash
pip install -e .
```

After installation, you can use the `mycli` command directly:

```bash
mycli --help
mycli resource list
mycli status
```

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
├── status
├── --help
└── --version
```

## Example Session

```bash
$ python mycli.py
Welcome to MyCliApp!
Use 'mycli --help' to see available commands.

$ python mycli.py resource create --name "test-vm" --type "vm"
✓ Creating vm resource...
  Name: test-vm
  Location: eastus
  Type: vm
✓ Resource 'test-vm' created successfully!

$ python mycli.py resource list
📋 Listing resources...

Name            Type       Location   Status    
--------------------------------------------------
myvm-001        vm         eastus     running   
mystorage-001   storage    westus     active    
mydb-001        database   eastus     running   

$ python mycli.py login
🔐 Opening browser for authentication...
✓ Successfully logged in!
  User: user@example.com
```

## Dependencies

- **click**: For building the command-line interface
- **colorama**: For cross-platform colored terminal output

## License

MIT License
