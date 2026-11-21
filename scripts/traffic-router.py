"""
ORBIT Platform — Hybrid Cloud Intelligent Traffic Router & Failover Controller
Simulates enterprise cloud ingress routing with automated health checking and failover.
Listens on local port 8080 and proxies traffic to Primary or Secondary cluster.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.error
import threading
import time
import json
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [TrafficRouter] %(message)s'
)
logger = logging.getLogger("orbit-router")

# Cluster Target Configurations
PRIMARY_URL = "http://127.0.0.1:5001"
SECONDARY_URL = "http://127.0.0.1:5002"
ROUTER_PORT = 8080

# State
state = {
    "active_target": "PRIMARY",
    "primary_healthy": True,
    "secondary_healthy": True,
    "primary_url": PRIMARY_URL,
    "secondary_url": SECONDARY_URL,
    "failover_count": 0,
    "last_failover_time": None,
    "last_check_time": None,
    "check_count": 0
}

def check_target_health(url):
    try:
        req = urllib.request.Request(f"{url}/health", headers={"User-Agent": "ORBIT-Router-HealthCheck/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode('utf-8'))
                return True, data.get("status", "healthy")
            return False, f"HTTP {response.status}"
    except Exception as e:
        return False, str(e)

def health_monitor_daemon():
    while True:
        try:
            p_ok, p_msg = check_target_health(state["primary_url"])
            s_ok, s_msg = check_target_health(state["secondary_url"])
            
            state["primary_healthy"] = p_ok
            state["secondary_healthy"] = s_ok
            state["last_check_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            state["check_count"] += 1

            if not p_ok and state["active_target"] == "PRIMARY":
                logger.warning(f"🚨 PRIMARY CLUSTER DOWN ({p_msg})! Initiating automatic failover to SECONDARY...")
                state["active_target"] = "SECONDARY"
                state["failover_count"] += 1
                state["last_failover_time"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                logger.info(f"✅ Failover complete. Active routing target: SECONDARY ({state['secondary_url']})")

            elif p_ok and state["active_target"] == "SECONDARY":
                logger.info("🔄 PRIMARY CLUSTER RECOVERED! Performing automated failback to PRIMARY...")
                state["active_target"] = "PRIMARY"
                logger.info(f"✅ Failback complete. Active routing target: PRIMARY ({state['primary_url']})")

        except Exception as e:
            logger.error(f"Health monitor error: {e}")
        time.sleep(2)

class RouterHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress default noisy console logs

    def do_GET(self):
        if self.path == "/router/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(state, indent=2).encode('utf-8'))
            return

        target_base = state["primary_url"] if state["active_target"] == "PRIMARY" else state["secondary_url"]
        target_full = f"{target_base}{self.path}"

        try:
            headers = {k: v for k, v in self.headers.items() if k.lower() != 'host'}
            headers["X-Forwarded-Host"] = self.headers.get("Host", "localhost")
            headers["X-ORBIT-Routed-By"] = "HybridCloudTrafficRouter"
            headers["X-ORBIT-Active-Cluster"] = state["active_target"]

            req = urllib.request.Request(target_full, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as response:
                content = response.read()
                self.send_response(response.status)
                for header, val in response.headers.items():
                    if header.lower() not in ['transfer-encoding', 'content-length']:
                        self.send_header(header, val)
                self.send_header("X-ORBIT-Cluster", state["active_target"])
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        except urllib.error.HTTPError as e:
            body = e.read()
            self.send_response(e.code)
            for header, val in e.headers.items():
                self.send_header(header, val)
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            err_payload = {
                "error": "Bad Gateway",
                "message": f"Failed to route traffic to {state['active_target']} ({target_base}): {str(e)}",
                "active_cluster": state["active_target"],
                "primary_healthy": state["primary_healthy"],
                "secondary_healthy": state["secondary_healthy"]
            }
            self.wfile.write(json.dumps(err_payload).encode('utf-8'))

def main():
    if len(sys.argv) > 1:
        state["primary_url"] = sys.argv[1]
    if len(sys.argv) > 2:
        state["secondary_url"] = sys.argv[2]

    monitor_thread = threading.Thread(target=health_monitor_daemon, daemon=True)
    monitor_thread.start()

    server = HTTPServer(("0.0.0.0", ROUTER_PORT), RouterHandler)
    logger.info(f"🚀 ORBIT Hybrid Cloud Router listening on http://0.0.0.0:{ROUTER_PORT}")
    logger.info(f"   Primary Target:   {state['primary_url']}")
    logger.info(f"   Secondary Target: {state['secondary_url']}")
    logger.info(f"   Status Endpoint:  http://0.0.0.0:{ROUTER_PORT}/router/status")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down router...")
        server.server_close()

if __name__ == "__main__":
    main()
