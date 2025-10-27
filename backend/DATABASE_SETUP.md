# 🗄️ EduVerse Database & Storage Setup Guide

## 📋 Overview

EduVerse supports multiple database backends and cloud storage providers with easy switching between them. This guide covers setup for all supported options.

## 🎯 Supported Databases

### 🐘 PostgreSQL (Recommended)
**Best for**: Production environments, complex queries, analytics
- ✅ Excellent performance and reliability
- ✅ JSONB support for flexible data
- ✅ Full-text search capabilities
- ✅ Strong ACID compliance
- ✅ Excellent cloud support

### 🐬 MySQL
**Best for**: Traditional web applications, existing MySQL infrastructure
- ✅ Wide compatibility and support
- ✅ Good performance
- ✅ JSON column support
- ✅ Cloud provider support

### 🍃 MongoDB
**Best for**: Document-based features, flexible schemas
- ✅ Schema flexibility
- ✅ Horizontal scaling
- ✅ Rich query language
- ✅ Good for content management

### 📁 SQLite
**Best for**: Development, testing, small deployments
- ✅ Zero configuration
- ✅ File-based storage
- ✅ Perfect for development

## ☁️ Supported Storage Providers

### 🚀 AWS S3 (Recommended)
- Global CDN integration
- Excellent performance
- Comprehensive features
- Cost-effective

### 🌐 Google Cloud Storage
- Global infrastructure
- Strong integration with GCP
- Good performance

### 🔷 Azure Blob Storage
- Microsoft ecosystem integration
- Enterprise features
- Good performance

### ⚡ Cloudflare R2
- S3-compatible API
- No egress fees
- Global edge network

### 🌊 DigitalOcean Spaces
- Simple and affordable
- S3-compatible API
- Good for smaller projects

## 🚀 Quick Setup

### 1. Choose Your Database

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` and set your database type:
```env
# Choose: postgresql, mysql, mongodb, sqlite
DB_TYPE=postgresql
```

### 2. Local Development Setup

#### PostgreSQL (Recommended)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres createdb eduverse
sudo -u postgres createuser eduverse_user
sudo -u postgres psql -c "ALTER USER eduverse_user PASSWORD 'eduverse_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE eduverse TO eduverse_user;"

# Update .env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=eduverse
POSTGRES_USER=eduverse_user
POSTGRES_PASSWORD=eduverse_password
```

#### MySQL Alternative
```bash
# Install MySQL
sudo apt-get install mysql-server

# Create database and user
mysql -u root -p
CREATE DATABASE eduverse;
CREATE USER 'eduverse_user'@'localhost' IDENTIFIED BY 'eduverse_password';
GRANT ALL PRIVILEGES ON eduverse.* TO 'eduverse_user'@'localhost';
FLUSH PRIVILEGES;

# Update .env
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=eduverse
MYSQL_USER=eduverse_user
MYSQL_PASSWORD=eduverse_password
```

#### MongoDB Alternative
```bash
# Install MongoDB
sudo apt-get install mongodb

# Update .env
DB_TYPE=mongodb
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=eduverse
```

### 3. Docker Setup (Easiest)

#### PostgreSQL (Default)
```bash
docker-compose up -d postgres redis
```

#### MySQL
```bash
docker-compose --profile mysql up -d mysql redis
```

#### MongoDB
```bash
docker-compose --profile mongodb up -d mongodb redis
```

### 4. Initialize Database
```bash
cd backend
python setup_database.py setup
```

## ☁️ Cloud Database Setup

### AWS RDS (PostgreSQL)
```env
DB_TYPE=postgresql
DATABASE_URL=postgresql+asyncpg://username:password@your-rds-endpoint:5432/eduverse
DB_SSL_MODE=require
```

### Google Cloud SQL
```env
DB_TYPE=postgresql
DATABASE_URL=postgresql+asyncpg://user:password@/eduverse?host=/cloudsql/project:region:instance
```

### Azure Database
```env
DB_TYPE=postgresql
DATABASE_URL=postgresql+asyncpg://user:password@server.postgres.database.azure.com:5432/eduverse
DB_SSL_MODE=require
```

### Supabase
```env
DB_TYPE=postgresql
DATABASE_URL=postgresql+asyncpg://postgres:password@db.project.supabase.co:5432/postgres
```

### PlanetScale (MySQL)
```env
DB_TYPE=mysql
DATABASE_URL=mysql+aiomysql://username:password@host/database?ssl_ca=/etc/ssl/certs/ca-certificates.crt
```

### MongoDB Atlas
```env
DB_TYPE=mongodb
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/eduverse?retryWrites=true&w=majority
```

## 📁 Cloud Storage Setup

### AWS S3 (Recommended)
```env
STORAGE_PROVIDER=aws_s3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
AWS_S3_BUCKET=eduverse-storage

# Optional: Enable CloudFront CDN
CDN_ENABLED=true
CDN_BASE_URL=https://d123456789.cloudfront.net
```

### Google Cloud Storage
```env
STORAGE_PROVIDER=google_cloud
GCP_PROJECT_ID=your-project-id
GCP_CREDENTIALS_PATH=/path/to/credentials.json
GCP_BUCKET=eduverse-storage
```

### Azure Blob Storage
```env
STORAGE_PROVIDER=azure_blob
AZURE_ACCOUNT_NAME=your-account-name
AZURE_ACCOUNT_KEY=your-account-key
AZURE_CONTAINER=eduverse-storage
```

### Cloudflare R2
```env
STORAGE_PROVIDER=cloudflare_r2
CLOUDFLARE_R2_ACCESS_KEY=your-access-key
CLOUDFLARE_R2_SECRET_KEY=your-secret-key
CLOUDFLARE_R2_BUCKET=eduverse-storage
CLOUDFLARE_R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
```

## 🔧 Database Management

### Setup Script Commands
```bash
# Full setup (recommended)
python setup_database.py setup

# Test all connections
python setup_database.py test

# Show cloud presets
python setup_database.py presets

# Help
python setup_database.py help
```

### Switching Databases
1. Update `DB_TYPE` in `.env`
2. Set appropriate connection parameters
3. Run setup: `python setup_database.py setup`

### Migration Between Databases
```bash
# Backup current database
python setup_database.py backup

# Change DB_TYPE in .env
# Run setup for new database
python setup_database.py setup

# Restore data (manual process)
```

## 🏗️ Production Deployment

### 1. Database Recommendations

**Small to Medium Scale (< 10k users)**
- PostgreSQL on managed service (AWS RDS, Google Cloud SQL)
- Single instance with read replicas

**Large Scale (10k+ users)**
- PostgreSQL with connection pooling (PgBouncer)
- Read replicas for analytics
- Separate databases for different services

**Global Scale**
- Multi-region PostgreSQL setup
- CDN for static content
- Caching layer (Redis)

### 2. Storage Recommendations

**Small Projects**
- Single cloud storage bucket
- CDN for global distribution

**Large Projects**
- Multi-region storage
- Separate buckets for different content types
- Image optimization and compression

### 3. Security Best Practices

```env
# Use strong passwords
POSTGRES_PASSWORD=very-long-random-password-here

# Enable SSL
DB_SSL_MODE=require
DB_SSL_CERT=/path/to/client-cert.pem

# Restrict access
ALLOWED_HOSTS=["yourdomain.com"]
```

## 🧪 Testing

### Test Database Connection
```bash
python setup_database.py test
```

### Test Storage
```bash
python -c "
import asyncio
from app.core.cloud_storage import storage_service

async def test():
    url = await storage_service.upload_file('test.txt', b'Hello World', 'text/plain')
    print(f'Upload successful: {url}')
    await storage_service.delete_file('test.txt')
    print('Cleanup successful')

asyncio.run(test())
"
```

## 🔍 Troubleshooting

### Common Issues

**Database Connection Failed**
1. Check if database service is running
2. Verify credentials in `.env`
3. Check firewall settings
4. Test with database client

**Storage Upload Failed**
1. Verify cloud credentials
2. Check bucket permissions
3. Test with cloud provider CLI
4. Check network connectivity

**Performance Issues**
1. Monitor connection pool usage
2. Check database query performance
3. Enable query logging
4. Consider read replicas

### Debug Commands
```bash
# Check database status
python -c "
import asyncio
from app.core.database import check_database_connection
print(asyncio.run(check_database_connection()))
"

# Check storage status
python -c "
import asyncio
from app.core.cloud_storage import storage_service
print(asyncio.run(storage_service.list_files()))
"
```

## 📊 Monitoring

### Database Metrics
- Connection pool usage
- Query performance
- Storage usage
- Backup status

### Storage Metrics
- Upload/download rates
- Storage usage
- CDN hit rates
- Error rates

## 🔄 Backup & Recovery

### Database Backup
```bash
# PostgreSQL
pg_dump -h localhost -U eduverse_user eduverse > backup.sql

# MySQL
mysqldump -u eduverse_user -p eduverse > backup.sql

# MongoDB
mongodump --db eduverse --out backup/
```

### Storage Backup
- Enable versioning on cloud storage
- Regular snapshots of critical data
- Cross-region replication for disaster recovery

---

**🎓 EduVerse Database & Storage Setup Complete!**

Your EduVerse platform now supports flexible database backends and cloud storage with easy switching between providers.