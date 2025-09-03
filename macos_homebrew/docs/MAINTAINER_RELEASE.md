# Maintainer Release Guide (Homebrew Binary Path)

## Prerequisites

* Tap repository created: `homebrew-mycli` (e.g. <https://github.com/naga-nandyala/homebrew-mycli>)
* This repository contains workflow `build-release-binaries` (copy from `macos_homebrew/workflow/release_binaries.yml`).
* Version updated in `src/mycli_app/__init__.py`.
* Git tag will follow `vX.Y.Z`.

## Steps

1. Update version constant:
   * Edit `src/mycli_app/__init__.py` `__version__ = "X.Y.Z"`.
   * Commit.

2. Tag & push:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

3. Wait for GitHub Actions to finish (it uploads release assets automatically):
   * Assets: `mycli-X.Y.Z-macos-arm64.tar.gz`, `mycli-X.Y.Z-macos-x86_64.tar.gz` (and `.sha256` files).

4. Compute / verify sha256 (already generated). If using a universal binary skip split arch formula.

5. In the tap repo:
   * Choose template: `mycli_split_arch.rb` or `mycli_universal.rb`.
   * Update `version`, `url`(s) and `sha256` placeholders.
   * Commit as `Formula/mycli.rb`.

6. Test end-to-end:

   ```bash
   brew uninstall mycli || true
   brew untap naga-nandyala/mycli || true
   brew tap naga-nandyala/mycli
   brew install mycli
   mycli --version
   ```

7. Publish instructions in main README (Install section).

## Optional: Universal Binary

After both arch builds:

```bash
   # On a mac with both binaries (rename them accordingly)
   lipo -create mycli-arm64 mycli-x86_64 -output mycli
   chmod +x mycli
   VERSION=X.Y.Z
   tar -czf mycli-${VERSION}-macos-universal.tar.gz mycli
   shasum -a 256 mycli-${VERSION}-macos-universal.tar.gz
```

Upload universal tarball, then use `mycli_universal.rb` template.

## Automating Tap Updates

Consider a separate workflow reacting to `release` event:

* Clone tap repo
* Download `.sha256` files
* Update formula using `sed` and commit
* Push PR / direct commit

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Binary blocked by Gatekeeper | Sign & notarize (not covered here) |
| "Bad CPU type" on Intel | Ensure Intel build (macos-13 runner) exists |
| Missing Azure auth libs | Rebuild with `MYCLI_WITH_AZURE=1` env var + updated spec |
| Formula hash mismatch | Redownload asset and recalc sha256 |

## Code Signing (Optional)

1. Import Developer ID cert in CI (secrets for cert + password).
2. Add step before packaging:

   ```bash
   codesign --force --options runtime --sign "Developer ID Application: YOUR NAME (TEAMID)" dist/mycli
   ```

3. Notarize using `xcrun notarytool submit` (requires API key secrets) then `xcrun stapler staple dist/mycli`.

---

Happy shipping! 🚀
