#!/usr/bin/env bash
# ==============================================================================
# ORBIT Platform — Cluster Health Check & Status Verification (Bash)
# ==============================================================================
PRIMARY_URL="${1:-http://localhost:5001}"
SECONDARY_URL="${2:-http://localhost:5002}"

echo "=================================================================="
echo " [ORBIT] Hybrid Cloud Health Check Verification                   "
echo "=================================================================="

check_endpoint() {
    local name="$1"
    local url="$2"
    echo -n "Probing $name ($url/health)... "
    if curl -s -f --max-time 3 "$url/health" > /tmp/health_resp.json 2>/dev/null; then
        echo -e "\e[32m[HEALTHY]\e[0m"
        cat /tmp/health_resp.json
        echo ""
        return 0
    else
        echo -e "\e[31m[UNAVAILABLE / DOWN]\e[0m"
        return 1
    fi
}

check_endpoint "PRIMARY CLUSTER" "$PRIMARY_URL" || true
check_endpoint "SECONDARY CLUSTER" "$SECONDARY_URL" || true
