# Postways &emsp; ![postways_changes_deploy_AWS](https://github.com/ruslanways/BlogPost/actions/workflows/postways-aws-deploy.yml/badge.svg)<br>
[https://postways.net/](https://postways.net/)<br>
Simple blog web-site that allow users to make some interest posts.<br>

The app build on Django 4.0 / Python 3.10.8 / Postgres 14.6 / Redis 7.0.5

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

### Settings Flow

#### 1. **Base Settings (`config/settings.py`)**

This is the main settings file that:
- Loads environment variables from root `.env` file via `load_dotenv()`
- Sets production defaults (DEBUG=False, specific ALLOWED_HOSTS)
- Configures database, Redis, Celery, etc.
- At the end, tries to import local overrides:

```python
try:
    from .local_settings import *  # Looks for config/local_settings.py
except ImportError:
    print("Production settings apply")
```

#### 2. **Local Settings Override (`config/local_settings.py`)**

**What it does**:
- Sets `DEBUG = True` for local development
- Overrides `ALLOWED_HOSTS = ['*']`
- Provides local database config (postgres/postgres/postgres)
- Only applies when NOT running in Docker

#### 3. **Environment Variables (`.env` file)**

**Single `.env` file:**
- **Root `.env`** (`/Users/ruslanways/code/postways/.env`)
  - Used by Docker Compose (all services reference `./.env`)
  - Used by production
  - Used by local development
  - Contains: SECRET_KEY, POSTGRES_BLOGPOST_USER_PASSWORD, etc.

**⚠️ CRITICAL**: The `.env` file must NEVER be deleted. It contains:
- SECRET_KEY
- DATABASE_URL
- DB_PASSWORD
- REDIS_URL
- EMAIL_* credentials
- DJANGO_SETTINGS_MODULE

### Django Settings Checks

Verify:
- STATIC_ROOT=/home/admin/BlogPost/static (production)
- MEDIA_ROOT=/home/admin/BlogPost/media (production)
- DEBUG=False (production)
- ALLOWED_HOSTS includes postways.net

### How Settings Work in Different Environments

#### **Local Development (without Docker)**

**How It Works**:
1. `settings.py` loads root `.env`
2. `settings.py` imports `local_settings.py` from same directory
3. `local_settings.py` overrides with DEBUG=True, local DB config
4. Uses `localhost` for database/Redis

#### **Docker Development/Production**

**How It Works**:
1. Dockerfile copies everything to `/app/`
2. Workdir is `/app`
3. `.dockerignore` excludes `.env` and `local_settings.py`
4. Docker Compose provides `.env` file to containers
5. `local_settings.py` is NOT in container (excluded)
6. Production settings apply (DEBUG=False)
7. Database/Redis use service names (`db`, `redis`) instead of `localhost`

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
   ```

5. **Run with WebSocket support (Channels)**:
   ```bash
   daphne -b localhost -p 8001 config.asgi:application
   # WebSocket server runs on http://localhost:8001
   ```

6. **Run Celery workers** (in separate terminals):
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