#!/bin/bash

# Health Monitoring Script for RunPod
# Monitors system health, application status, and sends alerts

set -e

# Configuration
HEALTH_CHECK_URL="${HEALTH_CHECK_URL:-http://localhost/health.json}"
CHECK_INTERVAL="${CHECK_INTERVAL:-30}"
LOG_FILE="${LOG_FILE:-/var/log/health-monitor.log}"
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEM=85
ALERT_THRESHOLD_DISK=90

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check application health endpoint
check_app_health() {
    local response=$(curl -s -w "\n%{http_code}" "$HEALTH_CHECK_URL" 2>/dev/null)
    local body=$(echo "$response" | head -n -1)
    local http_code=$(echo "$response" | tail -n 1)

    if [ "$http_code" = "200" ]; then
        local status=$(echo "$body" | grep -o '"status":"[^"]*"' | cut -d':' -f2 | tr -d '"')
        if [ "$status" = "healthy" ]; then
            echo "HEALTHY"
            return 0
        else
            echo "UNHEALTHY"
            return 1
        fi
    else
        echo "DOWN"
        return 1
    fi
}

# Check CPU usage
check_cpu() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    cpu_usage=${cpu_usage%.*}  # Convert to integer

    if [ "$cpu_usage" -gt "$ALERT_THRESHOLD_CPU" ]; then
        echo "CRITICAL:$cpu_usage%"
        return 1
    elif [ "$cpu_usage" -gt $((ALERT_THRESHOLD_CPU - 20)) ]; then
        echo "WARNING:$cpu_usage%"
        return 0
    else
        echo "OK:$cpu_usage%"
        return 0
    fi
}

# Check memory usage
check_memory() {
    local mem_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

    if [ "$mem_usage" -gt "$ALERT_THRESHOLD_MEM" ]; then
        echo "CRITICAL:$mem_usage%"
        return 1
    elif [ "$mem_usage" -gt $((ALERT_THRESHOLD_MEM - 20)) ]; then
        echo "WARNING:$mem_usage%"
        return 0
    else
        echo "OK:$mem_usage%"
        return 0
    fi
}

# Check disk usage
check_disk() {
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | tr -d '%')

    if [ "$disk_usage" -gt "$ALERT_THRESHOLD_DISK" ]; then
        echo "CRITICAL:$disk_usage%"
        return 1
    elif [ "$disk_usage" -gt $((ALERT_THRESHOLD_DISK - 20)) ]; then
        echo "WARNING:$disk_usage%"
        return 0
    else
        echo "OK:$disk_usage%"
        return 0
    fi
}

# Check GPU (if available)
check_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        local gpu_usage=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | head -n1)
        local gpu_mem=$(nvidia-smi --query-gpu=utilization.memory --format=csv,noheader,nounits | head -n1)
        local gpu_temp=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits | head -n1)

        echo "OK:GPU-${gpu_usage}%,MEM-${gpu_mem}%,TEMP-${gpu_temp}C"
        return 0
    else
        echo "N/A"
        return 0
    fi
}

# Check nginx status
check_nginx() {
    if pgrep -x nginx > /dev/null; then
        echo "RUNNING"
        return 0
    else
        echo "STOPPED"
        return 1
    fi
}

# Generate health report
generate_health_report() {
    local app_health=$(check_app_health)
    local cpu_status=$(check_cpu)
    local mem_status=$(check_memory)
    local disk_status=$(check_disk)
    local gpu_status=$(check_gpu)
    local nginx_status=$(check_nginx)

    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    cat > /tmp/health-report.json << EOF
{
  "timestamp": "$timestamp",
  "pod_id": "${RUNPOD_POD_ID:-local}",
  "overall_status": "$([ "$app_health" = "HEALTHY" ] && echo "healthy" || echo "degraded")",
  "checks": {
    "application": {
      "status": "$app_health",
      "endpoint": "$HEALTH_CHECK_URL"
    },
    "nginx": {
      "status": "$nginx_status"
    },
    "cpu": {
      "status": "$cpu_status"
    },
    "memory": {
      "status": "$mem_status"
    },
    "disk": {
      "status": "$disk_status"
    },
    "gpu": {
      "status": "$gpu_status"
    }
  },
  "metadata": {
    "uptime": "$(uptime -p)",
    "load_average": "$(uptime | awk -F'load average:' '{print $2}')"
  }
}
EOF

    echo "/tmp/health-report.json"
}

# Send alert (placeholder - integrate with your alerting system)
send_alert() {
    local severity=$1
    local message=$2

    log "[$severity] ALERT: $message"

    # TODO: Integrate with alerting system (Slack, Discord, PagerDuty, etc.)
    # Example:
    # curl -X POST https://hooks.slack.com/... -d "{\"text\":\"$message\"}"
}

# Main monitoring loop
monitor() {
    log "Starting health monitoring (interval: ${CHECK_INTERVAL}s)"

    while true; do
        # Generate health report
        local report_file=$(generate_health_report)

        # Parse report
        local overall_status=$(cat "$report_file" | grep -o '"overall_status":"[^"]*"' | cut -d':' -f2 | tr -d '"')
        local app_status=$(cat "$report_file" | grep -o '"application":{[^}]*}' | grep -o '"status":"[^"]*"' | cut -d':' -f2 | tr -d '"')

        # Log status
        if [ "$overall_status" = "healthy" ]; then
            log "${GREEN}✓ System healthy${NC}"
        else
            log "${YELLOW}⚠ System degraded${NC}"

            # Check for critical issues
            if [ "$app_status" = "DOWN" ]; then
                send_alert "CRITICAL" "Application is DOWN on pod ${RUNPOD_POD_ID:-local}"
            fi

            # Check resource alerts
            local cpu=$(check_cpu)
            local mem=$(check_memory)
            local disk=$(check_disk)

            if [[ "$cpu" == CRITICAL* ]]; then
                send_alert "CRITICAL" "CPU usage critical: $cpu"
            fi

            if [[ "$mem" == CRITICAL* ]]; then
                send_alert "CRITICAL" "Memory usage critical: $mem"
            fi

            if [[ "$disk" == CRITICAL* ]]; then
                send_alert "CRITICAL" "Disk usage critical: $disk"
            fi
        fi

        # Sleep before next check
        sleep "$CHECK_INTERVAL"
    done
}

# One-time health check
check_once() {
    local report_file=$(generate_health_report)
    cat "$report_file" | jq '.' 2>/dev/null || cat "$report_file"

    local overall_status=$(cat "$report_file" | grep -o '"overall_status":"[^"]*"' | cut -d':' -f2 | tr -d '"')

    if [ "$overall_status" = "healthy" ]; then
        echo -e "\n${GREEN}✓ System is healthy${NC}"
        exit 0
    else
        echo -e "\n${YELLOW}⚠ System has issues${NC}"
        exit 1
    fi
}

# Main
case "${1:-monitor}" in
    monitor)
        monitor
        ;;
    check)
        check_once
        ;;
    *)
        echo "Usage: $0 {monitor|check}"
        echo "  monitor - Start continuous monitoring"
        echo "  check   - Perform one-time health check"
        exit 1
        ;;
esac
