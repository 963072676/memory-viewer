"""Tests for hermes memory API endpoints."""


def test_read_file_safe_falls_back_to_legacy_windows_encoding(tmp_path):
    """Hermes files written with a Windows locale should not break parsing."""
    from app.services.hermes_memory import _parse_section_entries, _read_file_safe

    memory_file = tmp_path / "MEMORY.md"
    memory_file.write_bytes(b"Global memory entry one\n\xa1\xec\nGlobal memory entry two")

    content = _read_file_safe(str(memory_file))

    assert _parse_section_entries(content) == [
        "Global memory entry one",
        "Global memory entry two",
    ]


def test_get_hermes_memory(client):
    """Test GET /api/hermes-memory returns global + profile data."""
    resp = client.get("/api/hermes-memory")
    assert resp.status_code == 200
    data = resp.json()
    assert "global" in data
    assert "profiles" in data
    assert len(data["global"]["memory"]) == 2
    assert len(data["global"]["user"]) == 1


def test_get_hermes_memory_profiles(client):
    """Test hermes memory includes profile data."""
    resp = client.get("/api/hermes-memory")
    data = resp.json()
    assert "chief-agent" in data["profiles"]
    assert "daily" in data["profiles"]
    assert len(data["profiles"]["chief-agent"]["memory"]) == 1
