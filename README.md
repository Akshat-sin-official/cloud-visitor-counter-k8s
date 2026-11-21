# Deploy a Visitor Counter Web App (Flask + Redis) on Docker and Kubernetes

**Course:** Cloud Computing (CSE-401 / Cloud DevOps Engineering)  
**Student Name:** Akshat Kumar Singh  
**Student ID / Roll No:** `2410030341`  
**Class / Section:** `3CSE2`  
**Submission Date:** November 21, 2026  
**Repository:** [https://github.com/Akshat-sin-official/cloud-visitor-counter-k8s.git](https://github.com/Akshat-sin-official/cloud-visitor-counter-k8s.git)  
**Google Drive Submission Folder:** [Google Drive Archive](https://drive.google.com/drive/folders/1KufvIIZrEiJqsXuI5Fz78rXC87UwD8W_?usp=sharing)  

---

## 📌 Executive Summary

This repository hosts the complete academic implementation of an elastic, self-healing, and cost-optimized **Visitor Counter Web Application** engineered using **Flask, Redis, Docker, and Kubernetes**. 

It fulfills the 5 compulsory cloud computing milestones with empirical verification:
- **Task A — Docker Containerization:** Multi-stage Alpine Linux build (`python:3.12-alpine`), non-root execution (`appuser`, UID 10001), 90.4% image footprint reduction (from 1,044 MB to 100 MB).
- **Task B — Kubernetes Deployment & Self-Healing:** Declarative Kubernetes manifests (`k8s.yaml`), `PersistentVolumeClaim` (1Gi storage for Redis), ConfigMaps, Secrets, Liveness/Readiness probes, and verified 4.0-second automated pod self-healing.
- **Task C — Horizontal Pod Autoscaling (HPA):** Dynamic autoscaling from 2 to 8 replicas based on 50% CPU target utilization. Under sustained synthetic load (89% CPU), HPA dynamically scaled out replicas from 2 to 4 pods.
- **Task D — Hybrid Cloud Simulation with Failover:** Dual-cluster topology (`orbit-primary` on `:5001` and `orbit-secondary` on `:5002`) managed by an autonomous health-probing reverse proxy (`scripts/traffic-router.py`) executing automated failover in **3.03 seconds** and failback in **3.04 seconds**.
- **Task E — Cost Optimization:** Three measured techniques yielding **90.4% image reduction**, **80.0% CPU reservation reduction**, and **62.5% daily compute savings**.

---

## 📂 Repository Structure

```
├── app.py                      # Flask visitor counter microservice with Redis persistence
├── requirements.txt            # Minimal production dependencies (Flask, Redis, Gunicorn)
├── Dockerfile                  # Multi-stage Alpine production image (100 MB)
├── Dockerfile.unoptimized      # Baseline single-stage Debian image (1,044 MB)
├── docker-compose.yml          # Container orchestration (Visitor Counter + Redis 7)
├── k8s.yaml                    # Single consolidated Kubernetes deployment manifest
├── kubernetes/                 # Modular declarative Kubernetes manifests
│   ├── primary/                # Primary cluster (PVC, Deployments, Services, HPA)
│   └── secondary/              # Standby disaster recovery cluster
├── scripts/                    # Automation, health-probing & failover scripts
│   ├── traffic-router.py       # Asynchronous reverse proxy & health monitor daemon
│   ├── setup-primary.ps1/.sh   # Primary Minikube cluster setup
│   ├── setup-secondary.ps1/.sh # Secondary Minikube cluster setup
│   ├── failover.ps1/.sh        # Automated failover verification script
│   └── restore-primary.ps1/.sh # Automated failback restoration script
├── tests/                      # Automated test suites (23-gate verification)
│   ├── test_visitor_counter.py # Flask & Redis unit tests (6/6 passing)
│   ├── test_endpoints_http.py  # Live HTTP integration test suite
│   ├── test_failover.py        # Automated failover & failback test suite
│   ├── test_cost_optimization.py # Empirical cost calculations test suite
│   └── run_all_tests.py        # Consolidated test runner (100% pass rate)
├── docs/                       # Formal reports & architecture diagrams
│   ├── ORBIT_CLOUD_COMPUTING_PROJECT_REPORT.tex # Full academic LaTeX report source
│   ├── ORBIT_CLOUD_COMPUTING_PROJECT_REPORT.md  # Academic Markdown report
│   ├── TEST_REPORT.md          # 23-gate test execution report
│   ├── COST_OPTIMIZATION.md    # 3-technique cost optimization report
│   ├── LIVE_EVALUATION_LOGS.md # Raw terminal execution logs
│   └── system_architecture.svg # End-to-end cloud architecture diagram
└── screenshots/                # Evidence screenshots & capture instructions
```

---

## 🚀 Quickstart Guide

### 1. Run with Docker Compose
```bash
# Start Redis and the Visitor Counter
docker compose up -d

# Verify health and visitor count
curl http://localhost:5001/health
curl http://localhost:5001/api/count
```

### 2. Deploy to Kubernetes (Minikube)
```bash
# Start Minikube
minikube start -p orbit-primary --driver=docker

# Enable Metrics Server for HPA
minikube addons enable metrics-server -p orbit-primary

# Apply manifests and HPA
kubectl apply -f k8s.yaml
kubectl apply -f kubernetes/primary/hpa.yaml

# Verify pods and HPA
kubectl get pods,svc,hpa -n orbit-system
```

### 3. Run Hybrid Cloud Failover Simulation
```bash
# Start the intelligent traffic router on port 8080
python scripts/traffic-router.py http://localhost:5001 http://localhost:5002

# In a separate terminal, execute the automated failover test suite:
python tests/test_failover.py
```

### 4. Run All Test Suites
```bash
python tests/run_all_tests.py
```

---

## 📊 Summary of Cost Optimization (Task E)

| Technique | Baseline | Optimized | Savings |
| :--- | :--- | :--- | :--- |
| **1. Docker Image Size** | 1,044.0 MB | 100.0 MB | **90.42% Reduction** |
| **1b. Network Transfer** | 338.0 MB | 23.7 MB | **92.99% Bandwidth Saved** |
| **2. K8s CPU Request** | 500m / pod | 100m / pod | **80.00% Reservation Saved** |
| **2b. K8s RAM Request** | 512 MiB / pod | 64 MiB / pod | **87.50% Memory Saved** |
| **2c. Node Packing Density** | 7 pods/node | 36 pods/node | **+414% Density Improvement** |
| **3. Compute Commitment** | 19.20 vCPU-h/day | 7.20 vCPU-h/day | **62.50% Compute Saved** |

---

## 📄 Academic Project Report & LaTeX

The formal academic project report is available in two formats in the `docs/` folder:
- **LaTeX Source:** [`docs/ORBIT_CLOUD_COMPUTING_PROJECT_REPORT.tex`](docs/ORBIT_CLOUD_COMPUTING_PROJECT_REPORT.tex) (can be compiled in Overleaf or with `pdflatex`)
- **Markdown Document:** [`docs/ORBIT_CLOUD_COMPUTING_PROJECT_REPORT.md`](docs/ORBIT_CLOUD_COMPUTING_PROJECT_REPORT.md)
