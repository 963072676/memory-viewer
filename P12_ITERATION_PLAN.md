# P12 Iteration Plan — Enterprise Readiness, Resilience & Developer Productivity

> **Phase**: P12
> **Date**: 2026-05-29
> **Theme**: Enterprise Governance, Operational Resilience & Developer Productivity
> **Total Features**: 6 (F-57 through F-62)
> **Estimated Effort**: 3-4 weeks
> **Prerequisites**: P0-P11 completed (79 features total)

---

## P12 Design Principles

- **Enterprise hardening**: Production deployments demand SSO, governance, and compliance
- **Resilience first**: Disaster recovery and snapshot management ensure data safety at scale
- **Developer velocity**: API playground and interactive docs reduce integration friction
- **Cost awareness**: As LLM usage scales, visibility into token costs becomes critical
- **Build on existing infrastructure**: All features extend the FastAPI backend + Vue 3 frontend without architectural changes
- **Pragmatic scope**: Each feature is implementable in a single iteration

---

## P12 Features Overview

| # | Feature | Description | Complexity | Layer |
|---|---------|-------------|------------|-------|
| **F-57** | SSO / OIDC Integration | OpenID Connect-based single sign-on for enterprise authentication | 🟠 High | Backend + Frontend |
| **F-58** | Memory Governance Policies | Configurable rules for data retention, archival, and compliance enforcement | 🟡 Medium | Backend + Frontend |
| **F-59** | Disaster Recovery & Snapshot Management | Point-in-time snapshots, automated backups, and one-click restore | 🟡 Medium | Backend + Frontend |
| **F-60** | Interactive API Playground | In-browser API testing console with request builder, auth, and response viewer | 🟢 Low | Frontend |
| **F-61** | LLM Usage & Cost Dashboard | Track and visualize LLM token consumption, costs, and trends across features | 🟡 Medium | Backend + Frontend |
| **F-62** | Cross-Agent Knowledge Insights | Analyze memory overlap, gaps, and shared themes across agent profiles | 🟡 Medium | Backend + Frontend |

---

## Feature Details

### F-57 — SSO / OIDC Integration

**Problem**: Memory Viewer currently relies on API key authentication. Enterprise environments require integration with identity providers (Okta, Azure AD, Google Workspace, Keycloak) for centralized user management, MFA enforcement, and audit compliance.

**Solution**: OpenID Connect (OIDC) authentication layer that integrates with any standards-compliant identity provider, replacing or augmenting API key auth.

**Implementation**:
- Backend: New `backend/app/services/auth_service.py`
  - OIDC client implementation using `python-jose` for JWT verification
  - Configuration via environment variables:
    - `OIDC_ISSUER_URL` — identity provider issuer URL
    - `OIDC_CLIENT_ID` — registered client ID
    - `OIDC_CLIENT_SECRET` — client secret (optional for public clients)
    - `OIDC_REDIRECT_URI` — callback URL after authentication
  - Auth flow:
    1. Frontend redirects to `GET /api/auth/login` → OIDC provider
    2. Provider redirects back to `GET /api/auth/callback` with authorization code
    3. Backend exchanges code for tokens, verifies JWT, creates session
    4. Session stored as httpOnly secure cookie + optional JWT bearer token
  - Middleware: `backend/app/middleware/auth_middleware.py`
    - Extract user identity from session/JWT
    - Inject `user` context into requests
    - Skip auth for public endpoints (health, shared links)
  - User provisioning: auto-create local user record on first OIDC login
  - Role mapping: OIDC groups/claims → workspace roles (configurable mapping)
  - Fallback: API key authentication preserved for CLI/SDK usage (no breaking change)
  - New endpoints:
    - `GET /api/auth/login` → redirect to OIDC provider
    - `GET /api/auth/callback` → OIDC callback handler
    - `POST /api/auth/logout` → invalidate session
    - `GET /api/auth/me` → current user info
    - `GET /api/auth/providers` → list configured auth methods
- Frontend:
  - Login page with SSO button (branded per provider)
  - User profile dropdown in header (name, avatar, logout)
  - Auth guard for protected routes
  - Session persistence across page refreshes
  - New component: `frontend/src/components/LoginPage.vue`
  - New component: `frontend/src/components/UserProfile.vue`
  - New composable: `frontend/src/composables/useAuth.ts`

**Acceptance Criteria**:
- AC-F57-1: OIDC login flow completes successfully with a test provider (Keycloak)
- AC-F57-2: User info (name, email, avatar) displayed after login
- AC-F57-3: API key authentication still works for CLI/SDK (backward compatible)
- AC-F57-4: OIDC groups correctly mapped to workspace roles
- AC-F57-5: Logout invalidates session and redirects to login page
- AC-F57-6: Unauthenticated API requests return 401 with clear error
- AC-F57-7: OIDC disabled when env vars not configured (graceful fallback)

**Dependencies**: P11 F-54 (Team Workspaces & RBAC)

---

### F-58 — Memory Governance Policies

**Problem**: Enterprise teams need enforceable rules about memory lifecycle — how long memories are retained, when they must be archived, which types require approval before creation, and who can access sensitive data. Currently, all governance is manual and ad-hoc.

**Solution**: A policy engine that lets admins define rules for memory retention, archival, access control, and quality standards, with automated enforcement.

**Implementation**:
- Backend: New `backend/app/services/governance_service.py`
  - Policy schema:
    ```json
    {
      "id": "pol_retention_90d",
      "name": "90-Day Retention",
      "description": "Archive memories older than 90 days with strength < 5",
      "type": "retention",
      "conditions": [
        {"field": "age_days", "operator": "gt", "value": 90},
        {"field": "strength", "operator": "lt", "value": 5}
      ],
      "action": "archive",
      "enabled": true,
      "severity": "warning",
      "schedule": "daily"
    }
    ```
  - Policy types:
    - **Retention**: auto-archive or flag memories exceeding age thresholds
    - **Quality**: require minimum metadata (title length, concepts count, strength > 0)
    - **Access**: restrict memory types by workspace role
    - **Approval**: require admin approval for memories tagged as "critical" or "compliance"
  - Enforcement engine: scheduled evaluation (via P10 workflow scheduler) + real-time checks on create/update
  - Violation tracking: record policy violations with timestamps and affected memories
  - New endpoints:
    - `GET /api/governance/policies` → list all policies
    - `POST /api/governance/policies` → create policy
    - `PUT /api/governance/policies/{id}` → update policy
    - `DELETE /api/governance/policies/{id}` → delete policy
    - `POST /api/governance/policies/{id}/evaluate` → manually trigger evaluation
    - `GET /api/governance/violations` → list violations (with filters)
    - `GET /api/governance/compliance-report` → compliance summary
  - Storage: `backend/cache/governance_policies.json`, `backend/cache/governance_violations.jsonl`
- Frontend: New `frontend/src/views/GovernanceView.vue`
  - Policy list with toggle switches (enable/disable)
  - Policy editor: condition builder (field + operator + value)
  - Violation timeline with memory links
  - Compliance report: pie chart of compliant vs non-compliant memories
  - Sidebar entry: "📋 Governance" under Enterprise section
- New components:
  - `frontend/src/components/PolicyCard.vue`
  - `frontend/src/components/PolicyEditor.vue`
  - `frontend/src/components/ViolationTimeline.vue`
  - `frontend/src/components/ComplianceReport.vue`

**Acceptance Criteria**:
- AC-F58-1: Create a retention policy that archives memories older than 90 days
- AC-F58-2: Policy evaluation correctly identifies violating memories
- AC-F58-3: Quality policy flags memories missing required metadata
- AC-F58-4: Violations logged with timestamp, memory ID, and policy ID
- AC-F58-5: Compliance report shows percentage of compliant memories
- AC-F58-6: Policies can be enabled/disabled without deletion
- AC-F58-7: Manual "Evaluate Now" triggers immediate policy check

**Dependencies**: P11 F-54 (Workspaces — for role-based access policies), P10 F-47 (Workflow Automation — for scheduled evaluation)

---

### F-59 — Disaster Recovery & Snapshot Management

**Problem**: The current backup system (P5 F-30) provides basic export/import, but lacks point-in-time recovery, automated snapshot scheduling, and integrity verification. A data corruption event could require hours of manual recovery.

**Solution**: A comprehensive snapshot system that captures memory state at regular intervals, verifies integrity, and enables one-click restore to any point in time.

**Implementation**:
- Backend: New `backend/app/services/snapshot_service.py`
  - Snapshot format: compressed JSON with metadata
    ```json
    {
      "id": "snap_20260529_140000",
      "created_at": "2026-05-29T14:00:00Z",
      "type": "scheduled|manual|pre-restore",
      "memory_count": 156,
      "checksum_sha256": "abc123...",
      "size_bytes": 245678,
      "triggered_by": "system|user:admin",
      "tags": ["daily", "pre-governance-eval"]
    }
    ```
  - Snapshot storage: `backend/snapshots/` directory with rolling retention
  - Automated scheduling: configurable intervals (hourly/daily/weekly) via APScheduler
  - Retention policy: keep last N snapshots (configurable, default: 24 hourly + 7 daily + 4 weekly)
  - Integrity verification: SHA-256 checksum on creation and before restore
  - Restore workflow:
    1. Create "pre-restore" snapshot of current state (safety net)
    2. Validate target snapshot integrity
    3. Replace current cache with snapshot data
    4. Invalidate all caches
    5. Log restore event in audit trail
  - Export: download any snapshot as .json.gz file
  - Import: upload snapshot file for restore
  - New endpoints:
    - `GET /api/snapshots` → list all snapshots (sorted by date)
    - `POST /api/snapshots` → create manual snapshot `{description?}`
    - `GET /api/snapshots/{id}` → snapshot details
    - `GET /api/snapshots/{id}/download` → download snapshot file
    - `POST /api/snapshots/{id}/restore` → restore from snapshot
    - `POST /api/snapshots/verify` → verify all snapshot integrity
    - `DELETE /api/snapshots/{id}` → delete snapshot
    - `GET /api/snapshots/config` → get scheduling config
    - `PUT /api/snapshots/config` → update scheduling config
- Frontend: New `frontend/src/views/SnapshotsView.vue`
  - Snapshot timeline: visual timeline with markers for each snapshot
  - Snapshot details panel: metadata, size, memory count, checksum status
  - Restore confirmation dialog with "are you sure" + preview of changes
  - Scheduling config: interval selector, retention count settings
  - Download/upload buttons for manual backup exchange
  - Sidebar entry: "💾 Snapshots" under Operations section
- New components:
  - `frontend/src/components/SnapshotTimeline.vue`
  - `frontend/src/components/SnapshotCard.vue`
  - `frontend/src/components/RestoreDialog.vue`
  - `frontend/src/components/SnapshotConfig.vue`

**Acceptance Criteria**:
- AC-F59-1: Manual snapshot created via POST /api/snapshots
- AC-F59-2: Snapshot contains all memories with valid SHA-256 checksum
- AC-F59-3: Restore from snapshot correctly replaces current memories
- AC-F59-4: Pre-restore snapshot automatically created before restore
- AC-F59-5: Corrupted snapshot detected during verification (checksum mismatch)
- AC-F59-6: Scheduling config updates take effect on next cycle
- AC-F59-7: Snapshot download/upload works for manual backup exchange
- AC-F59-8: Retention policy automatically removes old snapshots

**Dependencies**: P5 F-30 (Backup & Restore — this is the evolved version)

---

### F-60 — Interactive API Playground

**Problem**: The Swagger/OpenAPI docs (P0 F-04) provide static API documentation, but developers can't test endpoints directly without external tools like Postman or curl. This increases friction for integrators and makes it harder to debug API issues interactively.

**Solution**: A rich, in-browser API testing console that lets developers build requests, set parameters, authenticate, and inspect responses — all within Memory Viewer's UI.

**Implementation**:
- Backend: No new endpoints needed
  - Existing `/api/docs` (Swagger) and `/api/openapi.json` provide the OpenAPI spec
  - Add CORS headers for playground origin if needed
- Frontend: New `frontend/src/views/PlaygroundView.vue`
  - Request builder:
    - Method selector (GET/POST/PUT/DELETE)
    - URL input with autocomplete from OpenAPI spec
    - Headers editor (key-value pairs, pre-filled with auth)
    - Query params editor
    - Request body editor (JSON with syntax highlighting)
  - Response viewer:
    - Status code with color indicator (2xx green, 4xx yellow, 5xx red)
    - Response headers
    - Response body (JSON with syntax highlighting and collapsible tree)
    - Response time and size
  - Auth integration:
    - Auto-inject API key from settings
    - Auto-inject OIDC bearer token if logged in
  - History: last 50 requests saved in localStorage
  - Templates: pre-built request templates for common operations
    - "Search memories" — GET /api/search?q=...
    - "Create memory" — POST /api/agentmemory
    - "Generate digest" — POST /api/digest/generate
    - "RAG search" — POST /api/search/rag
  - cURL import: paste cURL command → populate request builder
  - Response diff: compare two responses side-by-side
  - Sidebar entry: "🧪 Playground" under Developer section
- New components:
  - `frontend/src/components/RequestBuilder.vue`
  - `frontend/src/components/ResponseViewer.vue`
  - `frontend/src/components/HistoryPanel.vue`
  - `frontend/src/components/CurlImport.vue`

**Acceptance Criteria**:
- AC-F60-1: Can build and send GET/POST/PUT/DELETE requests
- AC-F60-2: Response displays status, headers, body, time, and size
- AC-F60-3: API key auto-injected from settings
- AC-F60-4: Request history saved and browsable
- AC-F60-5: Pre-built templates populate request builder correctly
- AC-F60-6: cURL import correctly parses and populates request
- AC-F60-7: JSON response body rendered with syntax highlighting

**Dependencies**: P0 F-04 (Swagger API Docs — provides OpenAPI spec)

---

### F-61 — LLM Usage & Cost Dashboard

**Problem**: Multiple features now consume LLM tokens (semantic search embeddings, auto-tagging, NLQ, RAG search, conflict detection, digests), but there's no visibility into total token consumption, cost per feature, or usage trends. Without this data, cost optimization is impossible.

**Solution**: A centralized tracking system that logs every LLM call with token counts and calculated costs, exposed through a dashboard with per-feature breakdowns and trend analysis.

**Implementation**:
- Backend: New `backend/app/services/llm_usage_service.py`
  - Usage record schema:
    ```json
    {
      "id": "usage_abc123",
      "timestamp": "2026-05-29T14:00:00Z",
      "feature": "rag_search|auto_tag|nlq|conflict_detection|digest|embedding",
      "provider": "openai|ollama|anthropic",
      "model": "gpt-4o|llama3|claude-3-haiku",
      "input_tokens": 1234,
      "output_tokens": 567,
      "total_tokens": 1801,
      "cost_usd": 0.0023,
      "latency_ms": 1450,
      "memory_id": "mem_xxx",
      "user_id": "user_xxx"
    }
    ```
  - Token pricing table (configurable per model):
    - gpt-4o: $2.50/M input, $10.00/M output
    - gpt-4o-mini: $0.15/M input, $0.60/M output
    - claude-3-haiku: $0.25/M input, $1.25/M output
    - ollama (local): $0.00
  - Usage aggregation: hourly/daily/weekly/monthly rollups
  - Cost alerting: threshold-based alerts (e.g., daily spend > $10)
  - Instrumentation: wrap existing LLM calls (P8 llm_service.py) with usage tracking
  - Storage: `backend/cache/llm_usage.jsonl` (append-only log) + `backend/cache/llm_usage_rollups.json`
  - New endpoints:
    - `GET /api/llm-usage/summary` → total tokens, cost, and breakdown by feature
    - `GET /api/llm-usage/timeline` → daily cost data `{date: cost}` for chart
    - `GET /api/llm-usage/recent` → recent usage records (paginated)
    - `GET /api/llm-usage/config` → pricing table and alert thresholds
    - `PUT /api/llm-usage/config` → update pricing and thresholds
- Frontend: New `frontend/src/views/LLMUsageView.vue`
  - Summary cards: total tokens, total cost, avg latency, top feature
  - Cost timeline chart: daily cost line chart with feature breakdown (stacked area)
  - Feature breakdown: horizontal bar chart showing cost per feature
  - Recent usage table: sortable, filterable log of recent LLM calls
  - Provider comparison: cost comparison across configured providers
  - Budget alerts: configure daily/weekly/monthly spending limits
  - Sidebar entry: "💰 LLM Usage" under Analytics section
- New components:
  - `frontend/src/components/CostTimeline.vue`
  - `frontend/src/components/FeatureBreakdown.vue`
  - `frontend/src/components/UsageTable.vue`
  - `frontend/src/components/BudgetAlerts.vue`

**Acceptance Criteria**:
- AC-F61-1: LLM calls automatically logged with token counts and cost
- AC-F61-2: Dashboard shows total cost for configurable time period
- AC-F61-3: Feature breakdown correctly attributes costs per feature
- AC-F61-4: Timeline chart shows daily cost trends
- AC-F61-5: Ollama (local) usage tracked with $0.00 cost
- AC-F61-6: Budget alert triggers when threshold exceeded
- AC-F61-7: Pricing table configurable per model

**Dependencies**: P8 F-34 (LLM Service — the calls being instrumented), P8 F-33 (Embedding Service — embedding cost tracking)

---

### F-62 — Cross-Agent Knowledge Insights

**Problem**: With multiple agent profiles (chief-agent, daily, dev-worker, pm-orchestrator, qa-worker), each accumulates its own memories independently. There's no analysis of knowledge overlap (duplicated knowledge across agents), knowledge gaps (topics covered by one agent but missing from another), or emergent themes across the entire agent ecosystem.

**Solution**: An analytical layer that compares memory content and metadata across agent profiles to surface overlap, gaps, and shared themes — helping optimize the collective knowledge base.

**Implementation**:
- Backend: New `backend/app/services/insights_service.py`
  - Analysis types:
    1. **Knowledge Overlap**: find memories with similar content across profiles (using P8 embeddings)
       - Similarity threshold: > 0.85 cosine similarity → "duplicate across agents"
       - Report: pairs/groups of overlapping memories with similarity scores
    2. **Knowledge Gap Analysis**: for each profile, identify topic areas present in other profiles but absent
       - Method: cluster centroids from P9 clustering → check which clusters each profile participates in
       - Report: per-profile list of missing topics with example memories from other profiles
    3. **Collective Themes**: identify themes that span multiple profiles (cross-cutting concerns)
       - Method: TF-IDF across all memories, weighted by number of distinct profiles
       - Report: top themes with contributing profiles and representative memories
    4. **Profile Specialization Score**: how focused vs diverse is each profile's knowledge
       - Method: entropy of cluster distribution per profile
       - Report: specialization score (0=diverse, 1=focused) with breakdown
  - Caching: insights cached for 4 hours, invalidated on memory changes
  - New endpoints:
    - `GET /api/insights/overlap` → cross-agent knowledge overlap report
    - `GET /api/insights/gaps` → per-profile knowledge gap analysis
    - `GET /api/insights/themes` → collective themes across all profiles
    - `GET /api/insights/specialization` → profile specialization scores
    - `POST /api/insights/refresh` → force recalculation
- Frontend: New `frontend/src/views/InsightsView.vue`
  - Overview tab: summary cards (total overlap pairs, gap count, top themes)
  - Overlap tab: matrix visualization (profile × profile) showing overlap count
    - Click cell → list of overlapping memories with similarity scores
  - Gaps tab: per-profile cards showing missing topics with "Import from other agent" action
  - Themes tab: word cloud / tag cloud of collective themes
  - Specialization tab: radar chart showing each profile's topic distribution
  - Sidebar entry: "🔍 Insights" under Intelligence section
- New components:
  - `frontend/src/components/OverlapMatrix.vue`
  - `frontend/src/components/GapAnalysis.vue`
  - `frontend/src/components/ThemeCloud.vue`
  - `frontend/src/components/SpecializationRadar.vue`

**Acceptance Criteria**:
- AC-F62-1: Overlap report identifies memories with >0.85 similarity across profiles
- AC-F62-2: Gap analysis lists topics present in some profiles but absent in others
- AC-F62-3: Collective themes correctly ranked by cross-profile frequency
- AC-F62-4: Specialization score reflects knowledge diversity per profile
- AC-F62-5: Insights refresh when memories change (cache invalidation)
- AC-F62-6: Matrix visualization correctly renders profile × profile overlap
- AC-F62-7: Insights generation completes in <10s for 200 memories across 5 profiles

**Dependencies**: P8 F-33 (Embedding Service — similarity calculations), P9 F-40 (Clustering — topic analysis), P11 F-54 (Workspaces — profile context)

---

## Implementation Order

### Week 1: Foundation & Developer Tools
1. **F-60 Interactive API Playground** — lightweight, frontend-only, immediate DX value
2. **F-62 Cross-Agent Knowledge Insights** — analytical backend, builds on existing embeddings

### Week 2: Enterprise & Operations
3. **F-57 SSO / OIDC Integration** — foundational for enterprise, backend-heavy
4. **F-59 Disaster Recovery & Snapshots** — critical for production resilience

### Week 3: Governance & Cost Management
5. **F-58 Memory Governance Policies** — policy engine, depends on workspaces
6. **F-61 LLM Usage & Cost Dashboard** — instrumentation + dashboard

### Week 4: Integration Testing & Polish
- Cross-feature integration testing
- Performance testing under load
- Documentation updates
- Bug fixes

---

## Dependency Graph

```
F-60 (API Playground) ─────────── depends on P0 F-04 (Swagger docs)
F-57 (SSO/OIDC) ──────────────── depends on P11 F-54 (Workspaces/RBAC)
F-58 (Governance) ────────────── depends on P11 F-54 (Workspaces) + P10 F-47 (Workflows)
F-59 (Disaster Recovery) ─────── depends on P5 F-30 (Backup/Restore)
F-61 (LLM Usage Dashboard) ───── depends on P8 F-34 (LLM Service) + P8 F-33 (Embeddings)
F-62 (Cross-Agent Insights) ──── depends on P8 F-33 (Embeddings) + P9 F-40 (Clustering)
```

---

## Technical Impact

| Feature | Backend Changes | Frontend Changes | New Files |
|---------|----------------|-----------------|-----------|
| F-57 | auth_service.py, auth_middleware.py, auth router | LoginPage, UserProfile, useAuth | 5 |
| F-58 | governance_service.py, governance router | GovernanceView, PolicyCard, PolicyEditor, ViolationTimeline, ComplianceReport | 6 |
| F-59 | snapshot_service.py, snapshot router, APScheduler job | SnapshotsView, SnapshotTimeline, SnapshotCard, RestoreDialog, SnapshotConfig | 6 |
| F-60 | none (uses existing OpenAPI spec) | PlaygroundView, RequestBuilder, ResponseViewer, HistoryPanel, CurlImport | 5 |
| F-61 | llm_usage_service.py, llm_usage router | LLMUsageView, CostTimeline, FeatureBreakdown, UsageTable, BudgetAlerts | 6 |
| F-62 | insights_service.py, insights router | InsightsView, OverlapMatrix, GapAnalysis, ThemeCloud, SpecializationRadar | 6 |

---

## New Dependencies

| Package | Purpose | Size | Used By |
|---------|---------|------|---------|
| python-jose[cryptography] | JWT token verification for OIDC | ~200KB | F-57 |
| httpx | OIDC provider HTTP calls | ~100KB | F-57 (already present) |
| pydantic | Auth model validation | — | F-57 (already present) |

*No new frontend dependencies — existing Vue 3 ecosystem (ECharts, Vue Router) covers all UI needs.*

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OIDC provider compatibility issues | Medium | High | Support OIDC discovery (.well-known); test with Keycloak + Google |
| Snapshot storage growth | Medium | Medium | Rolling retention policy; compressed snapshots |
| LLM cost tracking accuracy | Medium | Medium | Token counts from API response; fallback to estimation |
| Cross-agent insights quality with few memories | Medium | Low | Minimum threshold (5 memories per profile) before analysis |
| Governance policy conflicts | Low | Medium | Priority-based evaluation order; conflict detection between policies |
| API Playground security (SSRF) | Low | High | Restrict to /api/* paths only; no arbitrary URL access |

---

## Acceptance Test Plan

### Smoke Tests
- F-57: Login via OIDC → user profile displayed → logout works
- F-58: Create retention policy → trigger evaluation → violations recorded
- F-59: Create snapshot → verify checksum → restore from snapshot → memories restored
- F-60: Open playground → send GET /api/health → response displayed
- F-61: Make RAG search → check LLM usage dashboard → cost recorded
- F-62: Visit insights → overlap matrix shows cross-profile data

### Regression Tests
- All existing CRUD operations still work
- API key authentication unchanged for CLI/SDK
- Search (semantic, NLQ, RAG) unaffected
- Existing workspaces, RBAC, real-time updates fully functional
- Performance: API latency increase < 5ms

### Performance Tests
- Snapshot creation: < 5s for 500 memories
- Governance evaluation: < 10s for 500 memories × 10 policies
- Insights generation: < 10s for 200 memories across 5 profiles
- API Playground: request/response display < 100ms overhead
- LLM usage dashboard: load time < 2s
