# P21 Iteration Plan — Memory Viewer v2

> **Iteration:** P21 | **Orchestrator:** pm-orchestrator | **Date:** 2026-05-31
> **Previous:** P20 (pytest 189 passed, vue-tsc 0 errors — all tasks complete)
> **Goal:** 2–3 high-impact features, 4–6 tasks, verify with pytest + vue-tsc after each task

---

## 1. Background

### What was built in P20

| Area | Items |
|------|-------|
| Frontend views | HomeView, AgentMemoryView, HermesMemoryView, SearchResultsView |
| Stores | agentmemory, hermesMemory, ui |
| Router | /, /agentmemory, /hermes, /search |
| Backend APIs | /api/agentmemory, /api/hermes-memory, /api/profiles, /api/health, /api/search, /api/agentmemory/paginated |
| Tests | 31 pytest passed, 4 frontend test files |
| Known gaps | BUG-01 (no GET /api/agentmemory/{id}), BUG-02 (no /api/stats), no type filter UI |

### QA Report findings (P20)

```
BUG-01 [中]: GET /api/agentmemory/{memory_id} 未实现 → 无法深度链接单条记忆
BUG-02 [低]: GET /api/stats 未实现 → 缺少专用统计端点
```

---

## 2. Selected Features for P21

### Feature A — Single Memory Detail View (Frontend + Backend)

**Why:** Currently no way to view a single memory's full content. MemoryCard only shows a truncated preview. Users need to click-through to a detail page.

**Backend task:** `P21-T1` — Implement `GET /api/agentmemory/{memory_id}` endpoint

**Frontend task:** `P21-T2` — Create `MemoryDetailView.vue` at route `/memory/:id`

**Verification:** pytest (new test), vue-tsc

**Estimated:** 1.5 hr

---

### Feature B — Stats Endpoint (Backend)

**Why:** QA report identified missing `/api/stats` (BUG-02). While `/api/health` provides basic counts, a dedicated stats endpoint gives richer breakdown by type/source/profile.

**Backend task:** `P21-T3` — Implement `GET /api/stats` endpoint

**Verification:** pytest (new tests)

**Estimated:** 0.5 hr

---

### Feature C — Type Filter + Sort Controls (Frontend)

**Why:** AgentMemoryView currently has no filter controls. The paginated API already supports `type` filter and `sort`/`order` params but the UI doesn't expose them. Adding a filter dropdown + sort control improves UX significantly.

**Frontend task:** `P21-T4` — Add type filter dropdown + sort order controls to AgentMemoryView, connect to `/api/agentmemory/paginated`

**Verification:** vue-tsc

**Estimated:** 1.0 hr

---

## 3. Task Summary

| ID | Type | Title | Status | Verification |
|----|------|-------|--------|--------------|
| P21-T1 | backend | Implement GET /api/agentmemory/{memory_id} endpoint | todo | pytest |
| P21-T2 | frontend | Create MemoryDetailView.vue with full memory display | todo | vue-tsc |
| P21-T3 | backend | Implement GET /api/stats endpoint | todo | pytest |
| P21-T4 | frontend | Add type filter and sort controls to AgentMemoryView | todo | vue-tsc |

**Total: 4 tasks** (within 4–6 task constraint)

---

## 4. Execution Order

```
T1 (backend) → T2 (frontend, depends on T1 API contract)
T3 (backend, independent) → can run parallel with T1
T4 (frontend, independent)
```

After each task:
1. Write/update code
2. Run `pytest` (backend tasks) or `vue-tsc --noEmit` (frontend tasks)
3. Fix any errors before proceeding

---

## 5. Out of Scope for P21

- `/api/hermes-memory/{profile}` single profile endpoint (low priority)
- Frontend tests (npm proxy blocked in current env — tracked in P20 NOTE-02)
- Docker/build verification (deferred until npm proxy resolved)

---

## 6. Success Criteria

| Criterion | Measure |
|-----------|---------|
| All 4 tasks complete | Code merged |
| Backend tests pass | pytest shows new tests passing |
| Frontend type-safe | vue-tsc --noEmit exits 0 |
| No regression | Existing 31 pytest tests still pass |
| Feature A usable | Click MemoryCard → detail view shows full content |
| Feature B usable | GET /api/stats returns { agentmemory: {...}, hermes: {...}, profiles: {...} } |
| Feature C usable | Type filter + sort controls render and function in AgentMemoryView |