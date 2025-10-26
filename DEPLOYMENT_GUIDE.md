# 🚀 EduVerse Deployment Guide

## 📋 Overview

EduVerse is a next-generation e-learning platform with VR/AR capabilities, AI-powered learning, and automatic app updates. This guide covers the complete deployment process for both backend and frontend.

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with async/await
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT with refresh tokens
- **Real-time**: WebSockets for live features
- **Auto-updates**: Built-in app update system
- **Containerization**: Docker with multi-stage builds

### Frontend (Flutter)
- **Framework**: Flutter 3.x with Dart
- **State Management**: Riverpod
- **Navigation**: GoRouter
- **Auto-updates**: Automatic update checking and installation
- **Cross-platform**: Web, iOS, Android, Desktop

## 🛠️ Prerequisites

### Backend Requirements
- Python 3.11+
- Docker (optional)
- PostgreSQL (production)

### Frontend Requirements
- Flutter 3.16+
- Dart SDK
- Android Studio / Xcode (for mobile)
- Chrome (for web)

## 📦 Backend Deployment

### 1. Local Development

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

The API will be available at `http://localhost:8000`

### 2. Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual container
docker build -t eduverse-backend .
docker run -p 8000:8000 eduverse-backend
```

### 3. Production Deployment

#### Environment Variables
Create a `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/eduverse
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-super-secret-key-change-in-production
DEBUG=false
ALLOWED_HOSTS=["yourdomain.com"]

# OAuth Settings
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# App Update Settings
APP_URL=https://yourdomain.com
```

#### Database Setup
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb eduverse
sudo -u postgres createuser eduverse_user

# Run migrations (if using Alembic)
alembic upgrade head
```

#### Production Server
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📱 Frontend Deployment

### 1. Local Development

```bash
# Navigate to frontend directory
cd frontend

# Get dependencies
flutter pub get

# Run on web
flutter run -d chrome

# Run on mobile (with device connected)
flutter run
```

### 2. Web Deployment

```bash
# Build for web
flutter build web --release

# Deploy to hosting service
# The build files will be in build/web/
```

### 3. Mobile App Deployment

#### Android
```bash
# Build APK
flutter build apk --release

# Build App Bundle (recommended for Play Store)
flutter build appbundle --release
```

#### iOS
```bash
# Build for iOS
flutter build ios --release

# Archive for App Store
# Use Xcode to archive and upload
```

## 🔄 Auto-Update System

### Backend Update Endpoints

The backend provides several endpoints for app updates:

- `GET /api/v1/app/updates` - Check for updates
- `GET /api/v1/app/download/{platform}` - Download update files
- `GET /api/v1/app/version-info` - Get version information
- `GET /api/v1/app/changelog` - Get changelog

### Frontend Update Integration

The Flutter app automatically:
1. Checks for updates on startup
2. Shows update dialogs when available
3. Downloads and installs updates (Android)
4. Redirects to app stores (iOS)

### Update Configuration

Update the version information in `backend/app/api/v1/endpoints/app_updates.py`:

```python
APP_VERSIONS = {
    "android": {
        "current_version": "2.0.0",
        "build_number": "200",
        "download_url": "https://yourdomain.com/api/v1/app/download/android",
        "is_mandatory": False,
        "is_security_update": True,
        # ... other settings
    }
}
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python test_structure.py  # Structure tests
python -m pytest tests/   # Unit tests (requires pytest installation)
```

### Frontend Tests
```bash
cd frontend
flutter test test/simple_test.dart  # Simple tests
flutter test                        # All tests
```

## 🔧 Configuration

### Backend Configuration

Key configuration files:
- `backend/app/core/config.py` - Main configuration
- `backend/requirements.txt` - Python dependencies
- `backend/Dockerfile` - Container configuration

### Frontend Configuration

Key configuration files:
- `frontend/lib/core/app_config.dart` - App configuration
- `frontend/pubspec.yaml` - Flutter dependencies
- `frontend/lib/core/services/update_service.dart` - Update service

## 📊 Monitoring

### Health Checks

Backend health endpoints:
- `GET /health` - Basic health check
- `GET /health/database` - Database health
- `GET /health/complete` - Comprehensive health check

### Logging

The backend includes comprehensive logging:
- Request/response logging
- Error logging
- Performance logging
- Security event logging

## 🔒 Security

### Backend Security
- JWT authentication with refresh tokens
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention with SQLAlchemy
- Rate limiting ready

### Frontend Security
- Secure token storage
- Certificate pinning ready
- Biometric authentication support
- Secure update verification

## 🌐 Production Checklist

### Backend
- [ ] Set strong SECRET_KEY
- [ ] Configure production database
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS for production domains
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline

### Frontend
- [ ] Update API endpoints for production
- [ ] Configure app signing certificates
- [ ] Set up app store accounts
- [ ] Configure push notifications
- [ ] Test on multiple devices
- [ ] Set up crash reporting
- [ ] Configure analytics

## 🚀 Deployment Commands

### Quick Start (Development)
```bash
# Backend
cd backend && python main.py

# Frontend (new terminal)
cd frontend && flutter run -d chrome
```

### Production Deployment
```bash
# Backend with Docker
docker-compose -f docker-compose.production.yml up -d

# Frontend build
cd frontend && flutter build web --release
```

## 📞 Support

For deployment issues:
1. Check the logs in `backend/logs/`
2. Verify all environment variables are set
3. Ensure all dependencies are installed
4. Check firewall and network settings
5. Review the API documentation at `/docs`

## 🎯 Next Steps

After deployment:
1. Set up monitoring and alerting
2. Configure automated backups
3. Implement CI/CD pipeline
4. Set up staging environment
5. Configure load balancing (if needed)
6. Set up CDN for static assets
7. Implement caching strategy

---

**🎓 EduVerse - The Future of Learning**

This deployment guide ensures your EduVerse platform is production-ready with automatic updates, comprehensive monitoring, and scalable architecture.