---
# Homebrew Binary Distribution (Custom Tap)

This guide explains how we publish prebuilt macOS binaries for `mycli` via a Homebrew tap using a dual-architecture formula (arm64 + x64).

## Overview

Flow:

1. Tag release (`vX.Y.Z`)
2. GitHub Action builds PyInstaller single-file executables for arm64 & x64
3. Action uploads zipped binaries as release assets
4. Action updates tap repo formula (`naga-nandyala/homebrew-tap/Formula/mycli.rb`) with new URLs + SHA256 values
5. Users install / upgrade via: `brew install naga-nandyala/tap/mycli`

## Release Asset Naming

```
mycli-<version>-macos-arm64.zip
mycli-<version>-macos-x64.zip
```

Each zip MUST contain only the `mycli` executable at its root.

## Build Command (local example)

```bash
pip install .[azure,broker] pyinstaller
pyinstaller --name mycli --onefile --clean --paths src src/mycli_app/cli.py
cd dist
zip -9 mycli-1.0.0-macos-arm64.zip mycli   # build on arm machine
```

## Formula Template (Generated Automatically)

```ruby
class Mycli < Formula
  desc "CLI tool similar to Azure CLI for cloud management"
  homepage "https://github.com/naga-nandyala/mycli-app"
  version "1.0.0"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/naga-nandyala/mycli-app/releases/download/v1.0.0/mycli-1.0.0-macos-arm64.zip"
      sha256 "<ARM_SHA256>"
    else
      url "https://github.com/naga-nandyala/mycli-app/releases/download/v1.0.0/mycli-1.0.0-macos-x64.zip"
      sha256 "<X64_SHA256>"
    end
  end

  def install
    bin.install "mycli"
  end

  test do
    assert_match "MyCliApp version", shell_output("#{bin}/mycli --version")
  end
end
```

## Secrets Required

Add a classic PAT (repo scope) in this repo settings as `HOMEBREW_TAP_PAT` so the workflow can push to the tap repository.

## User Install Instructions

```bash
brew tap naga-nandyala/tap https://github.com/naga-nandyala/homebrew-tap
brew install mycli
mycli --version
```

## Upgrading

```bash
brew upgrade mycli
```

## Troubleshooting

- If install fails with 404: ensure release assets exist & formula URLs match tag
- If SHA mismatch: re-run workflow after confirming correct asset integrity
- If quarantine warning: user can run `xattr -d com.apple.quarantine $(which mycli)`

## Optional Enhancements

- Provide a universal2 binary (combine architectures via `lipo`) to simplify formula
- Codesign & notarize binaries for smoother Gatekeeper experience
- Add `brew livecheck` block for automatic version detection (after stability)

---
Maintained by the release workflow: `.github/workflows/release-homebrew-binary.yml`.
