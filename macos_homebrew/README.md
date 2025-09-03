# macOS Homebrew Packaging

This folder contains assets and automation tools for distributing `mycli` as a standalone prebuilt binary through a personal Homebrew tap.

## Files Overview

- `formula_template/mycli_split_arch.rb` - The main Homebrew formula template (architecture-specific)
- `formula_template/mycli_universal.rb` - Alternative universal binary formula (unused)
- `update_formula.py` - Python script to automatically update formula with latest release
- `pyinstaller/` - Build spec and helper scripts for producing macOS binaries
- `docs/` - User and maintainer documentation

## Automation Options

### 1. Automatic Updates via GitHub Actions

The `.github/workflows/update-homebrew-formula.yml` workflow automatically updates the formula whenever you publish a new release on GitHub.

**How it works:**
- Triggers when you publish a new GitHub release
- Fetches the latest release information
- Downloads SHA256 hashes from the `.sha256` files
- Updates the formula template
- Commits and pushes the changes

### 2. Manual Updates

#### Using Python Script

```bash
cd macos_homebrew
python update_formula.py
```

Requirements:

- Python 3.x
- `requests` library (`pip install requests`)

## High-Level Flow

1. Tag a release (e.g. `v0.1.0`).
2. GitHub Actions matrix build produces PyInstaller binary per architecture.
3. Release assets uploaded: `mycli-<version>-macos-[arm64|x86_64].tar.gz` with SHA256 hashes.
4. Update tap formula with new version + SHA256 (automatically or manually).
5. Users install via:

```bash
brew tap naga-nandyala/mycli-app
brew install mycli
```

## Publishing to Homebrew

### Option 1: Create a Homebrew Tap

1. Create a new repository named `homebrew-mycli-app`
2. Copy the updated formula to `Formula/mycli.rb` in that repository
3. Users can install with the commands above

### Option 2: Submit to Official Homebrew

1. Fork the [Homebrew/homebrew-core](https://github.com/Homebrew/homebrew-core) repository
2. Add your formula to `Formula/mycli.rb`
3. Submit a pull request

See `docs/MAINTAINER_RELEASE.md` for detailed steps.
