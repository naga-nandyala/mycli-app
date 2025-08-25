# Build script for MyCliApp Windows ZIP installer
# Mimics Azure CLI Windows ZIP package creation

param(
    [string]$Version = "1.0.0",
    [string]$OutputDir = ".\installers\windows-zip\dist",
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

Write-Host "=== MyCliApp Windows ZIP Builder ===" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Green

# Get script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent (Split-Path -Parent $ScriptDir)

Write-Host "Project Root: $ProjectRoot" -ForegroundColor Yellow
Write-Host "Building Windows ZIP package..." -ForegroundColor Yellow

# Change to project root
Push-Location $ProjectRoot

try {
    # Clean previous builds if requested
    if ($Clean -or (Test-Path $OutputDir)) {
        Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
        Remove-Item -Path $OutputDir -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -Path ".\installers\windows-zip\build" -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -Path ".\dist" -Recurse -Force -ErrorAction SilentlyContinue
    }

    # Create output directory
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

    # Activate virtual environment if it exists
    if (Test-Path ".\.venv\Scripts\Activate.ps1") {
        Write-Host "Activating virtual environment..." -ForegroundColor Green
        & ".\.venv\Scripts\Activate.ps1"
    } else {
        Write-Host "No virtual environment found - create .venv at root of project directory" -ForegroundColor Yellow
        exit
    }

    # Install/upgrade build dependencies
    Write-Host "Installing build dependencies..." -ForegroundColor Green
    python -m pip install --upgrade pip setuptools wheel pyinstaller

    # Install project in development mode
    Write-Host "Installing project dependencies..." -ForegroundColor Green
    python -m pip install -e .[azure,broker]

    # Build executable with PyInstaller
    Write-Host "Building executable with PyInstaller..." -ForegroundColor Green
    $SpecFile = ".\installers\windows-zip\mycli.spec"
    
    # Run PyInstaller
    pyinstaller --clean --distpath $OutputDir $SpecFile

    # Verify executable was created
    $ExePath = Join-Path $OutputDir "mycli.exe"
    if (-not (Test-Path $ExePath)) {
        throw "Executable not found at: $ExePath"
    }

    # Test the executable
    Write-Host "Testing executable..." -ForegroundColor Green
    $TestOutput = & $ExePath --version
    Write-Host "Executable test result: $TestOutput" -ForegroundColor Green

    # Create ZIP package directory structure
    $ZipDir = Join-Path $OutputDir "MyCliApp-Windows-x64"
    $AppDir = Join-Path $ZipDir "mycli"
    
    Write-Host "Creating ZIP package structure..." -ForegroundColor Green
    New-Item -ItemType Directory -Path $ZipDir -Force | Out-Null
    
    # Copy executable and dependencies
    New-Item -ItemType Directory -Path $AppDir -Force | Out-Null
    Copy-Item -Path $ExePath -Destination (Join-Path $AppDir "mycli.exe") -Force

    # Create installation batch file
    $InstallBat = @"
@echo off
setlocal EnableDelayedExpansion

echo === MyCliApp Installation ===
echo.

REM Get the current directory where this script is located
set "INSTALL_DIR=%~dp0"
set "APP_DIR=%INSTALL_DIR%mycli"
set "EXE_PATH=%APP_DIR%\mycli.exe"

REM Verify executable exists
if not exist "%EXE_PATH%" (
    echo ERROR: mycli.exe not found at %EXE_PATH%
    echo Please ensure the ZIP file was extracted completely.
    pause
    exit /b 1
)

REM Test the executable
echo Testing MyCliApp executable...
"%EXE_PATH%" --version
if !errorlevel! neq 0 (
    echo ERROR: Failed to run mycli.exe
    pause
    exit /b 1
)

echo.
echo Installation verification complete!
echo.
echo To use MyCliApp:
echo   1. Add to PATH: %APP_DIR%
echo   2. Or run directly: %EXE_PATH%
echo.
echo Quick start:
echo   mycli --help
echo   mycli auth login
echo.
pause
"@

    Set-Content -Path (Join-Path $ZipDir "install.bat") -Value $InstallBat -Encoding ASCII

    # Create README for ZIP package
    $ZipReadme = @"
# MyCliApp Windows ZIP Package

This package contains a standalone Windows build of MyCliApp.

## Installation

1. Extract this ZIP file to your desired location (e.g., C:\MyCliApp)
2. Run `install.bat` to verify the installation
3. Add the `mycli` folder to your PATH environment variable (optional)

## Usage

### Direct execution:
```
mycli\mycli.exe --help
mycli\mycli.exe auth login
```

### If added to PATH:
```
mycli --help
mycli auth login
```

## Features

- Azure authentication (device code, browser, broker)
- Resource management commands
- Cross-platform compatibility
- No Python installation required

## Support

For issues and documentation, visit: https://github.com/your-username/mycli-app

Version: $Version
Built: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
"@

    Set-Content -Path (Join-Path $ZipDir "README.md") -Value $ZipReadme -Encoding UTF8

    # Create the ZIP file
    $ZipPath = Join-Path $OutputDir "MyCliApp-$Version-Windows-x64.zip"
    Write-Host "Creating ZIP file: $ZipPath" -ForegroundColor Green
    
    # Use .NET compression for better compatibility
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::CreateFromDirectory($ZipDir, $ZipPath)

    # Get file sizes for summary
    $ExeSize = [math]::Round((Get-Item $ExePath).Length / 1MB, 2)
    $ZipSize = [math]::Round((Get-Item $ZipPath).Length / 1MB, 2)

    Write-Host "`n=== Build Summary ===" -ForegroundColor Cyan
    Write-Host "Executable: $ExePath ($ExeSize MB)" -ForegroundColor Green
    Write-Host "ZIP Package: $ZipPath ($ZipSize MB)" -ForegroundColor Green
    Write-Host "Build completed successfully!" -ForegroundColor Green

    # Clean up temporary directory
    Remove-Item -Path $ZipDir -Recurse -Force

} catch {
    Write-Host "Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Pop-Location
}
