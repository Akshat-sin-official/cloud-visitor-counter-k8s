# ==============================================================================
# ORBIT Platform — Cluster Health Check & Status Verification (PowerShell)
# Probes both Primary and Secondary clusters and reports status
# ==============================================================================

param (
    [string]$PrimaryUrl = "http://localhost:5001",
    [string]$SecondaryUrl = "http://localhost:5002"
)

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " [ORBIT] Hybrid Cloud Health Check Verification                   " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

function Test-Endpoint {
    param ([string]$Name, [string]$Url)
    Write-Host "`nProbing $Name ($Url/health)..." -NoNewline
    try {
        $response = Invoke-RestMethod -Uri "$Url/health" -Method Get -TimeoutSec 3 -ErrorAction Stop
        Write-Host " [HEALTHY]" -ForegroundColor Green
        Write-Host "   Status:    $($response.status)"
        Write-Host "   Cluster:   $($response.cluster)"
        Write-Host "   Redis:     $($response.services.redis)"
        Write-Host "   Pod Host:  $($response.details.hostname)"
        return $true
    } catch {
        Write-Host " [UNAVAILABLE / DOWN]" -ForegroundColor Red
        Write-Host "   Error:     $($_.Exception.Message)"
        return $false
    }
}

$pStatus = Test-Endpoint -Name "PRIMARY CLUSTER (Private Cloud)" -Url $PrimaryUrl
$sStatus = Test-Endpoint -Name "SECONDARY CLUSTER (Public Cloud DR)" -Url $SecondaryUrl

Write-Host "`n------------------------------------------------------------------" -ForegroundColor Gray
Write-Host "Summary:"
Write-Host "  Primary Cluster:   " -NoNewline
if ($pStatus) { Write-Host "ONLINE" -ForegroundColor Green } else { Write-Host "OFFLINE" -ForegroundColor Red }
Write-Host "  Secondary Cluster: " -NoNewline
if ($sStatus) { Write-Host "ONLINE" -ForegroundColor Green } else { Write-Host "OFFLINE" -ForegroundColor Red }
Write-Host "==================================================================" -ForegroundColor Cyan
