#!/usr/bin/env bash
# ==============================================================================
# ORBIT Platform — Setup Primary Minikube Cluster (Bash)
# Profile: orbit-primary (Simulated Private Cloud On-Premises Core)
# ==============================================================================
set -euo pipefail

echo "=================================================================="
echo " [ORBIT] Initializing PRIMARY Cluster (orbit-primary)            "
echo "=================================================================="

# 1. Start Minikube profile
echo -e "\n>>> [1/5] Starting Minikube profile 'orbit-primary'..."
minikube start -p orbit-primary --driver=docker --cpus=2 --memory=2200 --embed-certs

# 2. Enable Metrics Server for HPA
echo -e "\n>>> [2/5] Enabling metrics-server addon on orbit-primary..."
minikube addons enable metrics-server -p orbit-primary

# 3. Load Docker images into cluster
echo -e "\n>>> [3/5] Loading Docker image 'orbit-visitor-counter:latest' into orbit-primary..."
minikube image load orbit-visitor-counter:latest -p orbit-primary

# 4. Apply Kubernetes manifests
echo -e "\n>>> [4/5] Applying Kubernetes manifests..."
kubectl --context=orbit-primary apply -f kubernetes/primary/00-namespace.yaml
kubectl --context=orbit-primary apply -f kubernetes/primary/01-redis.yaml
kubectl --context=orbit-primary apply -f kubernetes/primary/02-configmap.yaml
kubectl --context=orbit-primary apply -f kubernetes/primary/03-secret.yaml
kubectl --context=orbit-primary apply -f kubernetes/primary/04-visitor-counter.yaml
kubectl --context=orbit-primary apply -f kubernetes/primary/hpa.yaml

# 5. Wait for rollouts
echo -e "\n>>> [5/5] Waiting for deployment rollouts to complete..."
kubectl --context=orbit-primary -n orbit-system rollout status deployment/orbit-redis --timeout=120s
kubectl --context=orbit-primary -n orbit-system rollout status deployment/orbit-visitor-counter --timeout=120s

echo "=================================================================="
echo " [SUCCESS] Primary Cluster 'orbit-primary' is fully deployed!     "
echo "=================================================================="
kubectl --context=orbit-primary -n orbit-system get pods,svc,hpa
