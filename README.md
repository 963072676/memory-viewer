# Memory Viewer

> Browse, search, and manage **agent memories** in a fast, focused dashboard.
> Built for the [Hermes Agent](https://github.com/nousresearch/hermes-agent) ecosystem — works with any agent that persists memory as files.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Vue](https://img.shields.io/badge/Vue-3.4-42b883)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688)

A single-page dashboard for everything your agent remembers: **agentmemory** (via MCP), **Hermes `MEMORY.md` / `USER.md`**, and per-profile memory across multiple agents. Vue 3 + TypeScript on the front, FastAPI + APScheduler on the back.

## ✨ Features

- 🔍 **Unified search** — full-text across all memory sources, instant client-side filter
- 🧠 **Memory browsing** — list, sort, paginate, and inspect any entry (with health score, version history, related items)
- ✏️ **CRUD** — create, edit, delete memories; mark favorites; smart collections
- 🗂️ **Multi-profile** — view memories from any Hermes profile side-by-side
- 🤖 **Hermes memory** — read `MEMORY.md` / `USER.md` files directly, including per-profile
- 📊 **Dashboard** — usage statistics, type breakdown, strength distribution
- 🌍 **i18n** — `zh-CN` (default) + `en-US`, design-token driven (dark mode out-of-box)
- 🔄 **Auto-refresh** — APScheduler pulls new memories every 30 min, no manual reload

## 🚀 Quick Start

### Docker (recommended)

```bash
docker run -d \
  --name memory-viewer \
  --restart unless-stopped \
  -p 8501:8501 \
  -v /opt/data/memory-viewer/v2/backend:/workspace/backend:ro \
  -v /opt/data/memory-viewer/v2/frontend/dist:/workspace/frontend/dist:ro \
  -v /opt/data/memory-viewer/v2/memory-viewer.yaml:/workspace/memory-viewer.yaml:ro \
  -v /opt/data/memory-viewer/v2/data:/workspace/data:rw \
  -v ~/.hermes/profiles:/workspace/hermes-profiles:ro \
  -v ~/.hermes/memories:/workspace/hermes-memories:ro \
  -v ~/.agentmemory:/workspace/agentmemory:ro \
  --user 10000:10000 \
  --entrypoint /bin/bash \
  nousresearch/hermes-agent:latest \
  -c "cd /workspace/backend && exec /opt/hermes/.venv/bin/python -m uvicorn --app-dir /workspace backend.app.main:app --host 0.0.0.0 --port 8501"
```

Then open <http://localhost:8501>.

> A drop-in `memory-viewer-up.sh` wrapper that handles stale-dist rebuild + chmod gotchas
> lives in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

### Development

```bash
# Backend (Python 3.11+)
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8501

# Frontend (Node 20+)
cd frontend
npm install
npm run dev
```

```powershell
# Backend (Python 3.11+)
cd backend
python -m venv .venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8501

# Frontend (Node 20+)
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173> (Vite dev server proxies API to `:8501`).

## 🛠️ Configuration

All paths are configurable via `memory-viewer.yaml` (env vars override):

```yaml
port: 8501
hermes_memories_dir: ~/.hermes/memories    # global MEMORY.md / USER.md
hermes_profiles_dir: ~/.hermes/profiles    # per-profile memory dirs
agentmemory_cache: ~/.agentmemory/standalone.json
cache_refresh_interval: 30                 # minutes
```

Or via env vars (prefix `MV_`):

| Env var | YAML key | Default |
|---|---|---|
| `MV_PORT` | `port` | `8501` |
| `MV_HERMES_MEMORIES_DIR` | `hermes_memories_dir` | `<repo>/data/memories` |
| `MV_HERMES_PROFILES_DIR` | `hermes_profiles_dir` | `<repo>/data/profiles` |
| `MV_AGENTMEMORY_CACHE` | `agentmemory_cache` | `<repo>/data/cache/agentmemory.json` |
| `MV_CACHE_REFRESH_INTERVAL` | `cache_refresh_interval` | `30` |

## 📁 Project Structure

```
memory-viewer/
├── backend/
│   ├── app/
│   │   ├── routers/    # 11 FastAPI routers
│   │   ├── services/   # agentmemory / hermes / compare / collections
│   │   ├── models/     # Pydantic schemas
│   │   └── main.py
│   ├── fetch_agentmemory.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/      # 10 pages
│   │   ├── components/ # shared UI
│   │   ├── stores/     # Pinia
│   │   ├── locales/    # zh-CN / en-US
│   │   └── styles/     # design tokens (CSS variables)
│   ├── package.json
│   └── vite.config.ts
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── memory-viewer.yaml
└── README.md
```

## 📖 API

See [`docs/API.md`](docs/API.md) for the full reference. Quick taste:

- `GET /api/health` — service status + memory counts
- `GET /api/profiles` — known Hermes profile names
- `GET /api/agentmemory?limit=50&offset=0` — list memories (filter, sort, search)
- `GET /api/agentmemory/{id}` — single memory with version history
- `GET /api/hermes?profile=chief-agent` — Hermes memory for a profile
- `POST /api/agentmemory` / `PUT /api/agentmemory/{id}` / `DELETE /api/agentmemory/{id}`
- `GET /api/compare?profile_a=...&profile_b=...` — side-by-side profile diff

## 🧪 Testing

```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && npm run type-check
```

## 🤝 Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Issues and PRs welcome.

## 📄 License

[MIT](LICENSE) — see `LICENSE` for the full text.

## 🙏 Credits

- Built for [Hermes Agent](https://github.com/nousresearch/hermes-agent)
- Uses [`agentmemory`](https://github.com/rohitg00/agentmemory) as one of the data sources
- Frontend powered by [Vue 3](https://vuejs.org/) + [Vite](https://vitejs.dev/) + [Pinia](https://pinia.vuejs.org/)
- Backend powered by [FastAPI](https://fastapi.tiangolo.com/) + [APScheduler](https://apscheduler.readthedocs.io/)
