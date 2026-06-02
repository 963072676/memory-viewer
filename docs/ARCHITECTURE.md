# Architecture

## Overview

Memory Viewer is a full-stack web application for managing agent memories.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │────▶│   FastAPI   │────▶│    Files    │
│  (Vue 3)    │◀────│  (Backend)  │◀────│             │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Frontend

- **Framework**: Vue 3 with Composition API
- **Build**: Vite 5
- **State**: Pinia
- **Routing**: Vue Router 4
- **Styling**: CSS Variables (dark theme ready)

### Directory Structure

```
frontend/src/
├── views/          # Page components
├── components/     # Reusable UI components
├── stores/         # Pinia state stores
├── router/         # Vue Router config
└── api/            # API client functions
```

## Backend

- **Framework**: FastAPI
- **Database**: JSON files (AgentMemory standalone format)
- **Cache**: In-memory with periodic refresh
- **Scheduler**: APScheduler for background tasks

### Directory Structure

```
backend/app/
├── routers/        # API endpoint modules
├── services/       # Business logic
├── models/         # Data models
├── config.py       # Configuration
└── main.py         # Application entry
```

## Data Sources

Memory Viewer aggregates from multiple sources:

1. **AgentMemory** — Primary memory store (JSON file)
2. **Hermes Memory** — Per-profile MEMORY.md files
3. **Hermes Profiles** — Profile configurations

## API Design

RESTful API with JSON responses. All endpoints prefixed with `/api`.

## Security

- CORS middleware for cross-origin requests
- Input validation via Pydantic models
- No sensitive data in responses

## Performance

- In-memory caching with configurable TTL
- Lazy loading for large datasets
- Virtual scrolling for long lists