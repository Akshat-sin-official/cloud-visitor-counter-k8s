# ORBIT Cloud Computing — Comprehensive Screenshot & Evidence Capture Guide

This guide details the exact procedures and commands to capture the 21 mandatory evidentiary screenshots for the cloud computing project submission.

All screenshot files must be saved under `screenshots/` in PNG format.

---

### Fig 01 — Project Directory & Source Tree
- **Command:** `tree /F /A` or `Get-ChildItem -Recurse | Select-Object -First 30`
- **Output:** Shows `visitor-counter/`, `kubernetes/`, `scripts/`, `docs/`, `tests/`.
- **Target File:** `screenshots/01_project_directory.png`

### Fig 02 — Docker Image Build Execution
- **Command:** `docker build -t orbit-visitor-counter:latest -f visitor-counter/Dockerfile visitor-counter/`
- **Output:** Demonstrates multi-stage build (`builder` stage installing dependencies, `runner` stage copying wheels to non-root `/home/appuser`).
- **Target File:** `screenshots/02_docker_builds.png`

### Fig 03 — Running Docker Containers
- **Command:** `docker ps`
- **Output:** Shows `orbit-visitor-counter` (healthy, port 5001), `orbit-redis` (healthy, port 6380), and `orbit-postgres` (healthy, port 5433).
- **Target File:** `screenshots/03_docker_containers.png`

### Fig 04 — Visitor Counter Web UI in Browser
- **Action:** Open Chrome/Edge and navigate to `http://localhost:5001/`
- **Output:** Shows styled ORBIT dark-mode branded dashboard with visitor count, cluster name (`ORBIT-PRIMARY`), and Redis status (`● Active`).
- **Target File:** `screenshots/04_visitor_browser.png`

### Fig 05 — Redis Persistent Counter Values
- **Command:** `docker exec orbit-redis redis-cli get orbit:visitor_count`
- **Output:** Displays current integer counter value stored directly in Redis memory.
- **Target File:** `screenshots/05_redis_values.png`

### Fig 06 — Minikube Cluster Status
- **Command:** `minikube status -p orbit-primary`
- **Output:** Confirms host, kubelet, and apiserver are `Running`.
- **Target File:** `screenshots/06_minikube_status.png`

### Fig 07 — Kubernetes Deployments
- **Command:** `kubectl -n orbit-system get deployments`
- **Output:** Shows `orbit-redis` (1/1) and `orbit-visitor-counter` (2/2 ready).
- **Target File:** `screenshots/07_k8s_deployments.png`

### Fig 08 — Running Kubernetes Pods
- **Command:** `kubectl -n orbit-system get pods -o wide`
- **Output:** Shows all running pods with IP addresses, node names, and 0 restarts.
- **Target File:** `screenshots/08_running_pods.png`

### Fig 09 — Kubernetes Services
- **Command:** `kubectl -n orbit-system get services`
- **Output:** Shows `orbit-redis` (ClusterIP: 6379) and `orbit-visitor-service` (NodePort: 30080:5001).
- **Target File:** `screenshots/09_k8s_services.png`

### Fig 10 — Kubernetes Self-Healing Demonstration
- **Command:** `kubectl -n orbit-system delete pod <pod-name>; kubectl -n orbit-system get pods -w`
- **Output:** Shows immediate termination of target pod and instantaneous scheduling/readiness of replacement replica.
- **Target File:** `screenshots/10_self_healing.png`

### Fig 11 — Initial HPA Configuration
- **Command:** `kubectl -n orbit-system get hpa`
- **Output:** Shows `orbit-visitor-hpa`, targets `50% CPU`, min 2, max 8, current replicas 2.
- **Target File:** `screenshots/11_hpa_initial.png`

### Fig 12 — CPU Load Generation Under Load
- **Command:** `python -c "import urllib.request; [urllib.request.urlopen('http://localhost:5001/load?duration=2&cycles=1000000') for _ in range(20)]"`
- **Output:** Terminal output confirming synthetic load injection.
- **Target File:** `screenshots/12_cpu_load.png`

### Fig 13 — HPA Scaling Event
- **Command:** `kubectl -n orbit-system get hpa,pods`
- **Output:** Shows CPU utilization exceeding 50% (e.g. 78%/50%) and replicas scaling from 2 to 4 pods.
- **Target File:** `screenshots/13_hpa_scaling.png`

### Fig 14 — Dual Independent Minikube Clusters
- **Command:** `minikube profile list`
- **Output:** Lists both profiles: `orbit-primary` (running) and `orbit-secondary` (running).
- **Target File:** `screenshots/14_dual_clusters.png`

### Fig 15 — Primary Cluster Active Routing
- **Command:** `curl.exe -s http://localhost:8080/router/status; curl.exe -s http://localhost:8080/api/count`
- **Output:** Confirms `active_target: PRIMARY` and cluster name `ORBIT-PRIMARY`.
- **Target File:** `screenshots/15_primary_response.png`

### Fig 16 — Simulated Primary Failure
- **Command:** `docker stop orbit-visitor-counter; curl.exe -s http://localhost:8080/router/status`
- **Output:** Shows primary container stopped and `primary_healthy: false`.
- **Target File:** `screenshots/16_primary_failure.png`

### Fig 17 — Secondary Failover Active Serving
- **Command:** `curl.exe -s http://localhost:8080/api/count`
- **Output:** Shows traffic served seamlessly by `ORBIT-SECONDARY (Public Cloud DR)` within 3 seconds.
- **Target File:** `screenshots/17_secondary_failover.png`

### Fig 18 — Primary Recovery & Failback
- **Command:** `docker start orbit-visitor-counter; curl.exe -s http://localhost:8080/router/status`
- **Output:** Shows `primary_healthy: true` and `active_target: PRIMARY` restored.
- **Target File:** `screenshots/18_primary_recovery.png`

### Fig 19 — Docker Image Size Comparison (Technique 1)
- **Command:** `docker images orbit-visitor-counter`
- **Output:** Shows baseline Debian image (1,044 MB) vs optimized Alpine image (100 MB).
- **Target File:** `screenshots/19_image_comparison.png`

### Fig 20 — Kubernetes Resource Right-Sizing (Technique 2)
- **Command:** `python tests/test_cost_optimization.py`
- **Output:** JSON table demonstrating 80% CPU savings and 87.5% memory savings.
- **Target File:** `screenshots/20_k8s_resources.png`

### Fig 21 — HPA Replica Elasticity Model (Technique 3)
- **Command:** Profile output showing 62.5% reduction in daily compute commitments.
- **Target File:** `screenshots/21_replica_optimization.png`
