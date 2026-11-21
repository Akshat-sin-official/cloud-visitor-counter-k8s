# ==============================================================================
# ORBIT Platform — Automated Screen / Window Evidence Capture Utility
# Captures PNG screenshots of running terminals and browser displays
# ==============================================================================

param (
    [string]$OutputPath = "screenshots/04_visitor_browser.png",
    [string]$TargetUrl = "http://localhost:5001/"
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

Write-Host "Opening target in browser: $TargetUrl" -ForegroundColor Cyan
Start-Process $TargetUrl
Start-Sleep -Seconds 3

$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)

$graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)

$fullOut = [System.IO.Path]::GetFullPath($OutputPath)
$dir = [System.IO.Path]::GetDirectoryName($fullOut)
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

$bitmap.Save($fullOut, [System.Drawing.Imaging.ImageFormat]::Png)

$graphics.Dispose()
$bitmap.Dispose()

Write-Host "Screenshot captured successfully: $fullOut" -ForegroundColor Green
