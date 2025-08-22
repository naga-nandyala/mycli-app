#!/usr/bin/env python3
"""
MyCliApp - A simple CLI application similar to Azure CLI
"""

import click
import sys
import os
import json
import base64
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama for Windows terminal color support
init()

# Azure authentication imports
try:
    from azure.identity import InteractiveBrowserCredential, AzureCliCredential, DefaultAzureCredential
    from azure.core.exceptions import ClientAuthenticationError

    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

__version__ = "1.0.0"

# Configuration file path
CONFIG_DIR = Path.home() / ".mycli"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Authentication state
_auth_state = {"is_authenticated": False, "user_info": None, "tenant_id": None, "credential": None}


def ensure_config_dir():
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(exist_ok=True)


def load_auth_state():
    """Load authentication state from config file."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                _auth_state.update(data.get("auth", {}))
        except (json.JSONDecodeError, IOError):
            pass


def save_auth_state():
    """Save authentication state to config file."""
    ensure_config_dir()
    try:
        config_data = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                config_data = json.load(f)

        # Only save serializable data
        config_data["auth"] = {
            "is_authenticated": _auth_state["is_authenticated"],
            "user_info": _auth_state["user_info"],
            "tenant_id": _auth_state["tenant_id"],
        }

        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=2)
    except IOError:
        pass


def get_azure_credential(tenant_id=None):
    """Get Azure credential for authentication."""
    if not AZURE_AVAILABLE:
        return None

    try:
        if tenant_id:
            # Use interactive browser credential with specific tenant
            credential = InteractiveBrowserCredential(tenant_id=tenant_id)
        else:
            # Try Azure CLI credential first, then fallback to interactive browser
            try:
                credential = AzureCliCredential()
                # Test the credential
                token = credential.get_token("https://management.azure.com/.default")
                return credential
            except ClientAuthenticationError:
                # Fallback to interactive browser credential
                credential = InteractiveBrowserCredential()

        return credential
    except Exception:
        return None


def authenticate_user(tenant_id=None):
    """Authenticate user with Azure."""
    if not AZURE_AVAILABLE:
        click.echo(f"{Fore.RED}Azure SDK not available. Install required packages:{Style.RESET_ALL}")
        click.echo("pip install azure-identity azure-mgmt-core azure-core msal")
        return False

    try:
        credential = get_azure_credential(tenant_id)
        if not credential:
            click.echo(f"{Fore.RED}Failed to create Azure credential{Style.RESET_ALL}")
            return False

        # Test authentication by getting a token
        click.echo(f"{Fore.BLUE}🔐 Authenticating with Azure...{Style.RESET_ALL}")

        # This will trigger browser authentication if needed
        if isinstance(credential, InteractiveBrowserCredential):
            click.echo(f"{Fore.YELLOW}Opening browser for authentication...{Style.RESET_ALL}")
        elif hasattr(credential, "__class__"):
            click.echo(f"{Fore.BLUE}Using {credential.__class__.__name__}...{Style.RESET_ALL}")

        token = credential.get_token("https://management.azure.com/.default")

        if token:
            _auth_state["is_authenticated"] = True
            _auth_state["credential"] = credential
            _auth_state["tenant_id"] = tenant_id

            # Extract real user information from the token
            user_info = parse_jwt_token(token.token)
            if user_info:
                _auth_state["user_info"] = user_info
                # Update tenant_id from token if not provided
                if not tenant_id and user_info.get("tenant_id"):
                    _auth_state["tenant_id"] = user_info["tenant_id"]
            else:
                # Fallback to generic info if token parsing fails
                _auth_state["user_info"] = {
                    "user_id": "authenticated_user@domain.com",
                    "display_name": "Authenticated User",
                }

            save_auth_state()
            return True

    except ClientAuthenticationError as e:
        click.echo(f"{Fore.RED}Authentication failed: {str(e)}{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}Unexpected error during authentication: {str(e)}{Style.RESET_ALL}")

    return False


def is_authenticated():
    """Check if user is currently authenticated."""
    return _auth_state.get("is_authenticated", False)


def clear_auth_state():
    """Clear authentication state."""
    _auth_state.update({"is_authenticated": False, "user_info": None, "tenant_id": None, "credential": None})
    save_auth_state()


def parse_jwt_token(token_string):
    """Parse JWT token to extract user information."""
    try:
        # JWT tokens have 3 parts separated by dots: header.payload.signature
        parts = token_string.split(".")
        if len(parts) != 3:
            return None

        # Decode the payload (middle part)
        payload = parts[1]
        # Add padding if needed for base64 decoding
        payload += "=" * (4 - len(payload) % 4)

        # Decode base64
        decoded_bytes = base64.urlsafe_b64decode(payload)
        payload_json = json.loads(decoded_bytes)

        # Extract user information
        user_info = {}

        # Common claims in Azure AD tokens
        if "upn" in payload_json:  # User Principal Name
            user_info["user_id"] = payload_json["upn"]
        elif "unique_name" in payload_json:
            user_info["user_id"] = payload_json["unique_name"]
        elif "email" in payload_json:
            user_info["user_id"] = payload_json["email"]
        else:
            user_info["user_id"] = payload_json.get("sub", "unknown")

        # Display name
        user_info["display_name"] = payload_json.get("name", user_info["user_id"])

        # Tenant information
        user_info["tenant_id"] = payload_json.get("tid")
        user_info["tenant_name"] = payload_json.get("tenant_name")

        # Additional info
        user_info["object_id"] = payload_json.get("oid")
        user_info["roles"] = payload_json.get("roles", [])

        return user_info

    except Exception as e:
        click.echo(f"{Fore.YELLOW}Warning: Could not parse token for user info: {e}{Style.RESET_ALL}")
        return None


# Load auth state on startup
load_auth_state()


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version information")
@click.pass_context
def cli(ctx, version):
    """MyCliApp - A simple CLI application with dummy commands."""
    if version:
        click.echo(f"MyCliApp version {__version__}")
        return

    if ctx.invoked_subcommand is None:
        click.echo("Welcome to MyCliApp!")
        click.echo("Use 'mycli --help' to see available commands.")


@cli.group()
def resource():
    """Manage resources (dummy commands)."""
    pass


@resource.command()
@click.option("--name", "-n", required=True, help="Name of the resource")
@click.option("--location", "-l", default="eastus", help="Location for the resource")
@click.option(
    "--type",
    "-t",
    default="vm",
    type=click.Choice(["vm", "storage", "database"], case_sensitive=False),
    help="Type of resource to create",
)
def create(name, location, type):
    """Create a new resource."""
    click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} Creating {type} resource...")
    click.echo(f"  Name: {Fore.CYAN}{name}{Style.RESET_ALL}")
    click.echo(f"  Location: {Fore.CYAN}{location}{Style.RESET_ALL}")
    click.echo(f"  Type: {Fore.CYAN}{type}{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} Resource '{name}' created successfully!")


@resource.command()
@click.option("--location", "-l", help="Filter by location")
@click.option("--type", "-t", help="Filter by resource type")
def list(location, type):
    """List all resources."""
    click.echo(f"{Fore.YELLOW}📋{Style.RESET_ALL} Listing resources...")

    # Dummy data
    resources = [
        {"name": "myvm-001", "type": "vm", "location": "eastus", "status": "running"},
        {"name": "mystorage-001", "type": "storage", "location": "westus", "status": "active"},
        {"name": "mydb-001", "type": "database", "location": "eastus", "status": "running"},
    ]

    # Apply filters
    filtered_resources = resources
    if location:
        filtered_resources = [r for r in filtered_resources if r["location"] == location]
    if type:
        filtered_resources = [r for r in filtered_resources if r["type"] == type]

    if not filtered_resources:
        click.echo(f"{Fore.YELLOW}No resources found matching the criteria.{Style.RESET_ALL}")
        return

    # Display table header
    click.echo(f"\n{Fore.BLUE}{'Name':<15} {'Type':<10} {'Location':<10} {'Status':<10}{Style.RESET_ALL}")
    click.echo("-" * 50)

    # Display resources
    for resource in filtered_resources:
        status_color = Fore.GREEN if resource["status"] == "running" or resource["status"] == "active" else Fore.RED
        click.echo(
            f"{resource['name']:<15} {resource['type']:<10} {resource['location']:<10} {status_color}{resource['status']:<10}{Style.RESET_ALL}"
        )


@resource.command()
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to delete this resource?")
def delete(name):
    """Delete a resource."""
    click.echo(f"{Fore.RED}🗑️{Style.RESET_ALL}  Deleting resource '{name}'...")
    click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} Resource '{name}' deleted successfully!")


@cli.group()
def config():
    """Manage configuration settings."""
    pass


@config.command()
@click.option("--key", "-k", required=True, help="Configuration key")
@click.option("--value", "-v", required=True, help="Configuration value")
def set(key, value):
    """Set a configuration value."""
    click.echo(f"{Fore.GREEN}✓{Style.RESET_ALL} Configuration set:")
    click.echo(f"  {key} = {Fore.CYAN}{value}{Style.RESET_ALL}")


@config.command()
@click.option("--key", "-k", help="Specific configuration key to show")
def show(key):
    """Show configuration values."""
    # Dummy configuration data
    config_data = {"default_location": "eastus", "output_format": "table", "subscription": "my-subscription-123"}

    if key:
        if key in config_data:
            click.echo(f"{key}: {Fore.CYAN}{config_data[key]}{Style.RESET_ALL}")
        else:
            click.echo(f"{Fore.RED}Configuration key '{key}' not found.{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.BLUE}Current configuration:{Style.RESET_ALL}")
        for k, v in config_data.items():
            click.echo(f"  {k}: {Fore.CYAN}{v}{Style.RESET_ALL}")


@cli.command()
@click.option("--tenant", "-t", help="Tenant ID to authenticate with")
@click.option("--use-device-code", is_flag=True, help="Use device code flow instead of browser")
@click.option("--demo", is_flag=True, hidden=True, help="Demo mode (for testing)")
def login(tenant, use_device_code, demo):
    """Authenticate with Azure."""
    if is_authenticated():
        click.echo(f"{Fore.YELLOW}Already authenticated. Use 'logout' to sign out first.{Style.RESET_ALL}")
        return

    click.echo(f"{Fore.BLUE}🔐 Starting Azure authentication...{Style.RESET_ALL}")

    if tenant:
        click.echo(f"  Tenant: {Fore.CYAN}{tenant}{Style.RESET_ALL}")

    if use_device_code:
        click.echo(f"{Fore.YELLOW}Device code flow not implemented yet. Using browser authentication.{Style.RESET_ALL}")

    # Demo mode for testing without actual Azure login
    if demo:
        click.echo(f"{Fore.YELLOW}[DEMO MODE] Simulating Azure authentication...{Style.RESET_ALL}")
        _auth_state["is_authenticated"] = True
        _auth_state["user_info"] = {"user_id": "demo.user@contoso.com", "display_name": "Demo User"}
        _auth_state["tenant_id"] = tenant or "demo-tenant-id"
        save_auth_state()
        click.echo(f"{Fore.GREEN}✓ Successfully authenticated! (Demo Mode){Style.RESET_ALL}")
        click.echo(f"  User: {Fore.CYAN}demo.user@contoso.com{Style.RESET_ALL}")
        return

    if authenticate_user(tenant):
        user_info = _auth_state.get("user_info", {})
        click.echo(f"{Fore.GREEN}✓ Successfully authenticated!{Style.RESET_ALL}")
        click.echo(f"  User: {Fore.CYAN}{user_info.get('user_id', 'unknown')}{Style.RESET_ALL}")
        if tenant:
            click.echo(f"  Tenant: {Fore.CYAN}{tenant}{Style.RESET_ALL}")
    else:
        click.echo(f"{Fore.RED}❌ Authentication failed{Style.RESET_ALL}")
        if not AZURE_AVAILABLE:
            click.echo(f"{Fore.YELLOW}💡 Tip: Install Azure packages with:{Style.RESET_ALL}")
            click.echo("    pip install azure-identity azure-mgmt-core azure-core msal")


@cli.command()
def logout():
    """Logout from Azure authentication."""
    if not is_authenticated():
        click.echo(f"{Fore.YELLOW}Not currently authenticated.{Style.RESET_ALL}")
        return

    click.echo(f"{Fore.YELLOW}👋 Logging out...{Style.RESET_ALL}")
    clear_auth_state()
    click.echo(f"{Fore.GREEN}✓ Successfully logged out!{Style.RESET_ALL}")
    click.echo(f"{Fore.BLUE}💡 Note: You may need to clear your browser cache for complete logout.{Style.RESET_ALL}")


@cli.command()
def whoami():
    """Show current authenticated user information."""
    if not is_authenticated():
        click.echo(f"{Fore.RED}Not authenticated. Use 'mycli login' to sign in.{Style.RESET_ALL}")
        return

    user_info = _auth_state.get("user_info", {})
    tenant_id = _auth_state.get("tenant_id")

    click.echo(f"{Fore.BLUE}Current Authentication:{Style.RESET_ALL}")
    click.echo(f"  User: {Fore.CYAN}{user_info.get('user_id', 'unknown')}{Style.RESET_ALL}")
    click.echo(f"  Display Name: {Fore.CYAN}{user_info.get('display_name', 'unknown')}{Style.RESET_ALL}")
    click.echo(f"  Tenant: {Fore.CYAN}{tenant_id or 'common'}{Style.RESET_ALL}")
    click.echo(f"  Status: {Fore.GREEN}Authenticated{Style.RESET_ALL}")
    click.echo(
        f"  Azure SDK: {Fore.GREEN if AZURE_AVAILABLE else Fore.RED}{'Available' if AZURE_AVAILABLE else 'Not Available'}{Style.RESET_ALL}"
    )


@cli.command()
def account():
    """Manage account and authentication settings."""
    if not is_authenticated():
        click.echo(f"{Fore.YELLOW}Account Information:{Style.RESET_ALL}")
        click.echo(f"  Status: {Fore.RED}Not Authenticated{Style.RESET_ALL}")
        click.echo("  Use 'mycli login' to sign in")
        return

    user_info = _auth_state.get("user_info", {})
    tenant_id = _auth_state.get("tenant_id")

    click.echo(f"{Fore.BLUE}Account Information:{Style.RESET_ALL}")
    click.echo(f"  Status: {Fore.GREEN}Authenticated{Style.RESET_ALL}")
    click.echo(f"  User: {Fore.CYAN}{user_info.get('user_id', 'unknown')}{Style.RESET_ALL}")
    click.echo(f"  Display Name: {Fore.CYAN}{user_info.get('display_name', 'unknown')}{Style.RESET_ALL}")
    click.echo(f"  Tenant: {Fore.CYAN}{tenant_id or 'common'}{Style.RESET_ALL}")

    if CONFIG_FILE.exists():
        click.echo(f"  Config File: {Fore.CYAN}{CONFIG_FILE}{Style.RESET_ALL}")


@cli.command()
def status():
    """Show current status and health."""
    auth_status = "Active" if is_authenticated() else "Not Authenticated"
    auth_color = Fore.GREEN if is_authenticated() else Fore.RED

    user_info = _auth_state.get("user_info", {}) if is_authenticated() else {}
    user_display = user_info.get("user_id", "None") if is_authenticated() else "None"

    click.echo(f"{Fore.BLUE}📊 System Status:{Style.RESET_ALL}")
    click.echo(f"  Service: {Fore.GREEN}Online{Style.RESET_ALL}")
    click.echo(f"  Authentication: {auth_color}{auth_status} ({user_display}){Style.RESET_ALL}")
    click.echo(
        f"  Azure SDK: {Fore.GREEN if AZURE_AVAILABLE else Fore.RED}{'Available' if AZURE_AVAILABLE else 'Not Available'}{Style.RESET_ALL}"
    )
    click.echo(f"  Version: {Fore.CYAN}{__version__}{Style.RESET_ALL}")

    if not AZURE_AVAILABLE:
        click.echo(f"\n{Fore.YELLOW}💡 Install Azure packages for full functionality:{Style.RESET_ALL}")
        click.echo("    pip install azure-identity azure-mgmt-core azure-core msal")


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
