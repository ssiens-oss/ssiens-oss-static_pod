#!/bin/bash

# Diagnostic Tool for RunPod Pod
# Troubleshoots common issues and generates diagnostic report

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================="
echo "RunPod Pod Diagnostic Tool"
echo "========================================="
echo ""

# Diagnostic Report File
REPORT_FILE="/tmp/diagnostic-report-$(date +%Y%m%d-%H%M%S).txt"

log_report() {
    echo "$1" | tee -a "$REPORT_FILE"
}

# Check 1: Environment Variables
check_environment() {
    echo -e "${BLUE}[1/10] Checking Environment Variables...${NC}"

    log_report "=== Environment Variables ==="

    local required_vars=("NODE_ENV" "RUNPOD_POD_ID")
    local all_ok=true

    for var in "${required_vars[@]}"; do
        if [ -n "${!var}" ]; then
            log_report "  ✓ $var: ${!var}"
        else
            log_report "  ⚠ $var: Not set"
            all_ok=false
        fi
    done

    if [ "$all_ok" = true ]; then
        echo -e "${GREEN}  ✓ Environment variables OK${NC}"
    else
        echo -e "${YELLOW}  ⚠ Some environment variables missing${NC}"
    fi
    echo ""
}

# Check 2: Nginx Status
check_nginx() {
    echo -e "${BLUE}[2/10] Checking Nginx...${NC}"

    log_report "=== Nginx Status ==="

    if pgrep -x nginx > /dev/null; then
        log_report "  ✓ Nginx is running"
        echo -e "${GREEN}  ✓ Nginx process active${NC}"

        # Check nginx config
        if nginx -t 2>&1 | grep -q "successful"; then
            log_report "  ✓ Nginx configuration valid"
        else
            log_report "  ✗ Nginx configuration has errors"
            nginx -t 2>&1 | tee -a "$REPORT_FILE"
        fi

        # Check worker processes
        local workers=$(pgrep nginx | wc -l)
        log_report "  Worker processes: $workers"

    else
        log_report "  ✗ Nginx is NOT running"
        echo -e "${RED}  ✗ Nginx not running${NC}"
    fi
    echo ""
}

# Check 3: Application Files
check_app_files() {
    echo -e "${BLUE}[3/10] Checking Application Files...${NC}"

    log_report "=== Application Files ==="

    local app_dir="/usr/share/nginx/html"
    local required_files=("index.html" "health.json")

    if [ -d "$app_dir" ]; then
        log_report "  ✓ Application directory exists: $app_dir"

        for file in "${required_files[@]}"; do
            if [ -f "$app_dir/$file" ]; then
                local size=$(stat -f%z "$app_dir/$file" 2>/dev/null || stat -c%s "$app_dir/$file" 2>/dev/null)
                log_report "  ✓ $file ($size bytes)"
            else
                log_report "  ✗ Missing: $file"
            fi
        done

        # Check assets
        if [ -d "$app_dir/assets" ]; then
            local asset_count=$(find "$app_dir/assets" -type f | wc -l)
            log_report "  ✓ Assets directory ($asset_count files)"
        else
            log_report "  ⚠ No assets directory"
        fi

        echo -e "${GREEN}  ✓ Application files checked${NC}"
    else
        log_report "  ✗ Application directory not found: $app_dir"
        echo -e "${RED}  ✗ Application directory missing${NC}"
    fi
    echo ""
}

# Check 4: Network Connectivity
check_network() {
    echo -e "${BLUE}[4/10] Checking Network...${NC}"

    log_report "=== Network Connectivity ==="

    # Check if port 80 is listening
    if netstat -tuln 2>/dev/null | grep -q ":80 " || ss -tuln 2>/dev/null | grep -q ":80 "; then
        log_report "  ✓ Port 80 is listening"
        echo -e "${GREEN}  ✓ Port 80 accessible${NC}"
    else
        log_report "  ✗ Port 80 is NOT listening"
        echo -e "${RED}  ✗ Port 80 not listening${NC}"
    fi

    # Test local health endpoint
    if curl -s -f http://localhost/health.json > /dev/null 2>&1; then
        log_report "  ✓ Health endpoint responds locally"
    else
        log_report "  ✗ Health endpoint not responding"
    fi

    # Check internet connectivity
    if curl -s -m 5 https://www.google.com > /dev/null 2>&1; then
        log_report "  ✓ Internet connectivity OK"
    else
        log_report "  ⚠ No internet connectivity (may be expected)"
    fi
    echo ""
}

# Check 5: Disk Space
check_disk() {
    echo -e "${BLUE}[5/10] Checking Disk Space...${NC}"

    log_report "=== Disk Usage ==="

    df -h | grep -E "Filesystem|/$" | tee -a "$REPORT_FILE"

    local disk_usage=$(df / | awk 'NR==2 {print $5}' | tr -d '%')

    if [ "$disk_usage" -lt 70 ]; then
        echo -e "${GREEN}  ✓ Disk space OK (${disk_usage}%)${NC}"
    elif [ "$disk_usage" -lt 90 ]; then
        echo -e "${YELLOW}  ⚠ Disk space getting full (${disk_usage}%)${NC}"
    else
        echo -e "${RED}  ✗ Disk space critical (${disk_usage}%)${NC}"
    fi
    echo ""
}

# Check 6: Memory Usage
check_memory() {
    echo -e "${BLUE}[6/10] Checking Memory...${NC}"

    log_report "=== Memory Usage ==="

    free -h | tee -a "$REPORT_FILE"

    local mem_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

    if [ "$mem_usage" -lt 70 ]; then
        echo -e "${GREEN}  ✓ Memory OK (${mem_usage}%)${NC}"
    elif [ "$mem_usage" -lt 90 ]; then
        echo -e "${YELLOW}  ⚠ Memory usage high (${mem_usage}%)${NC}"
    else
        echo -e "${RED}  ✗ Memory critical (${mem_usage}%)${NC}"
    fi
    echo ""
}

# Check 7: CPU Usage
check_cpu() {
    echo -e "${BLUE}[7/10] Checking CPU...${NC}"

    log_report "=== CPU Usage ==="

    top -bn1 | head -5 | tee -a "$REPORT_FILE"

    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    cpu_usage=${cpu_usage%.*}

    if [ "$cpu_usage" -lt 70 ]; then
        echo -e "${GREEN}  ✓ CPU OK (${cpu_usage}%)${NC}"
    elif [ "$cpu_usage" -lt 90 ]; then
        echo -e "${YELLOW}  ⚠ CPU usage high (${cpu_usage}%)${NC}"
    else
        echo -e "${RED}  ✗ CPU overloaded (${cpu_usage}%)${NC}"
    fi
    echo ""
}

# Check 8: Logs
check_logs() {
    echo -e "${BLUE}[8/10] Checking Logs...${NC}"

    log_report "=== Recent Logs ==="

    # Nginx error log
    if [ -f "/var/log/nginx/error.log" ]; then
        local error_count=$(wc -l < /var/log/nginx/error.log)
        log_report "  Nginx errors: $error_count lines"

        if [ "$error_count" -gt 0 ]; then
            log_report "  Last 5 errors:"
            tail -5 /var/log/nginx/error.log | tee -a "$REPORT_FILE"
        fi
    fi

    # Health monitor log
    if [ -f "/var/log/health-monitor.log" ]; then
        local health_lines=$(wc -l < /var/log/health-monitor.log)
        log_report "  Health monitor: $health_lines lines"
    fi

    echo -e "${GREEN}  ✓ Logs checked${NC}"
    echo ""
}

# Check 9: GPU (if available)
check_gpu() {
    echo -e "${BLUE}[9/10] Checking GPU...${NC}"

    log_report "=== GPU Status ==="

    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=name,driver_version,memory.total,utilization.gpu --format=csv | tee -a "$REPORT_FILE"
        echo -e "${GREEN}  ✓ GPU available${NC}"
    else
        log_report "  No GPU detected (CPU-only pod)"
        echo -e "${YELLOW}  ℹ No GPU (CPU-only)${NC}"
    fi
    echo ""
}

# Check 10: Process Status
check_processes() {
    echo -e "${BLUE}[10/10] Checking Processes...${NC}"

    log_report "=== Running Processes ==="

    ps aux | grep -E "(nginx|health-monitor)" | grep -v grep | tee -a "$REPORT_FILE"

    echo -e "${GREEN}  ✓ Process check complete${NC}"
    echo ""
}

# Generate recommendations
generate_recommendations() {
    echo "========================================="
    echo "Recommendations"
    echo "========================================="

    log_report ""
    log_report "=== Recommendations ==="

    local issues_found=false

    # Check nginx status
    if ! pgrep -x nginx > /dev/null; then
        log_report "  🔧 CRITICAL: Nginx is not running"
        log_report "     Fix: nginx"
        issues_found=true
    fi

    # Check disk space
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
    if [ "$disk_usage" -gt 85 ]; then
        log_report "  🔧 WARNING: Disk space low (${disk_usage}%)"
        log_report "     Fix: Clean up old logs or increase disk size"
        issues_found=true
    fi

    # Check memory
    local mem_usage=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    if [ "$mem_usage" -gt 85 ]; then
        log_report "  🔧 WARNING: Memory usage high (${mem_usage}%)"
        log_report "     Fix: Restart pod or upgrade memory"
        issues_found=true
    fi

    # Check health endpoint
    if ! curl -s -f http://localhost/health.json > /dev/null 2>&1; then
        log_report "  🔧 CRITICAL: Health endpoint not responding"
        log_report "     Fix: Check nginx configuration and restart"
        issues_found=true
    fi

    if [ "$issues_found" = false ]; then
        log_report "  ✓ No critical issues detected"
        echo -e "${GREEN}  ✓ System appears healthy${NC}"
    else
        echo -e "${YELLOW}  ⚠ Issues detected (see above)${NC}"
    fi

    echo ""
}

# Generate summary
generate_summary() {
    echo "========================================="
    echo "Diagnostic Summary"
    echo "========================================="
    echo ""
    echo "Report saved to: $REPORT_FILE"
    echo "Timestamp: $(date)"
    echo "Pod ID: ${RUNPOD_POD_ID:-local}"
    echo ""
    echo "To view full report:"
    echo "  cat $REPORT_FILE"
    echo ""
    echo "To share with support:"
    echo "  cat $REPORT_FILE | curl -F 'file=@-' https://file.io"
    echo ""
    echo "========================================="
}

# Main diagnostic routine
main() {
    log_report "Diagnostic Report"
    log_report "Generated: $(date)"
    log_report "Pod ID: ${RUNPOD_POD_ID:-local}"
    log_report ""

    check_environment
    check_nginx
    check_app_files
    check_network
    check_disk
    check_memory
    check_cpu
    check_logs
    check_gpu
    check_processes

    generate_recommendations
    generate_summary
}

# Run diagnostics
main
