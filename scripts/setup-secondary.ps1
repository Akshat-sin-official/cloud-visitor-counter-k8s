# ==============================================================================
# ORBIT Platform — Setup Secondary Minikube Cluster (PowerShell)
# Profile: orbit-secondary (Simulated Public Cloud DR Standby)
# ==============================================================================

param (
    [string]$Driver = "docker",
    [int]$Cpus = 2,
    [int]$Memory = 2200
)

$ErrorActionPreference = "Stop"
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " [ORBIT] Initializing SECONDARY Cluster (orbit-secondary)        " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# 1. Start Minikube profile
Write-Host "`n>>> [1/4] Starting Minikube profile 'orbit-secondary'..." -ForegroundColor Yellow
minikube start -p orbit-secondary --driver=$Driver --cpus=$Cpus --memory=$Memory --embed-certs

# 2. Load Docker images into cluster
Write-Host "`n>>> [2/4] Loading Docker image 'orbit-visitor-counter:latest' into orbit-secondary..." -ForegroundColor Yellow
minikube image load orbit-visitor-counter:latest -p orbit-secondary

# 3. Apply Kubernetes manifests
Write-Host "`n>>> [3/4] Applying Kubernetes manifests..." -ForegroundColor Yellow
kubectl --context=orbit-secondary apply -f kubernetes/secondary/00-namespace.yaml
kubectl --context=orbit-secondary apply -f kubernetes/secondary/01-redis.yaml
kubectl --context=orbit-secondary apply -f kubernetes/secondary/02-configmap.yaml
kubectl --context=orbit-secondary apply -f kubernetes/secondary/03-secret.yaml
kubectl --context=orbit-secondary apply -f kubernetes/secondary/04-visitor-counter.yaml

# 4. Wait for rollouts
Write-Host "`n>>> [4/4] Waiting for deployment rollouts to complete..." -ForegroundColor Yellow
kubectl --context=orbit-secondary -n orbit-system rollout status deployment/orbit-redis --timeout=120s
kubectl --context=orbit-secondary -n orbit-system rollout status deployment/orbit-visitor-counter --timeout=120s

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Secondary Cluster 'orbit-secondary' is fully deployed! " -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
kubectl --context=orbit-secondary -n orbit-system get pods,svc
