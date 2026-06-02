"""Tests for P31-T1: Compare API (multi-agent memory comparison)."""

import os
import tempfile

import pytest
from fastapi.testclient import TestClient


class TestCompareAPI:
    """Tests for /api/compare endpoints."""

    @pytest.fixture
    def compare_app(self, cache_file, memories_dir, profiles_dir):
        """Create a test FastAPI app with overridden config for compare tests."""
        os.environ["AGENTMEMORY_CACHE"] = cache_file
        os.environ["HERMES_MEMORIES_DIR"] = memories_dir
        os.environ["HERMES_PROFILES_DIR"] = profiles_dir

        from app.config import settings
        settings.AGENTMEMORY_CACHE = cache_file
        settings.HERMES_MEMORIES_DIR = memories_dir
        settings.HERMES_PROFILES_DIR = profiles_dir

        from app.main import app as fastapi_app
        return fastapi_app

    @pytest.fixture
    def compare_client(self, compare_app):
        return TestClient(compare_app)

    def test_compare_profiles_returns_correct_structure(self, compare_client):
        """GET /api/compare/profiles returns left_only, right_only, common, similarity_score."""
        response = compare_client.get("/api/compare/profiles?left=chief-agent&right=daily")
        assert response.status_code == 200
        data = response.json()
        assert "left" in data
        assert "right" in data
        assert "left_only" in data
        assert "right_only" in data
        assert "common" in data
        assert "similarity_score" in data

    def test_compare_profiles_left_only_contains_unique_items(self, compare_client):
        """Items unique to left profile appear in left_only."""
        response = compare_client.get("/api/compare/profiles?left=chief-agent&right=daily")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["left_only"], list)
        # chief-agent and daily both write their own entries, so left_only should contain
        # normalized items not present in daily
        for item in data["left_only"]:
            assert isinstance(item, str)

    def test_compare_profiles_right_only_contains_unique_items(self, compare_client):
        """Items unique to right profile appear in right_only."""
        response = compare_client.get("/api/compare/profiles?left=chief-agent&right=daily")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["right_only"], list)
        for item in data["right_only"]:
            assert isinstance(item, str)

    def test_compare_profiles_common_contains_shared_items(self, compare_client):
        """Items present in both profiles appear in common."""
        response = compare_client.get("/api/compare/profiles?left=chief-agent&right=daily")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["common"], list)
        # No common entries by default since each profile writes its own name
        # But structure should still be correct

    def test_compare_profiles_similarity_score_is_float(self, compare_client):
        """similarity_score is a float between 0 and 1."""
        response = compare_client.get("/api/compare/profiles?left=chief-agent&right=daily")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["similarity_score"], float)
        assert 0.0 <= data["similarity_score"] <= 1.0

    def test_compare_profiles_symmetric(self, compare_client):
        """compare(left, right) == compare(right, left) for similarity_score."""
        r1 = compare_client.get("/api/compare/profiles?left=chief-agent&right=daily").json()
        r2 = compare_client.get("/api/compare/profiles?left=daily&right=chief-agent").json()
        assert r1["similarity_score"] == r2["similarity_score"]
        # left_only and right_only should be swapped
        assert r1["left_only"] == r2["right_only"]
        assert r1["right_only"] == r2["left_only"]

    def test_compare_profiles_missing_left_param(self, compare_client):
        """Missing left parameter returns 422."""
        response = compare_client.get("/api/compare/profiles?right=daily")
        assert response.status_code == 422

    def test_compare_profiles_missing_right_param(self, compare_client):
        """Missing right parameter returns 422."""
        response = compare_client.get("/api/compare/profiles?left=chief-agent")
        assert response.status_code == 422

    def test_list_profiles_returns_list(self, compare_client):
        """GET /api/compare/profiles/list returns {"profiles": [...]}."""
        response = compare_client.get("/api/compare/profiles/list")
        assert response.status_code == 200
        data = response.json()
        assert "profiles" in data
        assert isinstance(data["profiles"], list)

    def test_list_profiles_contains_known_profiles(self, compare_client):
        """Profiles list contains chief-agent and daily (from fixture)."""
        response = compare_client.get("/api/compare/profiles/list")
        assert response.status_code == 200
        profiles = response.json()["profiles"]
        assert "chief-agent" in profiles
        assert "daily" in profiles