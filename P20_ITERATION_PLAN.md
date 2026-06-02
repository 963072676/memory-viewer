# P20 Iteration Plan — Memory Viewer v2

> **Iteration**: P20  
> **Date**: 2026-05-31  
> **Author**: pm-orchestrator

---

## 1. Iteration Summary

P20 delivers 4 features from P2/P3 backlog focused on **data organization** and **system visibility**:

| # | Feature | Description | Complexity | Layer |
|---|---------|-------------|-----------|-------|
| F-14 | Timeline View | Memory timeline grouped by date, with zoom control | 🟡 中 | 前端 |
| F-15 | Memory Archiving | Mark memories as "archived" — hidden by default, searchable | 🟡 中 | 前端+后端 |
| F-28 | Memory System Diagnosis | Detect duplicate entries, orphaned concepts, strength anomalies | 🟢 低 | 后端 |
| F-29 | Operation Audit Log | Record all CRUD operations with time/user/operation filters | 🟡 中 | 后端+前端 |

**Focus**: Data organization (timeline, archiving) + operational visibility (diagnosis, audit)

---

## 2. Feature Details

### F-14: Timeline View

**Description**: Display memories in a timeline grouped by date. Supports zoom in/out to show more/less detail. Replaces or supplements the card grid view.

**Implementation**:
- New `TimelineView.vue` component — date-grouped list with collapsible date headers
- Group memories by `updatedAt` date (YYYY-MM-DD)
- Zoom levels: Day / Week / Month — controls grouping granularity
- Use existing card components inside timeline groups
- New route `/timeline` or toggle within existing views

**Acceptance Criteria**:
- [ ] AC-F14-1: Memories grouped by date (newest date first)
- [ ] AC-F14-2: Date headers show count of memories per day
- [ ] AC-F14-3: Zoom control switches between Day/Week/Month grouping
- [ ] AC-F14-4: Clicking date header collapses/expands that group
- [ ] AC-F14-5: Timeline accessible via new view/tab

---

### F-15: Memory Archiving

**Description**: Mark memories as "archived" — archived memories don't appear in default view but can be retrieved via search or a filter toggle.

**Implementation**:
- Data model: add `isArchived: bool` field to memory entries (default `false`)
- Backend: extend `GET /api/agentmemory` with `?include_archived=true|false` query param
- Backend: add `PATCH /api/agentmemory/{id}/archive` endpoint to toggle archived status
- Frontend: add "Archive" action in memory card menu (three-dot menu)
- Frontend: add filter toggle "Show archived" in filter bar
- Archived memories shown with visual distinction (muted styling)

**Acceptance Criteria**:
- [ ] AC-F15-1: Archive action moves memory out of default view
- [ ] AC-F15-2: "Show archived" toggle reveals archived memories
- [ ] AC-F15-3: Archived memories searchable via search
- [ ] AC-F15-4: Unarchive action restores memory to default view
- [ ] AC-F15-5: Archived state persists across page reloads

---

### F-28: Memory System Diagnosis

**Description**: Run diagnostic rules against memory data to surface issues: duplicate entries (similar title/content), orphaned concepts (concepts not linked to any memory), strength anomalies (0 or extremely high values).

**Implementation**:
- New `GET /api/diagnosis` backend endpoint
- Runs diagnostic rules:
  - **Duplicates**: hash(title + content), flag if same hash appears >1
  - **Orphaned concepts**: concept appears in no memory
  - **Strength anomalies**: strength == 0 or strength > 10
- Returns structured report: `{issues: [{type, severity, count, items}]}`
- Frontend: new "Diagnosis" view accessible from settings/menu
- Display issues grouped by type with severity badges

**Acceptance Criteria**:
- [ ] AC-F28-1: Diagnosis runs on page load or manual trigger
- [ ] AC-F28-2: Duplicates detected based on title+content similarity
- [ ] AC-F28-3: Orphaned concepts flagged (concepts not in any memory)
- [ ] AC-F28-4: Strength anomalies (0 or >10) flagged
- [ ] AC-F28-5: Report shows count per issue type + item details

---

### F-29: Operation Audit Log

**Description**: Record all memory CRUD operations (create/update/delete) with timestamp, operation type, memory ID, and affected fields. Frontend shows a filterable audit log table.

**Implementation**:
- Backend: new `audit_log.json` file (append-only, JSONL format)
- On each memory write operation, append `{timestamp, operation, memory_id, title, user}` entry
- New `GET /api/audit` endpoint — supports filtering by:
  - `?operation=create|update|delete`
  - `?from=ISO datetime&to=ISO datetime`
  - `?memory_id=xxx`
- New `frontend/src/views/AuditLogView.vue` — table with filters
- Audit log accessible from settings menu

**Acceptance Criteria**:
- [ ] AC-F29-1: Create operation logs entry with type, memory_id, title, timestamp
- [ ] AC-F29-2: Update operation logs entry with changed fields
- [ ] AC-F29-3: Delete operation logs entry before deletion completes
- [ ] AC-F29-4: Audit log UI shows filterable table (by operation type, date range)
- [ ] AC-F29-5: Audit log persists across server restarts

---

## 3. Out of Scope

- Memory version history (F-24) — high complexity, deferred to future
- Memory association graph (F-18) — high complexity, deferred
- Smart recommendations (F-19) — high complexity, deferred
- MCP Server mode (F-27) — high complexity, deferred

---

## 4. Deliverables Checklist

### Backend
- [ ] `backend/app/routers/timeline.py` (new router for timeline grouping)
- [ ] `backend/app/routers/archive.py` (archive/unarchive endpoints)
- [ ] `backend/app/routers/diagnosis.py` (diagnosis endpoint)
- [ ] `backend/app/routers/audit.py` (audit log endpoints)
- [ ] `backend/app/services/diagnosis.py` (diagnostic rule engine)
- [ ] `backend/app/services/audit.py` (audit log writer)
- [ ] `backend/app/main.py` (register new routers)
- [ ] `backend/data/audit_log.json` (initialized empty)

### Frontend
- [ ] `frontend/src/views/TimelineView.vue`
- [ ] `frontend/src/components/DateGroupHeader.vue`
- [ ] `frontend/src/components/ZoomControl.vue`
- [ ] `frontend/src/components/MemoryCard.vue` (archive menu item)
- [ ] `frontend/src/views/DiagnosisView.vue`
- [ ] `frontend/src/views/AuditLogView.vue`
- [ ] `frontend/src/App.vue` or router (add timeline route)
- [ ] `frontend/src/stores/agentmemory.ts` (include_archived filter)

### Tests
- [ ] `backend/tests/test_diagnosis.py`
- [ ] `backend/tests/test_audit.py`
- [ ] `backend/tests/test_archive.py`

---

## 5. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-------------|
| Archiving requires data model migration | 🟡 Medium | High | Add isArchived field with default false (backward compatible) |
| Audit log grows unbounded | 🟡 Medium | Medium | Implement log rotation (age-based) in future iteration |
| Timeline performance with 1000+ memories | 🟢 Low | Low | Virtual grouping, only render visible groups |

---

## 6. Dependencies

- F-14 (Timeline): No backend changes — frontend grouping only
- F-15 (Archive): Requires backend API changes (filter + toggle)
- F-28 (Diagnosis): Independent — reads existing data
- F-29 (Audit): Independent — writes new audit log file