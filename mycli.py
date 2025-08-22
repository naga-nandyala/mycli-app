#!/usr/bin/env python3
"""
MyCliApp - A simple CLI application similar to Azure CLI
"""

import click
import sys
from colorama import init, Fore, Style

# Initialize colorama for Windows terminal color support
init()

__version__ = "1.0.0"


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
def login(tenant):
    """Simple authentication (simulation)."""
    click.echo(f"{Fore.BLUE}🔐 Opening browser for authentication...{Style.RESET_ALL}")
    if tenant:
        click.echo(f"  Tenant: {Fore.CYAN}{tenant}{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}✓ Successfully logged in!{Style.RESET_ALL}")
    click.echo(f"  User: {Fore.CYAN}user@example.com{Style.RESET_ALL}")


@cli.command()
def logout():
    """Logout (simulation)."""
    click.echo(f"{Fore.YELLOW}👋 Logging out...{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}✓ Successfully logged out!{Style.RESET_ALL}")


@cli.command()
def whoami():
    """Show current authenticated user information (simulation)."""
    click.echo(f"{Fore.BLUE}Current Authentication:{Style.RESET_ALL}")
    click.echo(f"  User: {Fore.CYAN}user@example.com{Style.RESET_ALL}")
    click.echo(f"  Tenant: {Fore.CYAN}common{Style.RESET_ALL}")
    click.echo(f"  Status: {Fore.GREEN}Authenticated{Style.RESET_ALL}")


@cli.command()
def account():
    """Manage account and authentication settings (simulation)."""
    click.echo(f"{Fore.BLUE}Account Information:{Style.RESET_ALL}")
    click.echo(f"  Status: {Fore.GREEN}Authenticated{Style.RESET_ALL}")
    click.echo(f"  User: {Fore.CYAN}user@example.com{Style.RESET_ALL}")
    click.echo(f"  Tenant: {Fore.CYAN}common{Style.RESET_ALL}")


@cli.command()
def status():
    """Show current status and health."""
    click.echo(f"{Fore.BLUE}📊 System Status:{Style.RESET_ALL}")
    click.echo(f"  Service: {Fore.GREEN}Online{Style.RESET_ALL}")
    click.echo(f"  Authentication: {Fore.GREEN}Active (user@example.com){Style.RESET_ALL}")
    click.echo(f"  Version: {Fore.CYAN}{__version__}{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        cli()
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
