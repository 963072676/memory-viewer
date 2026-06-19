"""Tests for provider management API."""


def test_get_providers_returns_strategy_inventory_and_health(client):
    response = client.get("/api/providers")

    assert response.status_code == 200
    data = response.json()
    provider_names = {provider["name"] for provider in data["providers"]}

    assert {"hermes", "agentmemory"}.issubset(provider_names)
    assert data["strategy"]["activeProvider"] in provider_names
    assert "fallbackProviders" in data["strategy"]
    assert "hermes" in data["health"]
    assert "agentmemory" in data["health"]
    for provider in data["providers"]:
        assert "queryModes" in provider
        assert "keyword" in provider["queryModes"]


def test_switch_provider_updates_runtime_active_provider(client):
    setup = client.patch(
        "/api/providers/strategy",
        json={"activeProvider": "hermes", "fallbackProviders": ["agentmemory"]},
    )
    assert setup.status_code == 200

    response = client.post("/api/providers/switch", json={"activeProvider": "agentmemory"})

    assert response.status_code == 200
    strategy = response.json()["strategy"]
    assert strategy["activeProvider"] == "agentmemory"
    assert "agentmemory" not in strategy["fallbackProviders"]

    restore = client.patch(
        "/api/providers/strategy",
        json={"activeProvider": "hermes", "fallbackProviders": ["agentmemory"]},
    )
    assert restore.status_code == 200


def test_patch_provider_strategy_updates_fallback_parallel_and_debug(client):
    response = client.patch(
        "/api/providers/strategy",
        json={
            "activeProvider": "hermes",
            "fallbackProviders": ["agentmemory"],
            "parallelQuery": True,
            "timeoutSeconds": 2.5,
            "retryAttempts": 2,
            "retryBackoffSeconds": 0.05,
            "debugRawResponse": True,
        },
    )

    assert response.status_code == 200
    strategy = response.json()["strategy"]
    assert strategy["activeProvider"] == "hermes"
    assert strategy["fallbackProviders"] == ["agentmemory"]
    assert strategy["parallelQuery"] is True
    assert strategy["timeoutSeconds"] == 2.5
    assert strategy["retryAttempts"] == 2
    assert strategy["retryBackoffSeconds"] == 0.05
    assert strategy["debugRawResponse"] is True

    restore = client.patch(
        "/api/providers/strategy",
        json={
            "parallelQuery": False,
            "timeoutSeconds": 10,
            "retryAttempts": 1,
            "retryBackoffSeconds": 0.1,
            "debugRawResponse": False,
        },
    )
    assert restore.status_code == 200


def test_provider_strategy_rejects_unknown_provider(client):
    response = client.patch(
        "/api/providers/strategy",
        json={"activeProvider": "not-a-provider"},
    )

    assert response.status_code == 404
    detail = response.json()["detail"]
    assert detail["code"] == "provider_config_error"
    assert detail["provider"] == "not-a-provider"


def test_provider_health_endpoint(client):
    response = client.get("/api/providers/health")

    assert response.status_code == 200
    health = response.json()["health"]
    assert health["hermes"]["healthy"] is True
    assert health["agentmemory"]["healthy"] is True


def test_provider_observability_endpoint_exposes_latency_routing_and_errors(client):
    health_response = client.get("/api/providers/health")
    assert health_response.status_code == 200

    response = client.get("/api/providers/observability?limit=10")

    assert response.status_code == 200
    observability = response.json()["observability"]
    assert "strategy" in observability
    assert "providers" in observability
    assert "routing" in observability
    assert "recentCalls" in observability
    assert {"hermes", "agentmemory"}.issubset(observability["providers"].keys())
    assert observability["providers"]["hermes"]["operations"]["health_check"]["calls"] >= 1
    assert observability["providers"]["agentmemory"]["operations"]["health_check"]["calls"] >= 1
    assert observability["recentCalls"][-1]["operation"] == "health_check"
    assert "fallbackUsed" in observability["routing"]
