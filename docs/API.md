# Memory Viewer API

## Base URL

```
http://localhost:8501/api
```

## Endpoints

### Health Check

```
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 3600
}
```

### Memories

```
GET /api/agentmemory
```

Query parameters:
- `limit` (int, default: 50)
- `offset` (int, default: 0)
- `type` (string: 'pattern' | 'fact' | 'workflow')
- `search` (string: keyword search)
- `profile` (string: filter by profile)

Response:
```json
{
  "memories": [...],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

### Create Memory

```
POST /api/agentmemory
```

Body:
```json
{
  "title": "Memory Title",
  "content": "Memory content",
  "type": "pattern",
  "concepts": ["tag1", "tag2"],
  "strength": 5
}
```

### Update Memory

```
PUT /api/agentmemory/{id}
```

### Delete Memory

```
DELETE /api/agentmemory/{id}
```

### Search

```
GET /api/search?q={keyword}
```

### Hermes Memory

```
GET /api/hermes-memory
```

Returns all Hermes MEMORY.md content organized by profile.

### Profiles

```
GET /api/profiles
```

Returns list of available agent profiles.

### Stats

```
GET /api/stats
```

Returns unified statistics across all memory sources.

### Collections

```
GET /api/collections
POST /api/collections
PUT /api/collections/{id}
DELETE /api/collections/{id}
```

### Config

```
GET /api/config
```

Returns application configuration and feature flags.

## Error Responses

```json
{
  "detail": "Error message"
}
```

Status codes:
- `200` — Success
- `400` — Bad Request
- `404` — Not Found
- `500` — Server Error