#!/bin/bash
# Quick build script for MyCliApp macOS distributions
#
# Usage:
#   ./build_macos.sh                    # Build all distributions
#   ./build_macos.sh zip               # Build only ZIP
#   ./build_macos.sh app               # Build only app bundle
#   ./build_macos.sh dmg               # Build only DMG
#   ./build_macos.sh pkg               # Build only PKG
#   ./build_macos.sh 1.2.0             # Build all with specific version
#   ./build_macos.sh zip 1.2.0         # Build ZIP with specific version

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root (assumes script is in packaging/macos/)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/../.."

echo -e "${BLUE}MyCliApp macOS Distribution Builder${NC}"
echo "======================================"

# Check if we're on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    echo -e "${RED}Error: This script must be run on macOS${NC}"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not found${NC}"
    echo "Install with: brew install python@3.12"
    exit 1
fi

# Parse arguments
BUILD_TYPE="all"
VERSION=""

if [[ $# -ge 1 ]]; then
    if [[ "$1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        # First argument is a version number
        VERSION="$1"
    elif [[ "$1" =~ ^(zip|app|dmg|pkg|all)$ ]]; then
        # First argument is a build type
        BUILD_TYPE="$1"
        if [[ $# -ge 2 && "$2" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
            VERSION="$2"
        fi
    else
        echo -e "${RED}Error: Invalid argument '$1'${NC}"
        echo "Usage: $0 [zip|app|dmg|pkg|all] [version]"
        exit 1
    fi
fi

echo "Build Type: ${BUILD_TYPE}"
if [[ -n "$VERSION" ]]; then
    echo "Version: ${VERSION}"
else
    echo "Version: auto-detected"
fi

# Navigate to project root
cd "$PROJECT_ROOT"

# Check if build script exists
BUILD_SCRIPT="packaging/macos/build_macos.py"
if [[ ! -f "$BUILD_SCRIPT" ]]; then
    echo -e "${RED}Error: Build script not found: $BUILD_SCRIPT${NC}"
    exit 1
fi

# Prepare build command
BUILD_CMD="python3 $BUILD_SCRIPT --type $BUILD_TYPE"
if [[ -n "$VERSION" ]]; then
    BUILD_CMD="$BUILD_CMD --version $VERSION"
fi

echo ""
echo -e "${BLUE}Starting build...${NC}"
echo "Command: $BUILD_CMD"
echo ""

# Run the build
if eval "$BUILD_CMD"; then
    echo ""
    echo -e "${GREEN}✅ Build completed successfully!${NC}"
    echo ""
    echo "Output directory: dist_macos/"
    echo ""
    echo "To install:"
    if [[ "$BUILD_TYPE" == "app" || "$BUILD_TYPE" == "all" ]]; then
        echo -e "${YELLOW}App Bundle:${NC} cp -R dist_macos/MyCliApp.app /Applications/"
    fi
    if [[ "$BUILD_TYPE" == "dmg" || "$BUILD_TYPE" == "all" ]]; then
        echo -e "${YELLOW}DMG:${NC} Double-click the .dmg file in dist_macos/"
    fi
    if [[ "$BUILD_TYPE" == "pkg" || "$BUILD_TYPE" == "all" ]]; then
        echo -e "${YELLOW}PKG:${NC} Double-click the .pkg file and follow installer"
    fi
    if [[ "$BUILD_TYPE" == "zip" || "$BUILD_TYPE" == "all" ]]; then
        echo -e "${YELLOW}ZIP:${NC} Extract and run: bin/mycli.sh --help"
    fi
else
    echo ""
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi
