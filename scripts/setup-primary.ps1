# ==============================================================================
# ORBIT Platform — Setup Primary Minikube Cluster (PowerShell)
# Profile: orbit-primary (Simulated Private Cloud On-Premises Core)
# ==============================================================================

param (
    [string]$Driver = "docker",
    [int]$Cpus = 2,
    [int]$Memory = 2200
)

$ErrorActionPreference = "Stop"
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " [ORBIT] Initializing PRIMARY Cluster (orbit-primary)            " -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# 1. Start Minikube profile
Write-Host "`n>>> [1/5] Starting Minikube profile 'orbit-primary'..." -ForegroundColor Yellow
minikube start -p orbit-primary --driver=$Driver --cpus=$Cpus --memory=$Memory --embed-certs

# 2. Enable Metrics Server for HPA
Write-Host "`n>>> [2/5] Enabling metrics-server addon on orbit-primary..." -ForegroundColor Yellow
minikube addons enable metrics-server -p orbit-primary

# 3. Load Docker images into cluster
Write-Host "`n>>> [3/5] Loading Docker image 'orbit-visitor-counter:latest' into orbit-primary..." -ForegroundColor Yellow
minikube image load orbit-visitor-counter:latest -p orbit-primary

# 4. Apply Kubernetes manifests
Write-Host "`n>>> [4/5] Applying Kubernetes manifests..." -ForegroundColor Yellow
kubectl --context=orbit-primary apply -f kubernetes/primary/00-namespace.yaml
kubectl --context=orbit-primary apply -f kubernetes/primary/01-redis.yaml
kubectl --context=orbit-primary apply -f kubernetes/primary/02-configmap.yaml
kubectl --context=orbit-primary apply -f kubernetes/primary/03-secret.yaml
kubectl --context=orbit-primary apply -f kubernetes/primary/04-visitor-counter.yaml
kubectl --context=orbit-primary apply -f kubernetes/primary/hpa.yaml

# 5. Wait for rollouts
Write-Host "`n>>> [5/5] Waiting for deployment rollouts to complete..." -ForegroundColor Yellow
kubectl --context=orbit-primary -n orbit-system rollout status deployment/orbit-redis --timeout=120s
kubectl --context=orbit-primary -n orbit-system rollout status deployment/orbit-visitor-counter --timeout=120s

Write-Host "`n==================================================================" -ForegroundColor Green
Write-Host " [SUCCESS] Primary Cluster 'orbit-primary' is fully deployed!     " -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
kubectl --context=orbit-primary -n orbit-system get pods,svc,hpa
