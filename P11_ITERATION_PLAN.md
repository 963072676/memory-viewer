# P11 Iteration Plan — Intelligent Insights, Developer Tools & Team Readiness

> **Phase**: P11
> **Date**: 2026-05-29
> **Theme**: AI-Powered Insights, Developer Experience & Enterprise Foundations
> **Total Features**: 6 (F-51 through F-56)
> **Estimated Effort**: 3-4 weeks

---

## P11 Features Overview

| # | Feature | Description | Complexity | Layer |
|---|---------|-------------|------------|-------|
| F-51 | AI Memory Digest | LLM-generated daily/weekly digest summarizing memory changes, trends, and insights | 🟡 Medium | Backend + Frontend |
| F-52 | Memory Templates | Predefined structured templates for creating consistent, typed memories | 🟢 Low | Backend + Frontend |
| F-53 | RAG-Powered Search Responses | Search returns LLM-synthesized answers using retrieval-augmented generation | 🟠 High | Backend + Frontend |
| F-54 | Team Workspaces & RBAC | Multi-user workspaces with role-based access control (admin, editor, viewer) | 🟠 High | Backend + Frontend |
| F-55 | Real-time Updates | WebSocket-based live updates for memory changes with presence indicators | 🟡 Medium | Backend + Frontend |
| F-56 | Bulk CLI Tool | Command-line interface and Python SDK for bulk memory operations | 🟡 Medium | CLI/SDK |

---

## Feature Details

### F-51 — AI Memory Digest

**Problem**: Users have no way to get a high-level overview of what changed in their memory base over time. Reviewing hundreds of memories manually is impractical. There's no automated way to surface emerging patterns, new knowledge areas, or significant changes.

**Solution**: LLM-powered digest generation that summarizes memory activity into readable reports — daily, weekly, or on-demand.

**Implementation**:
- Backend: New `backend/app/services/digest_service.py`
  - Digest generation: collect memories created/updated in time window → group by cluster/tag → LLM summarization per group → compose digest report
  - Digest types: daily (last 24h), weekly (last 7d), custom range
  - Digest sections: "New Memories" (count + highlights), "Top Changes" (most edited), "Emerging Themes" (new clusters/tags), "Health Alerts" (conflicts, low-strength memories)
  - LLM prompt template for summarization with configurable tone (brief/detailed)
  - Storage: generated digests cached in `backend/cache/digests/` as JSON files
  - New endpoints:
    - `POST /api/digest/generate` → generate digest for a time range `{period: "daily"|"weekly"|"custom", from, to}`
    - `GET /api/digest/latest` → get most recent digest
    - `GET /api/digest/history` → list past digests
    - `GET /api/digest/{id}` → get specific digest
  - Scheduled generation: integrate with P10 workflow scheduler for automatic daily/weekly digests
- Frontend: New `frontend/src/views/DigestView.vue`
  - Digest card layout with sections: summary stats, theme highlights, notable changes
  - Period selector (daily/weekly/custom)
  - "Generate Now" button for on-demand digests
  - Digest history sidebar with date navigation
  - Markdown-rendered digest content
  - Sidebar entry: "📋 Digest" under Intelligence section
- New component: `frontend/src/components/DigestCard.vue`
- New component: `frontend/src/components/DigestTimeline.vue`

**Acceptance Criteria**:
- AC-F51-1: POST /api/digest/generate creates a digest for the specified period
- AC-F52-2: Digest includes summary stats (new count, updated count, top themes)
- AC-F51-3: LLM generates coherent, relevant summaries grouped by theme
- AC-F51-4: Digest history is browsable with date navigation
- AC-F51-5: Digest generation completes within 15s for 200 memories
- AC-F51-6: Scheduled digests integrate with workflow engine

**Dependencies**: P8 F-34 (LLM Service), P10 F-47 (Workflow Automation), P6 F-37 (Clustering)

---

### F-52 — Memory Templates

**Problem**: Users create memories with inconsistent structure — some have rich metadata, others are bare text. This inconsistency degrades search quality, clustering accuracy, and makes it hard to build reliable automations.

**Solution**: A template system that provides predefined schemas for common memory types, guiding users to create well-structured memories.

**Implementation**:
- Backend: New `backend/app/services/template_service.py`
  - Template schema: `{id, name, description, icon, fields: [{key, label, type: "text"|"select"|"tags"|"number"|"date", required, default, options}], created_at, is_system}`
  - Built-in templates:
    - "User Preference" — preference_key, preference_value, confidence, source
    - "Conversation Summary" — participants, topic, key_points[], outcome
    - "Task Result" — task_name, status, result, duration, lessons_learned
    - "Learning Insight" — domain, insight, evidence, confidence_level
    - "Error/Failure" — error_type, context, root_cause, resolution
  - User-defined custom templates (CRUD)
  - Template validation on memory creation
  - New endpoints:
    - `GET /api/templates` → list all templates (system + custom)
    - `POST /api/templates` → create custom template
    - `PUT /api/templates/{id}` → update template
    - `DELETE /api/templates/{id}` → delete custom template (system templates immutable)
    - `POST /api/templates/{id}/create-memory` → create memory from template
  - Storage: `backend/cache/templates.json`
- Frontend: New `frontend/src/views/TemplatesView.vue`
  - Template gallery with card grid layout (icon, name, description, field count)
  - "Use Template" button opens memory creation form pre-filled with template fields
  - Template editor for creating custom templates (drag-and-drop field ordering)
  - System templates marked with badge, cannot be deleted
  - New component: `frontend/src/components/TemplateCard.vue`
  - New component: `frontend/src/components/TemplateEditor.vue`
  - New component: `frontend/src/components/TemplateForm.vue`
  - Integration: "Create from Template" option added to existing memory creation flow

**Acceptance Criteria**:
- AC-F52-1: 5 built-in system templates available on first load
- AC-F52-2: Can create custom template with multiple field types
- AC-F52-3: Creating memory from template pre-fills structured fields
- AC-F52-4: Template validation prevents missing required fields
- AC-F52-5: System templates cannot be edited or deleted
- AC-F52-6: Template-created memories include template_id in metadata

**Dependencies**: P0 F-07 (Memory Create/Edit)

---

### F-53 — RAG-Powered Search Responses

**Problem**: Current search (semantic and NLQ) returns ranked lists of matching memories. Users must read through results and synthesize answers themselves. For knowledge queries, users expect an answer, not a list.

**Solution**: A RAG (Retrieval-Augmented Generation) mode where search queries are answered by an LLM that synthesizes information from retrieved memories, citing sources.

**Implementation**:
- Backend: New `backend/app/services/rag_service.py`
  - Pipeline: query → semantic search (top-K=10) → LLM synthesis with citations → structured response
  - Response format: `{answer: string, sources: [{memory_id, snippet, relevance_score}], confidence: float, follow_up_questions: string[]}`
  - Confidence scoring: based on source agreement and relevance scores
  - Follow-up question generation: LLM suggests 2-3 follow-up queries
  - Streaming support: SSE (Server-Sent Events) for real-time answer generation
  - Citation format: inline `[1]` references linking to source memories
  - New endpoints:
    - `POST /api/search/rag` → RAG search `{query, max_sources?, stream?}`
    - `GET /api/search/rag/stream` → SSE stream for RAG responses
  - Token budget: configurable max tokens for synthesis (default 500)
- Frontend:
  - New "AI Answer" toggle on search bar (switches between list mode and RAG mode)
  - RAG response card: synthesized answer with inline citations
  - Clickable citations expand to show source memory snippet
  - Confidence indicator (color-coded bar)
  - Follow-up question chips (clickable to re-query)
  - Loading animation during LLM synthesis
  - New component: `frontend/src/components/RagResponse.vue`
  - New component: `frontend/src/components/RagCitation.vue`

**Acceptance Criteria**:
- AC-F53-1: POST /api/search/rag returns synthesized answer with sources
- AC-F53-2: Citations link to specific source memory IDs
- AC-F53-3: Confidence score reflects source quality and agreement
- AC-F53-4: Follow-up questions are contextually relevant
- AC-F53-5: SSE streaming shows progressive answer generation
- AC-F53-6: Response time < 5s for typical queries (10 source memories)

**Dependencies**: P8 F-33 (Semantic Search), P8 F-34 (LLM Service)

---

### F-54 — Team Workspaces & RBAC

**Problem**: Memory Viewer assumes a single user. In team settings, multiple people or agents share the same memory base but there's no access control — everyone can read, edit, or delete everything. There's no way to partition memories by team or project.

**Solution**: Workspace-based multi-tenancy with role-based access control. Users belong to workspaces, each workspace owns memories, and roles govern permissions.

**Implementation**:
- Backend: New `backend/app/services/workspace_service.py`
  - Data model:
    - Workspace: `{id, name, description, created_at, owner_id, settings}`
    - Membership: `{workspace_id, user_id, role: "admin"|"editor"|"viewer", joined_at}`
    - Memory → workspace_id foreign key (default workspace for backward compatibility)
  - Roles & permissions:
    - Admin: full CRUD on workspace settings, members, and all memories
    - Editor: CRUD on memories, read workspace settings
    - Viewer: read-only access to memories
  - API key-based authentication (existing webhook API key pattern extended)
  - Migration: existing memories assigned to "default" workspace
  - New endpoints:
    - `GET /api/workspaces` → list workspaces for current user
    - `POST /api/workspaces` → create workspace
    - `PUT /api/workspaces/{id}` → update workspace
    - `DELETE /api/workspaces/{id}` → delete workspace (admin only)
    - `GET /api/workspaces/{id}/members` → list members
    - `POST /api/workspaces/{id}/members` → add member with role
    - `PUT /api/workspaces/{id}/members/{user_id}` → update member role
    - `DELETE /api/workspaces/{id}/members/{user_id}` → remove member
  - Storage: `backend/cache/workspaces.json`, `backend/cache/memberships.json`
  - Middleware: `backend/app/middleware/workspace_context.py` — extracts workspace from header/query param
- Frontend: New `frontend/src/views/WorkspacesView.vue`
  - Workspace switcher in top navigation bar
  - Workspace management page: create, edit, delete workspaces
  - Member management: invite by name/key, assign roles, remove
  - Role badges on member list (Admin 🛡️, Editor ✏️, Viewer 👁️)
  - Workspace-scoped memory counts and stats
  - New component: `frontend/src/components/WorkspaceSwitcher.vue`
  - New component: `frontend/src/components/MemberManager.vue`
  - New component: `frontend/src/components/RoleBadge.vue`

**Acceptance Criteria**:
- AC-F54-1: Can create workspace and assign it a name
- AC-F54-2: Members can be added with admin/editor/viewer roles
- AC-F54-3: Viewers cannot create, edit, or delete memories (403 response)
- AC-F54-4: Editors can CRUD memories but not manage workspace settings
- AC-F54-5: Admins have full access to workspace and member management
- AC-F54-6: Existing memories assigned to "default" workspace automatically
- AC-F54-7: Workspace switcher filters memories to selected workspace

**Dependencies**: None (standalone, extends existing API key pattern)

---

### F-55 — Real-time Updates

**Problem**: When multiple users or agents modify memories, others see stale data until they manually refresh. There's no way to know if someone else is viewing or editing the same memory. The auto-refresh polling (P2) is wasteful and introduces latency.

**Solution**: WebSocket-based real-time updates that push memory changes, presence indicators, and live collaboration signals.

**Implementation**:
- Backend: New `backend/app/services/realtime_service.py`
  - WebSocket endpoint: `ws://host/ws/memories` — broadcasts memory events
  - Event types: `memory.created`, `memory.updated`, `memory.deleted`, `memory.archived`, `user.presence`
  - Presence tracking: which users are viewing which memory (heartbeat-based)
  - Connection management: per-workspace channels (F-54 integration)
  - Fallback: SSE endpoint for environments that don't support WebSocket
  - New endpoints:
    - `WS /ws/memories` — WebSocket connection (query param: workspace_id)
    - `GET /api/realtime/status` — connection count, active users
  - Heartbeat: 30s interval to detect stale connections
  - Event bus: in-memory pub/sub for broadcasting (no external dependencies)
- Frontend:
  - WebSocket connection manager: auto-reconnect, exponential backoff
  - Real-time memory list: new/updated/deleted memories appear/disappear without refresh
  - Presence indicators: "X users viewing" badge on memory detail
  - Live edit indicator: pulsing dot when another user is editing a memory
  - Toast notifications for real-time events (non-intrusive, auto-dismiss)
  - Connection status indicator in header (🟢 connected, 🟡 reconnecting, 🔴 disconnected)
  - New composable: `frontend/src/composables/useWebSocket.ts`
  - New component: `frontend/src/components/PresenceIndicator.vue`
  - New component: `frontend/src/components/ConnectionStatus.vue`

**Acceptance Criteria**:
- AC-F55-1: WebSocket connection established on page load
- AC-F55-2: New memory created by one user appears in another user's list instantly
- AC-F55-3: Deleted memory disappears from all connected clients
- AC-F55-4: Presence indicator shows number of viewers on a memory
- AC-F55-5: Auto-reconnect with backoff on connection loss
- AC-F55-6: Connection status visible in header
- AC-F55-7: Events scoped to workspace when workspaces are active

**Dependencies**: P2 F-12 (Auto Refresh — this replaces polling), F-54 (Workspaces — optional scope)

---

### F-56 — Bulk CLI Tool

**Problem**: Power users and automation pipelines need to interact with Memory Viewer at scale — importing thousands of memories, running batch operations, or integrating into CI/CD. The web UI doesn't support these workflows, and raw API calls are tedious.

**Solution**: A standalone CLI tool and Python SDK that wraps the Memory Viewer API for bulk operations and scripting.

**Implementation**:
- Backend: No new backend endpoints needed (uses existing API)
  - Documentation endpoint: `GET /api/cli/manifest` → returns CLI capabilities and endpoint map
- CLI Tool: New `tools/mv-cli/` directory
  - Python-based CLI using `click` library
  - Commands:
    - `mv import <file>` — bulk import from JSON/CSV/Markdown
    - `mv export --format json|csv|md --output <file>` — bulk export
    - `mv search <query> [--semantic] [--rag]` — search from CLI
    - `mv list [--tag <tag>] [--type <type>] [--limit N]` — list memories with filters
    - `mv tag <ids...> --add <tag>` — bulk add tags
    - `mv archive <ids...>` — bulk archive
    - `mv delete <ids...> [--confirm]` — bulk delete with confirmation
    - `mv stats` — show memory statistics
    - `mv digest [--period daily|weekly]` — generate and display digest
    - `mv config set <key> <value>` — configure API endpoint, API key
  - Config: `~/.mv-cli/config.json` for API URL and API key
  - Output formats: table (default), JSON, CSV
  - Progress bars for bulk operations using `rich` library
- Python SDK: New `tools/mv-sdk/` directory
  - `memory_viewer` Python package with typed client
  - Classes: `MemoryClient`, `Memory`, `SearchResult`, `Digest`
  - Async support via `httpx`
  - Example usage:
    ```python
    from memory_viewer import MemoryClient
    client = MemoryClient(api_url="http://localhost:8000", api_key="...")
    results = client.search("user preferences", semantic=True)
    client.import_memories("memories.json")
    ```
- New files:
  - `tools/mv-cli/mv_cli/main.py` — CLI entry point
  - `tools/mv-cli/mv_cli/commands/` — command modules
  - `tools/mv-cli/setup.py` — package setup
  - `tools/mv-sdk/memory_viewer/__init__.py` — SDK package
  - `tools/mv-sdk/memory_viewer/client.py` — API client
  - `tools/mv-sdk/memory_viewer/models.py` — data models

**Acceptance Criteria**:
- AC-F56-1: `mv import` handles JSON, CSV, and Markdown formats
- AC-F56-2: `mv search` returns formatted results with semantic option
- AC-F56-3: `mv tag` applies tags to multiple memories in one operation
- AC-F56-4: Progress bar shown for operations on >10 memories
- AC-F56-5: SDK `MemoryClient` supports all core CRUD operations
- AC-F56-6: SDK supports async usage with `httpx.AsyncClient`
- AC-F56-7: CLI config persists API URL and key across sessions

**Dependencies**: Existing API endpoints (all CRUD, search, import/export)

---

## Implementation Order

### Week 1: Foundation & Templates
1. **F-52 Memory Templates** — lightweight, self-contained, immediate user value
2. **F-54 Team Workspaces & RBAC** — backend-heavy, foundational for F-55

### Week 2: Intelligence Layer
3. **F-51 AI Memory Digest** — leverages LLM infrastructure, medium complexity
4. **F-53 RAG-Powered Search** — extends semantic search with LLM synthesis

### Week 3: Real-time & Developer Tools
5. **F-55 Real-time Updates** — WebSocket infrastructure, integrates with F-54
6. **F-56 Bulk CLI Tool** — standalone tool, no backend changes

---

## Dependency Graph

```
F-52 (Templates) ──────────────────────────── standalone
F-54 (Workspaces) ─────────────────────────── standalone
F-51 (Digest) ──── depends on ── P8 LLM + P10 Workflows + P6 Clustering
F-53 (RAG) ─────── depends on ── P8 Semantic Search + P8 LLM
F-55 (Real-time) ─ depends on ── P2 Auto Refresh + F-54 Workspaces (optional)
F-56 (CLI) ─────── depends on ── existing API endpoints
```

## Technical Impact

| Feature | Backend Changes | Frontend Changes | New Files |
|---------|----------------|-----------------|-----------|
| F-51 | digest_service.py, router | DigestView, DigestCard, DigestTimeline | 4 |
| F-52 | template_service.py, router | TemplatesView, TemplateCard, TemplateEditor, TemplateForm | 5 |
| F-53 | rag_service.py, router | RagResponse, RagCitation, search bar integration | 3 |
| F-54 | workspace_service.py, router, middleware | WorkspacesView, WorkspaceSwitcher, MemberManager, RoleBadge | 5 |
| F-55 | realtime_service.py, WebSocket handler | useWebSocket, PresenceIndicator, ConnectionStatus | 4 |
| F-56 | cli manifest endpoint | none (CLI/SDK only) | 8 |

## New Dependencies

| Package | Purpose | Size | Used By |
|---------|---------|------|---------|
| websockets | WebSocket server support for FastAPI | ~100KB | F-55 |
| click | CLI framework | ~50KB | F-56 |
| rich | Terminal formatting, progress bars | ~200KB | F-56 |
| httpx | Async HTTP client for SDK | ~100KB | F-56 |
| python-multipart | Already used, for CLI file uploads | — | F-56 |

*No new frontend dependencies needed — existing WebSocket API in browser is native.*

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| RAG hallucination (inaccurate answers) | Medium | High | Include citations, confidence score, "verify sources" prompt |
| WebSocket scaling with many clients | Medium | Medium | Connection limits, heartbeats, graceful degradation to polling |
| Workspace migration breaking existing data | Low | High | Default workspace auto-assignment, backward-compatible API |
| LLM cost increase from digest/RAG | Medium | Medium | Token budgets, configurable generation, cache digests |
| CLI tool distribution complexity | Low | Low | PyPI package, single-file fallback |

## Acceptance Test Plan

### Smoke Tests
- F-51: Generate daily digest → contains summary and stats
- F-52: Create memory from "User Preference" template → structured fields populated
- F-53: RAG search "what does the user prefer?" → synthesized answer with citations
- F-54: Create workspace, add viewer, viewer gets 403 on memory edit
- F-55: Open two browser tabs, create memory in one → appears in other instantly
- F-56: `mv import test.json` → memories created via CLI

### Regression Tests
- All existing CRUD operations still work
- Search (semantic, NLQ) unaffected
- Existing workflows, conflicts, annotations fully functional
- Performance: API latency increase < 5ms
- Memory card rendering unchanged

### Performance Tests
- Digest generation: < 15s for 200 memories
- RAG search: < 5s response time
- WebSocket: handles 50 concurrent connections
- CLI bulk import: 1000 memories in < 60s
