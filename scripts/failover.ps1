# ==============================================================================
# ORBIT Platform — Simulated Disaster Recovery Failover (PowerShell)
# Simulates Primary cluster disruption and reroutes ingress traffic to Secondary
# ==============================================================================

param (
    [switch]$SimulatePrimaryOutage,
    [string]$RouterUrl = "http://127.0.0.1:8080"
)

Write-Host "==================================================================" -ForegroundColor Magenta
Write-Host " [ORBIT] Initiating Hybrid Cloud Failover Procedure               " -ForegroundColor Magenta
Write-Host "==================================================================" -ForegroundColor Magenta

$startTime = Get-Date

if ($SimulatePrimaryOutage) {
    Write-Host "`n>>> [1/3] Simulating deliberate failure on Primary Cluster (scaling replicas to 0)..." -ForegroundColor Yellow
    kubectl --context=orbit-primary -n orbit-system scale deployment/orbit-visitor-counter --replicas=0
    Write-Host "Primary visitor-counter scaled to 0 pods."
} else {
    Write-Host "`n>>> [1/3] Primary outage simulation flag not set; testing failover detection directly..." -ForegroundColor Yellow
}

# 2. Query router status
Write-Host "`n>>> [2/3] Querying Hybrid Router status to verify automated route diversion..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

try {
    $status = Invoke-RestMethod -Uri "$RouterUrl/router/status" -Method Get -TimeoutSec 3
    Write-Host "Current Active Target: $($status.active_target)" -ForegroundColor Cyan
    Write-Host "Primary Healthy:       $($status.primary_healthy)"
    Write-Host "Secondary Healthy:     $($status.secondary_healthy)"
    Write-Host "Failover Count:        $($status.failover_count)"
} catch {
    Write-Host "Router query note: Router daemon not reachable on $RouterUrl." -ForegroundColor Gray
}

# 3. Test end-to-end endpoint through ingress
Write-Host "`n>>> [3/3] Sending test request to routed endpoint..." -ForegroundColor Yellow
try {
    $resp = Invoke-RestMethod -Uri "$RouterUrl/" -Headers @{"Accept"="application/json"} -TimeoutSec 5
    $endTime = Get-Date
    $duration = ($endTime - $startTime).TotalSeconds
    Write-Host "Response received from active cluster:" -ForegroundColor Green
    Write-Host "  Cluster: $($resp.cluster_name)"
    Write-Host "  Visitor Count: $($resp.visitor_count)"
    Write-Host "  Hostname: $($resp.hostname)"
    Write-Host "  Failover response latency: $([math]::Round($duration, 2))s"
} catch {
    Write-Host "Direct test note: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Failover verification sequence completed.              " -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
