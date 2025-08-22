#!/usr/bin/env pwsh
# Build script for PyInstaller standalone executable

param(
    [string]$Version = "1.0.0"
)

Write-Host "Building MyCliApp Standalone Executable v$Version" -ForegroundColor Green

try {
    # Install PyInstaller if not available
    if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
        Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
        pip install pyinstaller
    }

    # Clean previous builds
    Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    Remove-Item -Path "dist", "build" -Recurse -Force -ErrorAction SilentlyContinue

    # Build executable
    Write-Host "Building executable..." -ForegroundColor Yellow
    pyinstaller mycli.spec --clean --noconfirm

    if (Test-Path "dist\mycli.exe") {
        # Test the executable
        Write-Host "Testing executable..." -ForegroundColor Yellow
        $version = & ".\dist\mycli.exe" --version
        Write-Host "✅ Executable built successfully: $version" -ForegroundColor Green

        # Create distribution package
        Write-Host "Creating distribution package..." -ForegroundColor Yellow
        $distDir = "dist\MyCliApp-Standalone"
        New-Item -ItemType Directory -Path $distDir -Force | Out-Null

        # Copy files
        Copy-Item "dist\mycli.exe" -Destination $distDir
        Copy-Item "..\..\README.md" -Destination $distDir
        Copy-Item "..\..\LICENSE" -Destination $distDir

        # Create installation instructions
        @"
# MyCliApp Standalone Executable

## Installation
1. Copy mycli.exe to any folder (e.g., C:\Tools\)
2. Add the folder to your PATH environment variable
3. Open a new command prompt and run: mycli --help

## Quick Start
``````
mycli.exe --version
mycli.exe status
mycli.exe auth login
``````

## No Dependencies Required
This executable includes all necessary dependencies and doesn't require Python to be installed.

## File Information
- Version: $Version
- Build Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- Size: $([math]::Round((Get-Item "dist\mycli.exe").Length/1MB, 1)) MB
"@ | Out-File -FilePath "$distDir\INSTALL.txt" -Encoding UTF8

        # Create ZIP
        $zipName = "..\MyCliApp-$Version-Standalone.zip"
        Compress-Archive -Path "$distDir\*" -DestinationPath $zipName -Force
        Write-Host "✅ Created: $zipName" -ForegroundColor Green

        # Show file info
        $fileSize = [math]::Round((Get-Item "dist\mycli.exe").Length/1MB, 1)
        Write-Host "`nExecutable Information:" -ForegroundColor Cyan
        Write-Host "  📁 Path: .\dist\mycli.exe" -ForegroundColor White
        Write-Host "  📦 Size: $fileSize MB" -ForegroundColor White
        Write-Host "  📋 ZIP: $zipName" -ForegroundColor White

    } else {
        throw "Executable not found after build"
    }

} catch {
    Write-Host "❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
