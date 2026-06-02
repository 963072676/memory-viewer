# P10 Iteration Plan — Advanced Automation & Collaborative Intelligence

> **Phase**: P10
> **Date**: 2026-05-29
> **Theme**: Advanced Automation, Collaborative Intelligence & Self-Optimization
> **Total Features**: 6 (F-45 through F-50)
> **Estimated Effort**: 3-4 weeks

---

## P10 Features Overview

| # | Feature | Description | Complexity | Layer |
|---|---------|-------------|------------|-------|
| F-45 | Memory Conflict Detection | Detect contradictions between memories and surface conflicts | 🟠 High | Backend + Frontend |
| F-46 | Collaborative Annotations | Team-based comments and annotations on memories | 🟡 Medium | Backend + Frontend |
| F-47 | Memory Workflow Automation | Rule-based automation for memory lifecycle management | 🟠 High | Backend + Frontend |
| F-48 | Memory Lineage & Provenance | Track origin, transformations, and derivation chain of memories | 🟡 Medium | Backend + Frontend |
| F-49 | API Usage Analytics | Track and visualize API consumption patterns and costs | 🟡 Medium | Backend + Frontend |
| F-50 | Guided Setup Wizard | Interactive onboarding wizard for first-time configuration | 🟢 Low | Frontend |

---

## Feature Details

### F-45 — Memory Conflict Detection

**Problem**: As the memory base grows, contradictory information can accumulate (e.g., "User prefers Python" vs "User prefers TypeScript"). These conflicts silently degrade Agent decision quality.

**Solution**: LLM-powered conflict detection that scans for semantic contradictions and surfaces them for resolution.

**Implementation**:
- Backend: New `backend/app/services/conflict_service.py`
  - Periodic scan: compare new/updated memories against existing ones using embedding similarity + LLM verification
  - Conflict pipeline: find top-K similar memories by embedding → LLM判断是否矛盾 → 生成冲突报告
  - Conflict types: direct contradiction, outdated info, partial overlap
  - Resolution suggestions: keep newest, merge, manual review
  - New endpoints:
    - `GET /api/conflicts` → list of detected conflicts
    - `POST /api/conflicts/{id}/resolve` → resolve with action (keep_a, keep_b, merge, dismiss)
  - Cache: conflicts recalculated on memory write, cached for 2 hours
- Frontend: New `frontend/src/views/ConflictsView.vue`
  - Conflict cards: side-by-side display of conflicting memories with highlighted differences
  - Resolution actions: one-click resolve with preview
  - Conflict severity indicator (high/medium/low)
  - Sidebar entry: "⚠️ Conflicts" badge with count
- New component: `frontend/src/components/ConflictCard.vue`

**Acceptance Criteria**:
- AC-F45-1: POST /api/conflicts/scan triggers conflict detection
- AC-F45-2: Returns conflict pairs with similarity score and contradiction type
- AC-F45-3: LLM correctly identifies semantic contradictions (not just similar topics)
- AC-F45-4: Resolution actions update the memory base correctly
- AC-F45-5: Conflict count shown in sidebar with severity color
- AC-F45-6: Scan completes within 30s for 500 memories

**Dependencies**: P8 F-33 (Semantic Search), P8 F-34 (LLM Service), P9 F-40 (Clustering)

---

### F-46 — Collaborative Annotations

**Problem**: In team settings, multiple people interact with the same Agent but have no way to annotate, comment on, or flag memories for review. Knowledge curation is a solo activity.

**Solution**: Threaded comments and annotations on individual memories, supporting team collaboration.

**Implementation**:
- Backend: New `backend/app/services/annotation_service.py`
  - Data model: annotations stored per memory_id with {author, content, timestamp, parent_id (for threads), type (comment/flag/suggestion)}
  - New endpoints:
    - `GET /api/memories/{id}/annotations` → list annotations for a memory
    - `POST /api/memories/{id}/annotations` → add annotation
    - `PUT /api/annotations/{id}` → edit annotation
    - `DELETE /api/annotations/{id}` → delete annotation
    - `POST /api/annotations/{id}/resolve` → resolve flag/suggestion
  - Annotation types: comment, flag_for_review, suggest_edit, tag_suggestion
  - Storage: `backend/cache/annotations.json` (JSON file, consistent with existing architecture)
- Frontend:
  - Expand memory card detail view to include annotations section
  - Threaded comment UI with author avatars (initial-based)
  - "Add annotation" button on each memory card
  - Flag/suggestion badges on memory cards
  - New component: `frontend/src/components/AnnotationThread.vue`
  - New component: `frontend/src/components/AnnotationInput.vue`

**Acceptance Criteria**:
- AC-F46-1: Can add comment to any memory
- AC-F46-2: Comments support threading (reply to comment)
- AC-F46-3: Flag for review shows badge on memory card
- AC-F46-4: Annotations persist across page refreshes
- AC-F46-5: Can filter memories by "has flags" or "has suggestions"
- AC-F46-6: Annotation count visible on collapsed memory cards

**Dependencies**: P0 F-07 (Memory Create/Edit), existing memory card component

---

### F-47 — Memory Workflow Automation

**Problem**: Repetitive memory management tasks (archive old memories, adjust strength, tag patterns) waste time. Users need rules-based automation to maintain memory hygiene.

**Solution**: A workflow engine that executes user-defined rules triggered by events or schedules.

**Implementation**:
- Backend: New `backend/app/services/workflow_service.py`
  - Rule definition: `{name, trigger: {type: "schedule"|"event", config}, conditions: [{field, op, value}], actions: [{type, config}]}`
  - Trigger types: schedule (cron-like), on_memory_create, on_memory_update, on_strength_change
  - Condition types: age_days > X, strength < X, type == X, has_concept X
  - Action types: archive, adjust_strength, add_tag, send_notification, delete
  - Rule storage: `backend/cache/workflows.json`
  - Execution engine: asyncio scheduler for time-based, event hooks for event-based
  - New endpoints:
    - `GET /api/workflows` → list rules
    - `POST /api/workflows` → create rule
    - `PUT /api/workflows/{id}` → update rule
    - `DELETE /api/workflows/{id}` → delete rule
    - `POST /api/workflows/{id}/execute` → manual trigger
    - `GET /api/workflows/{id}/logs` → execution history
- Frontend: New `frontend/src/views/WorkflowsView.vue`
  - Visual rule builder: dropdown-based condition/action configuration
  - Rule cards with toggle enable/disable
  - Execution log table with timestamps and results
  - Pre-built templates: "Archive stale memories", "Low strength cleanup", "Auto-tag by pattern"
- New components: `frontend/src/components/WorkflowBuilder.vue`, `frontend/src/components/WorkflowLog.vue`

**Acceptance Criteria**:
- AC-F47-1: Can create a scheduled rule via UI
- AC-F47-2: Event-triggered rules fire on memory create/update
- AC-F47-3: Multiple conditions supported (AND logic)
- AC-F47-4: Execution logs show what was changed
- AC-F47-5: Rules can be enabled/disabled without deletion
- AC-F47-6: Pre-built templates work out of the box

**Dependencies**: P2 F-11 (Auto Refresh scheduler pattern), P1 F-09 (Memory Delete)

---

### F-48 — Memory Lineage & Provenance

**Problem**: Memories are created, merged, and transformed over time, but there's no record of where they came from or how they evolved. This makes it hard to trust or verify memory sources.

**Solution**: Track the full provenance chain of each memory: origin, transformations, merges, and derivations.

**Implementation**:
- Backend: New `backend/app/services/lineage_service.py`
  - Data model: each memory gets a `lineage` field: `{source: "manual"|"import"|"agent"|"merge"|"derived", parent_ids: [], created_at, transformations: [{type, timestamp, detail}]}`
  - Track events: creation, edit, merge (from multiple parents), split, import with source file
  - New endpoints:
    - `GET /api/memories/{id}/lineage` → full provenance chain
    - `GET /api/lineage/graph` → DAG visualization data of all memory derivations
  - Backfill: existing memories get lineage = {source: "legacy"}
- Frontend:
  - Lineage tab on memory detail view: breadcrumb-style provenance chain
  - Visual DAG (using existing force-graph library) showing derivation relationships
  - Source icons: ✍️ manual, 📥 import, 🤖 agent, 🔀 merge, 🔗 derived
  - New component: `frontend/src/components/LineageGraph.vue`

**Acceptance Criteria**:
- AC-F48-1: New memories automatically get lineage metadata
- AC-F48-2: Edited memories record transformation history
- AC-F48-3: Merged memories link to both parents
- AC-F48-4: Lineage graph renders correctly with force-graph
- AC-F48-5: Source type displayed with appropriate icon
- AC-F48-6: Backfilled legacy memories show "legacy" source

**Dependencies**: P3 F-18 (Relationship Graph uses force-graph), P0 F-07 (Memory Create)

---

### F-49 — API Usage Analytics

**Problem**: No visibility into how the Memory Viewer API is being consumed. Can't track which endpoints are hot, what's the error rate, or estimate LLM API costs.

**Solution**: Comprehensive API usage tracking with cost estimation and usage pattern visualization.

**Implementation**:
- Backend: New `backend/app/middleware/usage_tracker.py`
  - Middleware that records: endpoint, method, response_time, status_code, timestamp, request_size, response_size
  - LLM cost tracking: count tokens used by NLQ, auto-tag, semantic search, conflict detection
  - Aggregation: hourly/daily rollups stored in `backend/cache/usage_stats.json`
  - New endpoints:
    - `GET /api/analytics/usage` → usage summary (period, total requests, avg latency, error rate)
    - `GET /api/analytics/endpoints` → per-endpoint breakdown
    - `GET /api/analytics/costs` → LLM token usage and estimated cost
    - `GET /api/analytics/trends` → time-series data for charts
  - Data retention: raw data 7 days, hourly rollups 30 days, daily rollups 1 year
- Frontend: New `frontend/src/views/AnalyticsView.vue`
  - Dashboard with charts: request volume over time, top endpoints, error rate, latency distribution
  - LLM cost breakdown by feature (NLQ, auto-tag, semantic search, conflicts)
  - Time range selector (24h, 7d, 30d)
  - Sidebar entry under "System" section
- New component: `frontend/src/components/UsageChart.vue`

**Acceptance Criteria**:
- AC-F49-1: All API requests tracked without impacting performance (<1ms overhead)
- AC-F49-2: Usage dashboard shows request volume, latency, error rate
- AC-F49-3: LLM token usage broken down by feature
- AC-F49-4: Time range filtering works (24h, 7d, 30d)
- AC-F49-5: Data retention policies enforced automatically
- AC-F49-6: Cost estimation configurable (per-token pricing)

**Dependencies**: P5 F-32 (Performance Monitoring middleware pattern)

---

### F-50 — Guided Setup Wizard

**Problem**: New users face a blank slate with no guidance on how to configure their memory system, set up integrations, or import existing data.

**Solution**: An interactive step-by-step wizard that guides first-time setup.

**Implementation**:
- Frontend only (no new backend endpoints needed)
  - Multi-step wizard displayed on first visit (localStorage flag)
  - Steps:
    1. Welcome & overview
    2. Connect to Agent memory source (configure agentmemory.json path or API endpoint)
    3. Import existing memories (leverage F-08 import)
    4. Configure preferences (theme, auto-refresh interval, notification settings)
    5. Explore features tour (highlights key features with tooltips)
    6. Optional: set up first workflow rule
  - Progress indicator with step completion checkmarks
  - "Skip" option for experienced users
  - "Restart wizard" accessible from settings
  - New component: `frontend/src/components/SetupWizard.vue`
  - New component: `frontend/src/components/FeatureTour.vue`

**Acceptance Criteria**:
- AC-F50-1: Wizard auto-shows on first visit
- AC-F50-2: Can navigate forward/backward between steps
- AC-F50-3: Skip button available at any step
- AC-F50-4: Wizard completion sets localStorage flag
- AC-F50-5: "Restart wizard" available in settings
- AC-F50-6: Feature tour highlights real UI elements with tooltips

**Dependencies**: P0 F-08 (Memory Import), P2 F-13 (Dark Mode for theme config)

---

## Implementation Order

### Week 1: Foundation & Backend-Heavy Features
1. **F-48 Memory Lineage** — extends existing data model, minimal new UI
2. **F-49 API Usage Analytics** — middleware + aggregation, standalone

### Week 2: Intelligence & Automation
3. **F-45 Conflict Detection** — leverages LLM infrastructure, high value
4. **F-47 Workflow Automation** — rule engine, builds on scheduler pattern

### Week 3: Collaboration & Polish
5. **F-46 Collaborative Annotations** — UI-focused, builds on memory cards
6. **F-50 Setup Wizard** — frontend only, no backend dependency

---

## Dependency Graph

```
F-48 (Lineage) ──────────────────┐
F-49 (Analytics) ────────────────┤
F-45 (Conflicts) ── depends on ──┤── P8 Semantic Search + LLM
F-47 (Workflows) ── depends on ──┤── P2 Auto Refresh pattern
F-46 (Annotations) ──────────────┤── P0 Memory Create
F-50 (Wizard) ───── depends on ──┘── P0 Import + P2 Dark Mode
```

## Technical Impact

| Feature | Backend Changes | Frontend Changes | New Files |
|---------|----------------|-----------------|-----------|
| F-45 | conflict_service.py, router | ConflictsView, ConflictCard | 3 |
| F-46 | annotation_service.py, router | AnnotationThread, AnnotationInput | 3 |
| F-47 | workflow_service.py, router | WorkflowsView, WorkflowBuilder, WorkflowLog | 4 |
| F-48 | lineage_service.py, router, model update | LineageGraph | 2 |
| F-49 | usage_tracker.py, router, aggregation | AnalyticsView, UsageChart | 3 |
| F-50 | none | SetupWizard, FeatureTour | 2 |

## New Dependencies

| Package | Purpose | Size | Used By |
|---------|---------|------|---------|
| croniter | Cron expression parsing for workflow scheduling | ~50KB | F-47 |
| apscheduler | Async scheduler for workflow triggers | ~100KB | F-47 |

*No new frontend dependencies needed — existing force-chart, chart.js sufficient.*

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Conflict detection false positives | Medium | Medium | Confidence threshold + manual review queue |
| Workflow engine complexity | Medium | High | Start with simple rules, iterate |
| Usage tracking performance overhead | Low | Medium | Async logging, batch writes |
| Lineage backfill for legacy data | Low | Low | Mark as "legacy", no runtime impact |

## Acceptance Test Plan

### Smoke Tests
- F-45: Create two contradictory memories → conflict detected
- F-46: Add comment → appears on memory detail
- F-47: Create archive rule → old memory gets archived
- F-48: Create memory → lineage recorded
- F-49: Make API calls → usage tracked
- F-50: Clear localStorage → wizard appears

### Regression Tests
- All existing CRUD operations still work
- Search, NLQ, clustering unaffected
- Performance: API latency increase < 5ms
- Memory card rendering unchanged

### Performance Tests
- Conflict scan: < 30s for 500 memories
- Usage tracking overhead: < 1ms per request
- Workflow scheduler: handles 100 rules without lag
