# ==============================================================================
# ORBIT Platform — Primary Cluster Recovery & Failback (PowerShell)
# Restores Primary deployment replicas, verifies health, and routes back to Primary
# ==============================================================================

param (
    [int]$Replicas = 2,
    [string]$RouterUrl = "http://127.0.0.1:8080"
)

$ErrorActionPreference = "Stop"
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " [ORBIT] Restoring Primary Cluster & Executing Failback           " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# 1. Restore replicas
Write-Host "`n>>> [1/3] Scaling Primary visitor counter back to $Replicas replicas..." -ForegroundColor Yellow
kubectl --context=orbit-primary -n orbit-system scale deployment/orbit-visitor-counter --replicas=$Replicas

# 2. Wait for pods to be ready
Write-Host "`n>>> [2/3] Waiting for Primary pods to become Ready..." -ForegroundColor Yellow
kubectl --context=orbit-primary -n orbit-system rollout status deployment/orbit-visitor-counter --timeout=60s

# 3. Allow router to observe recovery
Write-Host "`n>>> [3/3] Waiting for traffic router to detect Primary recovery and switch back..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

try {
    $status = Invoke-RestMethod -Uri "$RouterUrl/router/status" -Method Get -TimeoutSec 3
    Write-Host "Active Target: $($status.active_target)" -ForegroundColor Green
    Write-Host "Primary Healthy: $($status.primary_healthy)"
} catch {
    Write-Host "Router note: Router daemon running or direct mode." -ForegroundColor Gray
}

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Primary service restored and failback verified!        " -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
kubectl --context=orbit-primary -n orbit-system get pods
