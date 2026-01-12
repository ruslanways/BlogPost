# Settings Flow and Project Structure Explanation

## Requirements

- **Python**: 3.10.x (required)
- **Django**: 4.0.6
- **PostgreSQL**: 14.6
- **Redis**: 7.0.5

## Project Directory Structure

```
postways/
├── .env                          # Root .env file (used by Docker & production)
├── manage.py                     # Django management script
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

## Settings Flow

### 1. **Base Settings (`config/settings.py`)**

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

### 2. **Local Settings Override (`config/local_settings.py`)**

**What it does**:
- Sets `DEBUG = True` for local development
- Overrides `ALLOWED_HOSTS = ['*']`
- Provides local database config (postgres/postgres/postgres)
- Only applies when NOT running in Docker

### 3. **Environment Variables (`.env` file)**

**Single `.env` file:**
- **Root `.env`** (`/Users/ruslanways/code/postways/.env`)
  - Used by Docker Compose (all services reference `./.env`)
  - Used by production
  - Used by local development
  - Contains: SECRET_KEY, POSTGRES_BLOGPOST_USER_PASSWORD, etc.

## How It Works in Different Environments

### **Local Development (without Docker)**

**How It Works**:
- Django loads `local_settings.py` from `config/`
- Local development settings apply (DEBUG=True)

**How It Works**:
1. `settings.py` loads root `.env`
2. `settings.py` imports `local_settings.py` from same directory
3. `local_settings.py` overrides with DEBUG=True, local DB config
4. Uses `localhost` for database/Redis

### **Docker Development/Production**

**How It Works**:
1. Dockerfile copies everything to `/app/`
2. Workdir is `/app`
3. `.dockerignore` excludes `.env` and `local_settings.py`
4. Docker Compose provides `.env` file to containers
5. `local_settings.py` is NOT in container (excluded)
6. Production settings apply (DEBUG=False)
7. Database/Redis use service names (`db`, `redis`) instead of `localhost`

## The Confusion Points

### 1. **Why `var/` directory?**

The `var/` directory serves as a container for runtime data:
- **Runtime data**: `media/`, `static/`, `logs/`, `celery/`, `redis/`
- **Generated files**: `schema.yaml`

**Note**: In Docker, these are in volumes, not in `var/`. The `var/` directory is primarily for local development to keep runtime data organized separately from the Django project code.

### 2. **Why flattened structure?**

- **Root level**: Contains all Django application code (manage.py, config/, diary/, templates/)
- **`var/`**: Contains runtime/generated data that changes during execution (user uploads, logs, collected static files)

This flattened structure makes the project easier to navigate and understand, while keeping runtime data organized in `var/`.

## Project Structure Summary

**Current Structure**: The project has a clean separation:
- All Django code and settings at root level (config/, diary/, templates/)
- All runtime data in `var/`
- Single `.env` file in root for all environments

---

## Development and Deployment Flows

### 🔧 **Local Development Flow**

**Prerequisites**:
- Python 3.10.x
- PostgreSQL running on `localhost:5432`
- Redis running on `localhost:6379`
- Virtual environment activated

**Setup Steps**:
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

**What Happens**:
- `settings.py` loads root `.env` file
- `local_settings.py` is imported (DEBUG=True, local DB config)
- Uses `localhost` for database and Redis
- Static/media files served from `var/static/` and `var/media/`

**Development Workflow**:
1. Make code changes
2. Run tests: `python manage.py test`
3. Create migrations: `python manage.py makemigrations`
4. Apply migrations: `python manage.py migrate`
5. Test locally
6. Commit and push to trigger deployment

---

### 🚀 **Production Flow (Current: GitHub Actions → EC2)**

**Current Deployment Method**: Direct deployment to EC2 via GitHub Actions (not Docker)

**Trigger**: Automatically runs on push to `main` branch

**Process Flow**:

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

**Production Server Setup** (on EC2):
- **Web Server**: Gunicorn serving Django WSGI app
- **WebSocket Server**: Daphne serving Django ASGI app (Channels)
- **Background Tasks**: Celery worker + beat
- **Reverse Proxy**: Nginx
- **Database**: PostgreSQL (local or RDS)
- **Cache/Queue**: Redis

**Configuration**:
- `DEBUG = False` (production settings from `settings.py`)
- `local_settings.py` is NOT used in production (excluded or not present)
- Environment variables from `.env` file on server
- Static files collected to `var/static/` or configured static root
- Media files in `var/media/`

**Key Points**:
- ✅ Tests run automatically before deployment
- ✅ Deployment only happens if tests pass
- ✅ Code is pulled directly to EC2 (not containerized)
- ✅ Services run as system processes on EC2
- ✅ **Fully automated deployment**: All post-deployment steps are automated (migrations, collectstatic, service restarts)
- ✅ Uses correct service versions: PostgreSQL 14.6, Redis 7.0.5 (matches requirements)
- ✅ `.env` file created in root directory (matches documentation)

---

### 🐳 **Production Flow with Docker** (Alternative/Future)

**Note**: This is the containerized approach using Docker Compose. Currently not used in production but available for future use.

**Prerequisites**:
- Docker and Docker Compose installed
- `.env` file configured in root

**Deployment Process**:

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

**Configuration**:
- `local_settings.py` is **excluded** via `.dockerignore`
- Production settings apply (DEBUG=False)
- Database/Redis use service names (`db`, `redis`) not `localhost`
- Environment variables from root `.env` file
- Static/media files in Docker volumes
- All services communicate via Docker network

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

## Summary: Deployment Methods Comparison

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
