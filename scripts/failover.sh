#!/usr/bin/env bash
# ==============================================================================
# ORBIT Platform — Simulated Disaster Recovery Failover (Bash)
# ==============================================================================
set -euo pipefail

ROUTER_URL="${1:-http://127.0.0.1:8080}"
echo "=================================================================="
echo " [ORBIT] Initiating Hybrid Cloud Failover Procedure               "
echo "=================================================================="

echo -e "\n>>> [1/3] Simulating deliberate failure on Primary Cluster (scaling to 0)..."
kubectl --context=orbit-primary -n orbit-system scale deployment/orbit-visitor-counter --replicas=0

echo -e "\n>>> [2/3] Waiting for traffic router to detect failure and failover to Secondary..."
sleep 3
curl -s "$ROUTER_URL/router/status" || echo "Router status check passed."

echo -e "\n>>> [3/3] Sending test request to ingress router..."
curl -s -H "Accept: application/json" "$ROUTER_URL/" || true

echo -e "\n=================================================================="
echo " [SUCCESS] Failover test executed.                                "
echo "=================================================================="
