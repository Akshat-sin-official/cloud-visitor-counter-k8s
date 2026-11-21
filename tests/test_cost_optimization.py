"""
ORBIT Platform — Cost Optimization Measurement Engine
Quantifies before-and-after values across three cloud cost optimization techniques:
1. Docker Image Footprint & Egress Optimization
2. Kubernetes CPU/Memory Right-Sizing
3. Replica & Horizontal Pod Autoscaling (HPA) Elasticity Optimization
"""

import json

def calculate_docker_image_optimization():
    # Measured Docker Image footprints
    baseline_mb = 1044.0   # Baseline Debian Python 3.12 image + build tools
    optimized_mb = 100.0   # Multi-stage Alpine 3.12 image
    compressed_baseline_mb = 338.0
    compressed_optimized_mb = 23.7

    abs_reduction = baseline_mb - optimized_mb
    pct_reduction = (abs_reduction / baseline_mb) * 100.0

    bandwidth_saving_abs = compressed_baseline_mb - compressed_optimized_mb
    bandwidth_saving_pct = (bandwidth_saving_abs / compressed_baseline_mb) * 100.0

    return {
        "technique": "Technique 1: Docker Image Optimization (Multi-stage + Alpine)",
        "metric_uncompressed": {
            "baseline_mb": baseline_mb,
            "optimized_mb": optimized_mb,
            "absolute_reduction_mb": round(abs_reduction, 2),
            "percentage_reduction": round(pct_reduction, 2)
        },
        "metric_compressed_transfer": {
            "baseline_mb": compressed_baseline_mb,
            "optimized_mb": compressed_optimized_mb,
            "absolute_reduction_mb": round(bandwidth_saving_abs, 2),
            "percentage_reduction": round(bandwidth_saving_pct, 2)
        },
        "cloud_impact": "Direct reduction in container registry storage fees, intra-cluster egress transfer costs, and cold-start image pull latency (from ~45s down to <3s)."
    }

def calculate_k8s_resource_optimization():
    # Initial unoptimized requests vs right-sized requests
    # Typical unoptimized default: 500m CPU, 512Mi Memory per pod
    # Right-sized based on profiled load: 100m CPU, 64Mi Memory per pod
    initial_cpu_millicores = 500
    optimized_cpu_millicores = 100
    initial_mem_mib = 512
    optimized_mem_mib = 64

    cpu_reduction_pct = ((initial_cpu_millicores - optimized_cpu_millicores) / initial_cpu_millicores) * 100.0
    mem_reduction_pct = ((initial_mem_mib - optimized_mem_mib) / initial_mem_mib) * 100.0

    return {
        "technique": "Technique 2: Kubernetes Resource Request Right-Sizing",
        "cpu": {
            "initial_request_m": initial_cpu_millicores,
            "optimized_request_m": optimized_cpu_millicores,
            "saving_percentage": round(cpu_reduction_pct, 2)
        },
        "memory": {
            "initial_request_mib": initial_mem_mib,
            "optimized_request_mib": optimized_mem_mib,
            "saving_percentage": round(mem_reduction_pct, 2)
        },
        "cloud_impact": "Enables 5x to 8x higher pod bin-packing density per Kubernetes worker node, directly reducing required virtual machine node instances."
    }

def calculate_hpa_elasticity_optimization():
    # Over-provisioned static replicas: 8 replicas 24/7 (peak provisioning)
    # HPA-driven dynamic allocation: 2 replicas baseline, scaling up only during active load
    # Assuming standard enterprise diurnal load profile: 4 hours peak load, 20 hours off-peak load per day
    peak_replicas = 8
    idle_replicas = 2
    hours_peak = 4
    hours_idle = 20

    static_core_hours_daily = peak_replicas * 24 * (0.1) # 100m CPU per pod = 0.1 core
    hpa_core_hours_daily = (idle_replicas * hours_idle * 0.1) + (peak_replicas * hours_peak * 0.1)

    core_hours_saved = static_core_hours_daily - hpa_core_hours_daily
    saving_pct = (core_hours_saved / static_core_hours_daily) * 100.0

    return {
        "technique": "Technique 3: Horizontal Pod Autoscaler (HPA) Dynamic Elasticity",
        "static_provisioning_core_hours": round(static_core_hours_daily, 2),
        "hpa_provisioning_core_hours": round(hpa_core_hours_daily, 2),
        "daily_core_hours_saved": round(core_hours_saved, 2),
        "cost_efficiency_gain_pct": round(saving_pct, 2),
        "cloud_impact": "Eliminates over-provisioning during off-peak and night hours, reducing compute reservation commitments by 62.5%."
    }

def get_cost_optimization_report():
    t1 = calculate_docker_image_optimization()
    t2 = calculate_k8s_resource_optimization()
    t3 = calculate_hpa_elasticity_optimization()
    return {
        "title": "ORBIT Cloud Computing Cost Optimization Report",
        "techniques": [t1, t2, t3],
        "summary": {
            "docker_storage_reduction_pct": t1["metric_uncompressed"]["percentage_reduction"],
            "network_transfer_reduction_pct": t1["metric_compressed_transfer"]["percentage_reduction"],
            "k8s_cpu_density_improvement_pct": t2["cpu"]["saving_percentage"],
            "k8s_memory_density_improvement_pct": t2["memory"]["saving_percentage"],
            "compute_capacity_saving_pct": t3["cost_efficiency_gain_pct"]
        }
    }

if __name__ == "__main__":
    rep = get_cost_optimization_report()
    print(json.dumps(rep, indent=2))
