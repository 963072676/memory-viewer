#!/usr/bin/env python3
"""
Memory Viewer v2 — Comprehensive API & Frontend Test Suite
Tests all backend API endpoints and frontend routes.
"""

import requests
import json
import time
import sys

BASE = "http://localhost:8501"
results = []
created_id = None

def test(name, method, path, timeout=8, **kwargs):
    """Run a single test and record result."""
    url = f"{BASE}{path}"
    start = time.time()
    try:
        resp = requests.request(method, url, timeout=timeout, **kwargs)
        elapsed = round((time.time() - start) * 1000)
        ok = resp.status_code < 400
        body_preview = ""
        try:
            data = resp.json()
            body_preview = json.dumps(data, ensure_ascii=False)[:200]
        except:
            body_preview = resp.text[:200]
        results.append({
            "name": name, "method": method, "path": path,
            "status": resp.status_code, "time_ms": elapsed, "ok": ok, "body": body_preview,
        })
        return resp
    except requests.exceptions.Timeout:
        elapsed = round((time.time() - start) * 1000)
        results.append({
            "name": name, "method": method, "path": path,
            "status": "TIMEOUT", "time_ms": elapsed, "ok": False, "body": "Request timed out",
        })
        return None
    except Exception as e:
        elapsed = round((time.time() - start) * 1000)
        results.append({
            "name": name, "method": method, "path": path,
            "status": "ERR", "time_ms": elapsed, "ok": False, "body": str(e)[:200],
        })
        return None

# ============================================================
# 1. CORE ENDPOINTS
# ============================================================
print("=" * 60)
print("1. CORE ENDPOINTS")

test("Health Check", "GET", "/api/health")
test("Config", "GET", "/api/config")
test("API Docs", "GET", "/api/docs")
test("OpenAPI JSON", "GET", "/api/openapi.json")
test("ReDoc", "GET", "/api/redoc")

# ============================================================
# 2. AGENTMEMORY CRUD
# ============================================================
print("2. AGENTMEMORY CRUD")

test("List All Memories", "GET", "/api/agentmemory")
test("Paginated (default)", "GET", "/api/agentmemory/paginated")
test("Paginated (custom)", "GET", "/api/agentmemory/paginated?limit=5&offset=0&sort=createdAt&order=asc")
test("Paginated (by type)", "GET", "/api/agentmemory/paginated?type=pattern")
test("Paginated (with archived)", "GET", "/api/agentmemory/paginated?include_archived=true")
test("Paginated (by tag)", "GET", "/api/agentmemory/paginated?tag=test")

# Get first memory ID
resp = test("Get Memories for ID", "GET", "/api/agentmemory")
first_id = None
if resp and resp.status_code == 200:
    data = resp.json()
    memories = data.get("memories", [])
    if memories:
        first_id = memories[0].get("id")
        print(f"  -> Found memory ID: {first_id}")

# Get single
if first_id:
    test("Get Single Memory", "GET", f"/api/agentmemory/{first_id}")

# Create
create_resp = test("Create Memory", "POST", "/api/agentmemory",
    json={"title": "Test Memory - Comprehensive Test", "content": "This is a test memory.", "type": "fact", "concepts": ["test"], "strength": 5, "tags": ["test-tag", "automated"]})

if create_resp and create_resp.status_code == 200:
    created_id = create_resp.json().get("memory", {}).get("id")
    print(f"  -> Created memory ID: {created_id}")

# Update
if created_id:
    test("Update Memory", "PUT", f"/api/agentmemory/{created_id}",
        json={"content": "Updated content.", "concepts": ["test", "updated"], "strength": 7, "tags": ["updated"]})

# Archive / Unarchive
if created_id:
    test("Archive Memory", "PATCH", f"/api/agentmemory/{created_id}/archive")
    test("Unarchive Memory", "PATCH", f"/api/agentmemory/{created_id}/unarchive")

# Tags
if created_id:
    test("Set Tags", "PUT", f"/api/agentmemory/{created_id}/tags", json={"tags": ["new-tag-1", "new-tag-2"]})

test("Get All Tags", "GET", "/api/agentmemory/tags")
test("Get Templates", "GET", "/api/agentmemory/templates")
test("Get Collections", "GET", "/api/agentmemory/collections")
test("Memory Stats", "GET", "/api/agentmemory/stats")
test("Export JSON", "GET", "/api/agentmemory/export?format=json")
test("Export Markdown", "GET", "/api/agentmemory/export?format=markdown")

# ============================================================
# 3. SEARCH
# ============================================================
print("3. SEARCH")

test("Search (basic)", "GET", "/api/search?q=test")
test("Search (empty)", "GET", "/api/search?q=")
test("Search (source filter)", "GET", "/api/search?q=memory&source=agentmemory")
test("Search (type filter)", "GET", "/api/search?q=&type=pattern")
test("Search (strength filter)", "GET", "/api/search?q=&strength_min=3&strength_max=8")
test("Search (date filter)", "GET", "/api/search?q=&date_from=2025-01-01&date_to=2026-12-31")
test("Quick Search", "GET", "/api/search/quick?q=test")

# ============================================================
# 4. HERMES MEMORY & PROFILES
# ============================================================
print("4. HERMES MEMORY & PROFILES")

test("Hermes Memory", "GET", "/api/hermes-memory")
test("Profiles", "GET", "/api/profiles")

# ============================================================
# 5. INTELLIGENCE FEATURES (P3)
# ============================================================
print("5. INTELLIGENCE FEATURES (P3)")

create_resp2 = test("Create Memory for Intel", "POST", "/api/agentmemory",
    json={"title": "Intel Test Memory", "content": "Testing intelligence features.", "type": "pattern", "strength": 6, "tags": ["intel-test"]})
intel_id = None
if create_resp2 and create_resp2.status_code == 200:
    intel_id = create_resp2.json().get("memory", {}).get("id")
    print(f"  -> Intel test ID: {intel_id}")

if intel_id:
    test("Memory Health", "GET", f"/api/agentmemory/{intel_id}/health")
    test("Memory Recommendations", "GET", f"/api/agentmemory/{intel_id}/recommendations")

test("Duplicates Detection", "GET", "/api/agentmemory/duplicates")
test("Graph Data", "GET", "/api/agentmemory/graph")

# ============================================================
# 6. CHANGELOG & WEBHOOK
# ============================================================
print("6. CHANGELOG & WEBHOOK")

test("Changelog", "GET", "/api/changelog")
test("Webhook List", "GET", "/api/webhook")

# ============================================================
# 7. P5 OPERATIONS
# ============================================================
print("7. P5 OPERATIONS")

test("Diagnostics", "GET", "/api/diagnostics")
test("Audit Log", "GET", "/api/audit")
test("Backup List", "GET", "/api/backup")
test("Metrics", "GET", "/api/metrics")
test("Instances", "GET", "/api/instances")

# ============================================================
# 8. P4 COLLABORATION
# ============================================================
print("8. P4 COLLABORATION")

if intel_id:
    test("Version History", "GET", f"/api/agentmemory/{intel_id}/versions")
test("Subscriptions", "GET", "/api/webhook/subscriptions")
test("MCP Health", "GET", "/mcp/health", timeout=5)

# ============================================================
# 9. P8 NEW FEATURES
# ============================================================
print("9. P8 NEW FEATURES")

test("Semantic Search", "GET", "/api/search/semantic?q=test")
if intel_id:
    test("Auto Tag", "POST", f"/api/memories/{intel_id}/auto-tag")
test("Heatmap", "GET", "/api/metrics/heatmap")
test("Plugins", "GET", "/api/plugins")

# ============================================================
# 10. P9 NEW FEATURES
# ============================================================
print("10. P9 NEW FEATURES")

test("PII Scan", "POST", "/api/redaction/scan", json={"text": "My email is test@example.com"})
test("Sharing List", "GET", "/api/sharing")
test("Clusters", "GET", "/api/clusters")
test("NLQ Query", "GET", "/api/nlq?q=show me all bugs")
test("Anomalies", "GET", "/api/anomalies")
test("Dashboard", "GET", "/api/dashboard")

# ============================================================
# 11. P10 NEW FEATURES
# ============================================================
print("11. P10 NEW FEATURES")

test("Lineage", "GET", "/api/lineage")
test("Analytics", "GET", "/api/analytics")
test("Conflicts", "GET", "/api/conflicts")
test("Workflows", "GET", "/api/workflows")
test("Annotations List", "GET", "/api/annotations")

# ============================================================
# 12. P11 NEW FEATURES
# ============================================================
print("12. P11 NEW FEATURES")

test("Digest", "GET", "/api/digest")
test("Templates (global)", "GET", "/api/templates")
test("RAG Search", "GET", "/api/search/rag?q=test")
test("Workspaces", "GET", "/api/workspaces")
# Skip realtime SSE - it's a streaming endpoint
test("Realtime Status", "GET", "/api/realtime/status", timeout=5)
test("CLI", "GET", "/api/cli")

# ============================================================
# 13. P12 NEW FEATURES
# ============================================================
print("13. P12 NEW FEATURES")

test("SSO Providers", "GET", "/api/auth/sso")
test("Governance", "GET", "/api/governance")
test("Snapshots", "GET", "/api/snapshots")
test("LLM Usage", "GET", "/api/llm-usage")
test("Cross Agent", "GET", "/api/cross-agent")

# ============================================================
# 14. P13 NEW FEATURES
# ============================================================
print("14. P13 NEW FEATURES")

if intel_id:
    test("Toggle Favorite", "POST", f"/api/agentmemory/{intel_id}/favorite")
    test("Check Favorite", "GET", f"/api/agentmemory/{intel_id}/favorite")
test("Favorites List", "GET", "/api/agentmemory/favorites")
test("Collections (global)", "GET", "/api/collections")
test("Links", "GET", "/api/links")
test("Health Scan", "GET", "/api/health-scan")

# ============================================================
# 15. BATCH OPERATIONS
# ============================================================
print("15. BATCH OPERATIONS")

if created_id:
    test("Batch Archive", "POST", "/api/agentmemory/batch",
        json={"ids": [created_id], "action": "archive"})
    test("Batch Unarchive", "POST", "/api/agentmemory/batch",
        json={"ids": [created_id], "action": "unarchive"})
    test("Batch Add Tags", "POST", "/api/agentmemory/batch",
        json={"ids": [created_id], "action": "add_tags", "params": {"tags": ["batch-tag"]}})

# ============================================================
# 16. EDGE CASES
# ============================================================
print("16. EDGE CASES")

test("Non-existent ID", "GET", "/api/agentmemory/nonexistent-id-12345")
test("Delete Non-existent", "DELETE", "/api/agentmemory/nonexistent-id-12345")
test("Update Non-existent", "PUT", "/api/agentmemory/nonexistent-id-12345", json={"content": "test"})
test("Archive Non-existent", "PATCH", "/api/agentmemory/nonexistent-id-12345/archive")
test("Invalid Batch Action", "POST", "/api/agentmemory/batch", json={"ids": [], "action": "invalid_action"})
test("Empty Batch Delete", "POST", "/api/agentmemory/batch/delete", json={"ids": []})
test("Search Quick (empty)", "GET", "/api/search/quick?q=")
test("Invalid Export Format", "GET", "/api/agentmemory/export?format=csv")
test("Invalid Paginated Sort", "GET", "/api/agentmemory/paginated?sort=invalid")
test("Create Empty Title", "POST", "/api/agentmemory", json={"title": "", "content": "test", "type": "fact"})

# ============================================================
# 17. FRONTEND ROUTES
# ============================================================
print("17. FRONTEND ROUTES")

frontend_routes = ["/", "/timeline", "/graph", "/stats", "/settings",
                   "/diagnostics", "/audit", "/backup", "/metrics",
                   "/instances", "/dashboard", "/plugins", "/compare"]
for route in frontend_routes:
    test(f"Frontend: {route}", "GET", route)

# ============================================================
# CLEANUP
# ============================================================
print("CLEANUP")
if intel_id:
    test("Cleanup: Delete Intel Memory", "DELETE", f"/api/agentmemory/{intel_id}")
if created_id:
    test("Cleanup: Delete Created Memory", "DELETE", f"/api/agentmemory/{created_id}")

# ============================================================
# REPORT
# ============================================================
print("\n\n" + "=" * 70)
print("COMPREHENSIVE TEST REPORT — Memory Viewer v2")
print("=" * 70)

passed = sum(1 for r in results if r["ok"])
failed = sum(1 for r in results if not r["ok"])
total = len(results)

api_results = [r for r in results if r["path"].startswith("/api/") or r["path"].startswith("/mcp/")]
api_passed = sum(1 for r in api_results if r["ok"])
api_failed = sum(1 for r in api_results if not r["ok"])

fe_results = [r for r in results if not r["path"].startswith("/api/") and not r["path"].startswith("/mcp/")]
fe_passed = sum(1 for r in fe_results if r["ok"])
fe_failed = sum(1 for r in fe_results if not r["ok"])

print(f"\n### 后端 API ({api_passed}/{len(api_results)} 通过)")
print(f"| {'端点':<50} | {'状态码':>6} | {'耗时ms':>7} | 结果 |")
print(f"|{'-'*52}|{'-'*8}|{'-'*9}|------|")
for r in api_results:
    status = "✅" if r["ok"] else "❌"
    endpoint = f"{r['method']:>4} {r['path']}"
    print(f"| {endpoint:<50} | {str(r['status']):>6} | {r['time_ms']:>6}ms | {status} |")

print(f"\n### 前端页面 ({fe_passed}/{len(fe_results)} 通过)")
print(f"| {'路由':<20} | {'状态码':>6} | 结果 |")
print(f"|{'-'*22}|{'-'*8}|------|")
for r in fe_results:
    status = "✅" if r["ok"] else "❌"
    print(f"| {r['path']:<20} | {str(r['status']):>6} | {status} |")

print(f"\n### 发现的问题")
issues = [r for r in results if not r["ok"]]
if issues:
    print(f"| {'#':<3} | {'端点':<50} | {'状态码':>8} | 问题描述 |")
    print(f"|{'-'*5}|{'-'*52}|{'-'*10}|----------|")
    for i, r in enumerate(issues, 1):
        endpoint = f"{r['method']} {r['path']}"
        print(f"| {i:<3} | {endpoint:<50} | {str(r['status']):>8} | {r['body'][:80]} |")
else:
    print("无问题发现！")

print(f"\n### 总结")
print(f"- 总测试数: {total}")
print(f"- 通过: {passed} ({round(passed/total*100, 1)}%)")
print(f"- 失败: {failed} ({round(failed/total*100, 1)}%)")
print(f"- 后端 API: {api_passed}/{len(api_results)} 通过")
print(f"- 前端页面: {fe_passed}/{len(fe_results)} 通过")
