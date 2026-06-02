# P13 Iteration Plan — UX Polish, Smart Collections & Operational Intelligence

> **Phase**: P13
> **Date**: 2026-05-29
> **Theme**: User Experience Polish, Smart Organization & Proactive Intelligence
> **Total Features**: 6 (F-63 through F-68)
> **Estimated Effort**: 3-4 weeks
> **Prerequisites**: P0-P12 completed (85 features total)

---

## P13 Design Principles

- **UX over features**: Polish existing interactions before adding new complexity
- **Smart defaults**: Automate organization so users spend less time managing memories
- **Proactive intelligence**: Surface insights before users ask for them
- **Progressive disclosure**: Simple surface with power features available on demand
- **Build on infrastructure**: Leverage existing embeddings, LLM service, plugin system, and clustering

---

## P13 Features Overview

| # | Feature | Description | User Value | Complexity | Layer |
|---|---------|-------------|------------|------------|-------|
| **F-63** | Memory Favorites & Pin-to-Top | Star/pin memories for instant access; favorites panel in sidebar | Quick access to most important memories without scrolling or searching | 🟢 Low | Frontend + Backend |
| **F-64** | Saved Searches & Smart Collections | Save search queries as dynamic collections that auto-update as memories change | Organize memories by rules instead of manual tagging; always-current filtered views | 🟡 Medium | Backend + Frontend |
| **F-65** | Memory Linking & Relation Graph | Create manual links between memories; visualize as interactive graph | Build explicit knowledge connections beyond concept co-occurrence; navigate related memories | 🟡 Medium | Backend + Frontend |
| **F-66** | Guided Onboarding Tour | Interactive first-time walkthrough highlighting key features and workflows | Reduce learning curve; ensure users discover core features on first visit | 🟢 Low | Frontend |
| **F-67** | Advanced Export & Reporting | Generate formatted PDF/HTML reports from memory data with customizable templates | Share memory insights with stakeholders who don't have system access; periodic reporting | 🟡 Medium | Backend + Frontend |
| **F-68** | Memory Health Scanner | Proactive system health check: orphaned concepts, stale memories, quality gaps | Discover and fix data quality issues before they cause problems | 🟡 Medium | Backend + Frontend |

---

## Feature Details

### F-63 — Memory Favorites & Pin-to-Top

**Problem**: Users have important memories they reference frequently (key patterns, critical workflows, important facts), but these get buried in a growing list. There's no way to mark memories as "important" for quick access.

**Solution**: A favorites/pinning system that lets users star memories and access them from a dedicated sidebar panel or filter.

**Implementation**:
- Backend:
  - New field `favorite: boolean` on memory model (default: false)
  - New endpoint: `PUT /api/agentmemory/{id}/favorite` → toggle favorite status
  - New endpoint: `GET /api/agentmemory/favorites` → list all favorited memories
  - Storage: `backend/cache/favorites.json` — lightweight file mapping memory IDs to favorite status
  - Favorite status persists across sessions
- Frontend:
  - Star icon (☆/★) on each MemoryCard — click to toggle
  - New sidebar section: "⭐ Favorites" showing pinned memories
  - Filter option in search: "Favorites only" toggle
  - Favorited memories sort to top when "Favorites first" sort option is active
  - Subtle animation on star toggle (scale bounce)
- New files:
  - `frontend/src/components/FavoriteButton.vue`
  - `frontend/src/components/FavoritesPanel.vue`

**Acceptance Criteria**:
- AC-F63-1: Click star icon on a memory card toggles favorite status
- AC-F63-2: Favorited memories appear in sidebar "⭐ Favorites" panel
- AC-F63-3: Favorite status persists across page refresh
- AC-F64-4: "Favorites first" sort option pins starred items to top
- AC-F63-5: Star icon visual state correctly reflects favorite status
- AC-F63-6: Favorites panel shows memory title and allows click-to-navigate

**Dependencies**: None (standalone feature)

---

### F-64 — Saved Searches & Smart Collections

**Problem**: Users repeatedly perform the same searches (e.g., "all bug memories from last month", "high-strength patterns", "memories tagged with deployment"). They have to re-type queries each time. There's no way to create dynamic groups that auto-update.

**Solution**: Save search queries as named "Smart Collections" that automatically update their contents as memories change — like smart playlists for memories.

**Implementation**:
- Backend: New `backend/app/services/collections_service.py`
  - Collection schema:
    ```json
    {
      "id": "col_abc123",
      "name": "Recent Bugs",
      "description": "Bug-type memories from the last 30 days",
      "query": {"type": "bug", "date_range": "30d"},
      "icon": "🐛",
      "color": "#ff3b30",
      "created_at": "2026-05-29T10:00:00Z",
      "memory_count": 12,
      "last_evaluated": "2026-05-29T10:05:00Z"
    }
    ```
  - Query types supported: type filter, strength range, date range, concept tags, text search, profile filter
  - Evaluation: lazy evaluation on access + periodic refresh (every 5 minutes via cache)
  - New endpoints:
    - `GET /api/collections` → list all saved collections
    - `POST /api/collections` → create collection `{name, description, query, icon?, color?}`
    - `PUT /api/collections/{id}` → update collection
    - `DELETE /api/collections/{id}` → delete collection
    - `GET /api/collections/{id}/memories` → get memories matching collection query
    - `POST /api/collections/evaluate-all` → force re-evaluation of all collections
  - Storage: `backend/cache/collections.json`
- Frontend:
  - New sidebar section: "📁 Collections" below Favorites
  - Each collection shows name, icon, memory count badge
  - Click collection → filtered memory view
  - "Save as Collection" button on search results (convert current search to collection)
  - Collection editor modal: name, description, icon picker, color picker, query builder
  - Pre-built templates: "Recent (7 days)", "High Priority (strength ≥ 8)", "Untagged", "All Bugs"
- New files:
  - `frontend/src/views/CollectionsView.vue`
  - `frontend/src/components/CollectionCard.vue`
  - `frontend/src/components/CollectionEditor.vue`

**Acceptance Criteria**:
- AC-F64-1: Create a collection with type+date filter, memories correctly matched
- AC-F64-2: Collection memory count updates when new memories are added
- AC-F64-3: "Save as Collection" from search results creates valid collection
- AC-F64-4: Collection editor supports at least 4 query dimensions (type, date, strength, text)
- AC-F64-5: Pre-built templates create working collections
- AC-F64-6: Collections persist across server restarts

**Dependencies**: None (uses existing search/filter infrastructure)

---

### F-65 — Memory Linking & Relation Graph

**Problem**: The existing concept co-occurrence analysis (P9 F-62 Cross-Agent Insights) finds implicit relationships, but users often know explicit relationships between memories that the system can't detect automatically. E.g., "this bug was caused by that pattern" or "this workflow depends on that architecture decision."

**Solution**: Manual memory linking with typed relationships, visualized as an interactive graph.

**Implementation**:
- Backend: New `backend/app/services/linking_service.py`
  - Link schema:
    ```json
    {
      "id": "link_abc123",
      "source_id": "mem_xxx",
      "target_id": "mem_yyy",
      "relation_type": "caused_by|depends_on|related_to|supersedes|contradicts",
      "label": "optional description",
      "created_at": "2026-05-29T10:00:00Z",
      "created_by": "user"
    }
    ```
  - New endpoints:
    - `GET /api/links` → list all links (with optional filters: source_id, target_id, type)
    - `POST /api/links` → create link `{source_id, target_id, relation_type, label?}`
    - `DELETE /api/links/{id}` → remove link
    - `GET /api/links/graph` → full graph data `{nodes: [...], edges: [...]}` for visualization
    - `GET /api/links/graph/{memory_id}` → subgraph centered on a specific memory
  - Storage: `backend/cache/memory_links.json`
  - Graph computation: nodes = memories, edges = links, with optional embedding-based implicit edges
- Frontend:
  - New view: `frontend/src/views/GraphView.vue`
    - Force-directed graph visualization (using D3.js force simulation or vis-network)
    - Nodes colored by memory type, sized by strength
    - Edges colored by relation type with labels
    - Click node → show memory details panel
    - Drag to rearrange, zoom/pan
    - Filter by relation type
  - Memory detail view: "Related Memories" section showing linked memories
  - "Link to..." action on memory cards (opens memory picker)
  - Sidebar entry: "🔗 Graph" under Intelligence section
- New files:
  - `frontend/src/views/GraphView.vue`
  - `frontend/src/components/RelationGraph.vue`
  - `frontend/src/components/LinkCreator.vue`
  - `frontend/src/components/RelatedMemories.vue`

**Acceptance Criteria**:
- AC-F65-1: Create a link between two memories with a relation type
- AC-F65-2: Graph view shows all memories and links as interactive nodes/edges
- AC-F65-3: Click a graph node shows memory details
- AC-F65-4: Relation types visually distinguishable (color-coded edges)
- AC-F65-5: "Link to..." action on memory card opens picker and creates link
- AC-F65-6: Graph is interactive: zoom, pan, drag nodes
- AC-F65-7: Subgraph view shows only neighbors of a selected memory

**Dependencies**: None (standalone; complements P9 F-62 Cross-Agent Insights)

---

### F-66 — Guided Onboarding Tour

**Problem**: New users face a feature-rich interface with 15+ sidebar items, multiple views, keyboard shortcuts, and AI-powered features. Without guidance, they may miss core features or feel overwhelmed.

**Solution**: An interactive step-by-step tour that highlights key features on first visit, with the ability to replay at any time.

**Implementation**:
- Frontend only (no backend changes)
- New composable: `frontend/src/composables/useOnboarding.ts`
  - Tour state: current step, completed steps, tour active/inactive
  - Persisted in localStorage: `mv_onboarding_completed: boolean`
  - Auto-trigger on first visit (if not completed)
  - Replay available via Command Palette or Settings
- Tour steps:
  1. Welcome overlay: "Welcome to Memory Viewer v2! Let's take a quick tour."
  2. Search bar: "Search across all your memories with keywords, semantic search, or natural language."
  3. Tab bar: "Switch between AgentMemory and Hermes Memory views."
  4. Memory card: "Click to expand details. Star to favorite. Use bulk select for batch operations."
  5. Sidebar navigation: "Explore clusters, timeline, graph, and AI-powered insights."
  6. Command palette: "Press ⌘K for instant access to any feature."
  7. Keyboard shortcuts: "Press ? to see all keyboard shortcuts."
  8. Completion: "You're all set! Explore and manage your agent's memories."
- New components:
  - `frontend/src/components/OnboardingTour.vue` — overlay with step highlight + tooltip
  - `frontend/src/components/TourTooltip.vue` — individual step tooltip with next/skip buttons
- Implementation approach: CSS highlight (box-shadow overlay) on target element + positioned tooltip
- Tour highlight: target element gets z-index boost + white border, rest gets dark overlay
- Navigation: Next / Previous / Skip Tour / Close buttons
- Responsive: adapts tooltip position for mobile viewports

**Acceptance Criteria**:
- AC-F66-1: Tour auto-starts on first visit to the application
- AC-F66-2: Each step highlights the relevant UI element with overlay
- AC-F66-3: "Next" / "Previous" buttons navigate between steps
- AC-F66-4: "Skip Tour" dismisses the tour entirely
- AC-F66-5: Tour completion recorded in localStorage; doesn't auto-start again
- AC-F66-6: Tour can be replayed from Command Palette or settings
- AC-F66-7: Tour tooltips are readable and positioned correctly on screen

**Dependencies**: None (standalone UX feature)

---

### F-67 — Advanced Export & Reporting

**Problem**: The existing export (P0 F-09) dumps raw JSON or Markdown, but users need formatted reports to share with stakeholders — weekly memory summaries, type distribution reports, health overviews — in PDF or HTML format with branding and structure.

**Solution**: A report generation engine that creates styled PDF/HTML reports from memory data using customizable templates.

**Implementation**:
- Backend: New `backend/app/services/report_service.py`
  - Report templates:
    1. **Memory Inventory**: Full list of memories grouped by type with metadata
    2. **Weekly Summary**: Memories created/updated in the past week with highlights
    3. **Type Distribution**: Statistical breakdown with charts (rendered server-side)
    4. **Health Report**: Strength distribution, staleness analysis, PII findings
    5. **Custom**: User-selectable sections and filters
  - Report generation:
    - Collect data based on template + filters
    - Render to HTML using Jinja2 templates
    - Convert HTML to PDF using `weasyprint` or `playwright` (headless browser)
    - Include charts as inline SVG (using matplotlib server-side or pre-rendered from frontend)
  - New endpoints:
    - `GET /api/reports/templates` → list available report templates
    - `POST /api/reports/generate` → generate report `{template, filters?, format: "html"|"pdf", title?}`
    - `GET /api/reports/{id}` → download generated report
    - `GET /api/reports/history` → list past generated reports
  - Storage: `backend/cache/reports/` directory
- Frontend:
  - New view: `frontend/src/views/ReportsView.vue`
  - Template selector with preview thumbnails
  - Filter configuration: date range, memory types, profiles
  - Format selector: HTML (preview in browser) or PDF (download)
  - Report history: list of previously generated reports with download links
  - "Generate Report" button with loading indicator
  - Sidebar entry: "📊 Reports" under Analytics section
- New files:
  - `frontend/src/views/ReportsView.vue`
  - `frontend/src/components/ReportTemplateCard.vue`
  - `frontend/src/components/ReportConfigurator.vue`
  - `backend/app/templates/` (Jinja2 HTML templates for reports)

**Acceptance Criteria**:
- AC-F67-1: Generate a "Memory Inventory" report in HTML format
- AC-F67-2: Generate a "Weekly Summary" report in PDF format
- AC-F67-3: Report includes memory data, statistics, and charts
- AC-F67-4: Custom filters (date range, type) applied to report content
- AC-F67-5: Generated reports downloadable from history list
- AC-F67-6: Report generation completes in <15s for 200 memories

**Dependencies**: P0 F-09 (Export — basic export infrastructure)

---

### F-68 — Memory Health Scanner

**Problem**: Over time, memory quality degrades: some memories have empty concepts, very low strength, duplicate content, stale information, or broken references. There's no automated way to identify and fix these issues.

**Solution**: A proactive health scanner that analyzes memory quality, identifies issues, and provides actionable recommendations with one-click fixes.

**Implementation**:
- Backend: New `backend/app/services/health_scanner_service.py`
  - Health checks:
    1. **Empty Metadata**: Memories missing concepts, title, or with default strength
    2. **Stale Memories**: Memories not updated in 90+ days with low strength
    3. **Duplicate Detection**: Memories with >90% content similarity (uses P8 embeddings)
    4. **Orphaned Concepts**: Concepts referenced by only 1 memory (typos or dead tags)
    5. **Strength Distribution**: Anomaly in strength distribution (all same value, all low, etc.)
    6. **PII Exposure**: Memories flagged by P9 redaction service
    7. **Broken Links**: Links (F-65) pointing to deleted memories
  - Health score: 0-100, computed as weighted average of check results
  - New endpoints:
    - `GET /api/health-scan` → run full health scan, return results
    - `GET /api/health-scan/summary` → quick summary (score + issue count)
    - `POST /api/health-scan/fix/{issue_id}` → auto-fix a specific issue
    - `GET /api/health-scan/history` → past scan results
  - Auto-fix capabilities:
    - Empty concepts → trigger AI auto-tagging (P8 F-34)
    - Duplicates → suggest merge with preview
    - Orphaned concepts → suggest removal
    - Stale low-strength → suggest archive (P2 F-15)
  - Storage: `backend/cache/health_scans/` directory
- Frontend:
  - New view: `frontend/src/views/HealthScanView.vue`
  - Health score gauge (circular progress, color-coded: green >80, yellow 50-80, red <50)
  - Issue categories as cards with severity badges (🔴 Critical, 🟡 Warning, 🟢 Info)
  - Each issue shows: description, affected memories count, "Fix" button
  - "Run Scan" button with progress indicator
  - Scan history timeline
  - Dashboard widget: health score summary card
  - Sidebar entry: "🏥 Health" under Operations section
- New files:
  - `frontend/src/views/HealthScanView.vue`
  - `frontend/src/components/HealthScoreGauge.vue`
  - `frontend/src/components/IssueCard.vue`
  - `frontend/src/components/ScanHistory.vue`

**Acceptance Criteria**:
- AC-F68-1: Health scan identifies memories with empty concepts
- AC-F68-2: Health scan detects duplicate memories (>90% similarity)
- AC-F68-3: Health score correctly computed as 0-100
- AC-F68-4: "Fix" button for empty concepts triggers auto-tagging
- AC-F68-5: Scan completes in <10s for 200 memories
- AC-F68-6: Health score gauge visually reflects severity
- AC-F68-7: Scan history shows past results with timestamps

**Dependencies**: P8 F-33 (Embedding Service — for duplicate detection), P8 F-34 (AI Auto-Tagging — for auto-fix), P9 F-41 (PII Redaction — for PII check)

---

## Implementation Order

### Week 1: Quick Wins & Organization
1. **F-63 Memory Favorites** — lightweight, frontend-heavy, immediate UX value
2. **F-66 Guided Onboarding** — frontend-only, no backend changes, quick to implement

### Week 2: Smart Organization
3. **F-64 Saved Searches & Smart Collections** — backend + frontend, moderate complexity
4. **F-65 Memory Linking & Graph** — backend + frontend with visualization

### Week 3: Intelligence & Reporting
5. **F-67 Advanced Export & Reporting** — backend-heavy with template rendering
6. **F-68 Memory Health Scanner** — leverages multiple existing services

### Week 4: Integration Testing & Polish
- Cross-feature integration testing
- Performance testing
- Documentation updates
- Bug fixes

---

## Dependency Graph

```
F-63 (Favorites) ──────────── standalone
F-64 (Smart Collections) ──── standalone (uses existing search infra)
F-65 (Memory Linking) ─────── standalone (complements P9 F-62)
F-66 (Onboarding Tour) ────── standalone (frontend-only)
F-67 (Export & Reporting) ─── depends on P0 F-09 (basic export)
F-68 (Health Scanner) ──────── depends on P8 F-33 (embeddings), P8 F-34 (AI tagging), P9 F-41 (PII)
```

---

## Technical Impact

| Feature | Backend Changes | Frontend Changes | New Files |
|---------|----------------|-----------------|-----------|
| F-63 | favorites.json storage, PUT toggle endpoint | FavoriteButton, FavoritesPanel | 3 |
| F-64 | collections_service.py, collections router | CollectionsView, CollectionCard, CollectionEditor | 4 |
| F-65 | linking_service.py, links router | GraphView, RelationGraph, LinkCreator, RelatedMemories | 5 |
| F-66 | none | OnboardingTour, TourTooltip, useOnboarding | 3 |
| F-67 | report_service.py, report templates, reports router | ReportsView, ReportTemplateCard, ReportConfigurator | 5 |
| F-68 | health_scanner_service.py, health-scan router | HealthScanView, HealthScoreGauge, IssueCard, ScanHistory | 5 |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Graph visualization performance with 200+ nodes | Medium | Medium | Use canvas renderer; limit initial view to 50 nodes with expand option |
| PDF generation dependency (weasyprint) heavy | Medium | Low | Fall back to HTML-only if weasyprint unavailable; use print-to-PDF as alternative |
| Health scan slow with embedding-based duplicate detection | Medium | Medium | Cache embeddings; run duplicate check async with progress indicator |
| Smart collection query complexity | Low | Medium | Limit to predefined query dimensions; no arbitrary expressions |
| Onboarding tour breaks with UI changes | Low | Low | Use data attributes for targeting; easy to update steps |

---

## Acceptance Test Plan

### Smoke Tests
- F-63: Star a memory → appears in favorites panel → unstar removes it
- F-64: Create collection with type filter → memories match → new memory auto-included
- F-65: Link two memories → graph shows edge → click navigates
- F-66: First visit → tour starts → complete tour → doesn't restart
- F-67: Generate HTML report → contains correct memory data → downloadable
- F-68: Run health scan → score displayed → fix empty concepts → score improves

### Regression Tests
- All existing CRUD operations unaffected
- Search, sort, filter all work correctly
- Favorites don't interfere with normal memory listing
- Collections don't modify underlying memory data
- Links are independent of memory content
- Report generation doesn't block API responses

### Performance Tests
- Favorites toggle: < 100ms
- Collection evaluation: < 2s for 200 memories
- Graph rendering: < 3s for 100 nodes + 200 edges
- Report generation: < 15s for 200 memories
- Health scan: < 10s for 200 memories
- Onboarding tour: < 50ms per step transition
