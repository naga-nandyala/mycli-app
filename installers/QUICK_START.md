# 🚀 Quick Start: Building Windows Installers

This guide helps you quickly create Windows installers for your MyCliApp.

## 🎯 TL;DR - Just Give Me the Executables!

```powershell
# Navigate to installers directory
cd installers

# Build standalone executable + ZIP package
.\build_all.ps1 -PyInstallerOnly

# Your files will be in:
# - pyinstaller\dist\mycli.exe (standalone executable)
# - MyCliApp-1.0.0-Standalone.zip (portable package)
```

## 📋 Prerequisites

1. **Python 3.8+** with your package built
2. **PowerShell** (Windows built-in)
3. **PyInstaller** (auto-installed by build script)

Optional for advanced installers:
- **WiX Toolset** for MSI: https://wixtoolset.org/
- **NSIS** for custom installer: https://nsis.sourceforge.io/

## 🔧 Quick Build Commands

### Option 1: Build Everything (Recommended)
```powershell
cd installers
.\build_all.ps1
```

### Option 2: Just Standalone EXE
```powershell
cd installers
.\build_all.ps1 -PyInstallerOnly
```

### Option 3: Manual PyInstaller Build
```powershell
cd installers\pyinstaller
.\build.ps1
```

## 📦 What You Get

After running the build, you'll have:

| File | Description | Size | Best For |
|------|-------------|------|----------|
| `mycli.exe` | Standalone executable | ~25MB | Power users |
| `MyCliApp-1.0.0-Standalone.zip` | Portable package | ~30MB | Distribution |
| `MyCliApp-1.0.0-Portable.zip` | Full portable Python | ~50MB | No Python systems |

## 🧪 Testing Your Build

```powershell
# Test all installers
.\test_installers.ps1

# Quick manual test
.\pyinstaller\dist\mycli.exe --version
.\pyinstaller\dist\mycli.exe status
```

## 🎯 Distribution

### For End Users
```text
📧 Email or Teams: MyCliApp-1.0.0-Standalone.zip
📁 Network Share: \\server\software\MyCliApp\
🌐 Download Link: https://yoursite.com/download/mycli.exe
```

### For Enterprise
```text
💿 MSI Installer: Follow WINDOWS_INSTALLERS.md
🏢 SCCM Package: Use MSI + documentation
📋 Group Policy: Deploy via software installation
```

## ❓ Troubleshooting

### Build Fails?
```powershell
# Check Python environment
python --version
pip list | grep mycli

# Install missing tools
pip install pyinstaller

# Clean and retry
Remove-Item installers\pyinstaller\dist, installers\pyinstaller\build -Recurse -Force
cd installers\pyinstaller
.\build.ps1
```

### Executable Won't Run?
```powershell
# Test in same directory
cd installers\pyinstaller\dist
.\mycli.exe --help

# Check for missing DLLs
.\mycli.exe status
```

### Too Large?
```powershell
# Check what's included
python -m zipfile -l installers\pyinstaller\dist\mycli.exe

# Exclude more modules (edit mycli.spec)
# Add to excludes: 'module_name'
```

## 🎉 Success!

If your build succeeds, you now have:
- ✅ Standalone Windows executable
- ✅ Portable ZIP packages  
- ✅ Professional distribution format
- ✅ No Python required for users

Your users can now install with:
```powershell
# Extract ZIP and run
mycli.exe --help

# Or just copy the EXE anywhere
copy mycli.exe C:\Tools\
mycli --version
```

## 📚 Next Steps

- **MSI Installer**: See `WINDOWS_INSTALLERS.md` for professional installation
- **Code Signing**: Sign your executables for enterprise deployment
- **Auto-Updates**: Add update checking to your CLI
- **CI/CD**: Automate builds with GitHub Actions

Happy distributing! 🎉
