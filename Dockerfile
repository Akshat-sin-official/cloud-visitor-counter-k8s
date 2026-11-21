# ==============================================================================
# ORBIT Platform — Visitor Counter Microservice (Optimized Production Build)
# Multi-stage Dockerfile achieving ultra-compact footprint & non-root security
# ==============================================================================

# Stage 1: Build & Dependency Wheel Builder
FROM python:3.12-alpine AS builder

WORKDIR /build

RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Minimal Distroless/Alpine Runtime Image
FROM python:3.12-alpine AS runner

LABEL maintainer="ORBIT Cloud DevOps Team"
LABEL description="ORBIT Flask + Redis Visitor Counter Microservice"
LABEL version="1.0.0"

# Security: Create non-privileged service user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application source
COPY app.py .

# Update environment to use user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5001 \
    REDIS_HOST=redis \
    REDIS_PORT=6379

# Change ownership to non-root user
RUN chown -R appuser:appgroup /app /home/appuser/.local

USER appuser

EXPOSE 5001

# Container Healthcheck
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/health', timeout=3)" || exit 1

# Launch with production Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "--threads", "4", "--worker-class", "gthread", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
