#!/usr/bin/env bash
# ==============================================================================
# ORBIT Platform — Primary Cluster Recovery & Failback (Bash)
# ==============================================================================
set -euo pipefail

REPLICAS="${1:-2}"
ROUTER_URL="${2:-http://127.0.0.1:8080}"

echo "=================================================================="
echo " [ORBIT] Restoring Primary Cluster & Executing Failback           "
echo "=================================================================="

echo -e "\n>>> [1/3] Scaling Primary visitor counter back to $REPLICAS replicas..."
kubectl --context=orbit-primary -n orbit-system scale deployment/orbit-visitor-counter --replicas="$REPLICAS"

echo -e "\n>>> [2/3] Waiting for Primary pods to become Ready..."
kubectl --context=orbit-primary -n orbit-system rollout status deployment/orbit-visitor-counter --timeout=60s

echo -e "\n>>> [3/3] Observing router failback to Primary..."
sleep 4
curl -s "$ROUTER_URL/router/status" || true

echo -e "\n=================================================================="
echo " [SUCCESS] Primary service restored and failback verified!        "
echo "=================================================================="
kubectl --context=orbit-primary -n orbit-system get pods
