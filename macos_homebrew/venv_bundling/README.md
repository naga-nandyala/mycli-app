# macOS Virtual Environment Bundling

This directory contains tools for creating portable macOS bundles using Python virtual environments for Homebrew distribution.

## Overview

This approach creates a self-contained virtual environment bundle that includes all dependencies and can be distributed through Homebrew. Unlike PyInstaller, this method preserves the Python runtime environment and provides better compatibility with native libraries.

## Files

### `create_macos_bundle.py`
Main script for creating macOS-specific portable bundles.

**Features:**
- Creates portable virtual environments with all dependencies
- Architecture-specific builds (Intel x86_64 and Apple Silicon arm64)
- Homebrew-compatible packaging (tar.gz with SHA256 checksums)
- Automatic launcher script generation
- Bundle metadata and documentation generation
- Homebrew formula template creation

**Usage:**
```bash
python3 create_macos_bundle.py [options]
```

**Options:**
- `--output, -o`: Output directory for the bundle (default: ./dist)
- `--python-version`: Python version to use (e.g., 3.11, 3.12)
- `--arch`: Target architecture (x86_64 or arm64, default: current system)

**Examples:**
```bash
# Create bundle with default settings
python3 create_macos_bundle.py

# Create bundle for specific architecture
python3 create_macos_bundle.py --arch arm64

# Create bundle with custom output directory
python3 create_macos_bundle.py --output ./releases
```

### `test_bundle_creation.sh`
Test script for validating bundle creation locally on macOS.

**Features:**
- Validates macOS environment
- Tests bundle creation process
- Verifies bundle functionality
- Reports bundle size and structure

**Usage:**
```bash
./test_bundle_creation.sh
```

## Architecture Support

The bundling process supports both macOS architectures:

- **Intel (x86_64)**: Traditional Mac hardware
- **Apple Silicon (arm64)**: M1, M2, M3+ Macs

The script automatically detects the current architecture but can be forced to build for a specific target using the `--arch` flag.

## Bundle Contents

The created bundle includes:

```
mycli-{arch}/
├── bin/
│   ├── mycli              # Main executable launcher
│   ├── mycli-homebrew     # Homebrew-compatible symlink
│   ├── python             # Python interpreter
│   └── ...                # Other executables
├── lib/
│   └── python3.x/
│       └── site-packages/ # All dependencies
├── include/               # Header files (if needed)
├── share/                 # Shared resources
├── bundle_info.json       # Bundle metadata
├── README.md              # Bundle documentation
└── pyvenv.cfg            # Virtual environment config
```

## Distribution Files

The script creates several files for distribution:

1. **`mycli-{arch}-{version}-{arch}.tar.gz`**: Main bundle archive
2. **`mycli-{arch}-{version}-{arch}.tar.gz.sha256`**: SHA256 checksum
3. **`mycli.rb`**: Homebrew formula template
4. **`mycli-{arch}-structure.txt`**: Bundle structure information

## GitHub Actions Integration

This bundling method is designed to work with GitHub Actions. The workflow should:

1. Use macOS runners (both Intel and Apple Silicon)
2. Set up Python environment
3. Run the bundle creation script
4. Upload artifacts for release

Example workflow integration:
```yaml
- name: Create macOS Bundle
  run: |
    cd macos_homebrew/venv_bundling
    python3 create_macos_bundle.py --output ../../dist --arch ${{ matrix.arch }}
```

## Homebrew Integration

The created bundles are specifically designed for Homebrew distribution:

1. **Formula Template**: Auto-generated `mycli.rb` file
2. **SHA256 Checksums**: Required for Homebrew security
3. **Architecture Tags**: Proper arm64/x86_64 dependencies
4. **Installation Scripts**: Homebrew-compatible install procedures

## Advantages over PyInstaller

1. **Better Compatibility**: Preserves Python environment and native libraries
2. **Smaller Size**: Only includes necessary dependencies
3. **Faster Startup**: No unpacking/extraction overhead
4. **Debugging**: Easier to debug with standard Python tools
5. **Updates**: Individual packages can be updated if needed
6. **Native Integration**: Better macOS system integration

## Requirements

- **macOS**: Darwin-based system required
- **Python 3.8+**: Compatible Python installation
- **System Tools**: `sw_vers`, `shasum`, `tar` (standard on macOS)
- **Dependencies**: Listed in project's `requirements.txt`

## Testing

Before using in production:

1. Run local tests: `./test_bundle_creation.sh`
2. Test on both Intel and Apple Silicon Macs
3. Verify Homebrew formula compatibility
4. Test bundle functionality after installation

## Troubleshooting

### Common Issues

1. **Architecture Mismatch**: Ensure correct `--arch` flag for target systems
2. **Missing Dependencies**: Check `requirements.txt` completeness
3. **Path Issues**: Script adjusts paths automatically but verify launcher scripts
4. **Permissions**: Ensure executable permissions on launcher scripts

### Debug Mode

For debugging, you can:
1. Examine the temporary bundle before packaging
2. Check the bundle structure file
3. Test the launcher script manually
4. Verify Python environment activation

## Comparison with PyInstaller

| Feature | venv Bundling | PyInstaller |
|---------|---------------|-------------|
| Bundle Size | Smaller | Larger |
| Startup Time | Fast | Slower (extraction) |
| Debugging | Easy | Difficult |
| Compatibility | High | Medium |
| Native Libraries | Better | Can be problematic |
| Distribution | Homebrew-ready | Generic |

## Future Enhancements

Potential improvements:
1. **Universal Binaries**: Support for universal macOS binaries
2. **Code Signing**: Integration with Apple's code signing
3. **Notarization**: Apple notarization support
4. **Incremental Updates**: Delta updates for efficiency
5. **Multiple Versions**: Side-by-side version support
