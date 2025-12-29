# Production Best Practices Guide

This guide covers best practices for running StaticWaves POD Studio in production on RunPod.

## 🎯 Production Readiness Checklist

### Before Going Live

#### Security
- [ ] Change default `SESSION_SECRET` in environment variables
- [ ] Configure CORS to specific origins (not `*`)
- [ ] Enable rate limiting in production
- [ ] Review and set security headers
- [ ] Disable debug logging (`LOG_LEVEL=warn` or `error`)
- [ ] Implement authentication (if handling sensitive data)
- [ ] Set up HTTPS (handled by RunPod proxy)
- [ ] Review file upload limits

#### Performance
- [ ] Enable gzip compression (already configured in nginx)
- [ ] Set appropriate cache headers
- [ ] Optimize image sizes in application
- [ ] Configure CDN for static assets (optional)
- [ ] Set resource limits appropriately
- [ ] Test under expected load
- [ ] Optimize database queries (if applicable)

#### Monitoring
- [ ] Enable health check monitoring
- [ ] Configure alerts for critical metrics
- [ ] Set up log aggregation
- [ ] Monitor error rates
- [ ] Track response times
- [ ] Monitor resource usage

#### Reliability
- [ ] Set up automated backups
- [ ] Test disaster recovery procedures
- [ ] Configure auto-restart policies
- [ ] Implement graceful shutdown
- [ ] Test failover scenarios
- [ ] Document incident response procedures

#### Documentation
- [ ] Document deployment procedures
- [ ] Create runbooks for common issues
- [ ] Document configuration options
- [ ] Maintain change log
- [ ] Update README with production URLs

## 🔒 Security Best Practices

### Environment Variables

**DO:**
```bash
# Use specific, strong secrets
SESSION_SECRET=a0f8j2l9k3m4n5o6p7q8r9s0t1u2v3w4x5y6z7
API_KEY=sk_live_real_key_not_test

# Use environment-specific values
NODE_ENV=production
CORS_ORIGIN=https://yourapp.com
```

**DON'T:**
```bash
# Don't use default or weak secrets
SESSION_SECRET=change-me-in-production
API_KEY=test123

# Don't enable debug in production
DEBUG=true
LOG_LEVEL=debug
```

### CORS Configuration

**Production nginx.conf:**
```nginx
# Replace * with your actual domain
add_header Access-Control-Allow-Origin "https://yourapp.com" always;
add_header Access-Control-Allow-Methods "GET, POST, OPTIONS" always;
add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
```

### Rate Limiting

Add to nginx.conf:
```nginx
# Limit requests
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;
limit_req_status 429;

server {
    location / {
        limit_req zone=one burst=20 nodelay;
        # ... rest of config
    }
}
```

## ⚡ Performance Optimization

### Resource Allocation

**CPU-Intensive Applications:**
```
Recommended: 4-8 vCPUs
Memory: 8-16 GB RAM
GPU: Only if using AI features
```

**Standard Web Applications:**
```
Recommended: 2-4 vCPUs
Memory: 4-8 GB RAM
GPU: Not needed
```

### Nginx Tuning

**For High Traffic:**
```nginx
worker_processes auto;
worker_connections 4096;

# Enable caching
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=10g inactive=60m;

# Connection keepalive
keepalive_timeout 65;
keepalive_requests 100;
```

### Image Optimization

1. **Use WebP format** for images (smaller size)
2. **Lazy load** off-screen images
3. **Use CDN** for static assets
4. **Compress** all images before upload

## 📊 Monitoring Setup

### Metrics to Track

**Application Metrics:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (% of requests)
- Active users (concurrent)

**System Metrics:**
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Network throughput (MB/s)

**Business Metrics:**
- User signups/day
- Feature usage
- Conversion rates

### Alert Thresholds

```yaml
Critical Alerts:
  - Application down: Health check fails for 3 minutes
  - High error rate: >5% errors for 5 minutes
  - Memory critical: >95% usage
  - Disk full: >95% usage

Warning Alerts:
  - High CPU: >80% for 10 minutes
  - High memory: >85% for 10 minutes
  - Slow responses: p95 >1000ms for 5 minutes
  - Disk filling: >80% usage
```

### Log Aggregation

**Using ELK Stack:**
```bash
# Install filebeat
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.0.0-linux-x86_64.tar.gz

# Configure to ship nginx logs
# to Elasticsearch
```

**Using CloudWatch (AWS):**
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb

# Configure log shipping
```

## 🔄 Deployment Strategies

### Blue-Green Deployment

```bash
# 1. Deploy new version (Green)
deploy-pipeline.sh

# 2. Test Green deployment
curl https://green-pod-id-80.proxy.runpod.net/health.json

# 3. Switch traffic to Green
# Update DNS or load balancer

# 4. Monitor for issues
# If OK: Terminate Blue
# If issues: Switch back to Blue
```

### Rolling Updates

```bash
# For multiple pods
# 1. Update pod 1, wait, verify
# 2. Update pod 2, wait, verify
# 3. Continue for all pods
```

### Canary Deployment

```bash
# 1. Deploy new version to 10% of pods
# 2. Monitor metrics for 1 hour
# 3. If OK: Deploy to 50%
# 4. If still OK: Deploy to 100%
# 5. If issues: Rollback
```

## 💾 Backup & Recovery

### What to Backup

```
Critical:
  - User data (if applicable)
  - Configuration files
  - Environment variables
  - Database dumps
  - Upload files

Optional:
  - Application logs (keep 30 days)
  - System logs
  - Metrics data
```

### Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/workspace/backups"
DATE=$(date +%Y%m%d-%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup uploads
tar -czf "$BACKUP_DIR/uploads-$DATE.tar.gz" /workspace/uploads

# Backup database (if applicable)
# pg_dump -U user database > "$BACKUP_DIR/db-$DATE.sql"

# Upload to S3 (if configured)
# aws s3 cp "$BACKUP_DIR/" s3://my-bucket/backups/ --recursive

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -type f -mtime +30 -delete
```

### Recovery Procedure

```bash
# 1. Deploy new pod
# 2. Download latest backup
aws s3 cp s3://my-bucket/backups/latest.tar.gz .

# 3. Extract
tar -xzf latest.tar.gz -C /workspace/

# 4. Restore database
# psql -U user database < backup.sql

# 5. Verify
curl https://pod-id-80.proxy.runpod.net/health.json
```

## 🚨 Incident Response

### Response Levels

**P0 - Critical (Complete Outage):**
- Response Time: Immediate
- Actions:
  1. Alert on-call team
  2. Create incident channel
  3. Begin investigation
  4. Implement fix or rollback
  5. Post-mortem within 24 hours

**P1 - High (Partial Outage):**
- Response Time: <30 minutes
- Actions:
  1. Investigate and diagnose
  2. Implement fix
  3. Monitor for recovery
  4. Document resolution

**P2 - Medium (Degraded Performance):**
- Response Time: <2 hours
- Actions:
  1. Investigate during business hours
  2. Schedule fix
  3. Monitor metrics

**P3 - Low (Minor Issues):**
- Response Time: <24 hours
- Actions:
  1. Add to backlog
  2. Fix in next release

### Common Issues & Solutions

**Pod Not Starting:**
```bash
# 1. Check Docker logs
docker logs <container-id>

# 2. Verify image exists
docker pull your-username/staticwaves-pod-studio:beta

# 3. Test locally
docker run -p 8080:80 your-username/staticwaves-pod-studio:beta

# 4. Check RunPod status page
https://status.runpod.io
```

**High Memory Usage:**
```bash
# 1. Identify memory leaks
top -p $(pgrep nginx)

# 2. Restart nginx
nginx -s reload

# 3. If persistent, restart pod

# 4. Upgrade memory tier
```

**Slow Response Times:**
```bash
# 1. Check CPU usage
top

# 2. Check nginx logs for slow requests
tail -f /var/log/nginx/access.log

# 3. Enable caching
# Update nginx.conf

# 4. Scale horizontally (add pods)
```

## 📈 Scaling Guide

### When to Scale

**Vertical Scaling (Bigger Pod):**
- CPU consistently >70%
- Memory consistently >80%
- Response times increasing
- Single-threaded bottleneck

**Horizontal Scaling (More Pods):**
- Need redundancy
- Geographic distribution
- Load balancing required
- Cost-effective scaling

### Scaling Checklist

- [ ] Monitor current metrics
- [ ] Identify bottleneck (CPU, memory, network)
- [ ] Test with larger tier or additional pods
- [ ] Configure load balancer (if horizontal)
- [ ] Update DNS/routing
- [ ] Monitor after scaling
- [ ] Adjust resource limits

### Cost Optimization

**Strategies:**
```
1. Use Spot Pods (50-70% cheaper)
   - Pros: Significant cost savings
   - Cons: May be terminated

2. Right-size Resources
   - Start small, scale up as needed
   - Monitor actual usage

3. Use CPU-only Pods
   - If not using GPU features
   - 80% cost reduction

4. Schedule Scaling
   - Scale down during off-hours
   - Scale up for peak times

5. Use CDN
   - Reduce bandwidth costs
   - Faster global delivery
```

## 🔍 Debugging in Production

### Safe Debugging Practices

**DO:**
- Use structured logging
- Enable debug logs temporarily
- Use feature flags for debug mode
- Monitor logs in real-time
- Use replica environment first

**DON'T:**
- Enable debug in production permanently
- Log sensitive data (passwords, tokens)
- Test fixes directly in production
- Restart services during peak hours

### Debug Commands

```bash
# View real-time logs
tail -f /var/log/nginx/access.log

# Check running processes
ps aux | grep nginx

# Monitor resources
top
htop

# Test health endpoint
curl http://localhost/health.json

# Run diagnostics
./runpod-config/diagnose.sh

# Check optimization status
cat /tmp/pod-optimization-status.json
```

## 📝 Change Management

### Deployment Process

1. **Develop** in feature branch
2. **Test** locally
3. **Review** code changes
4. **Deploy** to staging
5. **Test** in staging
6. **Deploy** to production during maintenance window
7. **Monitor** for 1 hour
8. **Rollback** if issues detected

### Version Control

```bash
# Tag releases
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0

# Use semantic versioning
# Major.Minor.Patch
# 1.0.0 -> 1.0.1 (patch)
# 1.0.1 -> 1.1.0 (minor)
# 1.1.0 -> 2.0.0 (major)
```

## 🎓 Production Checklist

### Daily
- [ ] Check pod status
- [ ] Review error logs
- [ ] Monitor resource usage
- [ ] Verify backups completed

### Weekly
- [ ] Review performance metrics
- [ ] Check for security updates
- [ ] Test disaster recovery
- [ ] Review and rotate logs

### Monthly
- [ ] Review and optimize costs
- [ ] Update dependencies
- [ ] Review security policies
- [ ] Conduct load testing
- [ ] Update documentation

### Quarterly
- [ ] Security audit
- [ ] Performance review
- [ ] Capacity planning
- [ ] Disaster recovery drill

---

**Last Updated:** 2025-12-29
**Version:** 6.0-beta.1
