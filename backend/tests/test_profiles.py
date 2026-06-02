"""Tests for profiles API endpoint."""


def test_get_profiles(client):
    """Test GET /api/profiles returns profile list."""
    resp = client.get("/api/profiles")
    assert resp.status_code == 200
    profiles = resp.json()
    assert isinstance(profiles, list)
    assert "chief-agent" in profiles
    assert "daily" in profiles
    assert len(profiles) == 2
