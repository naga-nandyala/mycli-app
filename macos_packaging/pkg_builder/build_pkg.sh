#!/bin/bash
set -euo pipefail

# Build macOS .pkg installer for MyCLI App
# This script creates a proper macOS installer package
# Version: 4.0 - Enhanced postinstall shebang fixing with debugging (Sept 23, 2025)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VERSION="${1:-1.0.0}"
ARCH="${2:-$(uname -m)}"

echo "🏗️  Building .pkg installer for MyCLI App"
echo "Version: $VERSION"
echo "Architecture: $ARCH"
echo "Script directory: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"

# Create temporary build directory
BUILD_DIR="$PROJECT_ROOT/build/pkg"
PAYLOAD_DIR="$BUILD_DIR/payload"
SCRIPTS_DIR="$BUILD_DIR/scripts"
PKG_DIR="$BUILD_DIR/pkg"

echo "📁 Setting up build directories..."
rm -rf "$BUILD_DIR"
mkdir -p "$PAYLOAD_DIR"
mkdir -p "$SCRIPTS_DIR"
mkdir -p "$PKG_DIR"

# Create the payload directory structure
echo "📦 Creating payload structure..."
mkdir -p "$PAYLOAD_DIR/usr/local/bin"
mkdir -p "$PAYLOAD_DIR/usr/local/lib/mycli-app"

# Copy the mycli application (assuming venv bundle approach)
VENV_BUNDLE_PATH="$PROJECT_ROOT/build/mycli-$ARCH"
echo "🔍 Looking for venv bundle at: $VENV_BUNDLE_PATH"
if [[ -d "$VENV_BUNDLE_PATH" ]]; then
    echo "📋 Copying venv bundle from: $VENV_BUNDLE_PATH"
    cp -r "$VENV_BUNDLE_PATH"/* "$PAYLOAD_DIR/usr/local/lib/mycli-app/"
    
    # Verify Azure dependencies in the bundle
    echo "🔍 Verifying Azure dependencies in bundle..."
    if [[ -f "$VENV_BUNDLE_PATH/pyvenv.cfg" ]]; then
        source "$VENV_BUNDLE_PATH/bin/activate"
        pip list | grep -E "(azure|msal)" && echo "✅ Azure dependencies found" || echo "⚠️  Azure dependencies missing"
        deactivate
    fi
    
    # Create symlink script in /usr/local/bin
    cat > "$PAYLOAD_DIR/usr/local/bin/mycli" << 'EOF'
#!/bin/bash
# MyCLI App launcher script
MYCLI_HOME="/usr/local/lib/mycli-app"
exec "$MYCLI_HOME/bin/mycli" "$@"
EOF
    chmod +x "$PAYLOAD_DIR/usr/local/bin/mycli"
else
    echo "❌ Venv bundle not found at: $VENV_BUNDLE_PATH"
    echo "Creating venv bundle with Azure dependencies..."
    
    # Verify pyproject.toml exists
    if [[ ! -f "$PROJECT_ROOT/pyproject.toml" ]]; then
        echo "❌ pyproject.toml not found at: $PROJECT_ROOT/pyproject.toml"
        exit 1
    fi
    
    # Create the venv bundle
    python3 -m venv "$VENV_BUNDLE_PATH"
    source "$VENV_BUNDLE_PATH/bin/activate"
    
    # Install the package with Azure dependencies
    pip install --upgrade pip
    pip install -e "$PROJECT_ROOT[azure,broker]"
    
    # Verify installation
    if ! mycli --version >/dev/null 2>&1; then
        echo "❌ Failed to install mycli with Azure dependencies"
        exit 1
    fi
    
    echo "✅ Created venv bundle with Azure dependencies"
    deactivate
    
    # Now copy the bundle
    cp -r "$VENV_BUNDLE_PATH"/* "$PAYLOAD_DIR/usr/local/lib/mycli-app/"
    
    # Fix shebang lines to use the target installation paths
    echo "🔧 Fixing shebang lines for portability..."
    find "$PAYLOAD_DIR/usr/local/lib/mycli-app/bin" -type f -executable | while read -r file; do
        if head -1 "$file" | grep -q "^#!.*python"; then
            echo "Fixing shebang in: $(basename "$file")"
            # Replace the first line with a portable shebang
            sed -i '' '1s|^#!.*python.*|#!/usr/local/lib/mycli-app/bin/python3|' "$file"
        fi
    done
    
    # Also fix any pth files that might have absolute paths
    find "$PAYLOAD_DIR/usr/local/lib/mycli-app" -name "*.pth" | while read -r pth_file; do
        if [[ -f "$pth_file" ]]; then
            echo "Fixing paths in: $(basename "$pth_file")"
            # Replace absolute paths with relative paths
            sed -i '' "s|$VENV_BUNDLE_PATH|/usr/local/lib/mycli-app|g" "$pth_file"
        fi
    done
    
    # Clean up Python cache files that might contain absolute paths
    echo "🧹 Cleaning up Python cache files..."
    find "$PAYLOAD_DIR/usr/local/lib/mycli-app" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$PAYLOAD_DIR/usr/local/lib/mycli-app" -name "*.pyc" -type f -delete 2>/dev/null || true
    find "$PAYLOAD_DIR/usr/local/lib/mycli-app" -name "*.pyo" -type f -delete 2>/dev/null || true
    
    echo "✅ Fixed shebang lines and paths for target installation"
    
    # Create symlink script in /usr/local/bin
    cat > "$PAYLOAD_DIR/usr/local/bin/mycli" << 'EOF'
#!/bin/bash
# MyCLI App launcher script
MYCLI_HOME="/usr/local/lib/mycli-app"
exec "$MYCLI_HOME/bin/mycli" "$@"
EOF
    chmod +x "$PAYLOAD_DIR/usr/local/bin/mycli"
    
    # Verify the mycli script works with the fixed paths
    echo "🧪 Verifying mycli script..."
    if [[ -f "$PAYLOAD_DIR/usr/local/lib/mycli-app/bin/python3" ]]; then
        echo "✅ Python interpreter found at target location"
        
        # Test that the fixed mycli script can at least try to run
        # (We can't fully test it since we're not in the target environment)
        if grep -q "#!/usr/local/lib/mycli-app/bin/python3" "$PAYLOAD_DIR/usr/local/lib/mycli-app/bin/mycli"; then
            echo "✅ mycli shebang correctly fixed"
        else
            echo "⚠️  mycli shebang may not be fixed properly"
        fi
    else
        echo "❌ Python interpreter not found in expected location"
        echo "Available files in bin directory:"
        ls -la "$PAYLOAD_DIR/usr/local/lib/mycli-app/bin/" || echo "Bin directory not found"
        exit 1
    fi
fi

# Create preinstall script
cat > "$SCRIPTS_DIR/preinstall" << 'EOF'
#!/bin/bash
# Preinstall script for MyCLI App

echo "📋 MyCLI App: Preparing installation..."

# Remove any existing installation
if [[ -f "/usr/local/bin/mycli" ]]; then
    echo "📋 Removing existing MyCLI installation..."
    rm -f "/usr/local/bin/mycli"
fi

if [[ -d "/usr/local/lib/mycli-app" ]]; then
    echo "📋 Removing existing MyCLI library..."
    rm -rf "/usr/local/lib/mycli-app"
fi

exit 0
EOF

# Create postinstall script
cat > "$SCRIPTS_DIR/postinstall" << 'EOF'
#!/bin/bash
# Postinstall script for MyCLI App
# Updated with Python virtual environment portability fixes

echo "📋 MyCLI App: Completing installation..."

# Ensure proper permissions
chown -R root:wheel "/usr/local/lib/mycli-app"
chmod -R 755 "/usr/local/lib/mycli-app"
chmod +x "/usr/local/bin/mycli"

# Fix shebang lines AFTER installation to ensure proper paths
echo "🔧 Fixing shebang lines for installed environment..."
find "/usr/local/lib/mycli-app/bin" -type f -executable | while read -r file; do
    if head -1 "$file" | grep -q "^#!.*python"; then
        echo "Fixing shebang in: $(basename "$file")"
        echo "Original shebang: $(head -1 "$file")"
        # Replace the first line with the correct installed path - more aggressive approach
        sed -i '' '1c\
#!/usr/local/lib/mycli-app/bin/python3' "$file"
        echo "New shebang: $(head -1 "$file")"
    fi
done

# Also specifically fix the main mycli script
if [[ -f "/usr/local/lib/mycli-app/bin/mycli" ]]; then
    echo "🎯 Specifically fixing main mycli script..."
    echo "Original shebang: $(head -1 /usr/local/lib/mycli-app/bin/mycli)"
    sed -i '' '1c\
#!/usr/local/lib/mycli-app/bin/python3' "/usr/local/lib/mycli-app/bin/mycli"
    echo "New shebang: $(head -1 /usr/local/lib/mycli-app/bin/mycli)"
fi

# Fix any .pth files that might have build paths
find "/usr/local/lib/mycli-app" -name "*.pth" | while read -r pth_file; do
    if [[ -f "$pth_file" ]]; then
        echo "Fixing paths in: $(basename "$pth_file")"
        # Replace any remaining absolute build paths with installation paths
        sed -i '' 's|/Users/runner/work/mycli-app/mycli-app/build/[^/]*/|/usr/local/lib/mycli-app/|g' "$pth_file"
        sed -i '' 's|/tmp/[^/]*/mycli-[^/]*/|/usr/local/lib/mycli-app/|g' "$pth_file"
    fi
done

# Clean and regenerate Python cache files
echo "🧹 Cleaning Python cache files..."
find "/usr/local/lib/mycli-app" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "/usr/local/lib/mycli-app" -name "*.pyc" -type f -delete 2>/dev/null || true

# Regenerate Python bytecode for the target environment
echo "🔄 Regenerating Python bytecode..."
if [[ -f "/usr/local/lib/mycli-app/bin/python3" ]]; then
    "/usr/local/lib/mycli-app/bin/python3" -m compileall "/usr/local/lib/mycli-app/lib/python3.12/site-packages/" 2>/dev/null || true
    echo "✅ Python bytecode regenerated"
else
    echo "⚠️  Python interpreter not found, skipping bytecode regeneration"
fi

# Test installation
echo "🧪 Testing installation..."
echo "Debug: About to test /usr/local/bin/mycli --version"
echo "Debug: Launcher script content:"
cat /usr/local/bin/mycli
echo "Debug: mycli script shebang:"
head -1 /usr/local/lib/mycli-app/bin/mycli
echo "Debug: Python interpreter exists: $(test -f /usr/local/lib/mycli-app/bin/python3 && echo 'Yes' || echo 'No')"

if /usr/local/bin/mycli --version >/dev/null 2>&1; then
    echo "✅ MyCLI App installed successfully!"
    
    # Show version info
    echo "Installed version: $(/usr/local/bin/mycli --version)"
else
    echo "⚠️  MyCLI App installation may have issues"
    echo "Debugging info:"
    echo "- Launcher script exists: $(test -f /usr/local/bin/mycli && echo 'Yes' || echo 'No')"
    echo "- Python interpreter exists: $(test -f /usr/local/lib/mycli-app/bin/python3 && echo 'Yes' || echo 'No')"
    echo "- mycli script exists: $(test -f /usr/local/lib/mycli-app/bin/mycli && echo 'Yes' || echo 'No')"
    if [[ -f "/usr/local/lib/mycli-app/bin/mycli" ]]; then
        echo "- mycli shebang: $(head -1 /usr/local/lib/mycli-app/bin/mycli)"
    fi
    echo "- Testing mycli script directly:"
    /usr/local/lib/mycli-app/bin/mycli --version 2>&1 || echo "Direct execution failed"
fi

echo ""
echo "🎉 MyCLI App installation complete!"
echo ""
echo "Usage:"
echo "  mycli --help      # Show help"
echo "  mycli --version   # Show version"
echo "  mycli login       # Login to Azure"
echo "  mycli status      # Check status"
echo ""

exit 0
EOF

# Create uninstall script (optional)
cat > "$PAYLOAD_DIR/usr/local/bin/mycli-uninstall.sh" << 'EOF'
#!/bin/bash
# Uninstall script for MyCLI App

echo "🗑️  Uninstalling MyCLI App..."

# Remove binary
if [[ -f "/usr/local/bin/mycli" ]]; then
    rm -f "/usr/local/bin/mycli"
    echo "✅ Removed /usr/local/bin/mycli"
fi

# Remove library
if [[ -d "/usr/local/lib/mycli-app" ]]; then
    rm -rf "/usr/local/lib/mycli-app"
    echo "✅ Removed /usr/local/lib/mycli-app"
fi

# Remove verification script
if [[ -f "/usr/local/bin/mycli-verify-dependencies.sh" ]]; then
    rm -f "/usr/local/bin/mycli-verify-dependencies.sh"
    echo "✅ Removed dependency verification script"
fi

# Remove this uninstall script
rm -f "/usr/local/bin/mycli-uninstall.sh"

echo "✅ MyCLI App uninstalled successfully!"
EOF

# Create dependency verification script
cp "$PROJECT_ROOT/macos_packaging/pkg_builder/verify_dependencies.sh" "$PAYLOAD_DIR/usr/local/bin/mycli-verify-dependencies.sh"

chmod +x "$SCRIPTS_DIR/preinstall"
chmod +x "$SCRIPTS_DIR/postinstall"
chmod +x "$PAYLOAD_DIR/usr/local/bin/mycli-uninstall.sh"
chmod +x "$PAYLOAD_DIR/usr/local/bin/mycli-verify-dependencies.sh"

# Build the package
PKG_NAME="mycli-app-$VERSION-$ARCH.pkg"
PKG_PATH="$PKG_DIR/$PKG_NAME"

echo "🔨 Building .pkg installer..."
pkgbuild \
    --root "$PAYLOAD_DIR" \
    --scripts "$SCRIPTS_DIR" \
    --identifier "com.nagarnandyala.mycli-app" \
    --version "$VERSION" \
    --install-location "/" \
    "$PKG_PATH"

echo "📋 Package info:"
echo "Name: $PKG_NAME"
echo "Path: $PKG_PATH"
echo "Size: $(du -h "$PKG_PATH" | cut -f1)"

# Calculate SHA256
echo "🔐 Calculating SHA256..."
SHA256=$(shasum -a 256 "$PKG_PATH" | cut -d' ' -f1)
echo "SHA256: $SHA256"

# Copy to project root for easy access
cp "$PKG_PATH" "$PROJECT_ROOT/$PKG_NAME"
echo "✅ Package copied to: $PROJECT_ROOT/$PKG_NAME"

# Create a cask template with the actual SHA256
CASK_TEMPLATE="$PROJECT_ROOT/_scratch_brew/cask_mycli-app-pkg-generated.rb"
sed "s/TBD_PKG_SHA256/$SHA256/g" "$PROJECT_ROOT/_scratch_brew/cask_mycli-app-pkg.rb" > "$CASK_TEMPLATE"
echo "✅ Generated cask template: $CASK_TEMPLATE"

echo ""
echo "🎉 .pkg installer build complete!"
echo ""
echo "To test the package:"
echo "  sudo installer -pkg '$PROJECT_ROOT/$PKG_NAME' -target /"
echo ""
echo "To test with Homebrew (after uploading to GitHub releases):"
echo "  brew install --cask mycli-app-pkg"
echo ""
echo "To uninstall:"
echo "  sudo mycli-uninstall.sh"
echo ""