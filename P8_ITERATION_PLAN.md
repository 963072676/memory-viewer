# P8 Iteration Plan — Next Generation

> **Phase**: P8
> **Date**: 2026-05-29
> **Theme**: AI-Powered Intelligence + Developer Experience
> **Total Features**: 6 (F-33 through F-38)
> **Estimated Effort**: 3-4 weeks

---

## P8 Features Overview

| # | Feature | Description | Complexity | Layer |
|---|---------|-------------|------------|-------|
| F-33 | Semantic Search | Vector-embedding-based search beyond keyword matching | 🟠 High | Backend + Frontend |
| F-34 | AI Auto-Tagging & Summarization | LLM-powered automatic tag generation and memory summarization | 🟠 High | Backend + Frontend |
| F-35 | Command Palette (⌘K) | Global command palette for instant navigation and actions | 🟡 Medium | Frontend |
| F-36 | Bulk Operations Toolbar | Multi-select memories with batch edit, tag, export, delete | 🟡 Medium | Frontend + Backend |
| F-37 | Memory Heatmap | Calendar heatmap showing memory creation/activity density | 🟡 Medium | Frontend + Backend |
| F-38 | Plugin System | Extensible plugin architecture for custom processors and visualizers | 🟠 High | Backend + Frontend |

---

## Feature Details

### F-33 — Semantic Search

**Problem**: Current search is keyword-only. Users searching "security concerns" won't find memories about "vulnerability" or "authentication issues".

**Solution**: Generate vector embeddings for all memories and support cosine-similarity search.

**Implementation**:
- Backend: New `backend/app/services/embedding_service.py`
  - Use sentence-transformers (all-MiniLM-L6-v2) for local embedding generation
  - Store embeddings in numpy `.npy` file alongside memory data
  - New endpoint: `GET /api/search/semantic?q=...&limit=10`
  - Fallback: if query has no embeddings match, fall back to keyword search
- Frontend: Extend search bar with toggle (keyword ↔ semantic)
  - Show similarity scores as percentage badges on results
  - Highlight "semantically matched" vs "keyword matched" differently
- Background task: Generate embeddings for new/updated memories on write

**Acceptance Criteria**:
- AC-F33-1: Searching "security" finds memories about "vulnerability", "authentication", "threat"
- AC-F33-2: Similarity score displayed as percentage (0-100%) on each result
- AC-F33-3: Toggle between keyword and semantic search in search bar
- AC-F33-4: Embeddings generated within 2s for a single memory
- AC-F33-5: Graceful degradation if embedding model unavailable (falls back to keyword)

**Dependencies**: `sentence-transformers`, `numpy`

---

### F-34 — AI Auto-Tagging & Summarization

**Problem**: Users manually enter tags/concepts and write summaries. With 100+ memories this is tedious and inconsistent.

**Solution**: LLM-powered auto-tagging on memory creation and one-click summarization.

**Implementation**:
- Backend: New `backend/app/services/llm_service.py`
  - Pluggable LLM provider (OpenAI API / local Ollama)
  - On memory create/update: generate 3-5 suggested tags from content
  - New endpoint: `POST /api/memories/{id}/suggest-tags` → returns suggested concepts
  - New endpoint: `POST /api/memories/{id}/summarize` → returns 1-2 sentence summary
  - New endpoint: `POST /api/memories/bulk-auto-tag` → batch process untagged memories
- Frontend: 
  - Auto-tag suggestions shown as chips in create/edit modal (click to accept)
  - "✨ Summarize" button on expanded memory view
  - Settings page: configure LLM provider, enable/disable auto-tagging
- Config: `LLM_PROVIDER` env var (openai|ollama|none), `LLM_API_KEY`, `LLM_MODEL`

**Acceptance Criteria**:
- AC-F34-1: Creating a memory shows AI-suggested tags that can be accepted/rejected
- AC-F34-2: "Summarize" generates a 1-2 sentence summary within 5s
- AC-F34-3: Bulk auto-tag processes all untagged memories with progress indicator
- AC-F34-4: Works without LLM configured (feature disabled gracefully)
- AC-F34-5: Suggested tags are relevant to memory content (>70% acceptance target)

**Dependencies**: `openai` (optional), `httpx` (for Ollama)

---

### F-35 — Command Palette (⌘K)

**Problem**: With 15+ views and many actions, navigation is slow. Power users need a fast keyboard-driven interface.

**Solution**: Spotlight/VSCode-style command palette triggered by ⌘K / Ctrl+K.

**Implementation**:
- Frontend: New `frontend/src/components/CommandPalette.vue`
  - Triggered by `⌘K` (Mac) / `Ctrl+K` (Windows/Linux)
  - Fuzzy search across: navigation items, recent memories, actions (create, export, backup)
  - Recent items shown by default
  - Keyboard navigation: ↑↓ to select, Enter to execute, Esc to close
  - Sections: "Actions", "Navigate", "Recent Memories", "Settings"
  - Backdrop blur overlay, centered modal, Apple-style design
- Commands include:
  - `Go to Dashboard`, `Go to Graph`, `Go to Timeline`, etc.
  - `Create Memory`, `Export All`, `Run Diagnostics`, `Backup Now`
  - `Search: {query}` — jumps to search with query pre-filled
  - `Toggle Dark Mode`, `Toggle Keyboard Shortcuts`

**Acceptance Criteria**:
- AC-F35-1: ⌘K/Ctrl+K opens command palette from any view
- AC-F35-2: Typing filters commands with fuzzy matching
- AC-F35-3: Enter executes selected command, Esc closes palette
- AC-F35-4: Recent memories appear in results and link to detail view
- AC-F35-5: Palette opens in <100ms, search results in <50ms
- AC-F35-6: Visually consistent with dark mode

---

### F-36 — Bulk Operations Toolbar

**Problem**: Users can only edit/delete memories one at a time. Managing 50+ memories requires tedious repetitive actions.

**Solution**: Multi-select with a floating toolbar for batch operations.

**Implementation**:
- Frontend:
  - Checkbox on each memory card (hidden until bulk mode active)
  - "Select" button in toolbar activates bulk mode
  - Floating action bar at bottom: shows count + action buttons
  - Actions: Delete Selected, Export Selected, Add Tag, Change Type, Archive
  - "Select All" / "Select None" toggle
  - Keyboard: `Shift+Click` for range select, `Cmd+A` for all
- Backend:
  - New `POST /api/agentmemory/bulk` endpoint for batch operations
  - Payload: `{ ids: [...], action: "delete"|"archive"|"tag"|"retag", params: {...} }`
  - Returns: `{ success: count, failed: count, errors: [...] }`
  - Audit log each bulk operation

**Acceptance Criteria**:
- AC-F36-1: Checkboxes appear when "Select" is clicked
- AC-F36-2: Can select multiple memories and batch delete with confirmation
- AC-F36-3: Batch tag: add a tag to all selected memories
- AC-F36-4: Batch export: download selected memories as JSON
- AC-F36-5: Progress indicator for operations on >10 items
- AC-F36-6: Bulk operations logged in audit trail
- AC-F36-7: Shift+Click selects range

---

### F-37 — Memory Activity Heatmap

**Problem**: The dashboard shows aggregate stats but lacks temporal granularity. Users can't see patterns in when memories are created/accessed.

**Solution**: GitHub-style calendar heatmap showing memory activity over the past year.

**Implementation**:
- Backend:
  - New endpoint: `GET /api/metrics/heatmap?metric=created|accessed|modified&days=365`
  - Returns: `{ "2026-01-15": 5, "2026-01-16": 12, ... }`
  - Aggregates from audit logs + memory timestamps
- Frontend:
  - New `frontend/src/components/ActivityHeatmap.vue`
  - GitHub-style grid: 52 columns × 7 rows
  - Color scale: light → dark (5 levels) based on activity count
  - Tooltip on hover: "12 memories created on Jan 15"
  - Toggle between: Created / Accessed / Modified metrics
  - Click a day → filters memory list to that date
  - Responsive: works on mobile with horizontal scroll
  - Integrated into DashboardView

**Acceptance Criteria**:
- AC-F37-1: Heatmap renders for past 365 days with correct color coding
- AC-F37-2: Hover shows tooltip with date and count
- AC-F37-3: Toggle between created/accessed/modified views
- AC-F37-4: Click a day navigates to filtered memory list for that date
- AC-F37-5: Responsive on screens ≥320px wide
- AC-F37-6: Dark mode compatible

---

### F-38 — Plugin System

**Problem**: Users want custom processing (e.g., auto-translate memories, custom health checks, specialized visualizations) without modifying core code.

**Solution**: File-based plugin system with hooks into memory lifecycle events.

**Implementation**:
- Backend:
  - New `backend/app/plugins/` directory with plugin loader
  - `backend/app/core/plugin_manager.py`:
    - Scans `plugins/` for Python files with `plugin.json` manifest
    - Manifest: `{ "name": "...", "version": "...", "hooks": ["on_memory_create", "on_memory_update", ...] }`
    - Hooks: `on_memory_create`, `on_memory_update`, `on_memory_delete`, `on_search`, `on_export`
    - Plugins run in isolated async tasks with timeout (5s default)
  - New endpoint: `GET /api/plugins` → list installed plugins + status
  - New endpoint: `POST /api/plugins/{name}/enable|disable`
  - Example plugin: `plugins/auto_translate/` — translates memory content to English
- Frontend:
  - New `frontend/src/views/PluginsView.vue`
  - List installed plugins with enable/disable toggle
  - Plugin detail: name, version, description, hooks, status
  - Log viewer: recent plugin execution logs
  - "Install Plugin" button (upload .zip or paste git URL)

**Acceptance Criteria**:
- AC-F38-1: Plugin in `plugins/` directory auto-discovered on startup
- AC-F38-2: `on_memory_create` hook fires when new memory is created
- AC-F38-3: Plugins can be enabled/disabled without restart
- AC-F38-4: Plugin execution timeout (5s) prevents hanging
- AC-F38-5: Plugin errors don't crash the main application
- AC-F38-6: UI shows plugin list, status, and recent logs
- AC-F38-7: Example auto_translate plugin works end-to-end

---

## Implementation Order

1. **Week 1**: F-35 (Command Palette) + F-36 (Bulk Operations) — UX polish, no new dependencies
2. **Week 2**: F-37 (Heatmap) + F-33 (Semantic Search) — data features
3. **Week 3**: F-34 (AI Auto-Tagging) + F-38 (Plugin System) — AI & extensibility
4. **Week 4**: Integration testing, bug fixes, documentation

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Embedding model too large for server | Medium | High | Use MiniLM (80MB); offer cloud embedding fallback |
| LLM API costs | Medium | Medium | Support local Ollama; cache results; make feature opt-in |
| Plugin security | Low | High | Sandboxed execution, timeout, no filesystem access outside plugin dir |
| Bulk operations on large datasets | Low | Medium | Process in batches of 50, show progress |

## New Dependencies

| Package | Purpose | Size |
|---------|---------|------|
| sentence-transformers | Embedding generation | ~80MB |
| numpy | Vector operations | ~15MB |
| openai | LLM API (optional) | ~1MB |
| httpx | Ollama HTTP client | ~1MB |
| rapidfuzz | Fuzzy search for command palette | ~2MB |
