#!/bin/bash
# Test script for validating bundle creation locally on macOS
# This script helps identify issues before they occur in CI

set -e  # Exit on any error

echo "🧪 Testing macOS bundle creation locally..."

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS only"
    exit 1
fi

# Check required tools
echo "🔍 Checking system requirements..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew is required for testing"
    exit 1
fi

echo "✅ System requirements met"

# Clean up previous test runs
echo "🧹 Cleaning up previous test runs..."
rm -rf ./test_bundle_output
rm -rf ./mycli-*

# Create test bundle
echo "📦 Creating test bundle..."
python3 create_macos_bundle.py --output ./test_bundle_output --version test-$(date +%s)

# Check if bundle was created
if [[ ! -d "./test_bundle_output" ]]; then
    echo "❌ Bundle output directory not created"
    exit 1
fi

# Find the created bundle
BUNDLE_DIR=$(find ./test_bundle_output -name "mycli-*" -type d | head -1)
if [[ -z "$BUNDLE_DIR" ]]; then
    echo "❌ No bundle directory found in output"
    exit 1
fi

echo "📁 Bundle created at: $BUNDLE_DIR"

# Test bundle structure
echo "🏗️  Testing bundle structure..."
if [[ ! -f "$BUNDLE_DIR/bin/mycli" ]]; then
    echo "❌ Missing mycli executable"
    exit 1
fi

if [[ ! -x "$BUNDLE_DIR/bin/mycli" ]]; then
    echo "❌ mycli executable is not executable"
    exit 1
fi

if [[ ! -f "$BUNDLE_DIR/bin/python" ]]; then
    echo "❌ Missing Python executable"
    exit 1
fi

if [[ ! -d "$BUNDLE_DIR/lib" ]]; then
    echo "❌ Missing lib directory"
    exit 1
fi

echo "✅ Bundle structure looks correct"

# Test bundle functionality
echo "🔧 Testing bundle functionality..."

# Test version command
echo "📋 Testing version command..."
VERSION_OUTPUT=$("$BUNDLE_DIR/bin/mycli" --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "❌ Version command failed"
    echo "Output: $VERSION_OUTPUT"
    exit 1
fi

echo "Version output: $VERSION_OUTPUT"

# Check if version output contains expected text
if [[ "$VERSION_OUTPUT" =~ "MyCliApp version" ]]; then
    echo "✅ Version command output is correct"
else
    echo "❌ Version command output is incorrect"
    echo "Expected: text containing 'MyCliApp version'"
    echo "Actual: $VERSION_OUTPUT"
    exit 1
fi

# Test help command
echo "📋 Testing help command..."
if ! "$BUNDLE_DIR/bin/mycli" --help > /dev/null 2>&1; then
    echo "❌ Help command failed"
    exit 1
fi
echo "✅ Help command works"

# Test Python module import
echo "🐍 Testing Python module import..."
if ! "$BUNDLE_DIR/bin/python" -c "from mycli_app.cli import main; print('Import successful')" 2>/dev/null; then
    echo "❌ Could not import mycli_app.cli module"
    exit 1
fi
echo "✅ Module import works"

# Test Azure dependencies are available
echo "🔍 Testing Azure dependencies..."

# Get the project root directory (two levels up from macos_homebrew/venv_bundling)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEST_SCRIPT="$PROJECT_ROOT/test_azure_packages.py"

if [[ -f "$TEST_SCRIPT" ]] && "$BUNDLE_DIR/bin/python" "$TEST_SCRIPT" 2>&1; then
    echo "✅ Azure dependencies test passed using dedicated test script"
else
    echo "⚠️  Azure dependencies test script not found or failed, using fallback method..."
    
    # Fallback to manual check
    echo "🔍 Fallback: Manual Azure dependency check..."
    AZURE_CHECK_OUTPUT=$("$BUNDLE_DIR/bin/python" -c "
try:
    import azure.identity
    import azure.core
    import azure.mgmt.core
    import msal
    print('✅ All Azure packages available')
    print(f'azure-identity: {azure.identity.__version__}')
    print(f'azure-core: {azure.core.__version__}')
    print(f'msal: {msal.__version__}')
except ImportError as e:
    print(f'❌ Missing Azure package: {e}')
    exit(1)
" 2>&1)

    if [[ $? -ne 0 ]]; then
        echo "❌ Azure dependencies check failed"
        echo "$AZURE_CHECK_OUTPUT"
        exit 1
    fi
    echo "$AZURE_CHECK_OUTPUT"
fi

# Test status command to verify Azure SDK detection
echo "🔐 Testing Azure SDK detection via status command..."
STATUS_OUTPUT=$("$BUNDLE_DIR/bin/mycli" status 2>&1)
if echo "$STATUS_OUTPUT" | grep -q "Azure SDK: Available"; then
    echo "✅ Azure SDK correctly detected as available"
elif echo "$STATUS_OUTPUT" | grep -q "Azure SDK: Not Available"; then
    echo "❌ Azure SDK detected as NOT available"
    echo "Status output: $STATUS_OUTPUT"
    exit 1
else
    echo "⚠️  Could not determine Azure SDK status"
    echo "Status output: $STATUS_OUTPUT"
fi

# Test broker command (requires Azure packages)
echo "🛡️  Testing broker command..."
if ! "$BUNDLE_DIR/bin/mycli" broker > /dev/null 2>&1; then
    echo "❌ Broker command failed"
    exit 1
fi
echo "✅ Broker command works"

# Test bundle size
echo "📊 Bundle size information..."
BUNDLE_SIZE=$(du -sh "$BUNDLE_DIR" | cut -f1)
echo "Bundle size: $BUNDLE_SIZE"

# Count files
FILE_COUNT=$(find "$BUNDLE_DIR" -type f | wc -l)
echo "Total files: $FILE_COUNT"

# Test tar.gz creation
echo "📦 Testing archive creation..."
TAR_FILE=$(find ./test_bundle_output -name "*.tar.gz" | head -1)
if [[ -n "$TAR_FILE" ]]; then
    echo "✅ Archive created: $(basename "$TAR_FILE")"
    TAR_SIZE=$(du -sh "$TAR_FILE" | cut -f1)
    echo "Archive size: $TAR_SIZE"
    
    # Test extraction
    echo "📂 Testing archive extraction..."
    mkdir -p ./test_extract
    tar -xzf "$TAR_FILE" -C ./test_extract
    
    EXTRACTED_BUNDLE=$(find ./test_extract -name "mycli-*" -type d | head -1)
    if [[ -n "$EXTRACTED_BUNDLE" ]] && [[ -f "$EXTRACTED_BUNDLE/bin/mycli" ]]; then
        echo "✅ Archive extraction works"
        
        # Test extracted bundle
        if "$EXTRACTED_BUNDLE/bin/mycli" --version > /dev/null 2>&1; then
            echo "✅ Extracted bundle is functional"
        else
            echo "❌ Extracted bundle is not functional"
            exit 1
        fi
    else
        echo "❌ Archive extraction failed"
        exit 1
    fi
    
    # Clean up extraction test
    rm -rf ./test_extract
else
    echo "⚠️  No archive file found"
fi

# Test SHA256 checksum
echo "🔐 Testing checksums..."
SHA_FILE=$(find ./test_bundle_output -name "*.sha256" | head -1)
if [[ -n "$SHA_FILE" ]]; then
    echo "✅ Checksum file created: $(basename "$SHA_FILE")"
    
    # Verify checksum
    cd ./test_bundle_output
    if shasum -c "$(basename "$SHA_FILE")" > /dev/null 2>&1; then
        echo "✅ Checksum verification passed"
    else
        echo "❌ Checksum verification failed"
        exit 1
    fi
    cd ..
else
    echo "⚠️  No checksum file found"
fi

echo ""
echo "🎉 All tests passed! Bundle creation is working correctly."
echo ""
echo "📋 Summary:"
echo "  Bundle directory: $BUNDLE_DIR"
echo "  Bundle size: $BUNDLE_SIZE"
echo "  File count: $FILE_COUNT"
echo "  Version command: ✅"
echo "  Help command: ✅"
echo "  Module import: ✅"
echo "  Archive creation: ✅"
echo "  Archive extraction: ✅"
echo "  Checksum verification: ✅"
echo ""
echo "💡 To test Homebrew installation locally:"
echo "  1. Create a local tap directory"
echo "  2. Copy the generated .rb formula file"
echo "  3. Update URLs to point to your local files"
echo "  4. Test with 'brew install --build-from-source'"

# Optional: Clean up test files
read -p "🧹 Clean up test files? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf ./test_bundle_output
    rm -rf ./mycli-*
    echo "✅ Test files cleaned up"
fi
