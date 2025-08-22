# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-08-22

### Added
- Initial release of MyCliApp
- Azure authentication support with multiple methods:
  - Interactive browser authentication
  - Broker-based authentication (Windows Hello, Microsoft Authenticator)
  - Device code flow for headless environments
  - Azure CLI credential fallback
- Resource management commands (create, list, delete)
- Configuration management (set, show)
- Colorized terminal output
- Cross-platform support (Windows, macOS, Linux)
- Persistent authentication state storage
- Comprehensive help system
- Status and health monitoring commands

### Features
- **Authentication Commands**: `login`, `logout`, `whoami`, `account`, `broker`
- **Resource Commands**: `resource create`, `resource list`, `resource delete`
- **Configuration Commands**: `config set`, `config show`
- **Utility Commands**: `status`, `clear-cache`
- **Optional Azure SDK Integration**: Install with `[azure]` or `[broker]` extras
- **Development Tools**: Install with `[dev]` extra for testing and linting

### Dependencies
- click>=8.0.0 (CLI framework)
- colorama>=0.4.0 (cross-platform colored output)
- Optional Azure packages for authentication features

### Installation Options
- Basic CLI: `pip install mycli-app`
- With Azure support: `pip install mycli-app[azure]` 
- With broker authentication: `pip install mycli-app[broker]`
- Development setup: `pip install mycli-app[dev]`
