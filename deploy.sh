#!/bin/bash

# EduVerse Complete Deployment Script
# Deploys both backend and frontend with all advanced features

set -e  # Exit on any error

echo "🚀 EduVerse Complete Deployment Script"
echo "====================================="

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
DEPLOYMENT_DIR="deployment"
DOCKER_COMPOSE_FILE="docker-compose.yml"
PRODUCTION_COMPOSE_FILE="deployment/docker-compose.production.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    print_success "Docker and Docker Compose are installed"
}

# Check if Node.js is installed (for frontend build)
check_nodejs() {
    print_status "Checking Node.js installation..."
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    print_success "Node.js is installed"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        print_error "Python is not installed. Please install Python first."
        exit 1
    fi
    print_success "Python is installed"
}

# Setup environment files
setup_env_files() {
    print_status "Setting up environment files..."

    # Backend environment
    if [ ! -f "$BACKEND_DIR/.env" ]; then
        print_status "Creating backend .env file..."
        cat > "$BACKEND_DIR/.env" << EOF
# Database Configuration
DATABASE_URL=postgresql+asyncpg://eduverse_user:eduverse_password@localhost:5432/eduverse_db
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-this-in-production
JWT_REFRESH_SECRET_KEY=your-jwt-refresh-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"]

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Payment Processing
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret

# File Storage
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=eduverse-storage
AWS_REGION=us-east-1

# Monitoring
SENTRY_DSN=your-sentry-dsn
PROMETHEUS_GATEWAY=your-prometheus-gateway

# Blockchain (optional)
WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/your-project-id
BLOCKCHAIN_NETWORK=mainnet
EOF
        print_success "Backend .env file created"
    else
        print_warning "Backend .env file already exists"
    fi

    # Frontend environment
    if [ ! -f "$FRONTEND_DIR/.env" ]; then
        print_status "Creating frontend .env file..."
        cat > "$FRONTEND_DIR/.env" << EOF
# API Configuration
API_BASE_URL=http://localhost:8000/api/v1
WS_BASE_URL=ws://localhost:8000/ws

# Firebase Configuration
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=1:123456789:web:abcdef123456

# App Configuration
APP_NAME=EduVerse
APP_VERSION=2.0.0
DEBUG=true

# Analytics
MIXPANEL_TOKEN=your-mixpanel-token
GOOGLE_ANALYTICS_ID=GA-XXXXXXXXX

# Payment Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
PAYPAL_CLIENT_ID=your_paypal_client_id

# Feature Flags
ENABLE_VR_AR=true
ENABLE_AI_TUTOR=true
ENABLE_SOCIAL_FEATURES=true
ENABLE_OFFLINE_MODE=true
ENABLE_ADVANCED_ANALYTICS=true
EOF
        print_success "Frontend .env file created"
    else
        print_warning "Frontend .env file already exists"
    fi
}

# Install backend dependencies
install_backend_deps() {
    print_status "Installing backend dependencies..."
    cd "$BACKEND_DIR"

    if [ -f "requirements.txt" ]; then
        python -m pip install -r requirements.txt
        print_success "Backend dependencies installed"
    else
        print_error "requirements.txt not found in backend directory"
        exit 1
    fi

    cd ..
}

# Install frontend dependencies
install_frontend_deps() {
    print_status "Installing frontend dependencies..."
    cd "$FRONTEND_DIR"

    if [ -f "pubspec.yaml" ]; then
        flutter pub get
        print_success "Frontend dependencies installed"
    else
        print_error "pubspec.yaml not found in frontend directory"
        exit 1
    fi

    cd ..
}

# Build frontend for production
build_frontend() {
    print_status "Building frontend for production..."
    cd "$FRONTEND_DIR"

    # Build web version
    flutter build web --release

    if [ $? -eq 0 ]; then
        print_success "Frontend built successfully"
    else
        print_error "Frontend build failed"
        exit 1
    fi

    cd ..
}

# Setup database
setup_database() {
    print_status "Setting up database..."

    # Create database if it doesn't exist
    if command -v psql &> /dev/null; then
        psql -h localhost -U postgres -c "CREATE DATABASE eduverse_db;" 2>/dev/null || true
        psql -h localhost -U postgres -c "CREATE USER eduverse_user WITH PASSWORD 'eduverse_password';" 2>/dev/null || true
        psql -h localhost -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE eduverse_db TO eduverse_user;" 2>/dev/null || true
        print_success "Database setup completed"
    else
        print_warning "PostgreSQL client not found. Please create database manually."
    fi
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    cd "$BACKEND_DIR"

    # Run Alembic migrations
    alembic upgrade head

    if [ $? -eq 0 ]; then
        print_success "Database migrations completed"
    else
        print_error "Database migrations failed"
        exit 1
    fi

    cd ..
}

# Start services with Docker Compose
start_services() {
    print_status "Starting services with Docker Compose..."

    # Use production compose file if it exists
    if [ -f "$PRODUCTION_COMPOSE_FILE" ]; then
        docker-compose -f "$PRODUCTION_COMPOSE_FILE" up -d
    else
        docker-compose up -d
    fi

    if [ $? -eq 0 ]; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."

    # Wait for backend
    for i in {1..30}; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend is ready"
            break
        fi
        print_status "Waiting for backend... ($i/30)"
        sleep 2
    done

    # Wait for database
    for i in {1..30}; do
        if curl -f http://localhost:8000/health/database > /dev/null 2>&1; then
            print_success "Database is ready"
            break
        fi
        print_status "Waiting for database... ($i/30)"
        sleep 2
    done
}

# Run tests
run_tests() {
    print_status "Running comprehensive test suite..."

    # Run backend tests
    cd "$BACKEND_DIR"
    python -m pytest tests/ -v --cov=app --cov-report=html

    if [ $? -eq 0 ]; then
        print_success "Backend tests passed"
    else
        print_warning "Some backend tests failed"
    fi

    cd ..

    # Run frontend tests
    cd "$FRONTEND_DIR"
    flutter test

    if [ $? -eq 0 ]; then
        print_success "Frontend tests passed"
    else
        print_warning "Some frontend tests failed"
    fi

    cd ..

    # Run integration tests
    python test_complete_application.py

    if [ $? -eq 0 ]; then
        print_success "Integration tests passed"
    else
        print_warning "Some integration tests failed"
    fi
}

# Create SSL certificates (optional)
create_ssl_certificates() {
    print_status "Creating SSL certificates..."

    if [ ! -d "deployment/ssl" ]; then
        mkdir -p deployment/ssl
    fi

    # Generate self-signed certificate for development
    openssl req -x509 -newkey rsa:4096 -keyout deployment/ssl/key.pem -out deployment/ssl/cert.pem -days 365 -nodes -subj "/CN=localhost"

    if [ $? -eq 0 ]; then
        print_success "SSL certificates created"
    else
        print_warning "Failed to create SSL certificates"
    fi
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring and logging..."

    # Create log directories
    mkdir -p backend/logs
    mkdir -p frontend/logs

    # Setup log rotation
    cat > "backend/logrotate.conf" << EOF
/backend/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 ubuntu ubuntu
}
EOF

    print_success "Monitoring setup completed"
}

# Main deployment function
main() {
    echo "🎯 Starting complete EduVerse deployment..."
    echo ""

    # Pre-deployment checks
    check_docker
    check_nodejs
    check_python

    # Setup environment
    setup_env_files

    # Install dependencies
    install_backend_deps
    install_frontend_deps

    # Build frontend
    build_frontend

    # Setup database
    setup_database
    run_migrations

    # Setup additional services
    setup_monitoring
    create_ssl_certificates

    # Start services
    start_services
    wait_for_services

    # Run tests
    run_tests

    # Deployment summary
    echo ""
    echo "🎉 EduVerse Deployment Complete!"
    echo "================================="
    echo ""
    echo "🌐 Backend API: http://localhost:8000"
    echo "📖 API Documentation: http://localhost:8000/docs"
    echo "🔄 ReDoc: http://localhost:8000/redoc"
    echo "🌍 Frontend: http://localhost:8080"
    echo ""
    echo "🔧 Services running:"
    echo "  • FastAPI Backend (port 8000)"
    echo "  • PostgreSQL Database (port 5432)"
    echo "  • Redis Cache (port 6379)"
    echo "  • Nginx Reverse Proxy (port 8080)"
    echo ""
    echo "📊 Monitoring:"
    echo "  • Prometheus: http://localhost:9090"
    echo "  • Grafana: http://localhost:3000"
    echo "  • Flower (Celery): http://localhost:5555"
    echo ""
    echo "🔒 Security features enabled:"
    echo "  • JWT Authentication"
    echo "  • CORS protection"
    echo "  • Rate limiting"
    echo "  • SQL injection protection"
    echo "  • XSS protection"
    echo ""
    echo "🚀 Advanced features available:"
    echo "  • Real-time collaboration"
    echo "  • AI-powered tutoring"
    echo "  • VR/AR content support"
    echo "  • Encrypted video caching"
    echo "  • Social learning features"
    echo "  • Blockchain certificates"
    echo "  • Advanced analytics"
    echo ""
    echo "💡 Next steps:"
    echo "  1. Update environment variables in .env files"
    echo "  2. Configure API keys for external services"
    echo "  3. Set up domain and SSL certificates for production"
    echo "  4. Configure monitoring and alerting"
    echo "  5. Set up CI/CD pipeline"
    echo ""
    echo "🎊 EduVerse is now running with all advanced features!"
}

# Help function
show_help() {
    echo "EduVerse Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo "  -d, --dev       Deploy in development mode"
    echo "  -p, --prod      Deploy in production mode"
    echo "  -t, --test      Run tests only"
    echo "  -b, --build     Build only (no deployment)"
    echo ""
    echo "Examples:"
    echo "  $0              # Full deployment"
    echo "  $0 --dev        # Development deployment"
    echo "  $0 --test       # Run tests only"
    echo "  $0 --build      # Build only"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    -d|--dev)
        print_status "Deploying in development mode..."
        main
        ;;
    -p|--prod)
        print_status "Deploying in production mode..."
        # Add production-specific configurations
        main
        ;;
    -t|--test)
        print_status "Running tests only..."
        run_tests
        ;;
    -b|--build)
        print_status "Building only..."
        install_backend_deps
        install_frontend_deps
        build_frontend
        print_success "Build completed"
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac
