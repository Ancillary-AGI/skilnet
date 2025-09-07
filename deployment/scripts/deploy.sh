#!/bin/bash

# EduVerse Production Deployment Script
# This script handles the complete deployment pipeline

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEPLOYMENT_DIR="${PROJECT_ROOT}/deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    local missing_tools=()
    
    # Check required tools
    command -v docker >/dev/null 2>&1 || missing_tools+=("docker")
    command -v kubectl >/dev/null 2>&1 || missing_tools+=("kubectl")
    command -v helm >/dev/null 2>&1 || missing_tools+=("helm")
    command -v terraform >/dev/null 2>&1 || missing_tools+=("terraform")
    command -v aws >/dev/null 2>&1 || missing_tools+=("aws-cli")
    command -v flutter >/dev/null 2>&1 || missing_tools+=("flutter")
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_error "Please install the missing tools and try again."
        exit 1
    fi
    
    # Check environment variables
    local missing_vars=()
    
    [ -z "${AWS_ACCESS_KEY_ID:-}" ] && missing_vars+=("AWS_ACCESS_KEY_ID")
    [ -z "${AWS_SECRET_ACCESS_KEY:-}" ] && missing_vars+=("AWS_SECRET_ACCESS_KEY")
    [ -z "${CLOUDFLARE_API_TOKEN:-}" ] && missing_vars+=("CLOUDFLARE_API_TOKEN")
    [ -z "${SECRET_KEY:-}" ] && missing_vars+=("SECRET_KEY")
    [ -z "${DB_PASSWORD:-}" ] && missing_vars+=("DB_PASSWORD")
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Build and push Docker images
build_and_push_images() {
    log_info "Building and pushing Docker images..."
    
    local registry="${DOCKER_REGISTRY:-eduverse}"
    local tag="${BUILD_TAG:-latest}"
    
    # Build backend image
    log_info "Building backend image..."
    docker build -t "${registry}/backend:${tag}" \
        --target production \
        "${PROJECT_ROOT}/backend"
    
    # Build frontend image
    log_info "Building frontend image..."
    cd "${PROJECT_ROOT}/frontend"
    flutter build web --release
    docker build -t "${registry}/frontend:${tag}" .
    
    # Build AI model server image
    log_info "Building AI model server image..."
    docker build -t "${registry}/ai-models:${tag}" \
        "${PROJECT_ROOT}/ai_models"
    
    # Build WebRTC signaling server image
    log_info "Building WebRTC signaling server image..."
    docker build -t "${registry}/webrtc-signaling:${tag}" \
        "${PROJECT_ROOT}/webrtc"
    
    # Push images if registry is specified
    if [ "${PUSH_IMAGES:-false}" = "true" ]; then
        log_info "Pushing images to registry..."
        docker push "${registry}/backend:${tag}"
        docker push "${registry}/frontend:${tag}"
        docker push "${registry}/ai-models:${tag}"
        docker push "${registry}/webrtc-signaling:${tag}"
    fi
    
    log_success "Docker images built successfully"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."
    
    cd "${DEPLOYMENT_DIR}/terraform"
    
    # Initialize Terraform
    terraform init -upgrade
    
    # Plan deployment
    terraform plan -var-file="environments/${ENVIRONMENT:-production}.tfvars" -out=tfplan
    
    # Apply if approved
    if [ "${AUTO_APPROVE:-false}" = "true" ]; then
        terraform apply -auto-approve tfplan
    else
        echo -n "Do you want to apply these changes? (y/N): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            terraform apply tfplan
        else
            log_warning "Terraform deployment cancelled"
            return 1
        fi
    fi
    
    # Get outputs
    export CLUSTER_NAME=$(terraform output -raw cluster_name)
    export CLUSTER_ENDPOINT=$(terraform output -raw cluster_endpoint)
    export RDS_ENDPOINT=$(terraform output -raw rds_cluster_endpoint)
    export REDIS_ENDPOINT=$(terraform output -raw redis_cluster_address)
    
    log_success "Infrastructure deployed successfully"
}

# Configure kubectl
configure_kubectl() {
    log_info "Configuring kubectl..."
    
    aws eks update-kubeconfig --region "${AWS_REGION:-us-east-1}" --name "${CLUSTER_NAME}"
    
    # Verify connection
    kubectl cluster-info
    
    log_success "kubectl configured successfully"
}

# Deploy Kubernetes resources
deploy_kubernetes() {
    log_info "Deploying Kubernetes resources..."
    
    cd "${DEPLOYMENT_DIR}/kubernetes"
    
    # Create namespace
    kubectl apply -f namespace.yaml
    
    # Create secrets
    create_kubernetes_secrets
    
    # Create config maps
    create_kubernetes_configmaps
    
    # Deploy persistent volumes
    kubectl apply -f pv.yaml
    
    # Deploy database
    kubectl apply -f postgres.yaml
    
    # Deploy Redis
    kubectl apply -f redis.yaml
    
    # Deploy backend
    kubectl apply -f backend-deployment.yaml
    
    # Deploy frontend
    kubectl apply -f frontend-deployment.yaml
    
    # Deploy AI services
    kubectl apply -f ai-services.yaml
    
    # Deploy ingress
    kubectl apply -f ingress.yaml
    
    # Deploy HPA
    kubectl apply -f hpa.yaml
    
    # Deploy monitoring
    kubectl apply -f monitoring.yaml
    
    log_success "Kubernetes resources deployed successfully"
}

# Create Kubernetes secrets
create_kubernetes_secrets() {
    log_info "Creating Kubernetes secrets..."
    
    kubectl create secret generic eduverse-secrets \
        --from-literal=database-url="postgresql+asyncpg://eduverse_user:${DB_PASSWORD}@${RDS_ENDPOINT}:5432/eduverse" \
        --from-literal=redis-url="redis://${REDIS_ENDPOINT}:6379" \
        --from-literal=secret-key="${SECRET_KEY}" \
        --from-literal=openai-api-key="${OPENAI_API_KEY:-}" \
        --from-literal=stripe-secret-key="${STRIPE_SECRET_KEY:-}" \
        --namespace=eduverse \
        --dry-run=client -o yaml | kubectl apply -f -
    
    # Create TLS secrets for ingress
    if [ -f "${DEPLOYMENT_DIR}/ssl/tls.crt" ] && [ -f "${DEPLOYMENT_DIR}/ssl/tls.key" ]; then
        kubectl create secret tls eduverse-tls \
            --cert="${DEPLOYMENT_DIR}/ssl/tls.crt" \
            --key="${DEPLOYMENT_DIR}/ssl/tls.key" \
            --namespace=eduverse \
            --dry-run=client -o yaml | kubectl apply -f -
    fi
}

# Create Kubernetes config maps
create_kubernetes_configmaps() {
    log_info "Creating Kubernetes config maps..."
    
    kubectl create configmap eduverse-config \
        --from-literal=environment="${ENVIRONMENT:-production}" \
        --from-literal=log-level="INFO" \
        --from-literal=max-workers="4" \
        --namespace=eduverse \
        --dry-run=client -o yaml | kubectl apply -f -
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Wait for database to be ready
    kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s -n eduverse
    
    # Run migrations using a job
    kubectl apply -f - <<EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: eduverse-migrations-$(date +%s)
  namespace: eduverse
spec:
  template:
    spec:
      containers:
      - name: migrations
        image: eduverse/backend:${BUILD_TAG:-latest}
        command: ["python", "-m", "alembic", "upgrade", "head"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: eduverse-secrets
              key: database-url
      restartPolicy: Never
  backoffLimit: 3
EOF
    
    # Wait for migration job to complete
    kubectl wait --for=condition=complete job -l job-name=eduverse-migrations --timeout=600s -n eduverse
    
    log_success "Database migrations completed"
}

# Deploy monitoring stack
deploy_monitoring() {
    log_info "Deploying monitoring stack..."
    
    # Add Helm repositories
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo add elastic https://helm.elastic.co
    helm repo update
    
    # Deploy Prometheus
    helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
        --namespace monitoring \
        --create-namespace \
        --values "${DEPLOYMENT_DIR}/helm-values/prometheus-values.yaml" \
        --wait
    
    # Deploy Grafana
    helm upgrade --install grafana grafana/grafana \
        --namespace monitoring \
        --values "${DEPLOYMENT_DIR}/helm-values/grafana-values.yaml" \
        --wait
    
    # Deploy Elasticsearch
    helm upgrade --install elasticsearch elastic/elasticsearch \
        --namespace logging \
        --create-namespace \
        --values "${DEPLOYMENT_DIR}/helm-values/elasticsearch-values.yaml" \
        --wait
    
    # Deploy Kibana
    helm upgrade --install kibana elastic/kibana \
        --namespace logging \
        --values "${DEPLOYMENT_DIR}/helm-values/kibana-values.yaml" \
        --wait
    
    log_success "Monitoring stack deployed successfully"
}

# Setup SSL certificates
setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    # Deploy cert-manager
    helm upgrade --install cert-manager jetstack/cert-manager \
        --namespace cert-manager \
        --create-namespace \
        --set installCRDs=true \
        --wait
    
    # Create cluster issuer
    kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@eduverse.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
    
    log_success "SSL certificates configured"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pod status
    kubectl get pods -n eduverse
    
    # Check services
    kubectl get services -n eduverse
    
    # Check ingress
    kubectl get ingress -n eduverse
    
    # Run health checks
    local backend_url="https://api.eduverse.com"
    local frontend_url="https://eduverse.com"
    
    # Wait for services to be ready
    sleep 30
    
    # Check backend health
    if curl -f "${backend_url}/health" >/dev/null 2>&1; then
        log_success "Backend health check passed"
    else
        log_error "Backend health check failed"
        return 1
    fi
    
    # Check frontend
    if curl -f "${frontend_url}" >/dev/null 2>&1; then
        log_success "Frontend health check passed"
    else
        log_error "Frontend health check failed"
        return 1
    fi
    
    log_success "Deployment verification completed"
}

# Rollback deployment
rollback_deployment() {
    log_warning "Rolling back deployment..."
    
    # Rollback Kubernetes deployments
    kubectl rollout undo deployment/eduverse-backend -n eduverse
    kubectl rollout undo deployment/eduverse-frontend -n eduverse
    
    # Wait for rollback to complete
    kubectl rollout status deployment/eduverse-backend -n eduverse
    kubectl rollout status deployment/eduverse-frontend -n eduverse
    
    log_success "Rollback completed"
}

# Cleanup resources
cleanup() {
    log_info "Cleaning up temporary resources..."
    
    # Remove temporary files
    rm -f "${DEPLOYMENT_DIR}/terraform/tfplan"
    
    # Clean up completed jobs
    kubectl delete jobs --field-selector status.successful=1 -n eduverse
    
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    local command="${1:-deploy}"
    
    case "$command" in
        "deploy")
            log_info "Starting EduVerse production deployment..."
            check_prerequisites
            build_and_push_images
            deploy_infrastructure
            configure_kubectl
            deploy_kubernetes
            run_migrations
            deploy_monitoring
            setup_ssl
            verify_deployment
            cleanup
            log_success "EduVerse deployment completed successfully!"
            ;;
        "rollback")
            log_info "Starting EduVerse rollback..."
            configure_kubectl
            rollback_deployment
            log_success "EduVerse rollback completed!"
            ;;
        "destroy")
            log_warning "Destroying EduVerse infrastructure..."
            echo -n "Are you sure you want to destroy all resources? (y/N): "
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                cd "${DEPLOYMENT_DIR}/terraform"
                terraform destroy -var-file="environments/${ENVIRONMENT:-production}.tfvars" -auto-approve
                log_success "Infrastructure destroyed"
            else
                log_info "Destruction cancelled"
            fi
            ;;
        "status")
            configure_kubectl
            kubectl get all -n eduverse
            ;;
        *)
            echo "Usage: $0 {deploy|rollback|destroy|status}"
            echo ""
            echo "Commands:"
            echo "  deploy   - Deploy EduVerse to production"
            echo "  rollback - Rollback to previous version"
            echo "  destroy  - Destroy all infrastructure"
            echo "  status   - Show deployment status"
            exit 1
            ;;
    esac
}

# Handle script interruption
trap cleanup EXIT

# Run main function
main "$@"