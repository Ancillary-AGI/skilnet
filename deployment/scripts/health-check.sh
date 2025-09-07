#!/bin/bash

# EduVerse Health Check Script
# Comprehensive health monitoring for all services

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Service endpoints
BACKEND_URL="${BACKEND_URL:-https://api.eduverse.com}"
FRONTEND_URL="${FRONTEND_URL:-https://eduverse.com}"
WEBRTC_URL="${WEBRTC_URL:-https://webrtc.eduverse.com}"
AI_SERVICE_URL="${AI_SERVICE_URL:-https://ai.eduverse.com}"

# Health check results
declare -A health_results
declare -A response_times
declare -A error_messages

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Measure response time
measure_response_time() {
    local url="$1"
    local start_time=$(date +%s%N)
    
    if curl -s -f "$url" >/dev/null 2>&1; then
        local end_time=$(date +%s%N)
        local response_time=$(( (end_time - start_time) / 1000000 ))
        echo "$response_time"
    else
        echo "-1"
    fi
}

# Check backend health
check_backend_health() {
    log_info "Checking backend health..."
    
    local health_url="${BACKEND_URL}/health"
    local ready_url="${BACKEND_URL}/ready"
    local metrics_url="${BACKEND_URL}/metrics"
    
    # Basic health check
    local response_time=$(measure_response_time "$health_url")
    if [ "$response_time" -gt 0 ]; then
        health_results["backend_health"]="✅ HEALTHY"
        response_times["backend_health"]="${response_time}ms"
        
        # Check if response time is acceptable
        if [ "$response_time" -gt 5000 ]; then
            log_warning "Backend response time is high: ${response_time}ms"
        fi
    else
        health_results["backend_health"]="❌ UNHEALTHY"
        error_messages["backend_health"]="Health endpoint not responding"
    fi
    
    # Readiness check
    response_time=$(measure_response_time "$ready_url")
    if [ "$response_time" -gt 0 ]; then
        health_results["backend_ready"]="✅ READY"
        response_times["backend_ready"]="${response_time}ms"
    else
        health_results["backend_ready"]="❌ NOT READY"
        error_messages["backend_ready"]="Readiness endpoint not responding"
    fi
    
    # Metrics check
    response_time=$(measure_response_time "$metrics_url")
    if [ "$response_time" -gt 0 ]; then
        health_results["backend_metrics"]="✅ AVAILABLE"
        response_times["backend_metrics"]="${response_time}ms"
    else
        health_results["backend_metrics"]="❌ UNAVAILABLE"
        error_messages["backend_metrics"]="Metrics endpoint not responding"
    fi
    
    # Database connectivity check
    local db_check_url="${BACKEND_URL}/health/database"
    response_time=$(measure_response_time "$db_check_url")
    if [ "$response_time" -gt 0 ]; then
        health_results["database"]="✅ CONNECTED"
        response_times["database"]="${response_time}ms"
    else
        health_results["database"]="❌ DISCONNECTED"
        error_messages["database"]="Database connection failed"
    fi
    
    # Redis connectivity check
    local redis_check_url="${BACKEND_URL}/health/redis"
    response_time=$(measure_response_time "$redis_check_url")
    if [ "$response_time" -gt 0 ]; then
        health_results["redis"]="✅ CONNECTED"
        response_times["redis"]="${response_time}ms"
    else
        health_results["redis"]="❌ DISCONNECTED"
        error_messages["redis"]="Redis connection failed"
    fi
}

# Check frontend health
check_frontend_health() {
    log_info "Checking frontend health..."
    
    local response_time=$(measure_response_time "$FRONTEND_URL")
    if [ "$response_time" -gt 0 ]; then
        health_results["frontend"]="✅ HEALTHY"
        response_times["frontend"]="${response_time}ms"
        
        # Check if main assets are loading
        local assets_check=$(curl -s "$FRONTEND_URL" | grep -c "main.*\.js\|main.*\.css" || echo "0")
        if [ "$assets_check" -gt 0 ]; then
            health_results["frontend_assets"]="✅ LOADED"
        else
            health_results["frontend_assets"]="⚠️ PARTIAL"
            error_messages["frontend_assets"]="Some assets may not be loading"
        fi
    else
        health_results["frontend"]="❌ UNHEALTHY"
        error_messages["frontend"]="Frontend not responding"
    fi
}

# Check WebRTC signaling server
check_webrtc_health() {
    log_info "Checking WebRTC signaling server..."
    
    local health_url="${WEBRTC_URL}/health"
    local response_time=$(measure_response_time "$health_url")
    
    if [ "$response_time" -gt 0 ]; then
        health_results["webrtc"]="✅ HEALTHY"
        response_times["webrtc"]="${response_time}ms"
    else
        health_results["webrtc"]="❌ UNHEALTHY"
        error_messages["webrtc"]="WebRTC signaling server not responding"
    fi
}

# Check AI services
check_ai_services() {
    log_info "Checking AI services..."
    
    local health_url="${AI_SERVICE_URL}/health"
    local models_url="${AI_SERVICE_URL}/models/status"
    
    # AI service health
    local response_time=$(measure_response_time "$health_url")
    if [ "$response_time" -gt 0 ]; then
        health_results["ai_service"]="✅ HEALTHY"
        response_times["ai_service"]="${response_time}ms"
    else
        health_results["ai_service"]="❌ UNHEALTHY"
        error_messages["ai_service"]="AI service not responding"
    fi
    
    # AI models status
    response_time=$(measure_response_time "$models_url")
    if [ "$response_time" -gt 0 ]; then
        health_results["ai_models"]="✅ LOADED"
        response_times["ai_models"]="${response_time}ms"
    else
        health_results["ai_models"]="❌ NOT LOADED"
        error_messages["ai_models"]="AI models not loaded"
    fi
}

# Check Kubernetes cluster health
check_kubernetes_health() {
    log_info "Checking Kubernetes cluster health..."
    
    if command -v kubectl >/dev/null 2>&1; then
        # Check cluster connectivity
        if kubectl cluster-info >/dev/null 2>&1; then
            health_results["k8s_cluster"]="✅ CONNECTED"
            
            # Check node status
            local ready_nodes=$(kubectl get nodes --no-headers | grep -c "Ready" || echo "0")
            local total_nodes=$(kubectl get nodes --no-headers | wc -l)
            
            if [ "$ready_nodes" -eq "$total_nodes" ] && [ "$total_nodes" -gt 0 ]; then
                health_results["k8s_nodes"]="✅ ALL READY ($ready_nodes/$total_nodes)"
            else
                health_results["k8s_nodes"]="⚠️ SOME NOT READY ($ready_nodes/$total_nodes)"
            fi
            
            # Check pod status in eduverse namespace
            local running_pods=$(kubectl get pods -n eduverse --no-headers | grep -c "Running" || echo "0")
            local total_pods=$(kubectl get pods -n eduverse --no-headers | wc -l)
            
            if [ "$running_pods" -eq "$total_pods" ] && [ "$total_pods" -gt 0 ]; then
                health_results["k8s_pods"]="✅ ALL RUNNING ($running_pods/$total_pods)"
            else
                health_results["k8s_pods"]="⚠️ SOME NOT RUNNING ($running_pods/$total_pods)"
            fi
            
        else
            health_results["k8s_cluster"]="❌ DISCONNECTED"
            error_messages["k8s_cluster"]="Cannot connect to Kubernetes cluster"
        fi
    else
        health_results["k8s_cluster"]="⚠️ KUBECTL NOT AVAILABLE"
        error_messages["k8s_cluster"]="kubectl command not found"
    fi
}

# Check external dependencies
check_external_dependencies() {
    log_info "Checking external dependencies..."
    
    # Check DNS resolution
    if nslookup google.com >/dev/null 2>&1; then
        health_results["dns"]="✅ WORKING"
    else
        health_results["dns"]="❌ FAILED"
        error_messages["dns"]="DNS resolution failed"
    fi
    
    # Check internet connectivity
    if curl -s -f https://www.google.com >/dev/null 2>&1; then
        health_results["internet"]="✅ CONNECTED"
    else
        health_results["internet"]="❌ DISCONNECTED"
        error_messages["internet"]="No internet connectivity"
    fi
    
    # Check CDN (CloudFlare)
    if curl -s -f https://cdnjs.cloudflare.com >/dev/null 2>&1; then
        health_results["cdn"]="✅ AVAILABLE"
    else
        health_results["cdn"]="❌ UNAVAILABLE"
        error_messages["cdn"]="CDN not accessible"
    fi
}

# Check SSL certificates
check_ssl_certificates() {
    log_info "Checking SSL certificates..."
    
    local domains=("eduverse.com" "api.eduverse.com" "cdn.eduverse.com")
    
    for domain in "${domains[@]}"; do
        local cert_info=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
        
        if [ -n "$cert_info" ]; then
            local expiry_date=$(echo "$cert_info" | grep "notAfter" | cut -d= -f2)
            local expiry_timestamp=$(date -d "$expiry_date" +%s 2>/dev/null || echo "0")
            local current_timestamp=$(date +%s)
            local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
            
            if [ "$days_until_expiry" -gt 30 ]; then
                health_results["ssl_$domain"]="✅ VALID ($days_until_expiry days)"
            elif [ "$days_until_expiry" -gt 0 ]; then
                health_results["ssl_$domain"]="⚠️ EXPIRING SOON ($days_until_expiry days)"
            else
                health_results["ssl_$domain"]="❌ EXPIRED"
            fi
        else
            health_results["ssl_$domain"]="❌ INVALID"
            error_messages["ssl_$domain"]="Cannot retrieve certificate information"
        fi
    done
}

# Check monitoring services
check_monitoring() {
    log_info "Checking monitoring services..."
    
    # Check Prometheus
    if command -v kubectl >/dev/null 2>&1; then
        local prometheus_pods=$(kubectl get pods -n monitoring -l app.kubernetes.io/name=prometheus --no-headers | grep -c "Running" || echo "0")
        if [ "$prometheus_pods" -gt 0 ]; then
            health_results["prometheus"]="✅ RUNNING"
        else
            health_results["prometheus"]="❌ NOT RUNNING"
        fi
        
        # Check Grafana
        local grafana_pods=$(kubectl get pods -n monitoring -l app.kubernetes.io/name=grafana --no-headers | grep -c "Running" || echo "0")
        if [ "$grafana_pods" -gt 0 ]; then
            health_results["grafana"]="✅ RUNNING"
        else
            health_results["grafana"]="❌ NOT RUNNING"
        fi
        
        # Check Elasticsearch
        local elasticsearch_pods=$(kubectl get pods -n logging -l app=elasticsearch --no-headers | grep -c "Running" || echo "0")
        if [ "$elasticsearch_pods" -gt 0 ]; then
            health_results["elasticsearch"]="✅ RUNNING"
        else
            health_results["elasticsearch"]="❌ NOT RUNNING"
        fi
    fi
}

# Generate health report
generate_report() {
    log_info "Generating health report..."
    
    echo ""
    echo "=========================================="
    echo "         EDUVERSE HEALTH REPORT"
    echo "=========================================="
    echo "Generated: $(date)"
    echo ""
    
    # Core Services
    echo "🔧 CORE SERVICES"
    echo "----------------------------------------"
    printf "%-20s %-20s %-15s\n" "Service" "Status" "Response Time"
    echo "----------------------------------------"
    
    for service in backend_health backend_ready frontend webrtc ai_service; do
        if [[ -n "${health_results[$service]:-}" ]]; then
            printf "%-20s %-20s %-15s\n" "$service" "${health_results[$service]}" "${response_times[$service]:-N/A}"
        fi
    done
    
    echo ""
    
    # Infrastructure
    echo "🏗️ INFRASTRUCTURE"
    echo "----------------------------------------"
    printf "%-20s %-20s\n" "Component" "Status"
    echo "----------------------------------------"
    
    for component in database redis k8s_cluster k8s_nodes k8s_pods; do
        if [[ -n "${health_results[$component]:-}" ]]; then
            printf "%-20s %-20s\n" "$component" "${health_results[$component]}"
        fi
    done
    
    echo ""
    
    # External Dependencies
    echo "🌐 EXTERNAL DEPENDENCIES"
    echo "----------------------------------------"
    printf "%-20s %-20s\n" "Dependency" "Status"
    echo "----------------------------------------"
    
    for dep in dns internet cdn; do
        if [[ -n "${health_results[$dep]:-}" ]]; then
            printf "%-20s %-20s\n" "$dep" "${health_results[$dep]}"
        fi
    done
    
    echo ""
    
    # SSL Certificates
    echo "🔒 SSL CERTIFICATES"
    echo "----------------------------------------"
    printf "%-25s %-20s\n" "Domain" "Status"
    echo "----------------------------------------"
    
    for key in "${!health_results[@]}"; do
        if [[ $key == ssl_* ]]; then
            local domain=${key#ssl_}
            printf "%-25s %-20s\n" "$domain" "${health_results[$key]}"
        fi
    done
    
    echo ""
    
    # Monitoring
    echo "📊 MONITORING"
    echo "----------------------------------------"
    printf "%-20s %-20s\n" "Service" "Status"
    echo "----------------------------------------"
    
    for service in prometheus grafana elasticsearch; do
        if [[ -n "${health_results[$service]:-}" ]]; then
            printf "%-20s %-20s\n" "$service" "${health_results[$service]}"
        fi
    done
    
    echo ""
    
    # Errors and Warnings
    if [ ${#error_messages[@]} -gt 0 ]; then
        echo "⚠️ ISSUES DETECTED"
        echo "----------------------------------------"
        for key in "${!error_messages[@]}"; do
            echo "❌ $key: ${error_messages[$key]}"
        done
        echo ""
    fi
    
    # Overall Status
    local total_checks=0
    local healthy_checks=0
    
    for status in "${health_results[@]}"; do
        total_checks=$((total_checks + 1))
        if [[ $status == *"✅"* ]]; then
            healthy_checks=$((healthy_checks + 1))
        fi
    done
    
    local health_percentage=$((healthy_checks * 100 / total_checks))
    
    echo "📈 OVERALL HEALTH"
    echo "----------------------------------------"
    echo "Healthy Services: $healthy_checks/$total_checks ($health_percentage%)"
    
    if [ "$health_percentage" -ge 90 ]; then
        echo "Status: 🟢 EXCELLENT"
    elif [ "$health_percentage" -ge 75 ]; then
        echo "Status: 🟡 GOOD"
    elif [ "$health_percentage" -ge 50 ]; then
        echo "Status: 🟠 DEGRADED"
    else
        echo "Status: 🔴 CRITICAL"
    fi
    
    echo ""
    echo "=========================================="
}

# Send alerts if needed
send_alerts() {
    local health_percentage=$1
    
    if [ "$health_percentage" -lt 75 ]; then
        log_warning "Health percentage below threshold: $health_percentage%"
        
        # Send Slack notification if webhook is configured
        if [ -n "${SLACK_WEBHOOK_URL:-}" ]; then
            local message="🚨 EduVerse Health Alert: System health at $health_percentage%"
            curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"$message\"}" \
                "$SLACK_WEBHOOK_URL" >/dev/null 2>&1 || true
        fi
        
        # Send email notification if configured
        if [ -n "${ALERT_EMAIL:-}" ] && command -v mail >/dev/null 2>&1; then
            echo "EduVerse system health has degraded to $health_percentage%. Please check the system." | \
                mail -s "EduVerse Health Alert" "$ALERT_EMAIL" || true
        fi
    fi
}

# Main function
main() {
    local output_file="${1:-}"
    local send_alerts_flag="${2:-false}"
    
    log_info "Starting EduVerse health check..."
    
    # Run all health checks
    check_backend_health
    check_frontend_health
    check_webrtc_health
    check_ai_services
    check_kubernetes_health
    check_external_dependencies
    check_ssl_certificates
    check_monitoring
    
    # Generate report
    if [ -n "$output_file" ]; then
        generate_report > "$output_file"
        log_success "Health report saved to: $output_file"
    else
        generate_report
    fi
    
    # Calculate overall health and send alerts if needed
    local total_checks=0
    local healthy_checks=0
    
    for status in "${health_results[@]}"; do
        total_checks=$((total_checks + 1))
        if [[ $status == *"✅"* ]]; then
            healthy_checks=$((healthy_checks + 1))
        fi
    done
    
    local health_percentage=$((healthy_checks * 100 / total_checks))
    
    if [ "$send_alerts_flag" = "true" ]; then
        send_alerts "$health_percentage"
    fi
    
    # Exit with appropriate code
    if [ "$health_percentage" -ge 75 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main function
main "$@"