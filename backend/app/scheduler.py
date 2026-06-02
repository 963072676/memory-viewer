"""Scheduler for periodic cache refresh (F-11)."""

import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger("memory-viewer.scheduler")

# Global state for scheduler status
scheduler_state = {
    "running": False,
    "last_refresh_at": None,
    "next_refresh_at": None,
    "last_refresh_success": None,
    "last_refresh_error": None,
}


def _run_fetch():
    """Execute fetch_agentmemory.py to refresh the cache."""
    logger.info("Starting cache refresh...")
    fetch_script = Path(__file__).resolve().parent.parent / "fetch_agentmemory.py"
    try:
        result = subprocess.run(
            [sys.executable, str(fetch_script)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0:
            scheduler_state["last_refresh_at"] = datetime.now(timezone.utc).isoformat()
            scheduler_state["last_refresh_success"] = True
            scheduler_state["last_refresh_error"] = None
            logger.info("Cache refresh completed successfully.")
        else:
            scheduler_state["last_refresh_at"] = datetime.now(timezone.utc).isoformat()
            scheduler_state["last_refresh_success"] = False
            scheduler_state["last_refresh_error"] = result.stderr[:500]
            logger.error(f"Cache refresh failed: {result.stderr[:500]}")
    except subprocess.TimeoutExpired:
        scheduler_state["last_refresh_at"] = datetime.now(timezone.utc).isoformat()
        scheduler_state["last_refresh_success"] = False
        scheduler_state["last_refresh_error"] = "Timeout after 120s"
        logger.error("Cache refresh timed out after 120s.")
    except Exception as e:
        scheduler_state["last_refresh_at"] = datetime.now(timezone.utc).isoformat()
        scheduler_state["last_refresh_success"] = False
        scheduler_state["last_refresh_error"] = str(e)[:500]
        logger.error(f"Cache refresh error: {e}")


async def on_startup(interval_minutes: int = 30):
    """Start the scheduler on FastAPI startup."""
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        _run_fetch,
        trigger=IntervalTrigger(minutes=interval_minutes),
        id="cache_refresh",
        name="Cache Auto-Refresh",
        replace_existing=True,
    )
    scheduler.start()
    scheduler_state["running"] = True

    # Calculate next run time
    job = scheduler.get_job("cache_refresh")
    if job and job.next_run_time:
        scheduler_state["next_refresh_at"] = job.next_run_time.isoformat()

    logger.info(f"Scheduler started, refresh interval: {interval_minutes}min")

    # Store scheduler reference for health endpoint
    from app.config import settings
    settings._scheduler = scheduler


async def on_shutdown():
    """Shutdown the scheduler on FastAPI shutdown."""
    from app.config import settings
    scheduler = getattr(settings, "_scheduler", None)
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler_state["running"] = False
        logger.info("Scheduler stopped.")


def get_scheduler_status() -> dict:
    """Get current scheduler status."""
    # Update next_refresh_at from actual scheduler
    from app.config import settings
    scheduler = getattr(settings, "_scheduler", None)
    if scheduler:
        job = scheduler.get_job("cache_refresh")
        if job and job.next_run_time:
            scheduler_state["next_refresh_at"] = job.next_run_time.isoformat()
    return dict(scheduler_state)
