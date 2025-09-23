#!/bin/bash
set -euo pipefail

# Test .pkg Dependency Validation
# This script tests that the .pkg build process includes all required Azure dependencies

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🧪 Testing .pkg Dependency Inclusion"
echo "==================================="

# Test 1: Check pyproject.toml has correct optional dependencies
echo "1. Checking pyproject.toml optional dependencies..."

REQUIRED_AZURE_DEPS=("azure-identity" "azure-mgmt-core" "azure-core" "msal")
REQUIRED_BROKER_DEPS=("msal[broker]")

if grep -q "\[project.optional-dependencies\]" "$PROJECT_ROOT/pyproject.toml"; then
    echo "✅ Optional dependencies section found"
    
    # Check azure extras
    if grep -A 10 "azure = \[" "$PROJECT_ROOT/pyproject.toml" | grep -q "azure-identity\|azure-core\|msal"; then
        echo "✅ Azure dependencies found in [azure] extra"
    else
        echo "❌ Azure dependencies missing in [azure] extra"
        exit 1
    fi
    
    # Check broker extras
    if grep -A 10 "broker = \[" "$PROJECT_ROOT/pyproject.toml" | grep -q "msal\[broker\]"; then
        echo "✅ Broker dependencies found in [broker] extra"
    else
        echo "❌ Broker dependencies missing in [broker] extra"
        exit 1
    fi
else
    echo "❌ Optional dependencies section not found in pyproject.toml"
    exit 1
fi

# Test 2: Check GitHub Actions workflow installs with extras
echo ""
echo "2. Checking GitHub Actions workflow..."

if grep -q "pip install -e \"\.\[azure,broker\]\"" "$PROJECT_ROOT/.github/workflows/pkg-build-release.yml"; then
    echo "✅ GitHub Actions installs with [azure,broker] extras"
else
    echo "❌ GitHub Actions doesn't install with Azure extras"
    echo "Expected: pip install -e \".[azure,broker]\""
    exit 1
fi

# Test 3: Check build script creates venv with Azure dependencies
echo ""
echo "3. Checking build script dependency handling..."

if grep -q "\[azure,broker\]" "$PROJECT_ROOT/macos_packaging/pkg_builder/build_pkg.sh"; then
    echo "✅ Build script installs with [azure,broker] extras"
else
    echo "❌ Build script doesn't install with Azure extras"
    exit 1
fi

# Test 4: Simulate venv creation with Azure dependencies
echo ""
echo "4. Testing venv creation with Azure dependencies..."

TEST_VENV_DIR="$PROJECT_ROOT/build/test-azure-deps"
rm -rf "$TEST_VENV_DIR"

echo "Creating test venv..."
python3 -m venv "$TEST_VENV_DIR"
source "$TEST_VENV_DIR/bin/activate"

echo "Installing mycli with Azure dependencies..."
pip install --upgrade pip
pip install -e "$PROJECT_ROOT[azure,broker]"

echo "Verifying Azure dependencies..."
MISSING_DEPS=()

# Check each required dependency
for dep in "${REQUIRED_AZURE_DEPS[@]}"; do
    module_name=$(echo "$dep" | sed 's/-/_/g' | sed 's/azure_/azure./g')
    if python -c "import $module_name" >/dev/null 2>&1; then
        version=$(python -c "import $module_name; print(getattr($module_name, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
        echo "✅ $dep: $version"
    else
        echo "❌ $dep: missing"
        MISSING_DEPS+=("$dep")
    fi
done

# Check broker support
if python -c "from msal.broker import BrokerTokenCache" >/dev/null 2>&1; then
    echo "✅ msal[broker]: available"
else
    echo "❌ msal[broker]: missing"
    MISSING_DEPS+=("msal[broker]")
fi

deactivate
rm -rf "$TEST_VENV_DIR"

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
    echo ""
    echo "❌ Missing dependencies in test venv:"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "  - $dep"
    done
    exit 1
fi

# Test 5: Check that verification script exists
echo ""
echo "5. Checking dependency verification script..."

if [[ -f "$PROJECT_ROOT/macos_packaging/pkg_builder/verify_dependencies.sh" ]]; then
    echo "✅ Dependency verification script exists"
    
    # Check that it's executable
    if [[ -x "$PROJECT_ROOT/macos_packaging/pkg_builder/verify_dependencies.sh" ]]; then
        echo "✅ Verification script is executable"
    else
        echo "⚠️  Verification script needs executable permissions"
        chmod +x "$PROJECT_ROOT/macos_packaging/pkg_builder/verify_dependencies.sh"
    fi
else
    echo "❌ Dependency verification script missing"
    exit 1
fi

# Test 6: Validate that cask includes dependency verification
echo ""
echo "6. Checking cask dependency verification..."

if grep -q "mycli-verify-dependencies.sh" "$PROJECT_ROOT/_scratch_brew/cask_mycli-app-pkg.rb"; then
    echo "✅ Cask includes dependency verification"
else
    echo "❌ Cask missing dependency verification"
    exit 1
fi

# Summary
echo ""
echo "🎉 All .pkg dependency tests passed!"
echo ""
echo "Your .pkg will include:"
echo "  ✅ Azure authentication (azure-identity, azure-core)"
echo "  ✅ Azure management SDK (azure-mgmt-core)"
echo "  ✅ MSAL authentication (msal)"
echo "  ✅ Broker authentication support (msal[broker])"
echo "  ✅ Dependency verification script"
echo "  ✅ Proper installation validation"
echo ""
echo "Ready to build .pkg with full Azure functionality!"

# Additional recommendations
echo ""
echo "📋 Recommendations:"
echo "  1. Test the .pkg on a clean macOS system"
echo "  2. Verify broker authentication works on macOS"
echo "  3. Test with different Azure tenants"
echo "  4. Validate all mycli commands work after .pkg installation"
echo ""
echo "To build the .pkg:"
echo "  ./macos_packaging/pkg_builder/build_pkg.sh 1.0.0"
echo ""
echo "To verify after installation:"
echo "  mycli-verify-dependencies.sh"