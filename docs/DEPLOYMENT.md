# Deployment Guide

This guide covers all deployment options for Memory Viewer.

---

## Docker (Recommended)

The fastest way to get Memory Viewer running in production.

### Prerequisites

- Docker Engine ≥ 20.10
- Docker Compose ≥ 2.0

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/xxx/memory-viewer.git
cd memory-viewer

# 2. Copy and edit the configuration
cp config/memory-viewer.example.yaml memory-viewer.yaml
# Edit memory-viewer.yaml to configure your memory sources

# 3. (Optional) Copy environment overrides
cp .env.example .env
# Edit .env as needed

# 4. Launch with Docker Compose
docker compose up -d

# 5. Open the browser
open http://localhost:8501
```

### Architecture

Docker Compose starts three services:

| Service  | Container                   | Port | Role                         |
|----------|-----------------------------|------|------------------------------|
| backend  | memory-viewer-backend       | 8000 | FastAPI API server           |
| frontend | memory-viewer-frontend      | 80   | Nginx serving Vue 3 SPA      |
| nginx    | memory-viewer-nginx         | 8501 | Reverse proxy (unified entry)|

Nginx proxies:
- `/api/*` → backend:8000
- `/*` → frontend:80

### Volumes

The backend mounts `/opt/data` as read-only by default. Adjust the volume mapping in `docker-compose.yml` to match your memory data location.

```yaml
volumes:
  - /path/to/your/data:/opt/data:ro
```

### Health Checks

The backend container includes a health check:
```
GET /api/health → 200 OK
```

Check status with:
```bash
docker compose ps
```

---

## Local Development

### Prerequisites

- Python ≥ 3.10
- Node.js ≥ 18
- npm ≥ 9

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the dev server (auto-reload enabled)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API is available at `http://localhost:8000`.
Swagger UI: `http://localhost:8000/api/docs`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server (with hot reload)
npm run dev
```

The dev server runs at `http://localhost:5173` by default and proxies `/api` requests to the backend.

### Build Frontend for Production

```bash
cd frontend
npm run build
# Output: frontend/dist/
```

### Serve Full Stack Locally (Production-like)

```bash
# Build frontend
cd frontend && npm run build && cd ..

# Start backend (serves built frontend from dist/)
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8501
```

Access at `http://localhost:8501`.

---

## Environment Variables

All environment variables use the `MV_` prefix (recommended). Legacy names are also supported for backward compatibility.

| Variable                      | Legacy Name                | Description                         | Default                                  |
|-------------------------------|----------------------------|-------------------------------------|------------------------------------------|
| `MV_PORT`                     | `MEMORY_VIEWER_PORT`       | Service port                        | `8501`                                   |
| `MV_HOST`                     | `MEMORY_VIEWER_HOST`       | Bind address                        | `0.0.0.0`                                |
| `MV_AGENTMEMORY_CACHE`       | `AGENTMEMORY_CACHE`        | Path to agentmemory JSON cache      | `./data/cache/agentmemory.json`          |
| `MV_HERMES_MEMORIES_DIR`     | `HERMES_MEMORIES_DIR`      | Hermes memories directory           | `./data/memories`                        |
| `MV_HERMES_PROFILES_DIR`     | `HERMES_PROFILES_DIR`      | Hermes profiles directory           | `./data/profiles`                        |
| `MV_BACKUP_DIR`              | `BACKUP_DIR`               | Backup storage directory            | `./data/backups`                         |
| `MV_VERSIONS_DIR`            | `VERSIONS_DIR`             | Version history directory           | `./data/versions`                        |
| `MV_CACHE_REFRESH_INTERVAL`  | `CACHE_REFRESH_INTERVAL`   | Cache refresh interval (minutes)    | `30`                                     |
| `MV_CORS_ORIGINS`            | `CORS_ORIGINS`             | Allowed CORS origins (comma-sep)    | `http://localhost:8501,http://localhost:5173` |
| `MV_AUDIT_LOG`               | `AUDIT_LOG`                | Audit log file path                 | `./data/cache/audit.json`                |

### Configuration Priority

```
MV_ prefix env vars > Legacy env vars > memory-viewer.yaml > Built-in defaults
```

---

## Configuration File

Copy `config/memory-viewer.example.yaml` to `memory-viewer.yaml` and customize:

```yaml
port: 8501
host: "0.0.0.0"

# Paths
agentmemory_cache: "./data/cache/agentmemory.json"
hermes_memories_dir: "./data/memories"
hermes_profiles_dir: "./data/profiles"
backup_dir: "./data/backups"
versions_dir: "./data/versions"

# CORS
cors_origins: "http://localhost:8501,http://localhost:5173"

# Cache
cache_refresh_interval: 30

# Memory Sources (P15 Adapter System)
sources:
  - name: hermes
    type: hermes
    enabled: true
    config:
      memories_dir: "${MV_HERMES_MEMORIES_DIR:./data/memories}"
      profiles_dir: "${MV_HERMES_PROFILES_DIR:./data/profiles}"

  - name: agentmemory
    type: agentmemory
    enabled: true
    config:
      cache_path: "${MV_AGENTMEMORY_CACHE:./data/cache/agentmemory.json}"

  - name: mem0
    type: mem0
    enabled: auto
    config:
      api_key: "${MEM0_API_KEY:}"
      base_url: https://api.mem0.ai/v1
```

The YAML file supports `${ENV_VAR}` and `${ENV_VAR:default}` interpolation syntax, allowing you to mix static config with environment overrides.

---

## Troubleshooting

### Port already in use

```bash
# Find and kill the process using port 8501
lsof -i :8501
kill -9 <PID>
```

Or change the port:
```bash
export MV_PORT=9000
```

### Cannot connect to memory source

1. Verify the path exists and is readable:
   ```bash
   ls -la /path/to/memories
   ```
2. Check the health endpoint:
   ```bash
   curl http://localhost:8501/api/health
   ```
3. List registered sources:
   ```bash
   curl http://localhost:8501/api/sources
   ```

### Docker: volume permission denied

Ensure the Docker user has read access to the mounted data directory:
```bash
chmod -R o+r /path/to/your/data
```

### Frontend not loading / blank page

1. Rebuild the frontend:
   ```bash
   cd frontend && npm run build
   ```
2. Check that `frontend/dist/` exists and is served correctly.
3. Verify nginx configuration if using Docker.

### CORS errors during development

Ensure `MV_CORS_ORIGINS` includes your frontend dev server URL:
```bash
export MV_CORS_ORIGINS=http://localhost:5173,http://localhost:8501
```

### Cache not refreshing

Check the refresh interval and manually trigger:
```bash
curl -X POST http://localhost:8501/api/cache/refresh
```

---

## Production Recommendations

1. **Reverse Proxy**: Use nginx or Caddy in front of the app for TLS termination.
2. **Persistent Data**: Mount `./data` as a named Docker volume or bind mount.
3. **Backups**: Configure regular backups via the Backup API or UI.
4. **Monitoring**: Use the `/api/health` and `/api/metrics` endpoints for uptime checks.
5. **Rate Limiting**: Apply rate limits at the reverse proxy layer.
