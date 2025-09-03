# macOS Homebrew Packaging

This folder contains assets and automation helpers for distributing `mycli` as a standalone prebuilt binary through a personal Homebrew tap.

## Layout

* `pyinstaller/`
  * Build spec and helper scripts for producing macOS binaries (arm64 + x86_64 / universal)
* `formula_template/`
  * Template Ruby formula variants (universal or per-arch) to copy into your tap repo (`homebrew-mycli`)
* `workflow/`
  * GitHub Actions workflow file to place under `.github/workflows` in the main repository
* `docs/`
  * User and maintainer docs (install instructions, release process)

## High-Level Flow

1. Tag a release (e.g. `v1.0.0`).
2. GitHub Actions matrix build produces PyInstaller binary per architecture.
3. (Optional) Combine into a universal binary with `lipo`.
4. Release assets uploaded: `mycli-<version>-macos-[arm64|x86_64].tar.gz` or universal.
5. Update tap formula with new version + SHA256.
6. Users install via:

```bash
brew tap naga-nandyala/mycli
brew install mycli
```

See `docs/MAINTAINER_RELEASE.md` for detailed steps.
