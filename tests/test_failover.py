"""
ORBIT Platform — Automated Hybrid Cloud Failover & Recovery Test Suite
Validates the failover controller, health probe thresholds, traffic redirection, and recovery.
"""

import urllib.request
import urllib.error
import subprocess
import json
import time
import sys

ROUTER_URL = "http://localhost:8080"
PRIMARY_CONTAINER = "orbit-visitor-counter"

def get_router_status():
    req = urllib.request.Request(f"{ROUTER_URL}/router/status")
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get_routed_count():
    req = urllib.request.Request(f"{ROUTER_URL}/api/count", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=4) as resp:
        return json.loads(resp.read().decode('utf-8'))

def run_failover_test():
    print("==================================================================")
    print(" ORBIT Platform — Automated Failover & Recovery Test Sequence    ")
    print("==================================================================")

    # 1. Verify router is operational and initially on PRIMARY
    print("\n[Step 1] Checking initial routing state...")
    init_state = get_router_status()
    print(f"  Active Target:   {init_state['active_target']}")
    print(f"  Primary Healthy: {init_state['primary_healthy']}")
    print(f"  Secondary Healthy: {init_state['secondary_healthy']}")
    assert init_state['active_target'] == 'PRIMARY', "Initial target must be PRIMARY"

    # 2. Query routed counter on primary
    c1 = get_routed_count()
    print(f"  Routed Response: Cluster={c1['cluster_name']}, Host={c1['hostname']}, Count={c1['visitor_count']}")

    # 3. Simulate Primary Outage (stop primary container)
    print("\n[Step 2] Injecting primary outage (docker stop orbit-visitor-counter)...")
    subprocess.run(["docker", "stop", PRIMARY_CONTAINER], check=True, stdout=subprocess.DEVNULL)
    print("  Primary container stopped. Waiting for health monitor detection...")
    
    start_detect = time.time()
    failover_detected = False
    for _ in range(10):
        time.sleep(1)
        state = get_router_status()
        if state['active_target'] == 'SECONDARY' and not state['primary_healthy']:
            elapsed = time.time() - start_detect
            print(f"  [PASS] Failover triggered in {round(elapsed, 2)}s! Active target: SECONDARY")
            failover_detected = True
            break

    assert failover_detected, "Failover to SECONDARY was not detected within timeout"

    # 4. Verify secondary serves traffic during primary outage
    print("\n[Step 3] Verifying secondary traffic serving during outage...")
    c2 = get_routed_count()
    print(f"  Routed Response: Cluster={c2['cluster_name']}, Host={c2['hostname']}, Count={c2['visitor_count']}")
    assert "SECONDARY" in c2['cluster_name'], "Traffic must be served by SECONDARY cluster"

    # 5. Restore primary
    print("\n[Step 4] Restoring primary container (docker start orbit-visitor-counter)...")
    subprocess.run(["docker", "start", PRIMARY_CONTAINER], check=True, stdout=subprocess.DEVNULL)
    print("  Primary container started. Waiting for failback detection...")

    start_restore = time.time()
    failback_detected = False
    for _ in range(12):
        time.sleep(1)
        state = get_router_status()
        if state['active_target'] == 'PRIMARY' and state['primary_healthy']:
            elapsed = time.time() - start_restore
            print(f"  [PASS] Failback completed in {round(elapsed, 2)}s! Active target: PRIMARY")
            failback_detected = True
            break

    assert failback_detected, "Failback to PRIMARY was not detected within timeout"

    # 6. Final verification
    print("\n[Step 5] Verifying final primary traffic serving...")
    c3 = get_routed_count()
    print(f"  Routed Response: Cluster={c3['cluster_name']}, Host={c3['hostname']}, Count={c3['visitor_count']}")
    assert "PRIMARY" in c3['cluster_name'] or "DOCKER-LOCAL" in c3['cluster_name']

    print("\n==================================================================")
    print(" [SUCCESS] Hybrid cloud failover and recovery test PASSED 100%!   ")
    print("==================================================================")

if __name__ == "__main__":
    try:
        run_failover_test()
        sys.exit(0)
    except Exception as e:
        print(f"\n[FAIL] Test aborted with error: {e}")
        sys.exit(1)
