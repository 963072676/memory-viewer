"""
Memory Viewer v2 — Backend API (FastAPI)

Simplified for open source release v1.0
保留了核心功能，移除了高级/AI/运维功能
"""

import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.routers import agentmemory, hermes_memory, profiles, search, health, changelog
from app.routers import sources as sources_router
from app.routers import favorites, collections, dashboard, compare

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan: start/stop scheduler."""
    from app import scheduler as sched
    await sched.on_startup(interval_minutes=settings.CACHE_REFRESH_INTERVAL)
    yield
    await sched.on_shutdown()


app = FastAPI(
    title="Memory Viewer API",
    description="Agent Memory Management Dashboard - View and manage your agent memories",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track startup time for health check
app.state.start_time = time.time()

# Register API routers
app.include_router(agentmemory.router, prefix="/api/agentmemory", tags=["agentmemory"])
app.include_router(hermes_memory.router, prefix="/api/hermes-memory", tags=["hermes-memory"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["profiles"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(changelog.router, prefix="/api/changelog", tags=["changelog"])
app.include_router(sources_router.router, prefix="/api", tags=["sources"])
app.include_router(favorites.router, prefix="/api", tags=["favorites"])
app.include_router(collections.router, prefix="/api/collections", tags=["collections"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(compare.router, prefix="/api/compare", tags=["compare"])


@app.get("/api/tags")
def redirect_tags():
    """Redirect /api/tags to /api/agentmemory/tags for frontend compatibility."""
    from app.services.agentmemory import get_all_tags
    return {"tags": get_all_tags()}


@app.get("/api/stats")
def get_unified_stats():
    """Unified statistics endpoint."""
    from app.services.agentmemory import get_stats as get_am_stats
    from app.services.hermes_memory import get_hermes_memory, get_profiles as get_hermes_profiles

    am_stats = get_am_stats()
    hermes_data = get_hermes_memory()
    hermes_profiles = get_hermes_profiles()

    hermes_total = (
        len(hermes_data.get("global", {}).get("memory", []))
        + len(hermes_data.get("global", {}).get("user", []))
    )
    for profile_vals in hermes_data.get("profiles", {}).values():
        hermes_total += len(profile_vals.get("memory", [])) + len(profile_vals.get("user", []))

    profiles_list = hermes_profiles if isinstance(hermes_profiles, list) else []

    return {
        "agentmemory": am_stats,
        "hermes": {
            "total": hermes_total,
            "profiles_count": len(profiles_list),
        },
        "profiles": {
            "count": len(profiles_list),
            "list": profiles_list,
        },
    }


@app.get("/api/config")
def get_config():
    """Get application configuration."""
    return {
        "version": "1.0.0",
        "features": {
            "search": True,
            "crud": True,
            "export": True,
            "import": True,
            "favorites": True,
            "collections": True,
            "hermes_memory": True,
            "profiles": True,
            "compare": True,
            "sources": True,
            "dashboard": True,
        },
    }


# Serve frontend static files
_frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if _frontend_dist.exists():
    _assets = _frontend_dist / "assets"
    if _assets.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets)), name="static-assets")

    @app.get("/")
    def serve_index():
        return FileResponse(str(_frontend_dist / "index.html"))

    @app.get("/favicon.svg")
    def serve_favicon():
        fav = _frontend_dist / "favicon.svg"
        if fav.exists():
            return FileResponse(str(fav))
        return JSONResponse({"detail": "Not Found"}, status_code=404)

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        if full_path.startswith("api/") or full_path.startswith("assets/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        return FileResponse(str(_frontend_dist / "index.html"))
else:
    @app.get("/")
    def root():
        return {"message": "Memory Viewer API v1.0", "docs": "/api/docs"}
