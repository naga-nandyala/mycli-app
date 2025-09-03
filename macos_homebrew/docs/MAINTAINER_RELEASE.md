# Maintainer Release Guide (Single Repository)

## Prerequisites

* Formula location: `Formula/mycli-app.rb` in this repository
* This repository contains automated workflows for building and formula updates
* Version updated in `src/mycli_app/__init__.py`
* Git tag follows `vX.Y.Z` format

## Automated Release Process

### 1. Update Version
```bash
# Edit version in source
vim src/mycli_app/__init__.py  # Update __version__ = "X.Y.Z"
git add . && git commit -m "Bump version to X.Y.Z"
```

### 2. Create Release
```bash
# Create and push tag
git tag vX.Y.Z
git push origin vX.Y.Z

# Create GitHub release (triggers automation)
gh release create vX.Y.Z --title "Release vX.Y.Z" --notes "Release notes here"
```

### 3. Automation Handles
- ✅ **Binary Building**: GitHub Actions builds macOS binaries (ARM64 + x86_64)
- ✅ **Formula Update**: Automatically updates `Formula/mycli-app.rb` with new SHA256 hashes
- ✅ **Release Upload**: Binaries and SHA256 files uploaded to GitHub release

## Manual Formula Update (if needed)

If automation fails, manually update the formula:

```bash
# Run the update script
cd macos_homebrew
python update_formula.py
```

## Installation Testing

Test the updated formula:

```bash
# Uninstall existing version
brew uninstall mycli 2>/dev/null || true

# Install from your repository
curl -L -o /tmp/mycli-app.rb https://raw.githubusercontent.com/naga-nandyala/mycli-app/main/Formula/mycli-app.rb
brew install /tmp/mycli-app.rb

# Verify installation
mycli --version
```

## Manual Process (Backup)

If automation completely fails:

1. **Download release assets manually**
2. **Calculate SHA256**:
   ```bash
   shasum -a 256 mycli-X.Y.Z-macos-arm64.tar.gz
   shasum -a 256 mycli-X.Y.Z-macos-x86_64.tar.gz
   ```
3. **Update `Formula/mycli-app.rb`** with new version and SHA256 values
4. **Commit and push**

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Binary blocked by Gatekeeper | Consider code signing & notarization |
| "Bad CPU type" on Intel | Ensure Intel build exists in release |
| Formula hash mismatch | Re-run `python update_formula.py` |
| Automation failed | Check GitHub Actions logs and run manual update |

## Repository Structure

```text
mycli-app/
├── Formula/
│   └── mycli-app.rb          # 🍺 Homebrew formula (auto-updated)
├── .github/workflows/
│   ├── release_binaries.yml  # Builds macOS binaries
│   └── update-homebrew-formula.yml  # Updates formula
└── macos_homebrew/
    ├── update_formula.py     # Manual formula update script
    └── pyinstaller/          # Build configuration
```

---

Happy shipping! 🚀
