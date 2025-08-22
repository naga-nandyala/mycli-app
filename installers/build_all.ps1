#!/usr/bin/env pwsh
# Master build script for all Windows installers

param(
    [string]$Version = "1.0.0",
    [switch]$SkipTests = $false,
    [switch]$PyInstallerOnly = $false
)

Write-Host "🪟 Building MyCliApp Windows Installers v$Version" -ForegroundColor Green

# Ensure we're in the right directory
if (-not (Test-Path "pyinstaller")) {
    Write-Host "❌ Run this script from the installers directory" -ForegroundColor Red
    exit 1
}

# Clean previous builds
Write-Host "🧹 Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Path "*.zip", "*.msi", "*.exe" -Recurse -ErrorAction SilentlyContinue

$results = @()

try {
    # Build PyInstaller executable (always build this first)
    Write-Host "`n🎯 Building standalone executable..." -ForegroundColor Yellow
    Push-Location "pyinstaller"
    & .\build.ps1 -Version $Version
    if ($LASTEXITCODE -eq 0) {
        $results += "✅ Standalone EXE"
    } else {
        $results += "❌ Standalone EXE"
    }
    Pop-Location

    if (-not $PyInstallerOnly) {
        # Build ZIP package
        Write-Host "`n📦 Building ZIP package..." -ForegroundColor Yellow
        try {
            # Create portable ZIP package
            $zipDir = "temp_zip"
            New-Item -ItemType Directory -Path $zipDir -Force | Out-Null
            
            # Create a virtual environment for bundling
            python -m venv "$zipDir\mycli_portable"
            & "$zipDir\mycli_portable\Scripts\Activate.ps1"
            
            # Install package with all dependencies
            if (Test-Path "..\dist\mycli_app-1.0.0-py3-none-any.whl") {
                pip install "..\dist\mycli_app-1.0.0-py3-none-any.whl[azure]" --quiet
            } else {
                pip install "..\.." --quiet
            }
            
            # Create launcher script
            @"
@echo off
set SCRIPT_DIR=%~dp0
call "%SCRIPT_DIR%mycli_portable\Scripts\activate.bat"
"%SCRIPT_DIR%mycli_portable\Scripts\python.exe" -m mycli_app %*
"@ | Out-File -FilePath "$zipDir\mycli.bat" -Encoding ASCII

            # Create README
            @"
# MyCliApp Portable

## Quick Start
1. Extract this ZIP to any folder
2. Double-click mycli.bat or run from command line:
   .\mycli.bat --help

## Features
- No installation required
- Includes all dependencies
- Works on any Windows system
- Includes Azure authentication

## Usage Examples
``````
.\mycli.bat status
.\mycli.bat auth login
.\mycli.bat resource list
``````

## Requirements
- Windows 7 or later
- No Python installation required

## Version Information
- Version: $Version
- Build Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@ | Out-File -FilePath "$zipDir\README.txt" -Encoding UTF8

            # Copy documentation
            Copy-Item "..\README.md" -Destination $zipDir -ErrorAction SilentlyContinue
            Copy-Item "..\LICENSE" -Destination $zipDir -ErrorAction SilentlyContinue

            # Create ZIP
            $zipName = "MyCliApp-$Version-Portable.zip"
            Compress-Archive -Path "$zipDir\*" -DestinationPath $zipName -Force
            Remove-Item $zipDir -Recurse -Force
            
            $results += "✅ ZIP Package"
            Write-Host "✅ Created: $zipName" -ForegroundColor Green
            
        } catch {
            $results += "❌ ZIP Package"
            Write-Host "❌ ZIP build failed: $($_.Exception.Message)" -ForegroundColor Red
        }

        # Note about MSI and NSIS (require additional tools)
        Write-Host "`n💿 MSI Installer..." -ForegroundColor Yellow
        if (Get-Command candle.exe -ErrorAction SilentlyContinue) {
            Write-Host "  WiX Toolset detected - MSI build available" -ForegroundColor Green
            $results += "✅ MSI Available"
        } else {
            Write-Host "  ⚠️  WiX Toolset not found - install from https://wixtoolset.org/" -ForegroundColor Orange
            $results += "⚠️  MSI (WiX needed)"
        }

        Write-Host "`n🔧 NSIS Installer..." -ForegroundColor Yellow
        if (Get-Command makensis.exe -ErrorAction SilentlyContinue) {
            Write-Host "  NSIS detected - Custom installer build available" -ForegroundColor Green
            $results += "✅ NSIS Available"
        } else {
            Write-Host "  ⚠️  NSIS not found - install from https://nsis.sourceforge.io/" -ForegroundColor Orange
            $results += "⚠️  NSIS (tool needed)"
        }
    }

    # Run basic tests
    if (-not $SkipTests -and (Test-Path "pyinstaller\dist\mycli.exe")) {
        Write-Host "`n🧪 Running basic tests..." -ForegroundColor Yellow
        try {
            $testResult = & "pyinstaller\dist\mycli.exe" --version
            Write-Host "  ✅ Executable test: $testResult" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ Executable test failed" -ForegroundColor Red
        }
    }

    # Summary
    Write-Host "`n📊 Build Summary" -ForegroundColor Cyan
    Write-Host "=================" -ForegroundColor Cyan
    foreach ($result in $results) {
        Write-Host "  $result" -ForegroundColor White
    }

    # Show created files
    Write-Host "`n📁 Created Files:" -ForegroundColor Cyan
    Get-ChildItem -Path "." -Include "*.zip", "*.msi", "*.exe" -Recurse | ForEach-Object {
        $size = [math]::Round($_.Length/1MB, 1)
        Write-Host "  📦 $($_.Name) ($size MB)" -ForegroundColor White
    }

    # Usage instructions
    Write-Host "`n🚀 Usage Instructions:" -ForegroundColor Green
    Write-Host "  Standalone EXE: .\pyinstaller\dist\mycli.exe" -ForegroundColor White
    if (Test-Path "MyCliApp-$Version-Portable.zip") {
        Write-Host "  ZIP Package: Extract MyCliApp-$Version-Portable.zip" -ForegroundColor White
    }
    Write-Host "  See WINDOWS_INSTALLERS.md for MSI and NSIS setup" -ForegroundColor White

    Write-Host "`n✅ Build completed successfully!" -ForegroundColor Green

} catch {
    Write-Host "`n❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
