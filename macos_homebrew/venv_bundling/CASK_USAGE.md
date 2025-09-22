# Homebrew Cask Installation (Venv Bundle)

You can now install the portable virtual environment bundle via a Homebrew Cask.

## 1. Tap the repository

```bash
brew tap naga-nandyala/mycli-app
```

## 2. Install the cask

```bash
brew install --cask mycli-app-venv
```

## 3. Use the CLI

```bash
mycli --help
mycli status
mycli login
```

## What the Cask Provides

The cask extracts a pre-built Python virtual environment (one per architecture) containing:

* mycli-app with extras: azure, broker
* azure-identity, azure-core, azure-mgmt-core
* msal with broker support

All dependencies are self-contained; after installation, no further network access is required to run basic commands.

## Relationship to the Formula

You now have two installation options:

* `brew install mycli-app` (formula – PyInstaller or standard packaging variant)
* `brew install --cask mycli-app-venv` (pre-built venv bundle)

Choose the cask if you prefer an isolated, updatable virtual environment without compiling or resolving Python deps locally.

## Updating

On each tagged release (`vX.Y.Z`), GitHub Actions regenerates the cask file with updated URLs and SHA256 checksums and pushes it to the tap.

## Uninstalling

```bash
brew uninstall --cask mycli-app-venv
```

## Troubleshooting

* Verify architecture: `uname -m`
* Show installation files: `brew list --cask mycli-app-venv`
* Reinstall: `brew reinstall --cask mycli-app-venv`
* Force cleanup: `brew uninstall --cask mycli-app-venv && brew cleanup --prune=all`

If issues persist, open an issue and include:

* macOS version
* Architecture
* Output of: `mycli --version` and `mycli status`
