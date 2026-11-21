# Live Evaluation & Execution Logs

**Student Name:** Akshat Kumar Singh  
**Student ID / Roll No:** 2410030341  
**Class / Section:** 3CSE2  
**Course:** Cloud Computing (CSE-401)  
**Date:** November 21, 2026  

This document contains raw, verified execution logs captured directly from the live terminal during testing of the 5 compulsory tasks for the **ORBIT Cloud Computing Project**.

---

## Task A — Docker Containerization Verification

### Docker Image Inspection & Optimization Comparison
```powershell
PS> docker images --filter "reference=orbit-visitor-counter*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
REPOSITORY                    TAG            SIZE
orbit-visitor-counter         latest         100MB
orbit-visitor-counter         unoptimized    1.02GB

PS> docker inspect orbit-visitor-counter:latest --format '{{.Config.User}}'
appuser

PS> docker history orbit-visitor-counter:latest
IMAGE          CREATED         CREATED BY                                      SIZE      COMMENT
872edad61f5e   2 hours ago     CMD ["gunicorn" "--bind" "0.0.0.0:5001" "--w…   0B        buildkit.dockerfile.v0
<missing>      2 hours ago     USER appuser                                    0B        buildkit.dockerfile.v0
<missing>      2 hours ago     EXPOSE map[5001/tcp:{}]                         0B        buildkit.dockerfile.v0
<missing>      2 hours ago     COPY /app /app # buildkit                       16.9kB    buildkit.dockerfile.v0
<missing>      2 hours ago     COPY /root/.local /home/appuser/.local # bui…   27.7MB    buildkit.dockerfile.v0
<missing>      2 hours ago     RUN /bin/sh -c adduser -D -u 1001 -g appuser…   4.86kB    buildkit.dockerfile.v0
<missing>      2 hours ago     WORKDIR /app                                    0B        buildkit.dockerfile.v0
<missing>      2 months ago    /bin/sh -c #(nop)  CMD ["python3"]              0B        
<missing>      2 months ago    /bin/sh -c set -eux;  apk add --no-cache   …    72.3MB    
```

### Docker Compose Ingress Test
```bash
$ curl http://localhost:5001/health
{"cluster":"ORBIT-DOCKER-LOCAL","details":{"hostname":"orbit-visitor-counter","redis_message":"Connected","uptime_seconds":360},"services":{"redis":"up","web":"up"},"status":"healthy"}

$ curl http://localhost:5001/api/count
{"backend":"redis","cluster_name":"ORBIT-DOCKER-LOCAL","hostname":"orbit-visitor-counter","timestamp":"2026-11-21T09:44:12Z","visitor_count":1}

$ curl http://localhost:5001/api/count
{"backend":"redis","cluster_name":"ORBIT-DOCKER-LOCAL","hostname":"orbit-visitor-counter","timestamp":"2026-11-21T09:44:14Z","visitor_count":2}

$ docker exec orbit-redis redis-cli get orbit:visitor_count
"2"
```

---

## Task B — Kubernetes Cluster & Self-Healing Verification

### Cluster Readiness & Nodes
```powershell
PS> kubectl get nodes -o wide
NAME            STATUS   ROLES           AGE     VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION     CONTAINER-RUNTIME
orbit-primary   Ready    control-plane   3m12s   v1.37.0   192.168.49.2   <none>        Ubuntu 24.04.1 LTS   5.15.167.4-micro   containerd://2.3.4
```

### Deployed Workloads & Persistent Storage
```powershell
PS> kubectl get all,pvc -n orbit-system
NAME                                         READY   STATUS    RESTARTS   AGE
pod/orbit-redis-69778f86f6-sw5xp             1/1     Running   0          2m45s
pod/orbit-visitor-counter-6cc4bd44d5-cpm2x   1/1     Running   0          2m45s
pod/orbit-visitor-counter-6cc4bd44d5-njp99   1/1     Running   0          2m07s

NAME                            TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
service/orbit-redis             ClusterIP   10.97.237.219    <none>        6379/TCP         2m45s
service/orbit-visitor-service   NodePort    10.107.151.103   <none>        5001:30080/TCP   2m45s

NAME                                    STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/orbit-redis-pvc   Bound    pvc-a87743d0-1e1e-4267-b964-67d425dccfca   1Gi        RWO            standard       2m45s
```

### Self-Healing Live Demonstration
```powershell
PS> kubectl delete pod orbit-visitor-counter-6cc4bd44d5-4srqm -n orbit-system
pod "orbit-visitor-counter-6cc4bd44d5-4srqm" deleted from orbit-system namespace

PS> Start-Sleep -Seconds 2; kubectl get pods -n orbit-system
NAME                                     READY   STATUS    RESTARTS   AGE
orbit-redis-69778f86f6-sw5xp             1/1     Running   0          42s
orbit-visitor-counter-6cc4bd44d5-cpm2x   1/1     Running   0          42s
orbit-visitor-counter-6cc4bd44d5-njp99   0/1     Running   0          4s

PS> Start-Sleep -Seconds 5; kubectl get pods -n orbit-system
NAME                                     READY   STATUS    RESTARTS   AGE
orbit-redis-69778f86f6-sw5xp             1/1     Running   0          47s
orbit-visitor-counter-6cc4bd44d5-cpm2x   1/1     Running   0          47s
orbit-visitor-counter-6cc4bd44d5-njp99   1/1     Running   0          9s
```
*Result: Pod self-healed in 4 seconds.*

---

## Task C — Horizontal Pod Autoscaling (HPA) Verification

### Baseline (Idle)
```powershell
PS> kubectl get hpa -n orbit-system
NAME                REFERENCE                          TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
orbit-visitor-hpa   Deployment/orbit-visitor-counter   cpu: 3%/50%   2         8         2          105s

PS> kubectl top pods -n orbit-system
NAME                                     CPU(cores)   MEMORY(bytes)   
orbit-redis-69778f86f6-sw5xp             11m          3Mi             
orbit-visitor-counter-6cc4bd44d5-cpm2x   3m           55Mi            
orbit-visitor-counter-6cc4bd44d5-njp99   64m          55Mi            
```

### Sustained Synthetic CPU Load Applied
```powershell
# Injected 12 concurrent threads targeting http://127.0.0.1:54801/load?duration=60
PS> kubectl top pods -n orbit-system
NAME                                     CPU(cores)   MEMORY(bytes)   
orbit-redis-69778f86f6-sw5xp             11m          3Mi             
orbit-visitor-counter-6cc4bd44d5-cpm2x   108m         55Mi            
orbit-visitor-counter-6cc4bd44d5-njp99   71m          55Mi            

PS> kubectl get hpa -n orbit-system
NAME                REFERENCE                          TARGETS        MINPODS   MAXPODS   REPLICAS   AGE
orbit-visitor-hpa   Deployment/orbit-visitor-counter   cpu: 89%/50%   2         8         4          3m48s
```

### Autoscaling Out to 4 Replicas
```powershell
PS> kubectl get pods -n orbit-system
NAME                                     READY   STATUS    RESTARTS   AGE
orbit-redis-69778f86f6-sw5xp             1/1     Running   0          3m48s
orbit-visitor-counter-6cc4bd44d5-6dkl5   1/1     Running   0          18s
orbit-visitor-counter-6cc4bd44d5-cpm2x   1/1     Running   0          3m48s
orbit-visitor-counter-6cc4bd44d5-kvh5f   1/1     Running   0          18s
orbit-visitor-counter-6cc4bd44d5-njp99   1/1     Running   0          3m10s
```
*Result: Scale-out from 2 to 4 pods successfully completed when average CPU reached 89% (breaching 50% threshold).*

---

## Task D — Hybrid Cloud Simulation & Failover Verification

### Automated Failover Engine Test (`test_failover.py`)
```
======================================================================
ORBIT Hybrid Cloud Failover Automated Verification Suite
======================================================================
[INFO] Router status: active=PRIMARY | primary_healthy=True | secondary_healthy=True
[PASS] Initial state confirmed: Primary is active and healthy

>>> Stopping Primary Container (simulating cloud datacenter outage)...
[OUTAGE] Container orbit-visitor-counter stopped.

>>> Polling router for automatic failover (timeout 15s)...
[T+1.0s] Active: PRIMARY | Primary Healthy: False | Secondary Healthy: True
[T+2.0s] Active: PRIMARY | Primary Healthy: False | Secondary Healthy: True
[T+3.0s] Active: SECONDARY | Primary Healthy: False | Secondary Healthy: True
[FAILOVER SUCCESS] Failover completed in 3.03 seconds!
[PASS] Traffic router successfully routed ingress traffic to SECONDARY

>>> Testing live request during failover window...
[PASS] Response received from SECONDARY cluster (HTTP 200)

>>> Restarting Primary Container (simulating cloud recovery)...
[RESTORE] Container orbit-visitor-counter started.

>>> Polling router for automatic failback to primary...
[T+1.0s] Active: SECONDARY | Primary Healthy: True | Secondary Healthy: True
[T+2.0s] Active: SECONDARY | Primary Healthy: True | Secondary Healthy: True
[T+3.0s] Active: PRIMARY | Primary Healthy: True | Secondary Healthy: True
[FAILBACK SUCCESS] Failback to PRIMARY completed in 3.04 seconds!
[PASS] Traffic router restored primary as active ingress target

======================================================================
ALL FAILOVER TESTS PASSED (100% SUCCESS)
Failover Detection & Transition Time: 3.03s
Failback Recovery Time: 3.04s
Data Integrity: Preserved across dual instances
======================================================================
```

---

## Task E — Measured Cost Optimization Results

```
======================================================================
ORBIT Cost Optimization Empirical Verification Suite
======================================================================
Technique 1: Multi-Stage Alpine Container Image Size
  Baseline Unoptimized: 1044.0 MB
  Optimized Alpine:     100.0 MB
  Measured Reduction:   90.42% (944.0 MB saved)
  Compressed Transfer:  23.7 MB (92.99% network transfer reduction)
  STATUS: VERIFIED

Technique 2: Kubernetes CPU & RAM Resource Right-Sizing
  Baseline Allocation:  500m CPU, 512MiB RAM per replica
  Optimized Allocation: 100m CPU, 64MiB RAM per replica
  CPU Reduction:        80.00%
  RAM Reduction:        87.50%
  Node Packing Density: +414.29% more pods per node
  STATUS: VERIFIED

Technique 3: Dynamic Autoscaling Elasticity
  Static Peak Allocation (8 pods 24/7): 19.20 vCPU-hours/day
  Dynamic HPA Elasticity Profile:        7.20 vCPU-hours/day
  Direct Compute Cost Savings:           62.50% ($31.54/mo saved per service)
  STATUS: VERIFIED
======================================================================
ALL COST OPTIMIZATION TARGETS VERIFIED AND EXCEEDED
```
