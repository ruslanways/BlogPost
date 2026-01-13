# Postways &emsp; ![postways_changes_deploy_AWS](https://github.com/ruslanways/BlogPost/actions/workflows/postways-aws-deploy.yml/badge.svg)<br>
[https://postways.net/](https://postways.net/)<br>
Simple blog web-site that allow users to make some interest posts.<br>

The app build on Django 4.0 / Python 3.10.19 / Postgres 14.6 / Redis 7.0.5

> OpenApi documentation available on page: /docs/

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Requirements](#2-requirements)
3. [Project Structure](#3-project-structure)
4. [Settings Configuration](#4-settings-configuration)
5. [Development Setup](#5-development-setup)
6. [Production Deployment](#6-production-deployment)
7. [Docker Deployment (Alternative)](#7-docker-deployment-alternative)
8. [Service Management](#8-service-management)
9. [Disaster Recovery](#9-disaster-recovery)
10. [Backup Strategy](#10-backup-strategy)

---

## 1. Architecture Overview

| Layer | Service | Purpose |
|------|--------|---------|
| Reverse proxy | Nginx | TLS termination, static/media serving, routing |
| WSGI | Gunicorn | Django HTTP requests |
| ASGI | Daphne | WebSocket / SSE |
| Workers | Celery + Celery Beat | Background jobs |
| Database | PostgreSQL | Primary data store |
| Cache / Broker | Redis | Celery broker, caching |
| CDN | Cloudflare | Caching, WAF, TLS |

**Note on Nginx Configuration**: The `nginx.conf` file in the project root is configured for Dockerized deployment (uses service names like `web:8000` and `channels:8001`). On the production server, Nginx uses different settings located at `/etc/nginx/sites-available/blogpost` that are configured for the actual EC2 deployment environment.

---

## 2. Requirements

- **Python**: 3.10.x (required)
- **Django**: 4.0.6
- **PostgreSQL**: 14.6
- **Redis**: 7.0.5

---

## 3. Project Structure

```
postways/
├── .env                          # Root .env file (used by Docker & production)
├── manage.py                     # Django management script
├── nginx.conf                    # Nginx config for Docker (see note above)
├── config/                       # Django project configuration
│   ├── settings.py              # Main settings file
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── celery.py
│   └── local_settings.py        # Local dev settings override
├── diary/                        # Django app
├── templates/                    # Project templates
├── var/                          # Runtime data directory
│   ├── media/                   # User-uploaded files
│   ├── static/                  # Collected static files
│   ├── logs/                    # Application logs
│   ├── celery/                  # Celery data
│   ├── redis/                   # Redis data
│   └── schema.yaml              # API schema
└── requirements.txt
```

### Production Server Directory Layout

| Path | Purpose |
|-----|--------|
| /home/admin/BlogPost | Project root |
| /home/admin/BlogPost/venv | Python virtualenv |
| /home/admin/BlogPost/static | Collected static files |
| /home/admin/BlogPost/media | User uploaded files |
| /etc/nginx/sites-available/blogpost | Nginx site config (production) |

---

## 4. Settings Configuration

### Settings Architecture Overview

Settings are organized in three clear layers:

1. **`config/settings.py`** - Main settings file with production defaults
2. **`.env` file** (root) - Environment variables (secrets, passwords, environment-specific values)
3. **`config/local_settings.py`** - Local development overrides (optional, not in Docker/production)

### Quick Reference: Where Settings Are Defined

| Setting Type | Location | Examples |
|-------------|----------|----------|
| **Application Structure** | `config/settings.py` (hardcoded) | INSTALLED_APPS, MIDDLEWARE, STATIC_URL, MEDIA_URL |
| **Production Defaults** | `config/settings.py` (hardcoded) | DEBUG=False, ALLOWED_HOSTS, database name/user |
| **Secrets & Passwords** | `.env` file (root) | SECRET_KEY, POSTGRES_BLOGPOST_USER_PASSWORD, EMAIL_HOST_PASSWORD |
| **Environment-Specific** | `.env` file (root) | DB_HOST, REDIS_HOST, WEEKLY_REPORT_RECIPIENTS |
| **Local Dev Overrides** | `config/local_settings.py` | DEBUG=True, ALLOWED_HOSTS=['*'], local DB config |

### Environment Variables Reference

All environment variables are documented in `config/settings.py` at the top of the file. Here's what goes in your `.env` file:

#### **Required Variables** (must be in `.env` for production):
```
SECRET_KEY=your-secret-key-here
DATABASE_PASSWORD=your-db-password
EMAIL_HOST_PASSWORD=your-email-password
```

#### **Optional Variables** (have defaults, override if needed):
```
DATABASE_HOST=localhost     # Use 'db' in Docker
DATABASE_PORT=5432
DATABASE_NAME=blogpost_db  # Database name (default: 'blogpost_db')
DATABASE_USER=blogpost_user # Database user (default: 'blogpost_user')
REDIS_HOST=localhost        # Use 'redis' in Docker
REDIS_PORT=6379
WEEKLY_REPORT_RECIPIENTS=ruslanways@gmail.com
```

#### **Local Development Overrides** (optional, used by `local_settings.py`):
```
# For local dev, you can override database settings with simpler defaults:
DATABASE_NAME=postgres      # Local database name (default: 'postgres')
DATABASE_USER=postgres      # Local database user (default: 'postgres')
DATABASE_PASSWORD=postgres  # Local database password (default: 'postgres')
# Note: DATABASE_HOST is always 'localhost' in local_settings.py
```

### Settings File Details

#### 1. **Base Settings (`config/settings.py`)**

**What it contains:**
- All Django application configuration (INSTALLED_APPS, MIDDLEWARE, etc.)
- Hardcoded production defaults (DEBUG=False, ALLOWED_HOSTS, etc.)
- Environment variable loading (centralized at the top)
- Production database configuration
- Redis/Celery/Email configuration using env vars
- At the end, tries to import local overrides:

```python
try:
    from .local_settings import *  # Looks for config/local_settings.py
except ImportError:
    print("Production settings apply")
```

**Key sections:**
- **Environment Variables Configuration** - Documents all env vars used
- **Database Configuration** - Uses DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD
- **Redis Configuration** - Uses REDIS_HOST, REDIS_PORT (for Channels and Celery)
- **Email Configuration** - Uses EMAIL_HOST_PASSWORD

#### 2. **Local Settings Override (`config/local_settings.py`)**

**What it does:**
- Sets `DEBUG = True` for local development
- Overrides `ALLOWED_HOSTS = ['*']`
- Provides local database config using environment variables:
  - `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_PORT`
  - Defaults to `postgres/postgres/postgres` if env vars not set
  - Always uses `localhost` for `DATABASE_HOST` (ignores .env value)
- Only applies when NOT running in Docker
- This file is excluded from Docker builds via `.dockerignore`

#### 3. **Environment Variables (`.env` file)**

**Single `.env` file location:**
- **Root `.env`** (`/Users/ruslanways/code/postways/.env`)
  - Used by Docker Compose (all services reference `./.env`)
  - Used by production (EC2 server)
  - Used by local development

**⚠️ CRITICAL**: The `.env` file must NEVER be deleted or committed to git. It contains:
- SECRET_KEY (Django secret key)
- DATABASE_PASSWORD (database password)
- EMAIL_HOST_PASSWORD (SMTP password)
- WEEKLY_REPORT_RECIPIENTS (optional)
- Local dev variables (DATABASE_NAME, DATABASE_USER, etc. - optional)

### Django Settings Checks

Verify:
- STATIC_ROOT=/home/admin/BlogPost/static (production)
- MEDIA_ROOT=/home/admin/BlogPost/media (production)
- DEBUG=False (production)
- ALLOWED_HOSTS includes postways.net

### How Settings Work in Different Environments

#### **Local Development (without Docker)**

**Settings Flow**:
1. `settings.py` loads environment variables from root `.env` file
2. `settings.py` sets production defaults (DEBUG=False, production DB config)
3. `settings.py` imports `local_settings.py` (if it exists)
4. `local_settings.py` overrides:
   - `DEBUG = True`
   - `ALLOWED_HOSTS = ['*']`
   - Database config using env vars: `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, etc.
   - Defaults to `postgres/postgres/postgres` if env vars not set
5. Database/Redis use `localhost` (default values)

**Required `.env` variables for local dev:**
- `SECRET_KEY` (required)
- `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD` (optional, have defaults)
- `EMAIL_HOST_PASSWORD` (optional, only if testing email)

#### **Docker Development/Production**

**Settings Flow**:
1. Dockerfile copies everything to `/app/` (excludes `.env` and `local_settings.py` via `.dockerignore`)
2. Docker Compose provides `.env` file to containers via `env_file: - ./.env`
3. `settings.py` loads environment variables from `.env`
4. `local_settings.py` is NOT in container (excluded by `.dockerignore`)
5. Production settings apply (DEBUG=False, production DB config)
6. Database/Redis use service names (`db`, `redis`) - set via Docker Compose environment variables

**Required `.env` variables for Docker/production:**
- `SECRET_KEY` (required)
- `DATABASE_PASSWORD` (required)
- `EMAIL_HOST_PASSWORD` (required)
- `WEEKLY_REPORT_RECIPIENTS` (optional)
- `DATABASE_HOST=db` and `REDIS_HOST=redis` (set in docker-compose.yml, not in .env)

#### **Production EC2 (Direct Deployment)**

**Settings Flow**:
1. `.env` file exists on server at `/home/admin/BlogPost/.env`
2. `settings.py` loads environment variables from `.env`
3. `local_settings.py` does NOT exist on server
4. Production settings apply (DEBUG=False)
5. Database/Redis use `localhost` (default values) or configured hosts

**Required `.env` variables for production:**
- `SECRET_KEY` (required)
- `DATABASE_PASSWORD` (required)
- `EMAIL_HOST_PASSWORD` (required)
- `WEEKLY_REPORT_RECIPIENTS` (optional)

---

## 5. Development Setup

### Prerequisites
- Python 3.10.x
- PostgreSQL running on `localhost:5432`
- Redis running on `localhost:6379`
- Virtual environment activated

### Setup Steps

1. **Clone and setup**:
   ```bash
   git clone <repository>
   cd postways
   # ⚠️ IMPORTANT: You MUST use Python 3.10.x to create the virtual environment
   # Verify your Python version: python --version
   # If you have multiple Python versions, use: python3.10 -m venv .venv
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   - Ensure `.env` file exists in root with required variables
   - `local_settings.py` should be in `config/`

3. **Database setup**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser  # Optional
   ```

4. **Run development server**:
   ```bash
   python manage.py runserver
   # Server runs on http://localhost:8000
   # Note: Django automatically uses ASGI/Daphne when Channels is installed,
   # so WebSocket support is included automatically on the same port
   ```

**Note on WebSocket Support**: 
- When Django Channels is installed and `ASGI_APPLICATION` is configured (as it is in this project),
  `python manage.py runserver` automatically uses Daphne (ASGI server) instead of the default WSGI server.
- This means **both HTTP and WebSocket connections work on the same port** (8000) during development.
- You don't need to run a separate Daphne server for local development.
- In production, HTTP and WebSocket are served separately (Gunicorn on port 8000, Daphne on port 8001).

5. **Run Celery workers** (in separate terminals):
   ```bash
   celery -A config worker -l info
   celery -A config beat -l info
   ```

**Development Workflow**:
1. Make code changes
2. Run tests: `python manage.py test`
3. Create migrations: `python manage.py makemigrations`
4. Apply migrations: `python manage.py migrate`
5. Test locally
6. Commit and push to trigger deployment

---

## 6. Production Deployment

**Current Deployment Method**: Direct deployment to EC2 via GitHub Actions (not Docker)

**Trigger**: Automatically runs on push to `main` branch

### Deployment Pipeline

#### **Step 1: Automated Testing** (GitHub Actions)

1. **Checkout code** from repository
2. **Setup Python 3.10.x** environment
3. **Start services**:
   - PostgreSQL 14.6 container (port 5432)
   - Redis 7.0.5 container (port 6379)
4. **Install dependencies**:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. **Setup test environment**:
   - Creates `.env` file in **root directory** from `DJANGO_ENV_FILE` secret
   - Creates `local_settings.py` in `config/` from `LOCAL_SETTINGS` secret
6. **Run tests**:
   ```bash
   python manage.py test
   ```

#### **Step 2: Automated Deployment** (if tests pass)

1. **SSH to EC2 instance**:
   - Uses AWS private key from secrets
   - Connects to EC2 instance via SSH

2. **Automated deployment steps** (all executed automatically):
   ```bash
   cd BlogPost/
   git pull origin main
   source .venv/bin/activate  # Activate virtual environment if it exists
   pip install -q -r requirements.txt  # Update dependencies
   python manage.py migrate --noinput  # Run migrations
   python manage.py collectstatic --noinput  # Collect static files
   sudo systemctl restart gunicorn  # Restart web server
   sudo systemctl restart daphne  # Restart WebSocket server
   sudo systemctl restart celery  # Restart Celery worker
   sudo systemctl restart celerybeat  # Restart Celery beat scheduler
   sudo systemctl reload nginx  # Reload reverse proxy
   ```

### Production Server Setup

- **Web Server**: Gunicorn serving Django WSGI app
- **WebSocket Server**: Daphne serving Django ASGI app (Channels)
- **Background Tasks**: Celery worker + beat
- **Reverse Proxy**: Nginx (configuration at `/etc/nginx/sites-available/blogpost`)
- **Database**: PostgreSQL (local or RDS)
- **Cache/Queue**: Redis

### Production Nginx Configuration

The production server uses Nginx configuration at `/etc/nginx/sites-available/blogpost`:

```
location /static/ {
    alias /home/admin/BlogPost/static/;
}
location /media/ {
    alias /home/admin/BlogPost/media/;
}
location / {
    include proxy_params;
    proxy_pass http://unix:/run/gunicorn.sock;
}
location /ws/ {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_pass https://127.0.0.1:8001;
}
```

**GitHub Actions Secrets Required**:
- DJANGO_ENV_FILE
- LOCAL_SETTINGS
- AWS_PRIVATE_KEY
- HOSTNAME
- USER_NAME

---

## 7. Docker Deployment (Alternative)

**Note**: This is the containerized approach using Docker Compose. Currently not used in production but available for future use.

### Prerequisites
- Docker and Docker Compose installed
- `.env` file configured in root

### Deployment Process

#### **Step 1: Build and Start Services**
```bash
docker-compose up -d --build
```

**What Happens**:

1. **Build Phase**:
   - Dockerfile copies entire project to `/app/` in container
   - Installs Python dependencies from `requirements.txt`
   - Creates non-root user `admin`
   - Sets working directory to `/app`

2. **Service Startup** (in order):

   **Database (PostgreSQL)**:
   - Image: `postgres:14.6`
   - Port: 5432 (internal)
   - Volume: `postgres_data` for persistence
   - Environment: Loaded from root `.env`

   **Redis**:
   - Image: `redis:7.0.5`
   - Port: 6379 (internal)
   - No persistence (can be added)

   **Web Service** (Gunicorn):
   - Waits for database: `wait_for_db`
   - Runs migrations: `makemigrations` + `migrate`
   - Collects static files: `collectstatic`
   - Starts Gunicorn: 3 workers on port 8000
   - Volume: `workdir` for code persistence

   **Channels Service** (Daphne):
   - Serves ASGI app on port 8001
   - Handles WebSocket connections
   - Depends on web service

   **Celery Service**:
   - Runs worker: `celery -A config worker`
   - Runs beat: `celery -A config beat`
   - Handles background tasks and scheduled jobs

   **Nginx**:
   - Reverse proxy on port 80
   - Routes `/` → web:8000 (HTTP)
   - Routes `/ws/` → channels:8001 (WebSocket)
   - Serves static/media files from volumes
   - Uses `nginx.conf` from project root

#### **Step 2: Service Management**

**View logs**:
```bash
docker-compose logs -f [service_name]
```

**Restart service**:
```bash
docker-compose restart [service_name]
```

**Stop all services**:
```bash
docker-compose down
```

**Stop and remove volumes** (⚠️ deletes data):
```bash
docker-compose down -v
```

**Update and redeploy**:
```bash
git pull
docker-compose up -d --build
```

**Advantages of Docker Approach**:
- ✅ Isolated environments
- ✅ Easy scaling
- ✅ Consistent across dev/staging/prod
- ✅ Simplified dependency management
- ✅ Easy rollback (previous image)
- ✅ Service orchestration handled by Compose

**Current Status**: 
- Docker setup is available and functional
- Not currently used in production deployment
- Can be used for local development or future production migration

---

## 8. Service Management

### Production Service Commands

| Service | Command |
|--------|--------|
| Gunicorn | `sudo systemctl restart gunicorn` |
| Daphne | `sudo systemctl restart daphne` |
| Celery | `sudo systemctl restart celery` |
| Celery Beat | `sudo systemctl restart celerybeat` |
| Nginx | `sudo systemctl reload nginx` |
| Postgres | `sudo systemctl restart postgresql` |
| Redis | `sudo systemctl restart redis` |

### One-Command Health Check

```bash
sudo systemctl status gunicorn daphne celery redis postgresql nginx
curl -I https://postways.net
curl -I https://postways.net/static/admin/css/base.css
curl -I https://postways.net/media/diary/images/IMG_8878.jpg
```

---

## 9. Disaster Recovery

| Symptom | Fix |
|--------|----|
| 500 errors | Check `.env`, restart gunicorn |
| WebSockets down | Restart daphne |
| No images | Restore `/home/admin/BlogPost/media` |
| No CSS | run `collectstatic` |
| Celery down | Restart redis + celery |
| DB auth error | Check DATABASE_URL / DB_PASSWORD |
| Nginx 502 | Check gunicorn socket |

---

## 10. Backup Strategy

**Daily Backups**:
- `tar /home/admin/BlogPost/media`
- `pg_dump blogpost_db`

**Retention**: Keep 14 days minimum.

---

## ⚠️ Never Do

- Never delete `.env`
- Never run pip outside `/venv`
- Never change project layout without updating nginx + systemd
- Never delete `/media` or `/static`

---

## Deployment Methods Comparison

| Aspect | Local Development | Production (Current) | Production (Docker) |
|--------|------------------|---------------------|---------------------|
| **Method** | Direct Python | GitHub Actions → EC2 | Docker Compose |
| **Settings** | `local_settings.py` | Production settings | Production settings |
| **DEBUG** | `True` | `False` | `False` |
| **Database** | `localhost` | EC2 PostgreSQL | Container `db` |
| **Redis** | `localhost` | EC2 Redis | Container `redis` |
| **Testing** | Manual | Automated (CI) | Manual/Automated |
| **Deployment** | N/A | Auto on push | Manual/CI |
| **Isolation** | None | Process-level | Container-level |
| **Scaling** | N/A | Manual | Easy (Docker) |

---

Status of last deployment:<br>