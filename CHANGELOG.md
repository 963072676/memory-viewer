# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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