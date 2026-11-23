# VideoDownloader (WinUI 3) 一键构建与打包脚本
# 用法示例：
#   powershell -ExecutionPolicy Bypass -File build.ps1
#   powershell -ExecutionPolicy Bypass -File build.ps1 -SkipInstaller
#   powershell -ExecutionPolicy Bypass -File build.ps1 -Clean

param(
    [switch]$Clean,
    [switch]$SkipInstaller,
    [ValidateSet("x64", "ARM64")]
    [string]$Arch = "x64",
    [string]$Iscc = "D:\InnoSetup6\ISCC.exe"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Project = Join-Path $Root "src\VideoDownloader\VideoDownloader.csproj"
$Rid = if ($Arch -eq "ARM64") { "win-arm64" } else { "win-x64" }
$PublishDir = Join-Path $Root "dist\VideoDownloader"

if ($Clean) {
    Write-Host "[1/3] 清理旧构建产物..." -ForegroundColor Cyan
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $Root "dist")
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $Root "src\VideoDownloader\bin")
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue (Join-Path $Root "src\VideoDownloader\obj")
}

Write-Host "[2/3] 发布 WinUI 3 应用 ($Arch / Release / Self-Contained / ReadyToRun)..." -ForegroundColor Cyan
dotnet publish $Project `
    -c Release `
    -p:Platform=$Arch `
    -r $Rid `
    --self-contained true `
    -p:WindowsAppSDKSelfContained=true `
    -p:PublishReadyToRun=true `
    -o $PublishDir

if ($LASTEXITCODE -ne 0) {
    throw "dotnet publish 失败（退出码 $LASTEXITCODE）"
}

Write-Host "发布目录：$PublishDir" -ForegroundColor Green

if (-not $SkipInstaller) {
    if (Test-Path $Iscc) {
        Write-Host "[3/3] 使用 Inno Setup 生成安装包..." -ForegroundColor Cyan
        & $Iscc (Join-Path $Root "installer.iss")
        if ($LASTEXITCODE -ne 0) {
            throw "ISCC 打包失败（退出码 $LASTEXITCODE）"
        }
        Write-Host "安装包已生成：$(Join-Path $Root 'dist\VideoDownloader_Setup.exe')" -ForegroundColor Green
    } else {
        Write-Host "[3/3] 未找到 ISCC.exe ($Iscc)，跳过安装包生成。" -ForegroundColor Yellow
    }
} else {
    Write-Host "[3/3] 已指定 -SkipInstaller，跳过安装包生成。" -ForegroundColor Yellow
}
