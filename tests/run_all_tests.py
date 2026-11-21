"""
ORBIT Platform — Consolidated Test Suite Runner
Executes all test suites in sequence and prints a unified test scorecard.
"""

import subprocess
import sys
import os

TESTS = [
    ("Live HTTP Integration Suite", ["python", "tests/test_endpoints_http.py", "http://localhost:5001"]),
    ("Hybrid Cloud Failover Suite", ["python", "tests/test_failover.py"]),
    ("Cost Optimization Calculations", ["python", "tests/test_cost_optimization.py"])
]

def main():
    print("==================================================================")
    print(" ORBIT CLOUD COMPUTING — CONSOLIDATED TEST HARNESS EXECUTION      ")
    print("==================================================================")
    results = []

    for name, cmd in TESTS:
        print(f"\n>>> Running: {name}...")
        proc = subprocess.run(cmd, capture_output=True, text=True)
        print(proc.stdout)
        if proc.stderr:
            print(proc.stderr)
        if proc.returncode == 0:
            results.append((name, "PASSED"))
        else:
            results.append((name, f"FAILED (Exit Code {proc.returncode})"))

    print("\n==================================================================")
    print(" CONSOLIDATED EXECUTION SCORECARD:")
    all_passed = True
    for name, status in results:
        passed = status == "PASSED"
        if not passed:
            all_passed = False
        badge = "\033[92m[PASS]\033[0m" if passed else "\033[91m[FAIL]\033[0m"
        print(f"  {badge} {name:<35}: {status}")

    print("==================================================================")
    if all_passed:
        print(" [ALL GATES PASSED] Project is 100% verified for submission!     ")
    else:
        print(" [WARNING] One or more verification gates failed.                ")
    print("==================================================================")
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
