# macOS Installation Guide for mycli

## Issue: "Not Trusted" Error

When you download the binary from GitHub releases, macOS will block it due to security restrictions. Here's how to fix it:

### Method 1: Remove Quarantine Attribute (Recommended)

1. **Download and extract** the `.tar.gz` file to a folder (e.g., `~/Downloads/mycli`)

2. **Open Terminal** and navigate to the extracted folder:
   ```bash
   cd ~/Downloads/mycli
   ```

3. **Remove the quarantine attribute** from all files:
   ```bash
   sudo xattr -r -d com.apple.quarantine .
   ```

4. **Make the binary executable**:
   ```bash
   chmod +x mycli/mycli
   ```

5. **Test the binary**:
   ```bash
   ./mycli/mycli --help
   ```

6. **Optional: Add to PATH** for system-wide access:
   ```bash
   # Copy to /usr/local/bin
   sudo cp mycli/mycli /usr/local/bin/
   
   # Or add current directory to PATH
   echo 'export PATH="$PATH:$(pwd)/mycli"' >> ~/.zshrc
   source ~/.zshrc
   ```

### Method 2: System Preferences Approach

1. **Try to run the binary** - macOS will show a security warning
2. **Go to System Preferences > Security & Privacy**
3. **Click "Allow Anyway"** for the mycli application
4. **Try running again** - click "Open" when prompted

### Method 3: Developer Override

If you're comfortable with developer tools:

```bash
# Sign the binary with ad-hoc signature
codesign --force --deep --sign - mycli/mycli

# Then run normally
./mycli/mycli --help
```

## Verification

After following any method above, you should be able to run:

```bash
./mycli/mycli --version
./mycli/mycli --help
```

## Troubleshooting

If you still get permission errors:

1. **Check file permissions**:
   ```bash
   ls -la mycli/mycli
   ```

2. **Verify quarantine removal**:
   ```bash
   xattr mycli/mycli
   # Should show no com.apple.quarantine attribute
   ```

3. **Check for other security restrictions**:
   ```bash
   spctl -a -v mycli/mycli
   ```

## Architecture Notes

- **Intel Macs**: Use the `x86_64` version
- **Apple Silicon (M1/M2/M3)**: Use the `arm64` version
- **Universal**: The build creates both architectures

If you're unsure of your architecture:
```bash
uname -m
# x86_64 = Intel
# arm64 = Apple Silicon
```
