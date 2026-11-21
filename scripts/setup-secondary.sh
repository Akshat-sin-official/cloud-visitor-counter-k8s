#!/usr/bin/env bash
# ==============================================================================
# ORBIT Platform — Setup Secondary Minikube Cluster (Bash)
# Profile: orbit-secondary (Simulated Public Cloud DR Standby)
# ==============================================================================
set -euo pipefail

echo "=================================================================="
echo " [ORBIT] Initializing SECONDARY Cluster (orbit-secondary)        "
echo "=================================================================="

# 1. Start Minikube profile
echo -e "\n>>> [1/4] Starting Minikube profile 'orbit-secondary'..."
minikube start -p orbit-secondary --driver=docker --cpus=2 --memory=2200 --embed-certs

# 2. Load Docker images into cluster
echo -e "\n>>> [2/4] Loading Docker image 'orbit-visitor-counter:latest' into orbit-secondary..."
minikube image load orbit-visitor-counter:latest -p orbit-secondary

# 3. Apply Kubernetes manifests
echo -e "\n>>> [3/4] Applying Kubernetes manifests..."
kubectl --context=orbit-secondary apply -f kubernetes/secondary/00-namespace.yaml
kubectl --context=orbit-secondary apply -f kubernetes/secondary/01-redis.yaml
kubectl --context=orbit-secondary apply -f kubernetes/secondary/02-configmap.yaml
kubectl --context=orbit-secondary apply -f kubernetes/secondary/03-secret.yaml
kubectl --context=orbit-secondary apply -f kubernetes/secondary/04-visitor-counter.yaml

# 4. Wait for rollouts
echo -e "\n>>> [4/4] Waiting for deployment rollouts to complete..."
kubectl --context=orbit-secondary -n orbit-system rollout status deployment/orbit-redis --timeout=120s
kubectl --context=orbit-secondary -n orbit-system rollout status deployment/orbit-visitor-counter --timeout=120s

echo "=================================================================="
echo " [SUCCESS] Secondary Cluster 'orbit-secondary' is fully deployed! "
echo "=================================================================="
kubectl --context=orbit-secondary -n orbit-system get pods,svc
