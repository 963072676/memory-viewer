# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [2.0.0] - 2026-06-06

### Added
- **i18n** — `zh-CN` (default) + `en-US` locales, 492 keys, manual edits + raw `$t()` sweep (P38 r30a/b, P50 r0)
- **Design tokens** — full CSS variable system: avatar, collection, graph source palettes
  (P47–P48); health badge, role badge, hex-sweep across all views (P47); `.hermes-card` family
  unification (P38 r35); collection-card `migrateCollectionColor` for legacy hex
- **CollectionCard** — token-ized with `iconBg` computed that accepts both new `var()` and legacy
  hex (P49 r1/r3)
- **MemoryDetailView** — compact action button density (5 buttons, ico+label, –30% desktop width,
  P49 r2)
- **Scroll progress bar** — 0.5px accent at top, rAF-throttled, GPU-composited, `reduce-motion`
  aware (P38 r31)
- **Toast spring animation** — cubic-bezier overshoot 0.45s, scale 0.92, `reduce-motion` aware
  (P38 r32)
- **Onboarding / Setup** — color-tokenized SetupWizard, 100% dark mode coverage (P46 r1)
- **AppHeader subtitle** — route-change fade-in (P45 r3)
- **Settings tab visual unification** — `accent-soft` → `accent-subtle` (P50 r1)

### Changed
- Simplified project structure for the v1.0 → v2.0 transition (10 views, 11 routers)
- `fetch_agentmemory.py` cache path unified: writes to `data/cache/agentmemory.json` only
- Memory-viewer 8501: now runs in a dedicated Docker container (see
  `docs/DEPLOYMENT.md`); the legacy bare-uvicorn process + cron watchdog was retired in v0.18.2

## [1.0.1] - 2026-06-02

### Fixed
- `fetch_agentmemory.py` was writing cache to `backend/cache/agentmemory.json`
  but the viewer reads from `<repo>/data/cache/agentmemory.json` (the
  `settings.AGENTMEMORY_CACHE` default). Cache was being written to a path
  nobody read — viewer always showed the stale v0.9.21 11-entry snapshot.
- Hard-coded `@agentmemory/mcp` path (`/opt/data/.npm/_npx/<hash>/...`) was
  broken because the npx cache root lives at `/home/.npm/`. Replaced with
  multi-root resolver + `AGENTMEMORY_MCP_BIN` env override.

### Added
- Read `/opt/data/.agentmemory/standalone.json` (the real persistent
  storage) as an authoritative source. Merge with MCP export, dedup by id,
  keep the most recent `updatedAt`. Result: 19 standalone + 4 MCP seeds
  = 23 memories, up from the stale 11.

## [1.0.0] - 2026-05-31

### Added
- Memory browsing with search and filtering
- Full-text search across all memory sources
- Dashboard with visual statistics
- Smart collections for categorization
- CRUD operations for memories
- Import/export functionality
- Multi-profile support
- Hermes Memory integration
- Favorites system
- Compare view for memory comparison

### Changed

- Simplified project structure for open source
- Reduced from 47 to 10 frontend views
- Reduced from 55 to 11 backend routers

### Documentation

- Added README.md
- Added CONTRIBUTING.md
- Added LICENSE (MIT)
- Added docs/API.md
- Added docs/ARCHITECTURE.md

### Removed

- Advanced AI features (semantic search, NLQ, RAG)
- Analytics and monitoring features
- Plugin system
- SSO integration
- MCP server
- Advanced management features

## Prior Versions

See git history for changes prior to v1.0.0.