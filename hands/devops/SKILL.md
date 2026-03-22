---
name: devops-hand-skill
version: "1.0.0"
description: "Expert knowledge for AI DevOps automation -- CI/CD patterns, infrastructure monitoring, deployment strategies, and incident response playbooks"
runtime: prompt_only
---

# DevOps Expert Knowledge

## CI/CD Pipeline Patterns

### GitHub Actions Reference

**Basic workflow structure**:
```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: make build
      - name: Test
        run: make test
      - name: Lint
        run: make lint

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        run: make deploy
```

**Useful API endpoints**:
```bash
# List workflow runs
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/actions/runs?per_page=10"

# Get workflow run details
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID"

# Re-run failed jobs
curl -s -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
  "https://api.github.com/repos/OWNER/REPO/actions/runs/RUN_ID/rerun-failed-jobs"
```

### Pipeline Optimization Checklist

- [ ] Cache dependencies (node_modules, .cargo, pip cache)
- [ ] Parallelize independent jobs
- [ ] Use matrix builds for multi-version testing
- [ ] Skip unnecessary steps on non-code changes
- [ ] Use shallow clones for faster checkout
- [ ] Optimize Docker layer caching
- [ ] Run expensive tests only on main branch

---

## Infrastructure Monitoring

### Health Check Patterns

**HTTP endpoint check**:
```bash
curl -s -o /dev/null -w "%{http_code} %{time_total}s" --max-time 10 "$URL"
```

**TCP port check**:
```bash
nc -z -w5 hostname port && echo "UP" || echo "DOWN"
```

**SSL certificate expiry**:
```bash
echo | openssl s_client -servername HOST -connect HOST:443 2>/dev/null | \
  openssl x509 -noout -dates
```

**DNS resolution**:
```bash
dig +short hostname
```

**Disk usage**:
```bash
df -h | grep -v tmpfs
```

**Memory usage**:
```bash
free -h
```

### The Four Golden Signals

| Signal | What to Measure | Alert Threshold |
|--------|----------------|-----------------|
| **Latency** | Request duration | P95 > 500ms |
| **Traffic** | Requests per second | Deviation > 50% from baseline |
| **Errors** | Error rate percentage | > 1% of requests |
| **Saturation** | Resource utilization | CPU/Memory > 80% |

### Docker Monitoring Commands

```bash
# Container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Resource usage
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Container logs (last 100 lines)
docker logs --tail 100 CONTAINER_NAME

# Inspect container health
docker inspect --format='{{.State.Health.Status}}' CONTAINER_NAME
```

### Kubernetes Monitoring Commands

```bash
# Pod status across all namespaces
kubectl get pods --all-namespaces -o wide

# Resource usage
kubectl top pods --all-namespaces
kubectl top nodes

# Recent events (errors and warnings)
kubectl get events --sort-by=.lastTimestamp --field-selector type!=Normal

# Pod logs
kubectl logs POD_NAME -n NAMESPACE --tail=100

# Describe failing pod
kubectl describe pod POD_NAME -n NAMESPACE
```

---

## Deployment Strategies

### Blue-Green Deployment
```
1. Run current version on "Blue" environment
2. Deploy new version to "Green" environment
3. Run health checks on Green
4. Switch traffic from Blue to Green
5. Keep Blue as rollback target
6. After validation period, decommission Blue
```

### Canary Deployment
```
1. Deploy new version to small subset (5-10% of traffic)
2. Monitor error rates and latency
3. If healthy, gradually increase traffic (25% -> 50% -> 100%)
4. If problems detected, route all traffic back to old version
```

### Rolling Update
```
1. Update instances one at a time
2. Wait for health check to pass before updating next
3. If any instance fails health check, pause and alert
4. Continue until all instances updated
```

### Deployment Checklist
- [ ] All tests passing in CI
- [ ] Database migrations compatible (backward and forward)
- [ ] Feature flags configured for new features
- [ ] Monitoring and alerting in place
- [ ] Rollback procedure documented and tested
- [ ] On-call engineer notified
- [ ] Change request approved (if required)

---

## Incident Response

### Incident Lifecycle
```
Detection -> Triage -> Mitigation -> Investigation -> Resolution -> Post-mortem
```

### Severity Levels

| Level | Impact | Response Time | Example |
|-------|--------|--------------|---------|
| SEV1 | Full outage | Immediate | Production down |
| SEV2 | Major impact | 15 min | Core feature broken |
| SEV3 | Minor impact | 1 hour | Non-critical feature degraded |
| SEV4 | Low impact | Next business day | Cosmetic issue |

### Incident Response Template
```markdown
# Incident Report: [Title]
**Severity**: SEV[1-4]
**Status**: [Investigating | Mitigated | Resolved]
**Duration**: [Start time] - [End time]

## Timeline
- HH:MM - [Event or action taken]
- HH:MM - [Event or action taken]

## Root Cause
[What caused the incident]

## Impact
[Who was affected and how]

## Mitigation
[What was done to restore service]

## Resolution
[What was done to fix the root cause]

## Action Items
- [ ] [Preventive measure 1]
- [ ] [Preventive measure 2]

## Lessons Learned
[What we can improve]
```

---

## Infrastructure as Code

### Terraform Quick Reference

```bash
# Initialize
terraform init

# Plan changes
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan

# Show current state
terraform show

# Destroy resources (DANGEROUS)
terraform destroy
```

### Docker Compose Quick Reference

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f SERVICE_NAME

# Rebuild and restart
docker compose up -d --build SERVICE_NAME

# Scale a service
docker compose up -d --scale SERVICE_NAME=3
```

---

## Common Failure Diagnosis Playbooks

### Memory Leak Detection
```bash
# Track memory growth over time
while true; do
  ps aux --sort=-%mem | head -5 | awk '{print strftime("%H:%M:%S"), $2, $4"%", $11}'
  sleep 60
done

# Check for OOM kills
dmesg | grep -i "oom\|killed" | tail -20

# Kubernetes memory pressure
kubectl top pods --sort-by=memory | head -10
```

### DNS Failure Cascade
```bash
# Test DNS resolution
dig hostname +short
dig @8.8.8.8 hostname +short  # Bypass local DNS

# Check /etc/resolv.conf
cat /etc/resolv.conf

# Test from inside a container
kubectl exec -it POD -- nslookup hostname
```

### Database Connection Pool Exhaustion
```bash
# Check active connections (PostgreSQL)
psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
psql -c "SELECT max_conn FROM pg_settings WHERE name = 'max_connections';"

# Check for long-running queries
psql -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query
         FROM pg_stat_activity WHERE state != 'idle' ORDER BY duration DESC LIMIT 10;"
```

### Certificate Expiry Monitoring
```bash
# Check cert expiry for a list of domains
for domain in api.example.com app.example.com; do
  expiry=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | \
    openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
  echo "$domain: $expiry"
done
```

---

## Worked Examples

### Example 1: Zero-Downtime Deployment Pipeline

Full lifecycle from code merge to production traffic switch with rollback safety.

**Phases**: CI build and push image -> deploy to Green -> health-gate -> traffic switch -> monitor -> done (or rollback).

**Traffic switch script** (the critical step):
```bash
#!/bin/bash
set -euo pipefail
# Record current slot for rollback, then switch
CURRENT=$(kubectl get svc myapp-active -n production -o jsonpath='{.spec.selector.slot}')
echo "$CURRENT" > /tmp/rollback-slot
kubectl patch svc myapp-active -n production -p '{"spec":{"selector":{"slot":"green"}}}'
# Verify
sleep 5 && curl -sf https://api.example.com/api/health | jq '.version'
```

**Rollback**: read `/tmp/rollback-slot`, patch the service selector back, verify health.

**Decision flowchart**:
```
Code merged to main
  |
  v
CI build + test ----[FAIL]----> Block merge, notify author
  |
  [PASS]
  v
Deploy to Green
  |
  v
Health checks ------[FAIL]----> Alert on-call, keep Blue active
  |
  [PASS]
  v
Switch traffic to Green
  |
  v
Monitor 15 min -----[ERROR SPIKE]----> Rollback to Blue, open incident
  |
  [STABLE]
  v
Mark Green as new Blue, done
```

---

### Example 2: Production Incident Response

Walkthrough of a real-world SEV1 incident: API latency spike caused by a database connection pool exhaustion.

**Timeline**

| Time (UTC) | Event | Actor |
|------------|-------|-------|
| 14:02 | PagerDuty alert: P95 latency > 2s on `/api/orders` | Monitoring |
| 14:04 | On-call acknowledges, opens incident channel `#inc-2025-0312` | On-call engineer |
| 14:06 | Check dashboard: request queue depth spiking, error rate at 12% | On-call engineer |
| 14:10 | Identify DB connection pool at 100% utilization | On-call engineer |
| 14:12 | Find long-running query from analytics job (started 13:55) | On-call engineer |
| 14:14 | Kill the runaway query, pool starts draining | On-call engineer |
| 14:18 | Latency returns to normal, error rate drops to 0.2% | Monitoring |
| 14:20 | Incident mitigated, continue monitoring | On-call engineer |
| 14:45 | Root cause confirmed: analytics cron job without query timeout | Investigation |
| 15:00 | Incident resolved, post-mortem scheduled | Incident commander |

**Detection -- Alerting rules that fired**

```yaml
# Prometheus alerting rule
groups:
  - name: api-latency
    rules:
      - alert: HighAPILatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="api"}[5m])) > 2
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "P95 latency above 2s for 2+ minutes"
          runbook: "https://wiki.internal/runbooks/high-latency"
```

**Triage -- Quick diagnosis commands**

```bash
# 1. Check if it's a specific endpoint or global
curl -s "http://prometheus:9090/api/v1/query?query=topk(5,rate(http_request_duration_seconds_sum[5m])/rate(http_request_duration_seconds_count[5m]))" | jq '.data.result[] | {endpoint: .metric.handler, avg_latency: .value[1]}'

# 2. Check database connection pool
psql -c "SELECT count(*) as total, state FROM pg_stat_activity GROUP BY state;"

# 3. Find the blocking query
psql -c "SELECT pid, now() - query_start AS duration, query
         FROM pg_stat_activity
         WHERE state = 'active' AND now() - query_start > interval '1 minute'
         ORDER BY duration DESC LIMIT 5;"
```

**Mitigation -- Kill the offending query**

```bash
# Kill the long-running query by PID
psql -c "SELECT pg_terminate_backend(12345);"

# Verify pool is recovering
watch -n 2 'psql -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = '\''active'\'';"'
```

**Prevention -- Fix applied after incident**

```sql
-- Set statement timeout for analytics role
ALTER ROLE analytics_readonly SET statement_timeout = '300s';
```

```yaml
# Add connection pool monitoring alert
- alert: DBConnectionPoolNearCapacity
  expr: pg_stat_activity_count / pg_settings_max_connections > 0.8
  for: 1m
  labels:
    severity: warning
  annotations:
    summary: "DB connection pool above 80% capacity"
```

**Post-mortem action items**:
- [ ] Add `statement_timeout` to all non-interactive database roles
- [ ] Add connection pool utilization alerts (threshold: 80%)
- [ ] Move analytics queries to read replica
- [ ] Add circuit breaker to API when pool utilization exceeds 90%

---

### Example 3: Infrastructure Scaling Event

Scaling a Kubernetes deployment in response to sustained load increase.

**Phase 1 -- Alert triggers**

```
Alert: HighCPUUtilization
  Condition: avg(cpu_usage) > 80% for 10 minutes
  Current:   87% across 3 pods
  Namespace: production
  Deployment: order-service
```

**Phase 2 -- Capacity analysis**

```bash
kubectl top pods -l app=order-service -n production   # Per-pod CPU/memory
kubectl describe nodes | grep -A 5 "Allocated resources"  # Node headroom
kubectl get hpa order-service -n production            # Current HPA state
# Result: 87% CPU across 3 pods, 842 req/s (2x baseline)
```

**Phase 3 -- Scaling decision matrix**

| Metric | Current | Target | Action |
|--------|---------|--------|--------|
| CPU usage | 87% | < 70% | Scale out |
| Request rate | 842/s | - | 2x normal, sustained |
| Memory | 258Mi avg | 512Mi limit | Headroom OK |
| Pod count | 3 | 6 (estimated) | Double replicas |
| Node capacity | 72% | < 85% | Sufficient for 6 pods |

**Phase 4 -- Implement scaling**

```bash
# Option A: Manual scale (immediate)
kubectl scale deployment order-service -n production --replicas=6

# Option B: Adjust HPA for sustained load (preferred)
kubectl patch hpa order-service -n production \
  -p '{"spec":{"minReplicas":5,"maxReplicas":15}}'

# Monitor rollout
kubectl rollout status deployment/order-service -n production

# Watch pods come up
kubectl get pods -l app=order-service -n production -w
```

**Phase 5 -- Verify scaling**

Confirm via `kubectl top pods` (CPU should drop to ~45% per pod), check P95 latency is back below SLO, and verify error rate < 1%.

**Post-scaling actions**:
- [ ] Investigate root cause of traffic increase (marketing event? bot traffic? organic growth?)
- [ ] Update capacity planning spreadsheet
- [ ] If sustained, adjust resource requests/limits and HPA baselines
- [ ] Set calendar reminder to review and potentially scale down in 48h

---

## Observability Deep Dive

### Structured Logging

Use consistent JSON log format across all services for machine-parseable aggregation.

**Log format standard**: JSON with required fields: `timestamp`, `level`, `service`, `trace_id`, `span_id`, `request_id`, `message`. Add `error` and `context` (structured key-value) as needed.

**Log levels -- when to use each**:

| Level | Purpose | Example | Persisted |
|-------|---------|---------|-----------|
| `error` | Requires human attention | Payment processing failed | 90 days |
| `warn` | Degraded but recoverable | Retry succeeded on 2nd attempt | 30 days |
| `info` | Business-significant events | Order placed, user logged in | 14 days |
| `debug` | Developer troubleshooting | Cache hit/miss, query timing | 3 days |
| `trace` | Fine-grained flow tracking | Function entry/exit, variable state | 1 day (sampled) |

**Correlation IDs**: generate `X-Request-ID` at API gateway, propagate through all downstream calls. Query across services by filtering on `request_id.keyword` in Elasticsearch/OpenSearch.

### Distributed Tracing

**Core concepts**: A Trace is the end-to-end request path. Each service call is a Span with timing. Spans nest to show the call tree (e.g., API Gateway -> Order Service -> DB Query + Payment Service -> Stripe API).

**OpenTelemetry propagation**: `traceparent: 00-<trace-id>-<span-id>-<flags>`, `tracestate: vendor=value`.

**Useful trace queries (Jaeger/Tempo)**:
```bash
curl -s "http://jaeger:16686/api/traces?service=order-service&minDuration=1s&limit=20"  # Slow traces
curl -s "http://jaeger:16686/api/traces?service=order-service&tags=error%3Dtrue&limit=20"  # Error traces
```

### Alerting Best Practices

**Avoid alert fatigue -- rules of thumb**:
- Every alert must have a runbook link
- Every alert must be actionable (if no one needs to act, it is a log, not an alert)
- Group related alerts to avoid notification storms
- Use inhibition rules: if the cluster is down, suppress per-pod alerts

**SLO-based alerting (burn rate)**:
```yaml
# SLO: 99.9% availability = 43.2 min/month error budget
# Fast burn (exhausts budget in 2h): error_ratio > 14.4 * 0.001 for 2m -> critical
# Slow burn (exhausts budget in 3d): error_ratio > 3 * 0.001 for 15m -> warning
groups:
  - name: slo-burn-rate
    rules:
      - alert: SLOBurnRateCritical
        expr: sum(rate(http_requests_total{code=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > (14.4 * 0.001)
        for: 2m
        labels: { severity: critical }
      - alert: SLOBurnRateWarning
        expr: sum(rate(http_requests_total{code=~"5.."}[1h])) / sum(rate(http_requests_total[1h])) > (3 * 0.001)
        for: 15m
        labels: { severity: warning }
```

**Runbook template**: Each alert runbook should cover: what the alert means (one sentence), impact scope, diagnosis steps (dashboard + commands), mitigation (quick fix vs proper fix), and escalation path (who to contact after 15 min).

### Metrics Collection Patterns

**RED Method (request-scoped services)**:

| Metric | What | PromQL Example |
|--------|------|----------------|
| **R**ate | Requests per second | `sum(rate(http_requests_total[5m]))` |
| **E**rrors | Failed requests per second | `sum(rate(http_requests_total{code=~"5.."}[5m]))` |
| **D**uration | Latency distribution | `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` |

**USE Method (infrastructure resources)**:

| Metric | What | Example Check |
|--------|------|---------------|
| **U**tilization | % time resource is busy | `avg(rate(node_cpu_seconds_total{mode!="idle"}[5m]))` |
| **S**aturation | Queue depth / backlog | `node_load1 / count(node_cpu_seconds_total{mode="idle"})` |
| **E**rrors | Error event count | `rate(node_disk_io_time_weighted_seconds_total[5m])` |

**When to use which**:
- RED for services that handle requests (APIs, web servers, message consumers)
- USE for infrastructure (CPU, memory, disk, network interfaces, queues)
- Combine both for a complete picture

---

## Security Operations

### Secret Management

**Principles**:
- Never store secrets in source code, environment variables (in Dockerfiles), or container images
- Use a secrets manager (Vault, AWS Secrets Manager, K8s Secrets with encryption at rest)
- Rotate secrets on a schedule and immediately after any suspected compromise
- Audit all secret access

**Vault pattern -- inject secrets at runtime**:
```bash
# Store a secret
vault kv put secret/myapp/db \
  username="app_user" \
  password="$(openssl rand -base64 32)"

# Read a secret (application startup)
vault kv get -format=json secret/myapp/db | jq -r '.data.data.password'

# Enable audit logging
vault audit enable file file_path=/var/log/vault-audit.log
```

**Kubernetes secrets -- from Vault using sidecar injector**:

Annotate the pod template with `vault.hashicorp.com/agent-inject: "true"`, specify the role and secret path. The Vault agent sidecar renders secrets to `/vault/secrets/` and the app sources them at startup. Key annotations: `agent-inject-secret-<name>` for the path, `agent-inject-template-<name>` for the rendering template.

**Secret rotation checklist**:
- [ ] Generate new secret value
- [ ] Update secret in secrets manager
- [ ] Restart/reload affected services (rolling, not all-at-once)
- [ ] Verify services authenticate with new secret
- [ ] Revoke the old secret value
- [ ] Confirm no services are still using the old secret

### Container Security Scanning

```bash
# Scan image for vulnerabilities (Trivy) -- fail CI on critical
trivy image --exit-code 1 --severity CRITICAL registry.example.com/myapp:$CI_COMMIT_SHA

# Scan K8s cluster for misconfigurations
trivy k8s --report summary cluster
```

**Dockerfile security essentials**: use pinned base image tags (not `:latest`), run as non-root (`USER app`), copy only needed files, never bake secrets into image layers.

### Network Security Policies

**Kubernetes NetworkPolicy -- default deny with explicit allow**:
```yaml
# Default deny all ingress, then allow specific paths
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-gateway-to-orders
  namespace: production
spec:
  podSelector:
    matchLabels: { app: order-service }
  ingress:
    - from:
        - podSelector:
            matchLabels: { app: api-gateway }
      ports:
        - { protocol: TCP, port: 8080 }
```

Apply a `default-deny-ingress` policy (empty `podSelector`, `policyTypes: [Ingress]`) per namespace first, then layer allow rules on top.

### Compliance as Code

**Policy enforcement with OPA/Gatekeeper**: use `K8sRequiredResources` constraints to enforce `limits.cpu`, `limits.memory`, `requests.cpu`, `requests.memory` on all pods in production namespaces.

**Quick compliance audit commands**:
```bash
# Find pods without resource limits
kubectl get pods -A -o json | jq -r '.items[] | select(.spec.containers[].resources.limits == null) | .metadata.namespace + "/" + .metadata.name'
# Find containers running as root
kubectl get pods -A -o json | jq -r '.items[] | select(.spec.containers[].securityContext.runAsNonRoot != true) | .metadata.namespace + "/" + .metadata.name'
# Find ingress without TLS
kubectl get ingress -A -o json | jq -r '.items[] | select(.spec.tls == null) | .metadata.namespace + "/" + .metadata.name'
```

---

## Automation Patterns

### Auto-Remediation

**Restart on OOM (Kubernetes)**:
```yaml
# Built-in: set resource limits and let K8s handle OOM restarts
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
        - name: myapp
          resources:
            limits:
              memory: "512Mi"
            requests:
              memory: "256Mi"
          # Liveness probe: restart if unhealthy
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 10
            failureThreshold: 3
```

**Scale on load (HPA with custom metrics)**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: order-service
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: order-service }
  minReplicas: 3
  maxReplicas: 20
  behavior:
    scaleUp:   { stabilizationWindowSeconds: 60,  policies: [{ type: Percent, value: 50, periodSeconds: 60 }] }
    scaleDown: { stabilizationWindowSeconds: 300, policies: [{ type: Percent, value: 25, periodSeconds: 120 }] }
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
    - type: Pods
      pods: { metric: { name: http_requests_per_second }, target: { type: AverageValue, averageValue: "1000" } }
```

**Rotate secrets on expiry (CronJob)**:

Use a K8s CronJob (e.g., monthly `"0 2 1 * *"`) with a `secret-rotator` service account that: generates new password -> updates Vault -> alters DB role password -> triggers rolling restart via `kubectl rollout restart`.

### GitOps Workflow

**Repository as source of truth**:
```
infrastructure-repo/
  |-- apps/
  |   |-- order-service/
  |   |   |-- deployment.yaml
  |   |   |-- service.yaml
  |   |   |-- hpa.yaml
  |   |   `-- kustomization.yaml
  |   `-- payment-service/
  |       |-- deployment.yaml
  |       `-- kustomization.yaml
  |-- base/
  |   |-- namespace.yaml
  |   |-- network-policies.yaml
  |   `-- resource-quotas.yaml
  `-- overlays/
      |-- staging/
      |   `-- kustomization.yaml
      `-- production/
          `-- kustomization.yaml
```

**Reconciliation loop (ArgoCD application)**:
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: order-service
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/org/infrastructure-repo.git
    targetRevision: main
    path: apps/order-service
  destination: { server: "https://kubernetes.default.svc", namespace: production }
  syncPolicy:
    automated: { prune: true, selfHeal: true }
    syncOptions: [CreateNamespace=true]
    retry: { limit: 3, backoff: { duration: 5s, factor: 2, maxDuration: 3m } }
```

**GitOps deployment flow**:
```
Developer pushes image tag update to infrastructure-repo
  |
  v
ArgoCD detects drift between git state and cluster state
  |
  v
ArgoCD syncs: applies manifests from git to cluster
  |
  v
Kubernetes rolls out new pods
  |
  v
ArgoCD verifies health (readiness probes pass)
  |
  [HEALTHY] --> Done
  [DEGRADED] --> ArgoCD marks sync as failed, alerts on-call
```

### Database Backup and Restore

**Automated backup (PostgreSQL)** -- run via cron `0 */6 * * *`:
```bash
#!/bin/bash
set -euo pipefail
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="production"
BACKUP_DIR="/backups/postgres"

pg_dump -Fc -Z 9 "$DB_NAME" > "${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump"
aws s3 cp "${BACKUP_DIR}/${DB_NAME}_${TIMESTAMP}.dump" \
  "s3://backups-bucket/postgres/" --storage-class STANDARD_IA
find "$BACKUP_DIR" -name "*.dump" -mtime +30 -delete
```

**Restore procedure**:
```bash
#!/bin/bash
set -euo pipefail
BACKUP_FILE=$1  # e.g., "production_20250315_060000.dump"
RESTORE_DB="production_restore"

aws s3 cp "s3://backups-bucket/postgres/$BACKUP_FILE" /tmp/restore.dump
psql -c "DROP DATABASE IF EXISTS $RESTORE_DB;" && psql -c "CREATE DATABASE $RESTORE_DB;"
pg_restore -d "$RESTORE_DB" -j 4 --no-owner /tmp/restore.dump
# Verify: check row counts on key tables, then clean up
rm /tmp/restore.dump
```

### Disaster Recovery Runbook Template

**Recovery Objectives**: Define RTO (e.g., 1 hour) and RPO (e.g., 6 hours) per service.

**Prerequisites**: backup storage access, Terraform state access, DNS management access, stakeholder comms channel.

| Scenario | Key Steps |
|----------|-----------|
| **Single service failure** | Check pod status -> restart deployment -> if fails, `kubectl rollout undo` -> verify health |
| **Database failure** | `pg_isready` -> promote replica (or restore from backup) -> update connection strings -> verify data integrity |
| **Full region outage** | Confirm via provider status page -> notify stakeholders -> switch DNS to DR region -> verify traffic -> failback when primary recovers |

**Communication template**: Subject `[INCIDENT] Service -- Status`. Body: what happened, impact, current status, ETA, next update time.

**Post-recovery checklist**: health checks passing, data integrity verified, monitoring restored, backups resumed, incident report filed, post-mortem scheduled within 48h.
