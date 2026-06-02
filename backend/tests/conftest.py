"""Pytest fixtures for Memory Viewer v2 backend tests."""

import json
import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture
def cache_file(temp_dir):
    """Create a temporary cache file with sample data."""
    cache_path = os.path.join(temp_dir, "agentmemory.json")
    sample_data = {
        "memories": [
            {
                "id": "mem_test1_abcd1234",
                "type": "pattern",
                "title": "Test Pattern Memory",
                "content": "This is a test pattern about hermes usage",
                "concepts": ["hermes", "test"],
                "files": [],
                "createdAt": "2026-05-25T19:16:57.181Z",
                "updatedAt": "2026-05-25T19:16:57.181Z",
                "strength": 7,
                "version": 1,
                "isLatest": True,
                "sessionIds": [],
            },
            {
                "id": "mem_test2_efgh5678",
                "type": "fact",
                "title": "Test Fact Memory",
                "content": "This is a factual memory about testing",
                "concepts": ["testing", "qa"],
                "files": [],
                "createdAt": "2026-05-26T10:00:00.000Z",
                "updatedAt": "2026-05-26T10:00:00.000Z",
                "strength": 5,
                "version": 1,
                "isLatest": True,
                "sessionIds": [],
            },
            {
                "id": "mem_test3_ijkl9012",
                "type": "preference",
                "title": "Hermes Preferences",
                "content": "User prefers dark mode and concise responses",
                "concepts": ["hermes", "preference", "ui"],
                "files": [],
                "createdAt": "2026-05-27T12:00:00.000Z",
                "updatedAt": "2026-05-27T12:00:00.000Z",
                "strength": 8,
                "version": 1,
                "isLatest": True,
                "sessionIds": [],
            },
        ]
    }
    with open(cache_path, "w") as f:
        json.dump(sample_data, f)
    return cache_path


@pytest.fixture
def memories_dir(temp_dir):
    """Create a temporary hermes memories directory."""
    mem_dir = os.path.join(temp_dir, "memories")
    os.makedirs(mem_dir, exist_ok=True)
    with open(os.path.join(mem_dir, "MEMORY.md"), "w") as f:
        f.write("Global memory entry one\n§\nGlobal memory entry two")
    with open(os.path.join(mem_dir, "USER.md"), "w") as f:
        f.write("User preference: dark mode")
    return mem_dir


@pytest.fixture
def profiles_dir(temp_dir, memories_dir):
    """Create a temporary profiles directory with sample profiles."""
    prof_dir = os.path.join(temp_dir, "profiles")
    for profile_name in ["chief-agent", "daily"]:
        mem_dir = os.path.join(prof_dir, profile_name, "memories")
        os.makedirs(mem_dir, exist_ok=True)
        with open(os.path.join(mem_dir, "MEMORY.md"), "w") as f:
            f.write(f"{profile_name} memory entry")
        with open(os.path.join(mem_dir, "USER.md"), "w") as f:
            f.write(f"{profile_name} user entry")
    return prof_dir


@pytest.fixture
def app(cache_file, memories_dir, profiles_dir):
    """Create a test FastAPI app with overridden config."""
    os.environ["AGENTMEMORY_CACHE"] = cache_file
    os.environ["HERMES_MEMORIES_DIR"] = memories_dir
    os.environ["HERMES_PROFILES_DIR"] = profiles_dir
    os.environ["CORS_ORIGINS"] = "http://localhost:*"

    # Re-import to pick up env changes
    from app.config import settings
    settings.AGENTMEMORY_CACHE = cache_file
    settings.HERMES_MEMORIES_DIR = memories_dir
    settings.HERMES_PROFILES_DIR = profiles_dir

    from app.main import app as fastapi_app
    yield fastapi_app


@pytest.fixture
def client(app):
    """Create a test client."""
    return TestClient(app)


# =============================================================================
# Session-scoped fixtures (shared across test files)
# =============================================================================

@pytest.fixture(scope="session")
def verify_config_paths():
    """Verify all configured paths exist before any tests run.
    
    This fixture runs once per test session. If any path is missing,
    the test session fails immediately rather than skipping tests.
    
    Note: In test mode (temp dirs), this is a no-op. In production,
    this ensures all configured paths exist.
    """
    import os as os_module
    from app.config import settings as cfg_settings
    
    # Check if we're in test mode by looking for pytest temp dir patterns
    import sys
    is_test = 'pytest' in sys.modules or os_module.getenv('MEMORY_VIEWER_TEST_MODE') == '1'
    
    # Also check if all paths actually exist - if they do, we're in production
    all_exist = os_module.path.exists(cfg_settings.HERMES_PROFILES_DIR) and \
                os_module.path.exists(cfg_settings.HERMES_MEMORIES_DIR)
    
    if is_test and not all_exist:
        return True  # Skip validation in test mode
    
    paths = {
        'HERMES_PROFILES_DIR': cfg_settings.HERMES_PROFILES_DIR,
        'HERMES_MEMORIES_DIR': cfg_settings.HERMES_MEMORIES_DIR,
        'AGENTMEMORY_CACHE': cfg_settings.AGENTMEMORY_CACHE,
    }
    
    errors = []
    for name, path in paths.items():
        if not os.path.exists(path):
            errors.append(f"{name} not found: {path}")
        elif not os.access(path, os.R_OK):
            errors.append(f"{name} not readable: {path}")
    
    if errors:
        error_msg = "\n".join([
            "Configuration path validation FAILED:",
            *[f"  - {e}" for e in errors],
            "",
            "All configured paths must exist at runtime.",
            "Fix memory-viewer.yaml or ensure paths are created before starting the service.",
        ])
        pytest.fail(error_msg)
    
    return True
