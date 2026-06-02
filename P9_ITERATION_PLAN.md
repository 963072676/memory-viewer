# P9 Iteration Plan — Data Governance & Advanced Intelligence

> **Phase**: P9
> **Date**: 2026-05-29
> **Theme**: Data Governance, Collaborative Intelligence & Operational Resilience
> **Total Features**: 6 (F-39 through F-44)
> **Estimated Effort**: 3-4 weeks

---

## P9 Features Overview

| # | Feature | Description | Complexity | Layer |
|---|---------|-------------|------------|-------|
| F-39 | Natural Language Query (NLQ) | LLM-powered natural language to structured query conversion | 🟠 High | Backend + Frontend |
| F-40 | Memory Clustering | Embedding-based automatic topic grouping | 🟡 Medium | Backend + Frontend |
| F-41 | Sensitive Info Masking (PII Redaction) | Detect and mask API keys, emails, passwords in memory content | 🟡 Medium | Backend + Frontend |
| F-42 | Memory Sharing | Shareable links with access control and expiration | 🟡 Medium | Backend + Frontend |
| F-43 | Anomaly Detection & Alerts | Health monitoring with proactive anomaly detection | 🟠 High | Backend + Frontend |
| F-44 | Custom Dashboard Views | Draggable widget-based customizable dashboard | 🟡 Medium | Frontend |

---

## Feature Details

### F-39 — Natural Language Query (NLQ)

**Problem**: Current search supports keyword and semantic matching, but users still need to understand filter syntax. Querying "show me all bugs from last week" requires combining multiple filter parameters manually.

**Solution**: LLM-powered natural language query parsing that converts conversational questions into structured API queries.

**Implementation**:
- Backend: New `backend/app/services/nlq_service.py`
  - Leverages P8's LLM service (llm_service.py) to parse natural language into JSON query conditions
  - NLQ Pipeline: user input → LLM parses to JSON query → execute standard API query → return results
  - Query condition mapping: supports type, date_range, strength_range, tags, profile, sort_by dimensions
  - Safety: LLM restricted to outputting JSON query conditions only, no arbitrary code execution
  - New endpoint: `POST /api/search/nlq` accepts `{ question: string }`, returns results + parsed conditions
- Frontend: Extend search bar
  - New "🤖 Ask" mode toggle (keyword / semantic / natural language)
  - NLQ mode shows conversational UI: input + results panel + parsed conditions display
  - Parsed conditions are editable (user confirms/modifies LLM's understanding)
  - Query history (last 10 NLQ queries) saved to localStorage
- New component: `frontend/src/components/NLQPanel.vue`

**Acceptance Criteria**:
- AC-F39-1: Input "上周创建的 bug 记忆" returns correct filtered results
- AC-F39-2: Displays parsed structured query conditions (type=bug, date=last_week)
- AC-F39-3: User can edit parsed conditions and re-query
- AC-F39-4: When LLM is not configured, NLQ mode is disabled with helpful message
- AC-F39-5: Query response time <5s (including LLM parsing)
- AC-F39-6: Query history is clickable and reusable

**Dependencies**: P8 F-34 (LLM Service), P8 F-33 (Semantic Search infrastructure)

---

### F-40 — Memory Clustering

**Problem**: With 100+ memories, linear lists make it hard to discover topic structures. Users don't know which areas their memories concentrate in or which areas are underrepresented.

**Solution**: Automatically group memories into topic clusters using embedding similarity.

**Implementation**:
- Backend: New `backend/app/services/clustering_service.py`
  - Uses P8's embedding service to get vector representations of all memories
  - Clustering algorithm: K-Means (auto-determine K via Silhouette Score) or HDBSCAN
  - Auto-generate cluster labels using TF-IDF top concepts from each cluster
  - New endpoint: `GET /api/clusters` → `{clusters: [{id, name, count, memory_ids, centroid_concepts}]}`
  - New endpoint: `GET /api/clusters/{id}` → detailed memory list for cluster
  - Cache: cluster results cached for 1 hour, invalidated on memory changes
- Frontend: New `frontend/src/views/ClustersView.vue`
  - Bubble chart visualization (each bubble = cluster, size = count, color = type distribution)
  - Click bubble to expand cluster's memory list
  - Optional 2D projection (t-SNE/UMAP) scatter plot for inter-cluster relationships
  - Sidebar integration: "Browse by Topic" entry in Smart Collections area

**Acceptance Criteria**:
- AC-F40-1: /clusters returns ≥3 meaningful clusters
- AC-F40-2: Each cluster has an understandable name (based on concepts)
- AC-F40-3: Bubble chart correctly reflects cluster sizes and relationships
- AC-F40-4: Clicking a cluster shows its contained memories
- AC-F40-5: Cluster generation completes in <10s for 100 memories
- AC-F40-6: Clusters auto-update after new memories are added (cache invalidation)

**Dependencies**: P8 F-33 (Embedding Service)

---

### F-41 — Sensitive Info Masking (PII Redaction)

**Problem**: Memories may contain API keys, passwords, emails, phone numbers. Sharing views or exporting data risks accidental credential leakage.

**Solution**: Detect and mask sensitive data using regex patterns and optional LLM enhancement.

**Implementation**:
- Backend: New `backend/app/services/redaction_service.py`
  - Regex detectors: API keys (`sk-...`, `AKIA...`), emails, phone numbers, IP addresses, passwords
  - Optional LLM-enhanced detection for patterns regex can't catch (internal codenames, etc.)
  - Masking strategy: `sk-abc123...xyz` → `sk-****...****`, `user@example.com` → `u***@***.com`
  - New endpoint: `POST /api/memories/{id}/redact` → returns masked content (doesn't modify original)
  - New endpoint: `POST /api/memories/scan-pii` → scans all memories, returns PII-containing list
  - New endpoint: `GET /api/memories/pii-report` → PII statistics report
- Frontend integration:
  - Memory cards show 🔒 icon for PII-containing memories
  - Expanded view shows masked content by default; "Show Original" requires confirmation
  - Settings page: configure masking rules (enable/disable each detector)
  - Auto-masking option on export (default: enabled)
  - PII scan report page (Dashboard sub-view)

**Acceptance Criteria**:
- AC-F41-1: `sk-` prefixed API keys are auto-detected and marked
- AC-F41-2: Email addresses are detected and partially masked
- AC-F41-3: PII scan report lists all memories containing sensitive info
- AC-F41-4: Export supports auto-masking option
- AC-F41-5: Viewing original content requires confirmation action
- AC-F41-6: Masking doesn't affect original data storage

**Dependencies**: None (independent feature)

---

### F-42 — Memory Sharing

**Problem**: Memory data is locked inside the system. There's no way to share specific memories with team members or external collaborators.

**Solution**: Generate shareable links with access control, expiration, and optional password protection.

**Implementation**:
- Backend: New `backend/app/services/sharing_service.py`
  - Share link generation: `POST /api/memories/{id}/share` → `{share_id, share_url, expires_at, access_level}`
  - Access levels: `view` (read-only) / `comment` (can comment) / `edit` (can edit)
  - Expiration options: 1 hour / 1 day / 7 days / 30 days / never
  - Share data storage: `backend/data/shares.json`
  - Public access endpoint: `GET /api/shared/{share_id}` → no auth required
  - Share management: `GET /api/shares` → list all active share links
  - Revoke share: `DELETE /api/shares/{share_id}`
- Frontend: New `frontend/src/components/ShareModal.vue`
  - "Share" button on memory detail page
  - Share modal: access level selection + expiration selection + link generation
  - Copy to clipboard + QR code display
  - Share management page: list all share links, support revoke
  - Batch sharing: select multiple memories to generate collection share link
- Security:
  - Share links contain unguessable UUIDs
  - Optional password protection
  - Access logging (who accessed when)

**Acceptance Criteria**:
- AC-F42-1: Generate share link for single memory; unauthenticated user can view
- AC-F42-2: Share link becomes inaccessible after expiration
- AC-F42-3: Supports view/comment/edit access levels
- AC-F42-4: Share links can be revoked
- AC-F42-5: Batch sharing generates collection links
- AC-F42-6: Auto-applies PII masking on share (depends on F-41)

**Dependencies**: F-41 (auto-masking on share)

---

### F-43 — Anomaly Detection & Alerts

**Problem**: Anomalies in the memory system (sudden data loss, abnormal strength distribution, API response spikes) are typically discovered after users notice issues. There's no proactive monitoring.

**Solution**: Monitor memory system health metrics and trigger alerts on detected anomalies.

**Implementation**:
- Backend: New `backend/app/services/anomaly_service.py`
  - Monitored metrics:
    - Memory count change rate (daily delta >20% → anomaly)
    - Average strength change (weekly delta >15% → anomaly)
    - API response time P95 (>500ms → anomaly)
    - Error rate (>5% → anomaly)
    - Memory type distribution shift (single type share change >30%)
  - Detection algorithm: Moving average + standard deviation threshold (Z-score > 2)
  - New endpoint: `GET /api/anomalies` → detected anomaly list
  - New endpoint: `GET /api/anomalies/health` → overall system health score (0-100)
  - New endpoint: `POST /api/anomalies/check` → manual trigger detection
  - Alert notification: integrate P4's webhook/Feishu notification on anomaly
  - Scheduled task: auto-detect every hour
- Frontend: New `frontend/src/views/AnomaliesView.vue`
  - Anomaly timeline: reverse chronological display of detected events
  - Health score dashboard: circular progress bar + per-dimension score breakdown
  - Anomaly details: type, time, impact scope, suggested fix action
  - Alert configuration: set thresholds and notification channels
  - Dashboard integration: health score displayed as card on main dashboard

**Acceptance Criteria**:
- AC-F43-1: Memory count sudden change triggers anomaly detection
- AC-F43-2: Health score correctly reflects system state
- AC-F43-3: Anomalies trigger webhook alerts
- AC-F43-4: Alert thresholds are configurable
- AC-F43-5: Anomaly history is traceable (30-day retention)
- AC-F43-6: Dashboard displays current health score

**Dependencies**: P4 F-26 (Webhook Notification), P5 F-32 (Performance Monitoring)

---

### F-44 — Custom Dashboard Views

**Problem**: All users see the same Dashboard layout, but different roles (developer, PM, ops) focus on different metrics.

**Solution**: User-configurable dashboard with draggable widget placement and preset templates.

**Implementation**:
- Frontend: New `frontend/src/components/DashboardWidget.vue` base component
  - Available widgets:
    - Memory total count (existing)
    - Type distribution pie chart (existing)
    - Activity heatmap (P8 F-37)
    - Health score (F-43)
    - Recently modified memories list
    - Cluster overview (F-40)
    - PII alert summary (F-41)
    - Anomaly event timeline (F-43)
    - Decay curve (P3 F-22)
    - Quick actions panel
  - Each widget supports: title, refresh, fullscreen, remove
- Frontend: New `frontend/src/views/CustomDashboard.vue`
  - Drag layout: use `vue-grid-layout` for grid-based drag-and-drop
  - Layout persistence: save to localStorage + backend `PUT /api/dashboard/layout`
  - Preset templates: "Developer View" / "Ops View" / "PM View" / "Default View"
  - Widget add panel: drag from available widget list into dashboard
  - Responsive: mobile auto-stacks to single column
- Backend: New `backend/app/routers/dashboard.py`
  - `GET /api/dashboard/layout` → retrieve saved layout
  - `PUT /api/dashboard/layout` → save layout configuration
  - Layout data: `{widgets: [{id, type, x, y, w, h, config}], preset: string}`

**Acceptance Criteria**:
- AC-F44-1: Dashboard supports drag to adjust widget position and size
- AC-F44-2: Widgets can be added/removed
- AC-F44-3: Layout persists after refresh (localStorage)
- AC-F44-4: Provides ≥3 preset layout templates
- AC-F44-5: Mobile auto-adapts to single column layout
- AC-F44-6: Each widget loads and refreshes independently

**Dependencies**: P8 F-37 (Heatmap Widget), F-43 (Health Score Widget)

---

## Implementation Order

```
Week 1: F-41 (PII Masking) + F-44 (Custom Dashboard)
        → Independent features, no cross-dependencies
        → PII masking is governance prerequisite for sharing

Week 2: F-42 (Memory Sharing) + F-40 (Clustering)
        → Sharing depends on PII masking being ready
        → Clustering depends on P8 embeddings

Week 3: F-39 (NLQ) + F-43 (Anomaly Detection)
        → Both are intelligence features with backend-heavy work
        → NLQ builds on P8 LLM service; Anomaly builds on P5 monitoring

Week 4: Integration testing, E2E testing, documentation
        → Cross-feature integration (Dashboard widgets from F-40, F-41, F-43)
        → Performance testing with 200+ memories
        → Documentation and changelog
```

**Rationale**:
1. F-41 first: PII masking is a governance prerequisite for F-42 (sharing). It's also independently valuable.
2. F-44 second (parallel with F-41): Pure frontend, no dependencies, can be developed concurrently.
3. F-42 third: Depends on F-41 for auto-masking on share. Week 2 start gives F-41 buffer time.
4. F-40 fourth: Depends on P8 embeddings. Backend-heavy, pairs well with F-42's frontend work.
5. F-39 fifth: NLQ requires LLM service (P8 F-34). Complex but isolated.
6. F-43 sixth: Anomaly detection builds on P5 monitoring infrastructure. Provides widgets for F-44.
7. Week 4: Integration week. Critical for Dashboard widget assembly from multiple features.

---

## Dependency Graph

```
P8 F-33 (Embedding) ──→ F-40 (Clustering)
P8 F-34 (LLM) ────────→ F-39 (NLQ)
P4 F-26 (Webhook) ─────→ F-43 (Anomaly) ──→ F-44 (Dashboard widgets)
P5 F-32 (Perf Monitor) → F-43 (Anomaly)
                         F-41 (PII) ──→ F-42 (Sharing)
P8 F-37 (Heatmap) ─────→ F-44 (Dashboard widgets)
```

---

## Technical Impact

| Feature | Backend Changes | Frontend Changes | New Files |
|---------|----------------|-----------------|-----------|
| F-39 | +nlq_service, +search/nlq endpoint | SearchBar mode toggle, NLQPanel | `services/nlq_service.py`, `NLQPanel.vue` |
| F-40 | +clustering_service, +clusters endpoints | ClustersView, bubble chart | `services/clustering_service.py`, `ClustersView.vue` |
| F-41 | +redaction_service, +redact/scan endpoints | PII icon, masked view, settings | `services/redaction_service.py`, `PIIReport.vue` |
| F-42 | +sharing_service, +share endpoints | ShareModal, share management | `services/sharing_service.py`, `ShareModal.vue` |
| F-43 | +anomaly_service, +anomaly endpoints | AnomaliesView, health dashboard | `services/anomaly_service.py`, `AnomaliesView.vue` |
| F-44 | +dashboard layout endpoints | CustomDashboard, DashboardWidget | `routers/dashboard.py`, `CustomDashboard.vue` |

---

## New Dependencies

| Package | Purpose | Size | Used By |
|---------|---------|------|---------|
| scikit-learn | K-Means clustering + TF-IDF | ~30MB | F-40 |
| hdbscan | Density-based clustering (optional) | ~5MB | F-40 |
| vue-grid-layout | Draggable grid layout | ~50KB | F-44 |
| qrcode | Share link QR code generation | ~200KB | F-42 |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| NLQ accuracy insufficient | Medium | Medium | Show parsed conditions for user correction; fallback to structured search |
| Clustering poor with small dataset | Medium | Low | Disable clustering when <30 memories; show guidance text |
| PII detection false positives | Medium | Medium | Provide whitelist mechanism; users can mark false positives |
| Share link security breach | Low | High | UUID unguessable + optional password + expiration mechanism |
| Custom layout data corruption | Low | Low | Layout data validation + reset to default option |
| Anomaly detection noise | Medium | Medium | Configurable thresholds; auto-tune after 2 weeks of baseline data |

---

## Acceptance Test Plan

### Smoke Tests (per feature)
- F-39: NLQ query → results displayed with parsed conditions
- F-40: /clusters → bubble chart rendered with ≥3 clusters
- F-41: Memory with API key → 🔒 icon shown; export with masking → keys masked
- F-42: Share → link generated → open in incognito → content visible
- F-43: Trigger anomaly → alert sent via webhook → AnomaliesView shows event
- F-44: Drag widget → position changes → refresh → position persists

### Regression Tests
- All P0-P8 features still work correctly
- New features don't break existing API contracts
- Dark mode works on all new views
- Responsive layout works on mobile (375px)
- Keyboard shortcuts still function

### Performance Tests
- F-40: Clustering 200 memories completes in <15s
- F-39: NLQ response <5s including LLM parsing
- F-44: Dashboard with 8 widgets loads in <3s
- F-43: Anomaly detection cycle completes in <5s
