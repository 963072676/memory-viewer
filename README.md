# Memory Viewer

> Agent Memory Management Dashboard - View and manage your agent memories in a beautiful, intuitive interface.

![Memory Viewer](docs/screenshot.png)

## ✨ Features

- 📋 **Memory Browsing** — View, search, and filter all agent memories
- 🔍 **Full-Text Search** — Fast keyword search across all memory sources
- 📊 **Dashboard** — Visual statistics and insights
- 📚 **Collections** — Smart categorization and grouping
- 🔄 **CRUD Operations** — Create, edit, and delete memories
- 📦 **Import/Export** — Backup and restore memories
- 🌐 **Multi-Profile** — Manage memories across multiple agent profiles
- 🤖 **Hermes Memory** — View Hermes MEMORY.md files

## 🚀 Quick Start

### Docker (Recommended)

```bash
docker run -d \
  --name memory-viewer \
  -p 8501:8501 \
  -v /path/to/hermes:/data \
  ghcr.io/nousresearch/memory-viewer:latest
```

Then open [http://localhost:8501](http://localhost:8501)

### Development

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8501

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## 📁 Project Structure

```
memory-viewer/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── routers/   # API endpoints
│   │   ├── services/  # Business logic
│   │   └── main.py    # Application entry
│   └── requirements.txt
├── frontend/          # Vue 3 frontend
│   ├── src/
│   │   ├── views/     # Page components
│   │   ├── components/# UI components
│   │   └── stores/    # Pinia stores
│   └── package.json
├── docs/              # Documentation
└── README.md
```

## 🛠️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HERMES_HOME` | `~/.hermes` | Hermes configuration directory |
| `MEMORY_DB_PATH` | auto | AgentMemory database path |
| `CACHE_REFRESH_INTERVAL` | `30` | Cache refresh interval (minutes) |

### CORS

Configure allowed origins in `backend/app/config.py`

## 📖 API

See [docs/API.md](docs/API.md) for full API documentation.

## 🧪 Testing

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - see [LICENSE](LICENSE)
