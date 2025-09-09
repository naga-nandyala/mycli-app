# Windows Bundle Creation Script for MyCLI
# PowerShell wrapper for easy execution

param(
    [string]$OutputDir = ".\dist\windows",
    [string]$Version = "1.0.0",
    [string]$Architecture = "",
    [switch]$Test = $false,
    [switch]$Help = $false
)

if ($Help) {
    Write-Host "Windows Bundle Creation for MyCLI" -ForegroundColor Cyan
    Write-Host "===================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\create_bundle.ps1 [options]"
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -OutputDir <path>    Output directory (default: .\dist\windows)"
    Write-Host "  -Version <version>   Package version (default: 1.0.0)"
    Write-Host "  -Architecture <arch> Target architecture (AMD64, x86, ARM64)"
    Write-Host "  -Test               Run test bundle creation"
    Write-Host "  -Help               Show this help"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\create_bundle.ps1"
    Write-Host "  .\create_bundle.ps1 -Version 2.0.0 -Architecture AMD64"
    Write-Host "  .\create_bundle.ps1 -Test"
    exit 0
}

$ErrorActionPreference = "Stop"

Write-Host "🪟 Windows Bundle Creation for MyCLI" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan

# Get script directory and paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$BundleScript = Join-Path $ScriptDir "create_windows_bundle.py"
$TestScript = Join-Path $ScriptDir "test_bundle_creation.py"

Write-Host "📁 Project root: $ProjectRoot" -ForegroundColor Green
Write-Host "📁 Script directory: $ScriptDir" -ForegroundColor Green

# Check if we're on Windows
if ($env:OS -ne "Windows_NT") {
    Write-Host "❌ This script must be run on Windows" -ForegroundColor Red
    exit 1
}

# Check if Python is available
try {
    $PythonVersion = python --version 2>&1
    Write-Host "🐍 $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  No virtual environment detected" -ForegroundColor Yellow
    Write-Host "💡 Recommendation: Activate .venv first:" -ForegroundColor Blue
    Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor Blue
    Write-Host ""
    
    # Try to activate venv if it exists
    $VenvActivate = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"
    if (Test-Path $VenvActivate) {
        Write-Host "🔄 Found .venv, attempting to activate..." -ForegroundColor Blue
        try {
            & $VenvActivate
            Write-Host "✅ Virtual environment activated" -ForegroundColor Green
        } catch {
            Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
            Write-Host "Please activate manually: $VenvActivate" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "❌ No .venv found at: $VenvActivate" -ForegroundColor Red
        Write-Host "Please create virtual environment first:" -ForegroundColor Yellow
        Write-Host "   python -m venv .venv" -ForegroundColor Yellow
        Write-Host "   .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
        Write-Host "   pip install -e .[azure,broker]" -ForegroundColor Yellow
        exit 1
    }
}

# Check if mycli is installed
Write-Host "🔍 Checking if mycli_app is installed..." -ForegroundColor Blue
try {
    python -c "import mycli_app.cli; print('OK')" 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ mycli_app is installed" -ForegroundColor Green
    } else {
        throw "Import failed"
    }
} catch {
    Write-Host "❌ mycli_app not found. Install with:" -ForegroundColor Red
    Write-Host "   pip install -e .[azure,broker]" -ForegroundColor Yellow
    exit 1
}

# Run test if requested
if ($Test) {
    Write-Host "🧪 Running test bundle creation..." -ForegroundColor Blue
    
    if (-not (Test-Path $TestScript)) {
        Write-Host "❌ Test script not found: $TestScript" -ForegroundColor Red
        exit 1
    }
    
    try {
        python $TestScript
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Test completed successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ Test failed with exit code: $LASTEXITCODE" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Error running test: $_" -ForegroundColor Red
        exit 1
    }
    
    exit 0
}

# Check if bundle script exists
if (-not (Test-Path $BundleScript)) {
    Write-Host "❌ Bundle script not found: $BundleScript" -ForegroundColor Red
    exit 1
}

# Create output directory
$OutputPath = Join-Path $ProjectRoot $OutputDir
Write-Host "📂 Output directory: $OutputPath" -ForegroundColor Green

try {
    New-Item -ItemType Directory -Path $OutputPath -Force | Out-Null
} catch {
    Write-Host "❌ Failed to create output directory: $_" -ForegroundColor Red
    exit 1
}

# Build command arguments
$BundleArgs = @(
    $BundleScript,
    "--output", $OutputPath,
    "--version", $Version
)

if ($Architecture) {
    $BundleArgs += @("--arch", $Architecture)
}

# Run the bundle creation script
Write-Host "🚀 Running bundle creation..." -ForegroundColor Blue
Write-Host "Command: python $($BundleArgs -join ' ')" -ForegroundColor Gray

try {
    Push-Location $ProjectRoot
    
    python @BundleArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Bundle creation completed successfully!" -ForegroundColor Green
        
        # List created files
        Write-Host "📋 Files created in ${OutputPath}:" -ForegroundColor Blue
        Get-ChildItem $OutputPath | ForEach-Object {
            if ($_.PSIsContainer) {
                Write-Host "   📁 $($_.Name)/" -ForegroundColor Yellow
            } else {
                $SizeMB = [math]::Round($_.Length / 1MB, 1)
                Write-Host "   📄 $($_.Name) ($SizeMB MB)" -ForegroundColor White
            }
        }
        
        # Show next steps
        Write-Host ""
        Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
        Write-Host "1. Extract and test the ZIP bundle" -ForegroundColor White
        Write-Host "2. Try running the bundled mycli:" -ForegroundColor White
        Write-Host "   - Extract the ZIP file" -ForegroundColor Gray
        Write-Host "   - Run: extracted_bundle\Scripts\mycli.bat --help" -ForegroundColor Gray
        Write-Host "3. Test Chocolatey package (if desired)" -ForegroundColor White
        Write-Host "4. Test Windows installer (if desired)" -ForegroundColor White
        
    } else {
        Write-Host "❌ Bundle creation failed with exit code: $LASTEXITCODE" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "❌ Error running bundle script: $_" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
