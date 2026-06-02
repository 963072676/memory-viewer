"""Tests for search API endpoint."""


def test_search_basic(client):
    """Test basic search across all sources."""
    resp = client.get("/api/search?q=hermes")
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "hermes"
    assert data["total"] > 0
    assert "results" in data


def test_search_agentmemory_source(client):
    """Test search filtered to agentmemory source."""
    resp = client.get("/api/search?q=hermes&source=agentmemory")
    assert resp.status_code == 200
    data = resp.json()
    assert all(r["source"] == "agentmemory" for r in data["results"])


def test_search_hermes_source(client):
    """Test search filtered to hermes source."""
    resp = client.get("/api/search?q=Global&source=hermes")
    assert resp.status_code == 200
    data = resp.json()
    assert all(r["source"] == "hermes" for r in data["results"])


def test_search_with_type_filter(client):
    """Test search with type filter."""
    resp = client.get("/api/search?q=hermes&type=pattern&source=agentmemory")
    assert resp.status_code == 200
    data = resp.json()
    assert all(r.get("type") == "pattern" for r in data["results"])


def test_search_pagination(client):
    """Test search pagination."""
    resp = client.get("/api/search?q=hermes&limit=1&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["limit"] == 1
    assert data["offset"] == 0
    assert len(data["results"]) <= 1


def test_search_no_results(client):
    """Test search with no matching results."""
    resp = client.get("/api/search?q=nonexistent_query_xyz")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert len(data["results"]) == 0


def test_search_highlight(client):
    """Test that search results contain highlight markup."""
    resp = client.get("/api/search?q=hermes")
    data = resp.json()
    if data["results"]:
        snippet = data["results"][0]["matchSnippet"]
        assert "<em>" in snippet
        assert "</em>" in snippet
