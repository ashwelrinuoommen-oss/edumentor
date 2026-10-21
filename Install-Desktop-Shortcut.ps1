# =====================================================================
# EduMentor - Desktop Shortcut Installer
# Creates a Windows Desktop shortcut pointing to Launch-EduMentor.bat
# using the custom EduMentor icon.
# =====================================================================

$ErrorActionPreference = "Stop"

# 1. Determine Project Root Directory
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $ProjectDir) {
    $ProjectDir = (Get-Location).Path
}

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "       EduMentor Desktop Shortcut Installer" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "Project Directory: $ProjectDir"

# 2. Verify Launcher Target Exists
$LauncherPath = Join-Path $ProjectDir "Launch-EduMentor.bat"
if (-not (Test-Path $LauncherPath)) {
    Write-Host "[ERROR] Launcher not found at: $LauncherPath" -ForegroundColor Red
    exit 1
}

# 3. Locate Custom EduMentor Icon
$IconPath = Join-Path $ProjectDir "assets\branding\EduMentor.ico"
if (-not (Test-Path $IconPath)) {
    $IconPath = Join-Path $ProjectDir "assets\EduMentor.ico"
}
if (-not (Test-Path $IconPath)) {
    Write-Host "[WARNING] Custom icon not found at expected path. Using default." -ForegroundColor Yellow
    $IconLocation = $LauncherPath + ",0"
} else {
    $IconLocation = $IconPath + ",0"
    Write-Host "[INFO] Using custom icon: $IconPath" -ForegroundColor Green
}

# 4. Determine User Desktop Path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
if (-not (Test-Path $DesktopPath)) {
    Write-Host "[ERROR] Could not resolve user Desktop directory." -ForegroundColor Red
    exit 1
}

$ShortcutPath = Join-Path $DesktopPath "EduMentor.lnk"

# 5. Create Desktop Shortcut via WScript.Shell
try {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $LauncherPath
    $Shortcut.WorkingDirectory = $ProjectDir
    $Shortcut.IconLocation = $IconLocation
    $Shortcut.Description = "EduMentor - AI Study Companion Workspace"
    $Shortcut.Save()

    if (Test-Path $ShortcutPath) {
        Write-Host ""
        Write-Host "=======================================================" -ForegroundColor Green
        Write-Host " [SUCCESS] EduMentor Desktop Shortcut Created!" -ForegroundColor Green
        Write-Host " Location: $ShortcutPath" -ForegroundColor Green
        Write-Host "=======================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now double-click the EduMentor icon on your desktop"
        Write-Host "to start your learning session anytime."
        Write-Host ""
    } else {
        Write-Host "[ERROR] Shortcut file was not detected after saving." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERROR] Failed to create shortcut: $($_.ToString())" -ForegroundColor Red
    exit 1
}
