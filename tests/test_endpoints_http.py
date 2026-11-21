"""
ORBIT Platform — End-to-End Live HTTP Endpoint Integration Test Suite
Validates the live running service via HTTP:
- Health check (/health)
- Visitor increment and state consistency (/api/count and /)
- Redis connectivity verification
- Content negotiation (JSON vs HTML)
- CPU stress endpoint (/load)
- Metrics export (/metrics)
"""

import urllib.request
import urllib.error
import json
import time
import sys

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5001"

def log(msg, status="INFO"):
    colors = {
        "INFO": "\033[94m",
        "PASS": "\033[92m",
        "FAIL": "\033[91m",
        "WARN": "\033[93m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}[{status}] {msg}{colors['RESET']}")

def test_health():
    log(f"Testing GET {BASE_URL}/health...", "INFO")
    req = urllib.request.Request(f"{BASE_URL}/health")
    with urllib.request.urlopen(req, timeout=3) as resp:
        assert resp.status == 200, f"Expected status 200, got {resp.status}"
        data = json.loads(resp.read().decode('utf-8'))
        assert data.get("status") in ["healthy", "degraded"], f"Unexpected status: {data}"
        assert data.get("services", {}).get("web") == "up", "Web service must be up"
        log(f"Health check verified: Status={data.get('status')}, Redis={data.get('services', {}).get('redis')}", "PASS")
        return data

def test_visitor_count():
    log(f"Testing GET {BASE_URL}/api/count...", "INFO")
    req = urllib.request.Request(f"{BASE_URL}/api/count")
    with urllib.request.urlopen(req, timeout=3) as resp:
        assert resp.status == 200, f"Expected 200, got {resp.status}"
        d1 = json.loads(resp.read().decode('utf-8'))
        c1 = d1["visitor_count"]

    with urllib.request.urlopen(req, timeout=3) as resp:
        d2 = json.loads(resp.read().decode('utf-8'))
        c2 = d2["visitor_count"]

    assert c2 == c1 + 1, f"Counter increment failure: {c1} -> {c2}"
    log(f"Visitor increment verified: {c1} -> {c2} (Backend: {d2.get('backend')})", "PASS")

def test_html_render():
    log(f"Testing GET {BASE_URL}/ (HTML Response)...", "INFO")
    req = urllib.request.Request(f"{BASE_URL}/", headers={"Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=3) as resp:
        assert resp.status == 200
        content = resp.read().decode('utf-8')
        assert "ORBIT Cloud Telemetry" in content, "Missing brand title in HTML"
        assert "Total Verified Visitors" in content, "Missing counter label in HTML"
        log("HTML render & styling elements verified.", "PASS")

def test_json_negotiation():
    log(f"Testing GET {BASE_URL}/?format=json...", "INFO")
    req = urllib.request.Request(f"{BASE_URL}/?format=json")
    with urllib.request.urlopen(req, timeout=3) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert "visitor_count" in data
        assert "hostname" in data
        log(f"JSON negotiation verified: Pod Host={data.get('hostname')}", "PASS")

def test_metrics():
    log(f"Testing GET {BASE_URL}/metrics...", "INFO")
    req = urllib.request.Request(f"{BASE_URL}/metrics")
    with urllib.request.urlopen(req, timeout=3) as resp:
        assert resp.status == 200
        content = resp.read().decode('utf-8')
        assert "orbit_visitor_counter_uptime_seconds" in content
        log("Prometheus metrics verified.", "PASS")

def test_load_simulation():
    log(f"Testing GET {BASE_URL}/load?duration=1&cycles=200000 (CPU Burner)...", "INFO")
    start = time.time()
    req = urllib.request.Request(f"{BASE_URL}/load?duration=1&cycles=200000")
    with urllib.request.urlopen(req, timeout=5) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode('utf-8'))
        assert data.get("status") == "load_complete"
        elapsed = time.time() - start
        log(f"CPU load simulation verified: Duration={data.get('duration_seconds')}s, Client Elapsed={round(elapsed, 2)}s", "PASS")

def run_all():
    print("==================================================================")
    print(" ORBIT Cloud — Automated Live HTTP Integration Test Suite       ")
    print(f" Target: {BASE_URL}")
    print("==================================================================")
    results = []
    tests = [
        ("Health Check Endpoint", test_health),
        ("Visitor Count Increment & State", test_visitor_count),
        ("HTML Dashboard Presentation", test_html_render),
        ("JSON Content Negotiation", test_json_negotiation),
        ("Prometheus Metrics Export", test_metrics),
        ("CPU Load Generation Endpoint", test_load_simulation)
    ]

    for name, test_func in tests:
        try:
            test_func()
            results.append((name, "PASSED"))
        except Exception as e:
            log(f"{name} FAILED: {e}", "FAIL")
            results.append((name, f"FAILED: {e}"))

    print("\n==================================================================")
    print(" Test Execution Summary:")
    passed_count = sum(1 for _, s in results if s == "PASSED")
    for name, res in results:
        status_col = "\033[92mPASSED\033[0m" if res == "PASSED" else "\033[91mFAILED\033[0m"
        print(f"  - {name:<35}: {status_col}")
    print(f"\n Total: {len(results)} | Passed: {passed_count} | Failed: {len(results) - passed_count}")
    print("==================================================================")
    return passed_count == len(results)

if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
