"""Tests for provider-neutral session inventory."""


def test_sessions_api_lists_provider_sessions(client):
    create_response = client.post(
        "/api/memories",
        json={
            "provider": "agentmemory",
            "title": "Session API Memory",
            "content": "Created to expose a session",
            "type": "fact",
            "sessionId": "session-api",
        },
    )
    assert create_response.status_code == 200

    response = client.get("/api/sessions?provider=agentmemory")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["activeProvider"], str)
    assert "agentmemory" in data["providers"]
    assert any(
        session["id"] == "session-api" and session["provider"] == "agentmemory"
        for session in data["sessions"]
    )


def test_sessions_api_rejects_unknown_provider(client):
    response = client.get("/api/sessions?provider=missing-provider")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "provider_config_error"
