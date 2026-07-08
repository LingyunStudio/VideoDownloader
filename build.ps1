#Requires -Version 5.1
<#
  VideoDownloader one-click build script.
  Outputs:
    dist\VideoDownloader\          (PyInstaller onedir)
    dist\VideoDownloader_Setup.exe (Inno Setup installer)

  Usage (in project root pyqt6-downloader):
    powershell -ExecutionPolicy Bypass -File build.ps1
  Options:
    -SkipInstaller   skip Inno Setup step
    -Clean           remove old build/dist first
    -Python <path>   python exe (default: conda env videodownload)
    -Iscc   <path>   ISCC.exe     (default: D:\InnoSetup6\ISCC.exe)
#>
[CmdletBinding()]
param(
    [string]$Python  = "D:\anaconda\envs\videodownload\python.exe",
    [string]$Iscc    = "D:\InnoSetup6\ISCC.exe",
    [string]$Project = $PSScriptRoot,
    [switch]$SkipInstaller,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
if (-not $Project) { $Project = $PSScriptRoot }
if (-not $Project) { $Project = Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $Project) { $Project = (Get-Location).Path }
Set-Location $Project
Write-Host "==> project dir: $Project" -ForegroundColor DarkGray

Write-Host "==> VideoDownloader build" -ForegroundColor Cyan

if ($Clean) {
    Write-Host "==> cleaning old build/dist" -ForegroundColor Yellow
    Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
}

# 1. Verify user icon present
if (-not (Test-Path "icon\1.ico")) {
    throw "icon\1.ico not found. Place your app icon there."
}
Write-Host "==> using icon: icon\1.ico" -ForegroundColor DarkGray

# 2. PyInstaller
Write-Host "==> PyInstaller" -ForegroundColor Yellow
& $Python -m PyInstaller --noconfirm --clean VideoDownloader.spec
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed (exit $LASTEXITCODE)" }

$appDir = Join-Path $Project "dist\VideoDownloader"
if (-not (Test-Path $appDir)) { throw "Output dir not found: $appDir" }

# 3. Trim unused folders to shrink size
Get-ChildItem $appDir -Recurse -Directory -Include "translations","examples","tests","__pycache__" -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

$sizeMB = [math]::Round((Get-ChildItem $appDir -Recurse -File | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Host "==> app dir size: ${sizeMB} MB" -ForegroundColor Green

# 5. Inno Setup
if ($SkipInstaller) {
    Write-Host "==> skipped installer (-SkipInstaller)" -ForegroundColor Yellow
    return
}
if (-not (Test-Path $Iscc)) {
    Write-Host "==> ISCC.exe not found ($Iscc), skipping installer" -ForegroundColor Yellow
    Write-Host "    install Inno Setup or pass -Iscc <path>" -ForegroundColor Yellow
    return
}
Write-Host "==> Inno Setup" -ForegroundColor Yellow
& $Iscc /Q "installer.iss"
if ($LASTEXITCODE -ne 0) { throw "ISCC failed (exit $LASTEXITCODE)" }

$setup = Join-Path $Project "dist\VideoDownloader_Setup.exe"
if (Test-Path $setup) {
    $setupMB = [math]::Round((Get-Item $setup).Length / 1MB, 1)
    Write-Host "==> installer: dist\VideoDownloader_Setup.exe (${setupMB} MB)" -ForegroundColor Green
}
Write-Host "==> done" -ForegroundColor Cyan
