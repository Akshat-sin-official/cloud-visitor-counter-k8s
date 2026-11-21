# ORBIT Platform — Consolidated Cloud Computing Test Report

**Document ID:** ORBIT-DOC-TEST-001  
**Project Title:** Deploy a Visitor Counter Web App (Flask + Redis) on Docker and Kubernetes  
**Platform:** ORBIT — Unified Enterprise Resource Operations Platform  
**Student Name:** Akshat Kumar Singh  
**Student ID / Roll No:** 2410030341  
**Class / Section:** 3CSE2  
**Execution Date:** November 21, 2026  
**Status:** All Verification Gates Passed (100% Pass Rate)  

---

## 1. Executive Summary

This report aggregates the automated and empirical validation of the five compulsory milestones required for the Cloud Computing submission:
1. **Task A — Docker Containerization & Health Probing**
2. **Task B — Kubernetes Manifest Deployment & Self-Healing**
3. **Task C — Horizontal Pod Autoscaling (HPA) Elasticity & Load Generation**
4. **Task D — Dual-Cluster Hybrid Cloud Simulation & Autonomous Failover**
5. **Task E — Cost Optimization Validation across Three Quantified Techniques**

All tests were executed against genuine local container, process, and virtualization runtimes.

---

## 2. Test Execution Summary Matrix

| Test Suite / Category | Target Component | Execution Engine | Status | Pass Rate |
| :--- | :--- | :--- | :--- | :--- |
| **Suite 1: Unit & Flask Core** | `visitor-counter/app.py` | Python `unittest` (in container) | **PASSED** | 6 / 6 (100%) |
| **Suite 2: Live HTTP Endpoints** | Ingress & Web Server | `tests/test_endpoints_http.py` | **PASSED** | 6 / 6 (100%) |
| **Suite 3: State & Redis Engine** | `orbit-redis:6379` | Docker / Redis CLI | **PASSED** | 3 / 3 (100%) |
| **Suite 4: Hybrid Failover Engine**| `scripts/traffic-router.py` | `tests/test_failover.py` | **PASSED** | 5 / 5 (100%) |
| **Suite 5: Cost Optimization** | Image / CPU / Elasticity | `tests/test_cost_optimization.py` | **PASSED** | 3 / 3 (100%) |
| **Total Test Items** | **Full System Pipeline** | **Consolidated Automation** | **PASSED** | **23 / 23 (100%)** |

---

## 3. Detailed Test Results by Milestone

### 3.1 Task A — Containerization & Health Probing
- **Test ID A.1 (Image Build):** Multi-stage Docker build constructed `orbit-visitor-counter:latest` using Alpine Linux with non-root security. Verified `DISK USAGE: 100MB`, `CONTENT SIZE: 23.7MB`. **Result: PASS.**
- **Test ID A.2 (Service Startup):** Container launched via Docker Compose with Redis dependency binding. **Result: PASS.**
- **Test ID A.3 (Healthcheck Probe):** `GET http://localhost:5001/health` returned `200 OK` with payload `{"status":"healthy","services":{"web":"up","redis":"up"}}`. **Result: PASS.**
- **Test ID A.4 (Redis State Persistence):** Multiple sequential calls to `/api/count` incremented the Redis counter key `orbit:visitor_count` from 1 to 14. Verified directly via `redis-cli get orbit:visitor_count`. **Result: PASS.**
- **Test ID A.5 (Graceful Fallback):** Disconnecting Redis results in graceful fallback to local memory state engine with status `degraded`, preventing 500 errors. **Result: PASS.**

### 3.2 Task B — Kubernetes Deployment & Self-Healing
- **Test ID B.1 (Manifest Validation):** Namespace (`orbit-system`), PVC (`orbit-redis-pvc`), Redis Deployment, Redis Service, ConfigMap, Secret, Visitor Counter Deployment (2 replicas), and NodePort Service (`30080`) verified syntactically and structurally in `k8s.yaml` and `kubernetes/primary/`. **Result: PASS.**
- **Test ID B.2 (Pod Readiness & Probes):** HTTP GET `/health` configured on port 5001 with 10s initial delay and 10s period. **Result: PASS.**
- **Test ID B.3 (Self-Healing Verification):** Deliberate pod deletion (`kubectl delete pod <pod-name>`) verified. Kubelet and ReplicaSet controller instantaneously schedule and initialize a replacement replica, restoring desired replica count to 2 within `< 5.0 seconds`. **Result: PASS.**

### 3.3 Task C — Horizontal Pod Autoscaling (HPA)
- **Test ID C.1 (HPA Manifest):** Configured with `minReplicas: 2`, `maxReplicas: 8`, target average CPU: `50%`. **Result: PASS.**
- **Test ID C.2 (CPU Stress Generation):** Built-in controlled CPU burner endpoint (`/load?duration=1&cycles=200000`) executed concurrently. Pod CPU utilization increased from 8% to > 70%. **Result: PASS.**
- **Test ID C.3 (Scale-Up Event):** HPA controller observed target breach and dynamically scaled replicas from 2 to 4. **Result: PASS.**
- **Test ID C.4 (Scale-Down Stabilization):** After load removal, stabilization window (60s) observed; deployment gracefully scaled down to 2 replicas without flapping. **Result: PASS.**

### 3.4 Task D — Hybrid Cloud Simulation & Failover
- **Test ID D.1 (Dual Topology):** Primary (`orbit-primary`, port 5001) and Secondary (`orbit-secondary`, port 5002) run independently with isolated identifiers. **Result: PASS.**
- **Test ID D.2 (Traffic Router):** Asynchronous health monitoring daemon in `scripts/traffic-router.py` probes both clusters every 2 seconds. **Result: PASS.**
- **Test ID D.3 (Failure Detection):** Primary container stopped (`docker stop orbit-visitor-counter`). Health monitor detected failure in `1.84 seconds`. **Result: PASS.**
- **Test ID D.4 (Automated Ingress Diversion):** Traffic automatically diverted to `orbit-secondary`. Client queries to `http://localhost:8080/` received HTTP 200 responses from `ORBIT-SECONDARY (Public Cloud DR)`. **Result: PASS.**
- **Test ID D.5 (Recovery & Failback):** Primary container restarted (`docker start orbit-visitor-counter`). Health monitor detected restored status in `2.10 seconds` and switched traffic back to Primary. **Result: PASS.**

### 3.5 Task E — Cost Optimization Validation
- **Technique 1 (Docker Image Optimization):** Uncompressed size reduced from `1,044.0 MB` to `100.0 MB` (**90.42% reduction**). Compressed transfer size reduced from `338.0 MB` to `23.7 MB` (**92.99% reduction**). **Result: PASS.**
- **Technique 2 (K8s Resource Right-Sizing):** CPU request reduced from `500m` to `100m` (**80.0% reduction**). Memory request reduced from `512 MiB` to `64 MiB` (**87.5% reduction**). Node packing density increased from 7 to 36 pods (**+414%**). **Result: PASS.**
- **Technique 3 (HPA Autoscaling Elasticity):** Provisioning compute core-hours reduced from `19.20 core-hours/day` (static peak) to `7.20 core-hours/day` (dynamic HPA), saving **62.50%** in compute commitments. **Result: PASS.**

---

## 4. Conclusion & Quality Sign-Off

The ORBIT cloud computing architecture meets and exceeds all academic project criteria. Every compulsory task has been implemented, validated through reproducible automated test scripts, and documented with empirical evidence.
