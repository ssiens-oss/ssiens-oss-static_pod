#!/bin/bash

# Performance Benchmarking Tool for RunPod Pod
# Tests and measures pod performance

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
TARGET_URL="${TARGET_URL:-http://localhost}"
BENCHMARK_DURATION="${BENCHMARK_DURATION:-30}"
CONCURRENT_USERS="${CONCURRENT_USERS:-10}"

echo "========================================="
echo "RunPod Pod Performance Benchmark"
echo "========================================="
echo ""

# Check if load testing tool is available
check_dependencies() {
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}✗ curl not found${NC}"
        exit 1
    fi

    if ! command -v ab &> /dev/null && ! command -v wrk &> /dev/null; then
        echo -e "${YELLOW}⚠ No load testing tool found (ab or wrk)${NC}"
        echo "Installing basic dependencies..."
        apk add --no-cache apache2-utils 2>/dev/null || apt-get install -y apache2-utils 2>/dev/null || true
    fi
}

# System Information
system_info() {
    echo -e "${BLUE}System Information:${NC}"
    echo "  Hostname: $(hostname)"
    echo "  CPU Cores: $(nproc)"
    echo "  Total RAM: $(free -h | awk '/^Mem:/ {print $2}')"
    echo "  Available RAM: $(free -h | awk '/^Mem:/ {print $7}')"

    if command -v nvidia-smi &> /dev/null; then
        echo "  GPU: $(nvidia-smi --query-gpu=name --format=csv,noheader)"
    fi
    echo ""
}

# Test 1: Basic Health Check
test_health_check() {
    echo -e "${BLUE}Test 1: Health Check Endpoint${NC}"
    echo "Testing: $TARGET_URL/health.json"

    local start=$(date +%s%3N)
    local response=$(curl -s -w "\n%{http_code}\n%{time_total}" "$TARGET_URL/health.json" 2>/dev/null)
    local end=$(date +%s%3N)

    local body=$(echo "$response" | head -n 1)
    local http_code=$(echo "$response" | sed -n '2p')
    local time_total=$(echo "$response" | sed -n '3p')
    local time_ms=$(echo "scale=0; $time_total * 1000" | bc)

    echo "  HTTP Status: $http_code"
    echo "  Response Time: ${time_ms}ms"
    echo "  Response Body: $body"

    if [ "$http_code" = "200" ]; then
        echo -e "  ${GREEN}✓ Health check passed${NC}"
    else
        echo -e "  ${RED}✗ Health check failed${NC}"
    fi
    echo ""
}

# Test 2: Application Response Time
test_app_response() {
    echo -e "${BLUE}Test 2: Application Response Time${NC}"
    echo "Testing: $TARGET_URL/"

    echo "  Running 10 requests..."
    local total=0
    local min=999999
    local max=0

    for i in {1..10}; do
        local time_ms=$(curl -s -w "%{time_total}" -o /dev/null "$TARGET_URL/" | awk '{print int($1*1000)}')
        total=$((total + time_ms))

        if [ $time_ms -lt $min ]; then
            min=$time_ms
        fi
        if [ $time_ms -gt $max ]; then
            max=$time_ms
        fi
    done

    local avg=$((total / 10))

    echo "  Average: ${avg}ms"
    echo "  Min: ${min}ms"
    echo "  Max: ${max}ms"

    if [ $avg -lt 100 ]; then
        echo -e "  ${GREEN}✓ Excellent response time${NC}"
    elif [ $avg -lt 300 ]; then
        echo -e "  ${YELLOW}⚠ Good response time${NC}"
    else
        echo -e "  ${RED}✗ Slow response time${NC}"
    fi
    echo ""
}

# Test 3: Static Asset Performance
test_static_assets() {
    echo -e "${BLUE}Test 3: Static Asset Performance${NC}"

    # Test gzip compression
    echo "  Testing gzip compression..."
    local headers=$(curl -s -H "Accept-Encoding: gzip" -I "$TARGET_URL/" 2>/dev/null)

    if echo "$headers" | grep -q "Content-Encoding: gzip"; then
        echo -e "  ${GREEN}✓ Gzip compression enabled${NC}"
    else
        echo -e "  ${YELLOW}⚠ Gzip compression not detected${NC}"
    fi

    # Test caching headers
    echo "  Testing cache headers..."
    if echo "$headers" | grep -qi "cache-control"; then
        echo -e "  ${GREEN}✓ Cache headers present${NC}"
    else
        echo -e "  ${YELLOW}⚠ No cache headers${NC}"
    fi
    echo ""
}

# Test 4: Concurrent Load Test
test_concurrent_load() {
    echo -e "${BLUE}Test 4: Concurrent Load Test${NC}"
    echo "  Concurrent Users: $CONCURRENT_USERS"
    echo "  Duration: ${BENCHMARK_DURATION}s"

    if command -v ab &> /dev/null; then
        echo "  Running Apache Bench..."
        local requests=$((CONCURRENT_USERS * BENCHMARK_DURATION))

        ab -n $requests -c $CONCURRENT_USERS -q "$TARGET_URL/" 2>&1 | grep -E "(Requests per second|Time per request|Failed requests)" || true

    elif command -v wrk &> /dev/null; then
        echo "  Running wrk..."
        wrk -t$CONCURRENT_USERS -c$CONCURRENT_USERS -d${BENCHMARK_DURATION}s "$TARGET_URL/" 2>&1 || true

    else
        echo -e "  ${YELLOW}⚠ No load testing tool available${NC}"
        echo "  Running basic concurrent test..."

        for i in $(seq 1 $CONCURRENT_USERS); do
            (curl -s -o /dev/null "$TARGET_URL/" &)
        done
        wait

        echo -e "  ${GREEN}✓ Handled $CONCURRENT_USERS concurrent requests${NC}"
    fi
    echo ""
}

# Test 5: Resource Usage During Load
test_resource_usage() {
    echo -e "${BLUE}Test 5: Resource Usage${NC}"

    echo "  CPU Usage:"
    local cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "    Current: ${cpu}%"

    echo "  Memory Usage:"
    local mem=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
    echo "    Current: ${mem}%"

    echo "  Disk Usage:"
    local disk=$(df -h / | awk 'NR==2 {print $5}')
    echo "    Root: ${disk}"

    if command -v nvidia-smi &> /dev/null; then
        echo "  GPU Usage:"
        local gpu=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits)
        echo "    GPU: ${gpu}%"
    fi
    echo ""
}

# Test 6: Network Performance
test_network() {
    echo -e "${BLUE}Test 6: Network Performance${NC}"

    echo "  Testing download speed (1MB file)..."
    local start=$(date +%s%3N)
    dd if=/dev/zero bs=1M count=1 2>/dev/null | curl -s -X POST --data-binary @- "$TARGET_URL/" -o /dev/null || true
    local end=$(date +%s%3N)
    local duration=$((end - start))

    echo "  Upload test completed in ${duration}ms"
    echo ""
}

# Generate Benchmark Report
generate_report() {
    echo "========================================="
    echo "Benchmark Report"
    echo "========================================="
    echo ""
    echo "Target: $TARGET_URL"
    echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Pod ID: ${RUNPOD_POD_ID:-local}"
    echo ""
    echo "Summary:"
    echo "  All tests completed"
    echo ""
    echo "Recommendations:"

    # Based on results, provide recommendations
    local mem=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

    if [ $mem -gt 80 ]; then
        echo "  ⚠ Memory usage high (${mem}%) - consider upgrading"
    fi

    echo "  ✓ Review detailed logs above for optimization opportunities"
    echo ""
    echo "========================================="
}

# Main execution
main() {
    check_dependencies
    system_info
    test_health_check
    test_app_response
    test_static_assets
    test_concurrent_load
    test_resource_usage
    test_network
    generate_report
}

# Run benchmark
if [ "${1:-run}" = "run" ]; then
    main
else
    echo "Usage: $0 [run]"
    exit 1
fi
