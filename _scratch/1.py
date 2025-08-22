#!/usr/bin/env python3
"""
MyCliApp - A simple CLI application similar to Azure CLI
"""

import click
import sys
import json
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama for Windows terminal color support
init()

__version__ = "1.0.0"

# Configuration
CONFIG_DIR = Path.home() / ".mycli"
TOKEN_FILE = CONFIG_DIR / "tokens.json"
CONFIG_FILE = CONFIG_DIR / "config.json"


class AuthBroker:
    """Handles broker-based authentication similar to Azure CLI."""

    def __init__(self):
        self.client_id = "mycli-app-12345"
        self.tenant_id = "common"
        self.scopes = ["https://management.core.windows.net/.default"]

    def device_code_flow(self):
        """Simulate device code flow authentication."""
        # Generate user code
        user_code = f"{uuid.uuid4().hex[:4].upper()}-{uuid.uuid4().hex[:4].upper()}"

        # Display device code instructions
        click.echo(f"{Fore.BLUE}🔐 Device Authentication Required{Style.RESET_ALL}")
        click.echo("\nTo sign in, use a web browser to open the page:")
        click.echo(f"{Fore.CYAN}https://microsoft.com/devicelogin{Style.RESET_ALL}")
        click.echo(f"\nAnd enter the code: {Fore.YELLOW}{user_code}{Style.RESET_ALL}")
        click.echo("\nWaiting for authentication...")

        # Simulate waiting for user authentication
        for i in range(5):
            click.echo(f"Waiting... ({i+1}/5)", nl=False)
            time.sleep(1)
            click.echo("\r" + " " * 20 + "\r", nl=False)

        # Simulate successful authentication
        token_data = {
            "access_token": f"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IjdkRC1nZWNOZ1gxWmY3R0xrT3ZwT0IyZGNWQSIsImtpZCI6IjdkRC1nZWNOZ1gxWmY3R0xrT3ZwT0IyZGNWQSJ9...{uuid.uuid4().hex}",
            "refresh_token": f"0.ARwA6WgJJ9X2qk2Z4jJX3Y8VQJzkhG1owukPb2EBxXGzkR9wADU...{uuid.uuid4().hex}",
            "expires_in": 3600,
            "expires_on": (datetime.now() + timedelta(hours=1)).isoformat(),
            "token_type": "Bearer",
            "scope": " ".join(self.scopes),
            "user_id": "user@example.com",
            "tenant_id": self.tenant_id,
        }

        return token_data

    def save_token(self, token_data):
        """Save token data to file."""
        CONFIG_DIR.mkdir(exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            json.dump(token_data, f, indent=2)

    def load_token(self):
        """Load token data from file."""
        if not TOKEN_FILE.exists():
            return None

        try:
            with open(TOKEN_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def is_token_valid(self, token_data):
        """Check if token is still valid."""
        if not token_data:
            return False

        try:
            expires_on = datetime.fromisoformat(token_data.get("expires_on", ""))
            return datetime.now() < expires_on
        except (ValueError, AttributeError):
            return False

    def get_current_user(self):
        """Get current authenticated user info."""
        token_data = self.load_token()
        if self.is_token_valid(token_data):
            return {
                "user_id": token_data.get("user_id"),
                "tenant_id": token_data.get("tenant_id"),
                "expires_on": token_data.get("expires_on"),
            }
        return None


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
@click.option("--use-broker", is_flag=True, default=True, help="Use broker-based authentication (default)")
@click.option("--use-device-code", is_flag=True, help="Use device code flow for authentication")
def login(tenant, use_broker, use_device_code):
    """Authenticate using broker-based login."""
    auth_broker = AuthBroker()

    # Check if already logged in
    current_user = auth_broker.get_current_user()
    if current_user:
        click.echo(f"{Fore.YELLOW}Already logged in as: {current_user['user_id']}{Style.RESET_ALL}")
        if not click.confirm("Do you want to login with a different account?"):
            return

    if tenant:
        auth_broker.tenant_id = tenant

    try:
        if use_device_code or use_broker:
            click.echo(f"{Fore.BLUE}🔐 Starting broker authentication...{Style.RESET_ALL}")
            token_data = auth_broker.device_code_flow()
            auth_broker.save_token(token_data)

            click.echo(f"\n{Fore.GREEN}✓ Successfully authenticated!{Style.RESET_ALL}")
            click.echo(f"  User: {Fore.CYAN}{token_data['user_id']}{Style.RESET_ALL}")
            click.echo(f"  Tenant: {Fore.CYAN}{token_data['tenant_id']}{Style.RESET_ALL}")
            expires_on = datetime.fromisoformat(token_data["expires_on"])
            click.echo(f"  Token expires: {Fore.CYAN}{expires_on.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        else:
            # Fallback to simple login
            click.echo(f"{Fore.BLUE}🔐 Opening browser for authentication...{Style.RESET_ALL}")
            click.echo(f"{Fore.GREEN}✓ Successfully logged in!{Style.RESET_ALL}")
            click.echo(f"  User: {Fore.CYAN}user@example.com{Style.RESET_ALL}")

    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}Authentication cancelled.{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}Authentication failed: {e}{Style.RESET_ALL}")


@cli.command()
def logout():
    """Logout and clear authentication tokens."""
    auth_broker = AuthBroker()
    current_user = auth_broker.get_current_user()

    if not current_user:
        click.echo(f"{Fore.YELLOW}No active login session found.{Style.RESET_ALL}")
        return

    try:
        # Remove token file
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()

        click.echo(f"{Fore.YELLOW}👋 Logging out...{Style.RESET_ALL}")
        click.echo(f"{Fore.GREEN}✓ Successfully logged out from {current_user['user_id']}{Style.RESET_ALL}")

    except Exception as e:
        click.echo(f"{Fore.RED}Error during logout: {e}{Style.RESET_ALL}")


@cli.command()
def whoami():
    """Show current authenticated user information."""
    auth_broker = AuthBroker()
    current_user = auth_broker.get_current_user()

    if not current_user:
        click.echo(f"{Fore.YELLOW}Not logged in. Use 'mycli login' to authenticate.{Style.RESET_ALL}")
        return

    click.echo(f"{Fore.BLUE}Current Authentication:{Style.RESET_ALL}")
    click.echo(f"  User: {Fore.CYAN}{current_user['user_id']}{Style.RESET_ALL}")
    click.echo(f"  Tenant: {Fore.CYAN}{current_user['tenant_id']}{Style.RESET_ALL}")

    expires_on = datetime.fromisoformat(current_user["expires_on"])
    time_remaining = expires_on - datetime.now()

    if time_remaining.total_seconds() > 0:
        hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        click.echo(f"  Token expires in: {Fore.GREEN}{hours}h {minutes}m{Style.RESET_ALL}")
    else:
        click.echo(f"  Token status: {Fore.RED}Expired{Style.RESET_ALL}")


@cli.command()
def account():
    """Manage account and authentication settings."""
    auth_broker = AuthBroker()
    current_user = auth_broker.get_current_user()

    click.echo(f"{Fore.BLUE}Account Information:{Style.RESET_ALL}")

    if current_user:
        click.echo(f"  Status: {Fore.GREEN}Authenticated{Style.RESET_ALL}")
        click.echo(f"  User: {Fore.CYAN}{current_user['user_id']}{Style.RESET_ALL}")
        click.echo(f"  Tenant: {Fore.CYAN}{current_user['tenant_id']}{Style.RESET_ALL}")

        # Token file info
        if TOKEN_FILE.exists():
            file_size = TOKEN_FILE.stat().st_size
            modified_time = datetime.fromtimestamp(TOKEN_FILE.stat().st_mtime)
            click.echo(f"  Token file: {Fore.CYAN}{TOKEN_FILE}{Style.RESET_ALL}")
            click.echo(f"  File size: {Fore.CYAN}{file_size} bytes{Style.RESET_ALL}")
            click.echo(f"  Last modified: {Fore.CYAN}{modified_time.strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
    else:
        click.echo(f"  Status: {Fore.YELLOW}Not authenticated{Style.RESET_ALL}")
        click.echo("  Use 'mycli login' to authenticate")

    # Configuration directory info
    click.echo(f"\n{Fore.BLUE}Configuration:{Style.RESET_ALL}")
    click.echo(f"  Config directory: {Fore.CYAN}{CONFIG_DIR}{Style.RESET_ALL}")
    click.echo(f"  Directory exists: {Fore.CYAN}{CONFIG_DIR.exists()}{Style.RESET_ALL}")


@cli.command()
def status():
    """Show current status and health."""
    auth_broker = AuthBroker()
    current_user = auth_broker.get_current_user()

    click.echo(f"{Fore.BLUE}📊 System Status:{Style.RESET_ALL}")
    click.echo(f"  Service: {Fore.GREEN}Online{Style.RESET_ALL}")

    if current_user:
        click.echo(f"  Authentication: {Fore.GREEN}Active ({current_user['user_id']}){Style.RESET_ALL}")
    else:
        click.echo(f"  Authentication: {Fore.YELLOW}Not authenticated{Style.RESET_ALL}")

    click.echo(f"  Version: {Fore.CYAN}{__version__}{Style.RESET_ALL}")
    click.echo(f"  Config directory: {Fore.CYAN}{CONFIG_DIR}{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
