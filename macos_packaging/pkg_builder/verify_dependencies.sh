#!/bin/bash
set -euo pipefail

# Verify MyCLI App .pkg Dependencies
# This script verifies that a MyCLI App installation has all required Azure dependencies

echo "🔍 MyCLI App Dependency Verification"
echo "=================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a Python package is installed
python_package_exists() {
    python3 -c "import $1" >/dev/null 2>&1
}

# Check if mycli is installed
echo "1. Checking MyCLI installation..."
if command_exists mycli; then
    echo "✅ mycli command found: $(which mycli)"
    
    # Test basic functionality
    if mycli --version >/dev/null 2>&1; then
        echo "✅ mycli version: $(mycli --version)"
    else
        echo "❌ mycli command failed"
        exit 1
    fi
else
    echo "❌ mycli command not found"
    exit 1
fi

# Get the Python executable used by mycli
echo ""
echo "2. Checking Python environment..."

# Find the actual mycli script
MYCLI_SCRIPT=$(which mycli)
if [[ -L "$MYCLI_SCRIPT" ]]; then
    MYCLI_SCRIPT=$(readlink "$MYCLI_SCRIPT")
fi

# Determine the Python environment
if [[ "$MYCLI_SCRIPT" == *"/usr/local/lib/mycli-app/"* ]]; then
    PYTHON_ENV="/usr/local/lib/mycli-app"
    PYTHON_EXEC="$PYTHON_ENV/bin/python"
    echo "✅ Using bundled Python environment: $PYTHON_ENV"
elif [[ "$MYCLI_SCRIPT" == *"/usr/local/bin/mycli"* ]]; then
    # Check if it's a launcher script
    if grep -q "MYCLI_HOME" "$MYCLI_SCRIPT" 2>/dev/null; then
        PYTHON_ENV="/usr/local/lib/mycli-app"
        PYTHON_EXEC="$PYTHON_ENV/bin/python"
        echo "✅ Using bundled Python environment via launcher: $PYTHON_ENV"
    else
        PYTHON_EXEC="python3"
        echo "✅ Using system Python: $(which python3)"
    fi
else
    PYTHON_EXEC="python3"
    echo "✅ Using system Python: $(which python3)"
fi

# Verify Python executable exists
if [[ -n "${PYTHON_ENV:-}" ]] && [[ ! -f "$PYTHON_EXEC" ]]; then
    echo "❌ Bundled Python not found: $PYTHON_EXEC"
    exit 1
fi

# Check core dependencies
echo ""
echo "3. Checking core dependencies..."

CORE_DEPS=("click" "colorama")
for dep in "${CORE_DEPS[@]}"; do
    if "$PYTHON_EXEC" -c "import $dep" >/dev/null 2>&1; then
        VERSION=$("$PYTHON_EXEC" -c "import $dep; print($dep.__version__)" 2>/dev/null || echo "unknown")
        echo "✅ $dep: $VERSION"
    else
        echo "❌ $dep: missing"
        exit 1
    fi
done

# Check Azure dependencies
echo ""
echo "4. Checking Azure dependencies..."

AZURE_DEPS=(
    "azure.core:azure-core"
    "azure.identity:azure-identity" 
    "azure.mgmt.core:azure-mgmt-core"
    "msal:msal"
)

MISSING_DEPS=()

for dep_spec in "${AZURE_DEPS[@]}"; do
    IFS=':' read -r module_name package_name <<< "$dep_spec"
    
    if "$PYTHON_EXEC" -c "import $module_name" >/dev/null 2>&1; then
        VERSION=$("$PYTHON_EXEC" -c "import $module_name; print(getattr($module_name, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        echo "✅ $package_name: $VERSION"
    else
        echo "❌ $package_name: missing"
        MISSING_DEPS+=("$package_name")
    fi
done

# Check broker authentication capability
echo ""
echo "5. Checking broker authentication support..."

if "$PYTHON_EXEC" -c "from msal.broker import BrokerTokenCache" >/dev/null 2>&1; then
    echo "✅ MSAL broker support: available"
else
    echo "❌ MSAL broker support: missing (msal[broker] not installed)"
    MISSING_DEPS+=("msal[broker]")
fi

# Test Azure authentication functionality
echo ""
echo "6. Testing Azure authentication functionality..."

AUTH_TEST_SCRIPT="
try:
    from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
    from azure.core.credentials import TokenCredential
    from msal import PublicClientApplication
    import msal.broker
    
    print('✅ Azure authentication imports successful')
    
    # Test credential creation (don't actually authenticate)
    try:
        cred = DefaultAzureCredential()
        print('✅ DefaultAzureCredential creation successful')
    except Exception as e:
        print(f'⚠️  DefaultAzureCredential creation warning: {e}')
    
    try:
        app = PublicClientApplication('fake-client-id')
        print('✅ MSAL PublicClientApplication creation successful')
    except Exception as e:
        print(f'❌ MSAL PublicClientApplication creation failed: {e}')
        
except ImportError as e:
    print(f'❌ Azure authentication import failed: {e}')
    exit(1)
"

if "$PYTHON_EXEC" -c "$AUTH_TEST_SCRIPT"; then
    echo "✅ Azure authentication test passed"
else
    echo "❌ Azure authentication test failed"
    MISSING_DEPS+=("azure-authentication")
fi

# Summary
echo ""
echo "7. Summary"
echo "=========="

if [[ ${#MISSING_DEPS[@]} -eq 0 ]]; then
    echo "🎉 All dependencies verified successfully!"
    echo ""
    echo "Your MyCLI App installation includes:"
    echo "  ✅ Core CLI functionality"
    echo "  ✅ Azure authentication support"
    echo "  ✅ Broker authentication support"
    echo "  ✅ Full Azure SDK integration"
    echo ""
    echo "Ready to use Azure features:"
    echo "  mycli login       # Interactive Azure login"
    echo "  mycli status      # Check authentication status"
    echo "  mycli --help      # Show all available commands"
else
    echo "❌ Missing dependencies detected!"
    echo ""
    echo "Missing packages:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo "This installation may not support full Azure functionality."
    echo "Consider reinstalling with Azure dependencies:"
    echo "  pip install mycli-app[azure,broker]"
    exit 1
fi

# Additional system info
echo ""
echo "8. System Information"
echo "===================="
echo "OS: $(uname -s) $(uname -r)"
echo "Architecture: $(uname -m)"
echo "Python version: $("$PYTHON_EXEC" --version)"
echo "Installation type: $([[ -n "${PYTHON_ENV:-}" ]] && echo "Bundled (.pkg)" || echo "System")"

if [[ -n "${PYTHON_ENV:-}" ]]; then
    echo "Bundle location: $PYTHON_ENV"
    echo "Bundle size: $(du -sh "$PYTHON_ENV" 2>/dev/null | cut -f1 || echo "unknown")"
fi

echo ""
echo "✅ Dependency verification complete!"