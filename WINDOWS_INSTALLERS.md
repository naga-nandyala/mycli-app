# 🪟 Windows Installers Guide for MyCliApp

This guide shows you how to create professional Windows installers for your Python CLI application, including `.zip` archives and `.msi` installers.

## 📖 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Method 1: ZIP Archive Distribution](#method-1-zip-archive-distribution)
4. [Method 2: Standalone Executable with PyInstaller](#method-2-standalone-executable-with-pyinstaller)
5. [Method 3: MSI Installer with WiX Toolset](#method-3-msi-installer-with-wix-toolset)
6. [Method 4: NSIS Installer](#method-4-nsis-installer)
7. [Method 5: Modern Package Managers (2025)](#method-5-modern-package-managers-2025)
8. [Method 6: MSIX Package for Microsoft Store](#method-6-msix-package-for-microsoft-store)
9. [Testing Your Installers](#testing-your-installers)
10. [Distribution Strategies](#distribution-strategies)
11. [Code Signing](#code-signing)
12. [Best Practices](#best-practices)

---

## Overview

We'll create **six different Windows distribution formats** for 2025:

- **📦 ZIP Archive**: Simple portable version
- **🎯 Standalone EXE**: Single executable file
- **💿 MSI Installer**: Professional Windows installer
- **🔧 NSIS Installer**: Lightweight custom installer
- **📋 WinGet Package**: Microsoft's native package manager (NEW for 2025)
- **🏪 MSIX Package**: Microsoft Store and enterprise deployment (NEW for 2025)

Each method has different advantages:

| Method | Size | Installation | User Experience | Enterprise-Friendly | 2025 Recommended |
|--------|------|-------------|-----------------|-------------------|-----------------|
| ZIP | Small | Manual | Simple | ✅ | For developers |
| EXE | Large | None needed | Excellent | ✅ | For power users |
| MSI | Medium | Windows native | Professional | ✅✅ | For enterprises |
| NSIS | Medium | Custom | Branded | ✅ | For legacy systems |
| **WinGet** | **Auto** | **Native** | **Modern** | **✅✅** | **✅ PRIMARY** |
| **MSIX** | **Medium** | **Store/Enterprise** | **Seamless** | **✅✅** | **✅ ENTERPRISE** |

---

## Prerequisites

### Required Tools

```powershell
# Install PyInstaller for executable creation
pip install pyinstaller

# Install cx_Freeze as alternative
pip install cx_Freeze

# For MSI creation, download and install:
# - WiX Toolset: https://wixtoolset.org/
# - Visual Studio Build Tools (optional)

# For NSIS installer:
# - NSIS: https://nsis.sourceforge.io/
```

### Project Structure Check

Ensure your project structure is ready:

```
mycli-app/
├── src/mycli_app/
│   ├── __init__.py
│   ├── __main__.py
│   └── cli.py
├── dist/                     # Built Python packages
├── installers/              # We'll create this
│   ├── pyinstaller/
│   ├── msi/
│   └── nsis/
└── scripts/                 # Build scripts
```

---

## Method 1: ZIP Archive Distribution

The simplest method - bundle your Python package with a portable Python runtime.

### Step 1: Create Portable Python Bundle

```powershell
# Create installers directory
New-Item -ItemType Directory -Path "installers\zip" -Force

# Create a virtual environment for bundling
python -m venv installers\zip\mycli_portable
.\installers\zip\mycli_portable\Scripts\Activate.ps1

# Install your package with all dependencies
pip install .\dist\mycli_app-1.0.0-py3-none-any.whl[azure]

# Create launcher script
@"
@echo off
set SCRIPT_DIR=%~dp0
call "%SCRIPT_DIR%mycli_portable\Scripts\activate.bat"
"%SCRIPT_DIR%mycli_portable\Scripts\python.exe" -m mycli_app %*
"@ | Out-File -FilePath "installers\zip\mycli.bat" -Encoding ASCII
```

### Step 2: Create ZIP Package

```powershell
# Create README for users
@"
# MyCliApp Portable

## Quick Start
1. Extract this ZIP to any folder
2. Double-click `mycli.bat` or run from command line:
   `.\mycli.bat --help`

## Features
- No installation required
- Includes all dependencies
- Works on any Windows system
- Includes Azure authentication

## Usage Examples
```
.\mycli.bat status
.\mycli.bat auth login
.\mycli.bat resource list
```

## Requirements
- Windows 7 or later
- No Python installation required
"@ | Out-File -FilePath "installers\zip\README.txt" -Encoding UTF8

# Create the ZIP file
Compress-Archive -Path "installers\zip\*" -DestinationPath "installers\MyCliApp-1.0.0-Portable.zip" -Force
```

---

## Method 2: Standalone Executable with PyInstaller

Creates a single `.exe` file that contains everything.

### Step 1: Create PyInstaller Spec File

Create `installers/pyinstaller/mycli.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Add the src directory to sys.path
src_path = Path(__file__).parent.parent.parent / 'src'
sys.path.insert(0, str(src_path))

block_cipher = None

a = Analysis(
    ['../../src/mycli_app/__main__.py'],  # Entry point
    pathex=[str(src_path)],
    binaries=[],
    datas=[
        # Include documentation files
        ('../../README.md', '.'),
        ('../../LICENSE', '.'),
        ('../../USER_GUIDE.md', '.'),
        ('../../CHANGELOG.md', '.'),
    ],
    hiddenimports=[
        'mycli_app',
        'mycli_app.cli',
        'click',
        'colorama',
        'requests',
        # Azure imports (optional)
        'azure.identity',
        'azure.mgmt.core',
        'azure.core',
        'msal',
        'json',
        'urllib3',
        'certifi',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'scipy',
        'numpy',
        'pandas',
        'jupyter',
        'IPython',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mycli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress executable (if UPX is available)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add 'icon.ico' if you have one
    version_file='version_info.txt',
)
```

### Step 2: Create Version Info File

Create `installers/pyinstaller/version_info.txt`:

```text
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Your Company'),
        StringStruct(u'FileDescription', u'MyCliApp - Azure CLI Tool'),
        StringStruct(u'FileVersion', u'1.0.0'),
        StringStruct(u'InternalName', u'mycli'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025 Your Name'),
        StringStruct(u'OriginalFilename', u'mycli.exe'),
        StringStruct(u'ProductName', u'MyCliApp'),
        StringStruct(u'ProductVersion', u'1.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
```

### Step 3: Build Executable

```powershell
# Create directory and build
New-Item -ItemType Directory -Path "installers\pyinstaller" -Force
cd installers\pyinstaller

# Build the executable
pyinstaller mycli.spec --clean --noconfirm

# The executable will be in dist/mycli.exe
# Test it
.\dist\mycli.exe --version
```

### Step 4: Create Distribution Package

```powershell
# Create a distribution folder
New-Item -ItemType Directory -Path "dist\MyCliApp-Standalone" -Force

# Copy executable and documentation
Copy-Item "dist\mycli.exe" -Destination "dist\MyCliApp-Standalone\"
Copy-Item "..\..\README.md" -Destination "dist\MyCliApp-Standalone\"
Copy-Item "..\..\LICENSE" -Destination "dist\MyCliApp-Standalone\"

# Create installation instructions
@"
# MyCliApp Standalone Executable

## Installation
1. Copy mycli.exe to any folder (e.g., C:\Tools\)
2. Add the folder to your PATH environment variable
3. Open a new command prompt and run: mycli --help

## Quick Start
```
mycli.exe --version
mycli.exe status
mycli.exe auth login
```

## No Dependencies Required
This executable includes all necessary dependencies and doesn't require Python to be installed.
"@ | Out-File -FilePath "dist\MyCliApp-Standalone\INSTALL.txt" -Encoding UTF8

# Create ZIP
Compress-Archive -Path "dist\MyCliApp-Standalone\*" -DestinationPath "..\MyCliApp-1.0.0-Standalone.zip" -Force
```

---

## Method 3: MSI Installer with WiX Toolset

Creates a professional Windows installer that integrates with Windows' Add/Remove Programs.

### Step 1: Install WiX Toolset

Download and install from: https://wixtoolset.org/

### Step 2: Create WiX Configuration

Create `installers/msi/mycli.wxs`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" 
           Name="MyCliApp" 
           Language="1033" 
           Version="1.0.0" 
           Manufacturer="Your Company" 
           UpgradeCode="12345678-1234-1234-1234-123456789012">
    
    <Package InstallerVersion="200" 
             Compressed="yes" 
             InstallScope="perMachine" 
             Description="MyCliApp - Azure CLI Tool"
             Comments="A comprehensive CLI tool for Azure resource management" />

    <MajorUpgrade DowngradeErrorMessage="A newer version of [ProductName] is already installed." />
    <MediaTemplate EmbedCab="yes" />

    <Feature Id="ProductFeature" Title="MyCliApp" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
      <ComponentRef Id="EnvironmentPath" />
    </Feature>

    <!-- Installation directory -->
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="MyCliApp" />
      </Directory>
      <Directory Id="ProgramMenuFolder" />
    </Directory>

    <!-- Components to install -->
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="MainExecutable" Guid="*">
        <File Id="MyCliExe" 
              Source="mycli.exe" 
              KeyPath="yes" 
              Checksum="yes" />
      </Component>
      
      <Component Id="Documentation" Guid="*">
        <File Id="ReadmeFile" Source="README.md" />
        <File Id="LicenseFile" Source="LICENSE" />
        <File Id="UserGuideFile" Source="USER_GUIDE.md" />
      </Component>
    </ComponentGroup>

    <!-- Add to PATH environment variable -->
    <Component Id="EnvironmentPath" Directory="INSTALLFOLDER" Guid="*">
      <Environment Id="UpdatePath" 
                   Name="PATH" 
                   Value="[INSTALLFOLDER]" 
                   Permanent="no" 
                   Part="last" 
                   Action="set" 
                   System="yes" />
    </Component>

    <!-- Start Menu shortcuts -->
    <DirectoryRef Id="ProgramMenuFolder">
      <Component Id="ApplicationShortcut" Guid="*">
        <Shortcut Id="ApplicationStartMenuShortcut"
                  Name="MyCliApp Command Prompt"
                  Description="Open command prompt with MyCliApp"
                  Target="[System64Folder]cmd.exe"
                  Arguments='/k "cd /d [INSTALLFOLDER] &amp;&amp; echo MyCliApp is ready! Type: mycli --help"'
                  WorkingDirectory="INSTALLFOLDER" />
        <RemoveFolder Id="CleanUpShortCut" Directory="ProgramMenuFolder" On="uninstall" />
        <RegistryValue Root="HKCU" 
                       Key="Software\MyCliApp" 
                       Name="installed" 
                       Type="integer" 
                       Value="1" 
                       KeyPath="yes" />
      </Component>
    </DirectoryRef>
  </Product>
</Wix>
```

### Step 3: Build MSI

```powershell
# Navigate to MSI directory
cd installers\msi

# Copy files needed for installer
Copy-Item "..\pyinstaller\dist\mycli.exe" -Destination "."
Copy-Item "..\..\README.md" -Destination "."
Copy-Item "..\..\LICENSE" -Destination "."
Copy-Item "..\..\USER_GUIDE.md" -Destination "."

# Compile WiX source to object file
candle.exe mycli.wxs

# Link object file to create MSI
light.exe mycli.wixobj -out MyCliApp-1.0.0.msi

# Test installation (run as administrator)
# msiexec /i MyCliApp-1.0.0.msi /l*v install.log
```

---

## Method 4: NSIS Installer

Creates a lightweight, customizable installer with modern UI.

### Step 1: Install NSIS

Download from: https://nsis.sourceforge.io/

### Step 2: Create NSIS Script

Create `installers/nsis/mycli.nsi`:

```nsis
; MyCliApp NSIS Installer Script
; Author: Your Name
; Version: 1.0.0

!define APPNAME "MyCliApp"
!define COMPANYNAME "Your Company"
!define DESCRIPTION "A comprehensive CLI tool for Azure resource management"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/naga-nandyala/mycli-app"
!define UPDATEURL "https://github.com/naga-nandyala/mycli-app/releases"
!define ABOUTURL "https://github.com/naga-nandyala/mycli-app"
!define INSTALLSIZE 50000  ; Size in KB

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES64\${APPNAME}"
LicenseData "LICENSE"
Name "${APPNAME}"
Icon "mycli.ico"  ; Add if you have an icon
outFile "MyCliApp-1.0.0-Setup.exe"

!include LogicLib.nsh
!include "MUI2.nsh"

; Modern UI Configuration
!define MUI_ABORTWARNING
!define MUI_ICON "mycli.ico"  ; Add if you have an icon
!define MUI_UNICON "mycli.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

!insertmacro MUI_LANGUAGE "English"

section "install"
    setOutPath $INSTDIR
    
    ; Install files
    file "mycli.exe"
    file "README.md"
    file "LICENSE"
    file "USER_GUIDE.md"
    
    ; Add to PATH
    EnVar::SetHKLM
    EnVar::AddValue "PATH" "$INSTDIR"
    
    ; Create uninstaller
    writeUninstaller "$INSTDIR\uninstall.exe"
    
    ; Start Menu shortcuts
    createDirectory "$SMPROGRAMS\${APPNAME}"
    createShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\mycli.exe"
    createShortCut "$SMPROGRAMS\${APPNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    
    ; Desktop shortcut (optional)
    createShortCut "$DESKTOP\${APPNAME}.lnk" "$INSTDIR\mycli.exe"
    
    ; Registry information for Add/Remove Programs
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayName" "${APPNAME} - ${DESCRIPTION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "InstallLocation" "$\"$INSTDIR$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayIcon" "$\"$INSTDIR\mycli.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd

; Uninstaller
section "uninstall"
    ; Remove from PATH
    EnVar::SetHKLM
    EnVar::DeleteValue "PATH" "$INSTDIR"
    
    ; Remove files
    delete "$INSTDIR\mycli.exe"
    delete "$INSTDIR\README.md"
    delete "$INSTDIR\LICENSE"
    delete "$INSTDIR\USER_GUIDE.md"
    delete "$INSTDIR\uninstall.exe"
    
    ; Remove shortcuts
    delete "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk"
    delete "$SMPROGRAMS\${APPNAME}\Uninstall.lnk"
    rmDir "$SMPROGRAMS\${APPNAME}"
    delete "$DESKTOP\${APPNAME}.lnk"
    
    ; Remove installation directory
    rmDir "$INSTDIR"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
sectionEnd
```

### Step 3: Build NSIS Installer

```powershell
# Navigate to NSIS directory
cd installers\nsis

# Copy files
Copy-Item "..\pyinstaller\dist\mycli.exe" -Destination "."
Copy-Item "..\..\README.md" -Destination "."
Copy-Item "..\..\LICENSE" -Destination "."
Copy-Item "..\..\USER_GUIDE.md" -Destination "."

# Build installer (assuming NSIS is in PATH)
makensis mycli.nsi

# This creates MyCliApp-1.0.0-Setup.exe
```

---

## Method 5: Modern Package Managers (2025)

### WinGet Package Manager

Microsoft's native Windows Package Manager is now the recommended distribution method for modern Windows applications.

#### Step 1: Create WinGet Manifest

Create `installers/winget/manifests/MyCliApp.yaml`:

```yaml
# Created using wingetcreate
PackageIdentifier: YourCompany.MyCliApp
PackageVersion: 1.0.0
PackageName: MyCliApp
Publisher: Your Company
ShortDescription: A comprehensive CLI tool for Azure resource management
License: MIT
LicenseUrl: https://github.com/naga-nandyala/mycli-app/blob/main/LICENSE
Installers:
- Architecture: x64
  InstallerType: zip
  InstallerUrl: https://github.com/naga-nandyala/mycli-app/releases/download/v1.0.0/MyCliApp-1.0.0-Standalone.zip
  InstallerSha256: [SHA256_HASH]
  Commands:
  - mycli
ManifestType: singleton
ManifestVersion: 1.4.0
```

#### Step 2: Submit to WinGet Community Repository

```powershell
# Install winget-create tool
winget install winget-create

# Create manifest automatically
wingetcreate new https://github.com/naga-nandyala/mycli-app/releases/download/v1.0.0/MyCliApp-1.0.0-Standalone.zip

# Submit via GitHub PR to microsoft/winget-pkgs repository
```

### Enhanced Chocolatey Package (2025)

#### Create Modern Chocolatey Package

Create `installers/chocolatey/mycli-app.nuspec`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://schemas.microsoft.com/packaging/2015/06/nuspec.xsd">
  <metadata>
    <id>mycli-app</id>
    <version>1.0.0</version>
    <packageSourceUrl>https://github.com/naga-nandyala/mycli-app</packageSourceUrl>
    <owners>Your Name</owners>
    <title>MyCliApp</title>
    <authors>Your Name</authors>
    <projectUrl>https://github.com/naga-nandyala/mycli-app</projectUrl>
    <licenseUrl>https://github.com/naga-nandyala/mycli-app/blob/main/LICENSE</licenseUrl>
    <requireLicenseAcceptance>false</requireLicenseAcceptance>
    <projectSourceUrl>https://github.com/naga-nandyala/mycli-app</projectSourceUrl>
    <bugTrackerUrl>https://github.com/naga-nandyala/mycli-app/issues</bugTrackerUrl>
    <tags>cli azure authentication command-line tool admin</tags>
    <summary>A comprehensive CLI tool for Azure resource management</summary>
    <description>MyCliApp provides a complete command-line interface for managing Azure resources with built-in authentication support.</description>
    <releaseNotes>https://github.com/naga-nandyala/mycli-app/blob/main/CHANGELOG.md</releaseNotes>
  </metadata>
  <files>
    <file src="tools\**" target="tools" />
  </files>
</package>
```

---

## Method 6: MSIX Package for Microsoft Store

Modern Windows applications increasingly use MSIX packaging for store distribution and enterprise deployment.

### Step 1: Create MSIX Package

```powershell
# Install Windows SDK for MSIX tools
# Download from: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/

# Create MSIX from existing installer
MakeAppx pack /d "installers\msix\source" /p "installers\MyCliApp-1.0.0.msix"
```

### Step 2: Configure Package Manifest

Create `installers/msix/source/AppxManifest.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10">
  <Identity Name="YourCompany.MyCliApp" 
            Publisher="CN=Your Company" 
            Version="1.0.0.0" />
  
  <Properties>
    <DisplayName>MyCliApp</DisplayName>
    <PublisherDisplayName>Your Company</PublisherDisplayName>
    <Logo>images\logo.png</Logo>
    <Description>A comprehensive CLI tool for Azure resource management</Description>
  </Properties>
  
  <Dependencies>
    <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="10.0.22000.0" />
  </Dependencies>
  
  <Applications>
    <Application Id="MyCliApp" Executable="mycli.exe" EntryPoint="Windows.FullTrustApplication">
      <uap:VisualElements DisplayName="MyCliApp" Description="Azure CLI Tool" 
                         BackgroundColor="transparent" Square150x150Logo="images\logo.png" 
                         Square44x44Logo="images\logo44.png" />
    </Application>
  </Applications>
  
  <Capabilities>
    <Capability Name="internetClient" />
    <rescap:Capability Name="runFullTrust" xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities" />
  </Capabilities>
</Package>
```

---

## Testing Your Installers

### Test Matrix

Create a comprehensive testing strategy:

```powershell
# Create test script
@"
# Windows Installer Testing Script

Write-Host "Testing MyCliApp Installers..." -ForegroundColor Green

# Test 1: Standalone EXE
Write-Host "`n1. Testing Standalone EXE..." -ForegroundColor Yellow
& ".\installers\pyinstaller\dist\mycli.exe" --version
& ".\installers\pyinstaller\dist\mycli.exe" status

# Test 2: ZIP Package
Write-Host "`n2. Testing ZIP Package..." -ForegroundColor Yellow
Expand-Archive -Path "installers\MyCliApp-1.0.0-Portable.zip" -DestinationPath "test_zip" -Force
Set-Location "test_zip"
& ".\mycli.bat" --version
Set-Location ".."
Remove-Item "test_zip" -Recurse -Force

# Test 3: MSI Installer (requires admin)
Write-Host "`n3. MSI Installer available at:" -ForegroundColor Yellow
Write-Host "installers\msi\MyCliApp-1.0.0.msi"

# Test 4: NSIS Installer (requires admin)
Write-Host "`n4. NSIS Installer available at:" -ForegroundColor Yellow
Write-Host "installers\nsis\MyCliApp-1.0.0-Setup.exe"

Write-Host "`nTesting complete!" -ForegroundColor Green
"@ | Out-File -FilePath "test_installers.ps1" -Encoding UTF8
```

### Virtual Machine Testing

Test on clean Windows VMs:

1. **Windows 10** (latest)
2. **Windows 11** (latest)
3. **Windows Server 2019**
4. **Windows Server 2022**

---

## Distribution Strategies

### For Different User Types

| User Type | Recommended Installer | Reason |
|-----------|----------------------|---------|
| **End Users (2025)** | WinGet Package | Native Windows experience, automatic updates |
| **Developers** | ZIP Portable | No admin rights needed |
| **Enterprise** | MSI + MSIX | Group Policy deployment, Store integration |
| **Power Users** | Standalone EXE | Simple, no installation |
| **Legacy Systems** | NSIS Setup.exe | Compatible with older Windows versions |

### Distribution Channels

```text
📁 GitHub Releases
├── MyCliApp-1.0.0-Portable.zip           (5MB)
├── MyCliApp-1.0.0-Standalone.zip         (25MB)
├── MyCliApp-1.0.0.msi                    (30MB)
└── MyCliApp-1.0.0-Setup.exe              (28MB)

📦 Internal Distribution
├── Network share: \\company\software\MyCliApp\
├── Software Center (SCCM)
├── Chocolatey package (choco install mycli-app)
├── WinGet package (winget install mycli-app)
└── Microsoft Store (enterprise apps)
```

---

## Code Signing

### Why Sign Your Installers?

- **Trust**: Users trust signed software
- **Security**: Windows SmartScreen won't block
- **Enterprise**: Required for many organizations
- **Store Requirements**: Microsoft Store requires signed packages
- **WinGet**: Signed packages get prioritized in WinGet repository

### Modern Signing Process (2025)

```powershell
# Option 1: Traditional certificate signing
signtool sign /f "certificate.pfx" /p "password" /t "http://timestamp.digicert.com" "MyCliApp-1.0.0-Setup.exe"

# Option 2: Azure Code Signing (Cloud HSM) - Recommended
signtool sign /tr "http://timestamp.acs.microsoft.com" /td sha256 /fd sha256 /a "MyCliApp-1.0.0-Setup.exe"

# Option 3: GitHub Actions with Azure Key Vault
# See: https://docs.microsoft.com/en-us/azure/key-vault/certificates/tutorial-import-cert

# Verify signature
signtool verify /pa "MyCliApp-1.0.0-Setup.exe"
```

### Certificate Sources (2025)

1. **Azure Code Signing** (Recommended)
   - Cloud-based HSM
   - No local certificate management
   - Integrated with CI/CD pipelines

2. **Traditional Code Signing Certificates**
   - DigiCert, Sectigo, GlobalSign
   - Hardware tokens or software certificates
   - Annual renewal required

---

## Best Practices

### File Organization

```text
installers/
├── build_all.ps1              # Master build script
├── pyinstaller/
│   ├── mycli.spec
│   ├── version_info.txt
│   └── build.ps1
├── msi/
│   ├── mycli.wxs
│   └── build.ps1
├── nsis/
│   ├── mycli.nsi
│   ├── mycli.ico
│   └── build.ps1
└── zip/
    └── build.ps1
```

### Master Build Script

Create `installers/build_all.ps1`:

```powershell
#!/usr/bin/env pwsh
# Master build script for all Windows installers

param(
    [string]$Version = "1.0.0",
    [switch]$SkipTests = $false
)

Write-Host "Building MyCliApp Windows Installers v$Version" -ForegroundColor Green

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Path "*.zip", "*.msi", "*.exe" -ErrorAction SilentlyContinue

try {
    # Build PyInstaller executable
    Write-Host "`nBuilding standalone executable..." -ForegroundColor Yellow
    Set-Location "pyinstaller"
    & .\build.ps1
    Set-Location ".."

    # Build ZIP package
    Write-Host "`nBuilding ZIP package..." -ForegroundColor Yellow
    Set-Location "zip"
    & .\build.ps1
    Set-Location ".."

    # Build MSI installer
    Write-Host "`nBuilding MSI installer..." -ForegroundColor Yellow
    Set-Location "msi"
    & .\build.ps1
    Set-Location ".."

    # Build NSIS installer
    Write-Host "`nBuilding NSIS installer..." -ForegroundColor Yellow
    Set-Location "nsis"
    & .\build.ps1
    Set-Location ".."

    # Run tests
    if (-not $SkipTests) {
        Write-Host "`nRunning tests..." -ForegroundColor Yellow
        & .\test_installers.ps1
    }

    Write-Host "`n✅ All installers built successfully!" -ForegroundColor Green
    Write-Host "`nFiles created:" -ForegroundColor Cyan
    Get-ChildItem -Path "." -Include "*.zip", "*.msi", "*.exe" -Recurse | ForEach-Object {
        Write-Host "  📦 $($_.Name) ($([math]::Round($_.Length/1MB, 1)) MB)" -ForegroundColor White
    }

} catch {
    Write-Host "`n❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
```

### CI/CD Integration (Updated for 2025)

```yaml
# GitHub Actions example - Modern Windows packaging
name: Build and Deploy Windows Packages

on:
  release:
    types: [published]

jobs:
  build-windows-packages:
    runs-on: windows-latest
    permissions:
      contents: write
      id-token: write  # For Azure Code Signing
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller winget-create
          
      # Traditional installers
      - name: Build traditional installers
        run: |
          cd installers
          .\build_all.ps1 -Version ${{ github.event.release.tag_name }}
      
      # Code signing with Azure
      - name: Azure Code Signing
        uses: azure/code-signing-action@v1
        with:
          certificate-name: 'MyCertificate'
          files: 'installers/**/*.exe,installers/**/*.msi'
          
      # WinGet package submission
      - name: Submit to WinGet
        run: |
          wingetcreate update YourCompany.MyCliApp \
            --urls https://github.com/${{ github.repository }}/releases/download/${{ github.event.release.tag_name }}/MyCliApp-${{ github.event.release.tag_name }}-Standalone.zip \
            --version ${{ github.event.release.tag_name }} \
            --submit
        env:
          WINGET_TOKEN: ${{ secrets.WINGET_TOKEN }}
          
      # Upload to release
      - name: Upload installers
        uses: softprops/action-gh-release@v1
        with:
          files: |
            installers/*.zip
            installers/*.exe
            installers/*.msi
            installers/*.msix
```

---

## Summary

You now have **six different Windows distribution methods** for 2025:

1. **📦 ZIP Archive** - Portable, no installation
2. **🎯 Standalone EXE** - Single file, easy to share
3. **💿 MSI Installer** - Professional Windows installer
4. **🔧 NSIS Installer** - Custom branded installer
5. **📋 WinGet Package** - Microsoft's native package manager (2025)
6. **🏪 MSIX Package** - Microsoft Store and enterprise deployment

Each serves different use cases and user preferences. **For 2025, WinGet is recommended as the primary distribution method** for modern Windows applications, with MSI as backup for enterprise environments.

### Quick Commands Summary

```powershell
# Build all traditional installers
cd installers
.\build_all.ps1

# Test all installers
.\test_installers.ps1

# Individual builds
cd pyinstaller && .\build.ps1  # Standalone EXE
cd zip && .\build.ps1           # ZIP package
cd msi && .\build.ps1           # MSI installer
cd nsis && .\build.ps1          # NSIS installer

# Modern package managers (2025)
winget install winget-create    # Create WinGet manifest
choco pack                      # Create Chocolatey package
MakeAppx pack                   # Create MSIX package
```

**For 2025, prioritize WinGet distribution for the best user experience!** 🎉
