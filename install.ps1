# Sift Windows Installer
# Usage: pwsh -ExecutionPolicy Bypass -File install.ps1
# Or: iex "& { $(iwr -useb https://github.com/laghab/sift/releases/latest/download/install.ps1) }"

param(
    [string]$Version = "latest"
)

$Repo = "laghab/sift"
$InstallDir = "$env:LOCALAPPDATA\sift"
$BinDir = "$env:USERPROFILE\.local\bin"

if ($Version -eq "latest") {
    $DownloadUrl = "https://github.com/$Repo/releases/latest/download"
} else {
    $DownloadUrl = "https://github.com/$Repo/releases/download/$Version"
}

Write-Host "  Sift Installer (Windows)" -ForegroundColor Cyan
Write-Host ""

# Create install directories
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

# Determine architecture
$Arch = "x86_64"
if ([Environment]::Is64BitOperatingSystem -eq $false) {
    Write-Host "  Error: 32-bit Windows is not supported." -ForegroundColor Red
    exit 1
}

$Filename = "sift_windows_${Arch}.tar.gz"
$Url = "$DownloadUrl/$Filename"
$ArchivePath = "$env:TEMP\sift.tar.gz"

Write-Host "  Downloading $Url ..."
try {
    Invoke-WebRequest -Uri $Url -OutFile $ArchivePath
} catch {
    Write-Host "  Download failed: $_" -ForegroundColor Red
    exit 1
}

# Extract tar.gz
$ExtractDir = "$env:TEMP\sift-extract"
Remove-Item -Recurse -Force $ExtractDir -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $ExtractDir | Out-Null

tar -xzf $ArchivePath -C $ExtractDir

$Output = "$InstallDir\sift.exe"
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Copy-Item "$ExtractDir\sift.exe" $Output -Force

Write-Host "  Installed to: $Output" -ForegroundColor Green
Write-Host ""

# Add to PATH if not already
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$UserPath;$BinDir", "User")
    $env:PATH = "$env:PATH;$BinDir"
    Write-Host "  Added $BinDir to PATH." -ForegroundColor Yellow
    Write-Host "  You may need to restart your terminal." -ForegroundColor Yellow
} else {
    Write-Host "  $BinDir is already in PATH." -ForegroundColor Green
}

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
Copy-Item $Output "$BinDir\sift.exe" -Force

Remove-Item $ArchivePath -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $ExtractDir -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "  Run 'sift --help' to get started." -ForegroundColor Cyan
