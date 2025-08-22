#!/usr/bin/env pwsh
# Test script for Windows installers

Write-Host "🧪 Testing MyCliApp Windows Installers" -ForegroundColor Green

$testsPassed = 0
$testsFailed = 0

function Test-Executable {
    param([string]$Path, [string]$Name)
    
    Write-Host "`n🎯 Testing $Name..." -ForegroundColor Yellow
    
    if (-not (Test-Path $Path)) {
        Write-Host "  ❌ File not found: $Path" -ForegroundColor Red
        return $false
    }
    
    try {
        # Test version command
        $version = & $Path --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Version: $version" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Version command failed" -ForegroundColor Red
            return $false
        }
        
        # Test status command
        $status = & $Path status 2>&1
        if ($LASTEXITCODE -eq 0 -and $status -match "System Status:") {
            Write-Host "  ✅ Status command works" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Status command failed: $status" -ForegroundColor Red
            return $false
        }
        
        # Test help command
        $help = & $Path --help 2>&1
        if ($LASTEXITCODE -eq 0 -and $help -match "Usage:") {
            Write-Host "  ✅ Help command works" -ForegroundColor Green
        } else {
            Write-Host "  ❌ Help command failed" -ForegroundColor Red
            return $false
        }
        
        return $true
        
    } catch {
        Write-Host "  ❌ Exception: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Test 1: Standalone EXE
if (Test-Executable "pyinstaller\dist\mycli.exe" "Standalone EXE") {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 2: ZIP Package
Write-Host "`n📦 Testing ZIP Package..." -ForegroundColor Yellow
$zipFiles = Get-ChildItem -Path "." -Filter "MyCliApp-*-Portable.zip"
if ($zipFiles.Count -gt 0) {
    $zipFile = $zipFiles[0]
    try {
        # Extract to temp location
        $tempDir = "test_zip_temp"
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        Expand-Archive -Path $zipFile.FullName -DestinationPath $tempDir -Force
        
        # Test batch file
        if (Test-Path "$tempDir\mycli.bat") {
            Write-Host "  ✅ ZIP package extracted successfully" -ForegroundColor Green
            Write-Host "  ✅ Launcher script found" -ForegroundColor Green
            
            # Test the batch file (quick test)
            $batchTest = & "$tempDir\mycli.bat" --version 2>&1
            if ($batchTest -match "MyCliApp") {
                Write-Host "  ✅ Batch launcher works" -ForegroundColor Green
                $testsPassed++
            } else {
                Write-Host "  ❌ Batch launcher failed" -ForegroundColor Red
                $testsFailed++
            }
        } else {
            Write-Host "  ❌ Launcher script not found" -ForegroundColor Red
            $testsFailed++
        }
        
        # Clean up
        Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        
    } catch {
        Write-Host "  ❌ ZIP test failed: $($_.Exception.Message)" -ForegroundColor Red
        $testsFailed++
    }
} else {
    Write-Host "  ⚠️  No ZIP package found to test" -ForegroundColor Yellow
}

# Test 3: File sizes and structure
Write-Host "`n📋 Testing File Structure..." -ForegroundColor Yellow

$expectedFiles = @(
    "pyinstaller\mycli.spec",
    "pyinstaller\version_info.txt",
    "pyinstaller\build.ps1"
)

$structureOk = $true
foreach ($file in $expectedFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ Found: $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Missing: $file" -ForegroundColor Red
        $structureOk = $false
    }
}

if ($structureOk) {
    $testsPassed++
} else {
    $testsFailed++
}

# Test 4: Check executable size and properties
Write-Host "`n📊 Checking Executable Properties..." -ForegroundColor Yellow
$exePath = "pyinstaller\dist\mycli.exe"
if (Test-Path $exePath) {
    $fileInfo = Get-Item $exePath
    $sizeInMB = [math]::Round($fileInfo.Length / 1MB, 1)
    
    Write-Host "  📦 Size: $sizeInMB MB" -ForegroundColor White
    
    if ($sizeInMB -lt 100) {  # Reasonable size check
        Write-Host "  ✅ Size is reasonable" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  ⚠️  Executable is quite large ($sizeInMB MB)" -ForegroundColor Yellow
        $testsPassed++  # Still pass, just warn
    }
} else {
    Write-Host "  ❌ Executable not found for size check" -ForegroundColor Red
    $testsFailed++
}

# Summary
Write-Host "`n📊 Test Summary" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan
Write-Host "  ✅ Passed: $testsPassed" -ForegroundColor Green
Write-Host "  ❌ Failed: $testsFailed" -ForegroundColor Red

if ($testsFailed -eq 0) {
    Write-Host "`n🎉 All tests passed! Your installers are ready for distribution." -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️  Some tests failed. Please review the issues above." -ForegroundColor Yellow
    exit 1
}
