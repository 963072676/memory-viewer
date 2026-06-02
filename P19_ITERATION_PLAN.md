# P19 Iteration Plan — Memory Viewer v2

> **Iteration**: P19  
> **Date**: 2026-05-31  
> **Author**: pm-orchestrator

---

## 1. Iteration Summary

P19 delivers 3 user-visible quality-of-life features from P2 backlog:

| # | Feature | Description | Complexity | Layer |
|---|---------|-------------|-----------|-------|
| F-13 | Dark Mode | Light/Dark theme toggle with system preference detection | 🟡 中 | 前端 |
| F-12 | What's New Changelog | Version update popup on first deployment visit | 🟢 低 | 前端+后端 |
| F-17 | Feishu Webhook Notifications | Memory CRUD events sent to configured Feishu webhook | 🟡 中 | 后端 |

**Focus**: UI polish (dark mode) + user communication (changelog) + team collaboration (webhook)

---

## 2. Feature Details

### F-13: Dark Mode

**Description**: Add Light/Dark theme toggle with system preference detection and manual override. Persists choice in localStorage.

**Implementation**:
- Extend `variables.css` with dark mode CSS variable set (duplicate light vars with dark values)
- Create `ThemeToggle.vue` button component (sun/moon icon)
- Create `useTheme.ts` composable for theme management (detect system preference, apply class to `<html>`)
- Theme choice persisted to `localStorage.theme`

**Acceptance Criteria**:
- [ ] AC-F13-1: Toggle switches between light/dark themes
- [ ] AC-F13-2: On first visit, theme matches system preference (prefers-color-scheme)
- [ ] AC-F13-3: Theme choice persists across page reloads
- [ ] AC-F13-4: All existing components render correctly in both themes

---

### F-12: What's New Changelog

**Description**: On first visit after a version deploy, show a modal popup with current version's changelog. Users can dismiss and not see it again (localStorage tracks "last seen version").

**Implementation**:
- New `GET /api/changelog` backend endpoint returning `{version, changelog_items[]}`
- Frontend: `WhatsNewModal.vue` component + check on `App.vue` mount
- `localStorage.lastSeenVersion` stores the version user has acknowledged

**Acceptance Criteria**:
- [ ] AC-F12-1: Modal appears on first visit after P19 deployment
- [ ] AC-F12-2: Modal shows version number and changelog items
- [ ] AC-F12-3: User can dismiss modal; it won't reappear until next version
- [ ] AC-F12-4: `/api/changelog` returns structured JSON

---

### F-17: Feishu Webhook Notifications

**Description**: When any memory CRUD operation occurs (create/update/delete), send a formatted message card to a configured Feishu webhook URL.

**Implementation**:
- Backend: new `POST /api/webhook/feishu/test` endpoint for testing connectivity
- Config: `FEISHU_WEBHOOK_URL` env var
- On memory write operations (POST/PUT/DELETE in `agentmemory.py` router), trigger async webhook delivery
- Feishu message card format: title + memory type + operation type + timestamp

**Acceptance Criteria**:
- [ ] AC-F17-1: Memory create → Feishu card with "🆕 New Memory" title
- [ ] AC-F17-2: Memory update → Feishu card with "✏️ Updated Memory" title
- [ ] AC-F17-3: Memory delete → Feishu card with "🗑️ Deleted Memory" title
- [ ] AC-F17-4: Webhook failure does NOT break the main operation (fire-and-forget)
- [ ] AC-F17-5: Test endpoint `POST /api/webhook/feishu/test` sends a test card

---

## 3. Out of Scope

- Timeline view (F-14) — complexity higher than iteration allows; moved to P20
- Memory archiving (F-15) — requires data model change
- Virtual scrolling (F-16) — current data volume (~100 items) doesn't need it yet

---

## 4. Deliverables Checklist

- [ ] `frontend/src/components/ThemeToggle.vue`
- [ ] `frontend/src/composables/useTheme.ts`
- [ ] `frontend/src/styles/variables.css` (dark mode extension)
- [ ] `frontend/src/components/WhatsNewModal.vue`
- [ ] `frontend/src/App.vue` (mount check)
- [ ] `backend/app/routers/changelog.py` (new router)
- [ ] `backend/app/main.py` (register changelog router)
- [ ] `backend/app/services/feishu_webhook.py` (notification service)
- [ ] `backend/app/routers/agentmemory.py` (webhook trigger on write ops)
- [ ] `backend/app/config.py` (FEISHU_WEBHOOK_URL setting)
- [ ] Unit tests for new services

---

## 5. Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-------------|
| Dark mode breaks existing components | 🟡 Medium | High | Pair test both themes |
| Webhook URL misconfigured causes errors | 🟡 Medium | Low | Fire-and-forget + logging |
| Changelog API needs versioning strategy | 🟢 Low | Medium | Simple endpoint returning current version |

---

## 6. Dependencies

- None — all 3 features are independent
- F-13 requires no backend changes
- F-12 requires backend changelog endpoint only
- F-17 only affects backend write paths