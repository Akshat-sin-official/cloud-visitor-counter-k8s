from flask import Flask, jsonify, render_template_string, request
import os
import socket
import time
import redis
import logging

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
)
logger = logging.getLogger("orbit-visitor-counter")

app = Flask(__name__)

# Configurable environment variables
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
REDIS_DB = int(os.environ.get("REDIS_DB", 0))
REDIS_SOCKET_TIMEOUT = float(os.environ.get("REDIS_SOCKET_TIMEOUT", 1.5))
REDIS_KEY = os.environ.get("VISITOR_KEY", "orbit:visitor_count")
CLUSTER_NAME = os.environ.get("CLUSTER_NAME", "ORBIT-PRIMARY")
ENVIRONMENT = os.environ.get("ENVIRONMENT", "production")

# In-memory fallback if Redis is unavailable
_memory_counter = 0
_start_time = time.time()

def get_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        db=REDIS_DB,
        socket_timeout=REDIS_SOCKET_TIMEOUT,
        decode_responses=True
    )

def increment_visitor_count():
    global _memory_counter
    try:
        r = get_redis_client()
        count = r.incr(REDIS_KEY)
        return int(count), "redis"
    except Exception as e:
        logger.warning(f"Redis connection failure: {e}. Falling back to in-memory counter.")
        _memory_counter += 1
        return _memory_counter, "fallback_memory"

def get_redis_status():
    try:
        r = get_redis_client()
        r.ping()
        return True, "Connected"
    except Exception as e:
        return False, str(e)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ORBIT Cloud — Telemetry & Visitor Counter</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #090A0F;
            --bg-card: #12151F;
            --bg-card-border: #1E2333;
            --primary: #3B82F6;
            --primary-glow: rgba(59, 130, 246, 0.25);
            --accent-green: #10B981;
            --accent-amber: #F59E0B;
            --text-main: #F3F4F6;
            --text-muted: #9CA3AF;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(circle at 50% 0%, #151B2E 0%, var(--bg-base) 70%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 24px;
        }
        .container {
            width: 100%;
            max-width: 680px;
            background: var(--bg-card);
            border: 1px solid var(--bg-card-border);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 80px var(--primary-glow);
        }
        .header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 32px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--bg-card-border);
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .brand-badge {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #3B82F6, #1D4ED8);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 18px;
            color: white;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        }
        .brand-title {
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .brand-subtitle {
            font-size: 12px;
            color: var(--text-muted);
            font-family: 'JetBrains Mono', monospace;
        }
        .cluster-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 14px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            background: rgba(59, 130, 246, 0.1);
            color: #60A5FA;
            border: 1px solid rgba(59, 130, 246, 0.3);
        }
        .cluster-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #60A5FA;
            box-shadow: 0 0 8px #60A5FA;
        }
        .counter-hero {
            text-align: center;
            padding: 36px 20px;
            background: linear-gradient(180deg, rgba(30, 35, 51, 0.5) 0%, rgba(18, 21, 31, 0.8) 100%);
            border-radius: 16px;
            border: 1px solid var(--bg-card-border);
            margin-bottom: 32px;
            position: relative;
            overflow: hidden;
        }
        .counter-label {
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-muted);
            font-weight: 600;
            margin-bottom: 8px;
        }
        .counter-value {
            font-size: 72px;
            font-weight: 800;
            font-family: 'JetBrains Mono', monospace;
            background: linear-gradient(135deg, #FFFFFF 0%, #93C5FD 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            line-height: 1.1;
            margin-bottom: 8px;
        }
        .storage-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 11px;
            font-family: 'JetBrains Mono', monospace;
            padding: 4px 10px;
            border-radius: 6px;
            background: rgba(16, 185, 129, 0.1);
            color: #34D399;
            border: 1px solid rgba(16, 185, 129, 0.25);
        }
        .storage-badge.fallback {
            background: rgba(245, 158, 11, 0.1);
            color: #FBBF24;
            border: 1px solid rgba(245, 158, 11, 0.25);
        }
        .meta-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }
        .meta-card {
            background: #0D0F17;
            border: 1px solid var(--bg-card-border);
            border-radius: 12px;
            padding: 16px;
        }
        .meta-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            margin-bottom: 6px;
        }
        .meta-val {
            font-size: 13px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            color: #E5E7EB;
            word-break: break-all;
        }
        .footer {
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-muted);
            padding-top: 16px;
            border-top: 1px solid var(--bg-card-border);
        }
        .footer a {
            color: #60A5FA;
            text-decoration: none;
        }
        .footer a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="brand">
                <div class="brand-badge">O</div>
                <div>
                    <div class="brand-title">ORBIT Cloud Telemetry</div>
                    <div class="brand-subtitle">Visitor Counter Microservice</div>
                </div>
            </div>
            <div class="cluster-pill">
                <span class="cluster-dot"></span>
                <span>{{ cluster_name }}</span>
            </div>
        </div>

        <div class="counter-hero">
            <div class="counter-label">Total Verified Visitors</div>
            <div class="counter-value">{{ visitor_count }}</div>
            <div>
                {% if backend == 'redis' %}
                <span class="storage-badge">● Redis In-Memory State Engine (Key: {{ redis_key }})</span>
                {% else %}
                <span class="storage-badge fallback">▲ Fallback Local State Engine (Redis Unreachable)</span>
                {% endif %}
            </div>
        </div>

        <div class="meta-grid">
            <div class="meta-card">
                <div class="meta-title">Host / Pod Identifier</div>
                <div class="meta-val">{{ hostname }}</div>
            </div>
            <div class="meta-card">
                <div class="meta-title">Redis Target Host</div>
                <div class="meta-val">{{ redis_host }}:{{ redis_port }}</div>
            </div>
            <div class="meta-card">
                <div class="meta-title">Redis Connection Status</div>
                <div class="meta-val" style="color: {{ '#10B981' if redis_ok else '#F59E0B' }}">
                    {{ '● Active' if redis_ok else '○ Offline' }} ({{ redis_msg }})
                </div>
            </div>
            <div class="meta-card">
                <div class="meta-title">Service Uptime</div>
                <div class="meta-val">{{ uptime }}s</div>
            </div>
        </div>

        <div class="footer">
            <span>ORBIT Enterprise Resource Ops Mgt</span>
            <span>Endpoints: <a href="/health">/health</a> | <a href="/api/count">/api/count</a> | <a href="/metrics">/metrics</a></span>
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    count, backend = increment_visitor_count()
    redis_ok, redis_msg = get_redis_status()
    hostname = socket.gethostname()
    uptime = int(time.time() - _start_time)

    # Content negotiation
    if request.args.get("format") == "json" or "application/json" in request.headers.get("Accept", ""):
        return jsonify({
            "visitor_count": count,
            "backend": backend,
            "cluster_name": CLUSTER_NAME,
            "environment": ENVIRONMENT,
            "hostname": hostname,
            "redis": {
                "host": REDIS_HOST,
                "port": REDIS_PORT,
                "connected": redis_ok,
                "message": redis_msg
            },
            "uptime_seconds": uptime,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })

    return render_template_string(
        HTML_TEMPLATE,
        visitor_count=f"{count:,}",
        backend=backend,
        cluster_name=CLUSTER_NAME,
        hostname=hostname,
        redis_host=REDIS_HOST,
        redis_port=REDIS_PORT,
        redis_key=REDIS_KEY,
        redis_ok=redis_ok,
        redis_msg=redis_msg,
        uptime=uptime
    )

@app.route("/api/count", methods=["GET"])
def api_count():
    count, backend = increment_visitor_count()
    return jsonify({
        "visitor_count": count,
        "backend": backend,
        "cluster_name": CLUSTER_NAME,
        "hostname": socket.gethostname(),
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })

@app.route("/health", methods=["GET"])
@app.route("/healthz", methods=["GET"])
def health():
    redis_ok, redis_msg = get_redis_status()
    status_str = "healthy" if redis_ok else "degraded"
    status_code = 200

    return jsonify({
        "status": status_str,
        "cluster": CLUSTER_NAME,
        "services": {
            "web": "up",
            "redis": "up" if redis_ok else "down"
        },
        "details": {
            "redis_message": redis_msg,
            "hostname": socket.gethostname(),
            "uptime_seconds": int(time.time() - _start_time)
        }
    }), status_code

@app.route("/metrics", methods=["GET"])
def metrics():
    redis_ok, _ = get_redis_status()
    uptime = int(time.time() - _start_time)
    
    # Expose Prometheus-compatible plain metrics
    lines = [
        "# HELP orbit_visitor_counter_uptime_seconds Total runtime of the service in seconds.",
        "# TYPE orbit_visitor_counter_uptime_seconds counter",
        f"orbit_visitor_counter_uptime_seconds {uptime}",
        "# HELP orbit_visitor_counter_redis_connected Redis connectivity status (1=up, 0=down).",
        "# TYPE orbit_visitor_counter_redis_connected gauge",
        f"orbit_visitor_counter_redis_connected {1 if redis_ok else 0}",
    ]
    return "\n".join(lines) + "\n", 200, {"Content-Type": "text/plain; version=0.0.4"}

@app.route("/load", methods=["GET"])
def generate_cpu_load():
    """
    Controlled CPU load generator for Horizontal Pod Autoscaler (HPA) stress verification.
    Accepts:
      - duration: duration in seconds (default: 2, max: 30)
      - cycles: iteration count for arithmetic computation (default: 5000000)
    """
    duration = min(float(request.args.get("duration", 2.0)), 30.0)
    cycles = int(request.args.get("cycles", 5000000))
    start = time.time()
    
    # Generate controlled CPU-bound workload
    res = 0.0
    for i in range(1, cycles + 1):
        res += (i ** 0.5)
        if time.time() - start >= duration:
            break

    elapsed = time.time() - start
    return jsonify({
        "status": "load_complete",
        "hostname": socket.gethostname(),
        "duration_seconds": round(elapsed, 4),
        "target_duration": duration,
        "cycles_executed": cycles,
        "load_metric": round(res, 2)
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    logger.info(f"Starting ORBIT Visitor Counter on port {port} (Redis: {REDIS_HOST}:{REDIS_PORT})")
    app.run(host="0.0.0.0", port=port, debug=debug)
