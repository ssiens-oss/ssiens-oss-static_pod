#!/bin/bash

# RunPod API Integration Script
# Manage pods via RunPod GraphQL API

set -e

# Configuration
RUNPOD_API_KEY="${RUNPOD_API_KEY:-}"
API_ENDPOINT="https://api.runpod.io/graphql"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check API key
check_api_key() {
    if [ -z "$RUNPOD_API_KEY" ]; then
        echo -e "${RED}Error: RUNPOD_API_KEY environment variable not set${NC}"
        echo "Get your API key from: https://www.runpod.io/console/user/settings"
        echo "Set it with: export RUNPOD_API_KEY=your-api-key"
        exit 1
    fi
}

# Make GraphQL query
query() {
    local query="$1"

    curl -s -X POST "$API_ENDPOINT" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $RUNPOD_API_KEY" \
        -d "{\"query\": \"$query\"}"
}

# List all pods
list_pods() {
    echo -e "${BLUE}Fetching pods...${NC}"

    local query='query { myself { pods { id name runtime { uptimeInSeconds } imageName gpuCount } } }'

    local response=$(query "$query")

    echo "$response" | jq '.data.myself.pods[] | {
        id: .id,
        name: .name,
        uptime_hours: (.runtime.uptimeInSeconds / 3600 | floor),
        image: .imageName,
        gpus: .gpuCount
    }' 2>/dev/null || echo "$response"
}

# Get pod details
get_pod() {
    local pod_id="$1"

    if [ -z "$pod_id" ]; then
        echo -e "${RED}Error: Pod ID required${NC}"
        echo "Usage: $0 get-pod <pod_id>"
        exit 1
    fi

    echo -e "${BLUE}Fetching pod details: $pod_id${NC}"

    local query="query { pod(input: {podId: \\\"$pod_id\\\"}) { id name imageName machineId desiredStatus runtime { uptimeInSeconds gpus { id gpuUtilPercent memoryUtilPercent } ports { ip isIpPublic publicPort } } } }"

    local response=$(query "$query")

    echo "$response" | jq '.data.pod' 2>/dev/null || echo "$response"
}

# Start pod
start_pod() {
    local pod_id="$1"

    if [ -z "$pod_id" ]; then
        echo -e "${RED}Error: Pod ID required${NC}"
        echo "Usage: $0 start-pod <pod_id>"
        exit 1
    fi

    echo -e "${YELLOW}Starting pod: $pod_id${NC}"

    local mutation="mutation { podResume(input: {podId: \\\"$pod_id\\\"}) { id desiredStatus } }"

    local response=$(query "$mutation")

    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo -e "${GREEN}✓ Pod start command sent${NC}"
}

# Stop pod
stop_pod() {
    local pod_id="$1"

    if [ -z "$pod_id" ]; then
        echo -e "${RED}Error: Pod ID required${NC}"
        echo "Usage: $0 stop-pod <pod_id>"
        exit 1
    fi

    echo -e "${YELLOW}Stopping pod: $pod_id${NC}"

    local mutation="mutation { podStop(input: {podId: \\\"$pod_id\\\"}) { id desiredStatus } }"

    local response=$(query "$mutation")

    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo -e "${GREEN}✓ Pod stop command sent${NC}"
}

# Terminate pod
terminate_pod() {
    local pod_id="$1"

    if [ -z "$pod_id" ]; then
        echo -e "${RED}Error: Pod ID required${NC}"
        echo "Usage: $0 terminate-pod <pod_id>"
        exit 1
    fi

    echo -e "${RED}Terminating pod: $pod_id${NC}"
    read -p "Are you sure? This action cannot be undone. (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi

    local mutation="mutation { podTerminate(input: {podId: \\\"$pod_id\\\"}) { id } }"

    local response=$(query "$mutation")

    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo -e "${GREEN}✓ Pod terminated${NC}"
}

# Create pod from template
create_pod() {
    local template_file="${1:-runpod-config/pod-template.json}"

    if [ ! -f "$template_file" ]; then
        echo -e "${RED}Error: Template file not found: $template_file${NC}"
        exit 1
    fi

    echo -e "${BLUE}Creating pod from template: $template_file${NC}"

    # Read template (simplified - in production use proper JSON parsing)
    local image_name=$(cat "$template_file" | grep imageName | cut -d'"' -f4)
    local gpu_type=$(cat "$template_file" | grep gpuTypeId | cut -d'"' -f4)

    echo "Image: $image_name"
    echo "GPU: $gpu_type"

    # Note: This is a simplified version. Full implementation would need to properly construct the mutation
    echo -e "${YELLOW}Note: Create pod via RunPod console for now${NC}"
    echo "Or use the RunPod Python SDK for programmatic creation"
}

# Get account info
account_info() {
    echo -e "${BLUE}Fetching account information...${NC}"

    local query='query { myself { id creditBalance serverlessDiscount } }'

    local response=$(query "$query")

    echo "$response" | jq '.data.myself' 2>/dev/null || echo "$response"
}

# Monitor pod metrics
monitor_pod() {
    local pod_id="$1"
    local interval="${2:-30}"

    if [ -z "$pod_id" ]; then
        echo -e "${RED}Error: Pod ID required${NC}"
        echo "Usage: $0 monitor-pod <pod_id> [interval_seconds]"
        exit 1
    fi

    echo -e "${BLUE}Monitoring pod: $pod_id (interval: ${interval}s)${NC}"
    echo "Press Ctrl+C to stop"
    echo ""

    while true; do
        clear
        echo "========================================="
        echo "Pod Metrics - $(date)"
        echo "========================================="

        local query="query { pod(input: {podId: \\\"$pod_id\\\"}) { runtime { uptimeInSeconds gpus { gpuUtilPercent memoryUtilPercent } } } }"

        local response=$(query "$query")

        echo "$response" | jq '.data.pod.runtime' 2>/dev/null || echo "$response"

        echo ""
        echo "Next update in ${interval}s..."

        sleep "$interval"
    done
}

# Usage
usage() {
    cat << EOF
RunPod API Integration Script

Usage: $0 <command> [options]

Commands:
    list-pods              List all your pods
    get-pod <id>           Get detailed pod information
    start-pod <id>         Start a stopped pod
    stop-pod <id>          Stop a running pod
    terminate-pod <id>     Terminate a pod (permanent)
    create-pod [template]  Create pod from template
    account-info           Show account information
    monitor-pod <id> [int] Monitor pod metrics (default: 30s)

Environment Variables:
    RUNPOD_API_KEY        Your RunPod API key (required)

Examples:
    export RUNPOD_API_KEY=your-api-key
    $0 list-pods
    $0 get-pod abc123xyz
    $0 monitor-pod abc123xyz 60

Get your API key from:
    https://www.runpod.io/console/user/settings
EOF
}

# Main
main() {
    local command="${1:-help}"

    case "$command" in
        list-pods)
            check_api_key
            list_pods
            ;;
        get-pod)
            check_api_key
            get_pod "$2"
            ;;
        start-pod)
            check_api_key
            start_pod "$2"
            ;;
        stop-pod)
            check_api_key
            stop_pod "$2"
            ;;
        terminate-pod)
            check_api_key
            terminate_pod "$2"
            ;;
        create-pod)
            check_api_key
            create_pod "$2"
            ;;
        account-info)
            check_api_key
            account_info
            ;;
        monitor-pod)
            check_api_key
            monitor_pod "$2" "$3"
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            echo ""
            usage
            exit 1
            ;;
    esac
}

main "$@"
