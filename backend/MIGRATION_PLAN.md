# FastAPI Migration Plan - Gun Del Sol

## Goal
Replace Flask (port 5001) + separate WebSocket server (port 5002) with unified FastAPI service on port 5001.

## Performance Targets
- First load: 2-3s → <1s (cold start)
- Subsequent loads: <500ms (cached)
- Refresh balances: 2-5s → 1-2s (async concurrent)
- WebSocket latency: <100ms

## Architecture Change

### Before:
```
Flask (5001) ← HTTP requests ← Frontend
WebSocket Server (5002) ← WS connection ← Frontend
```

### After:
```
FastAPI (5001) ← HTTP + WebSocket ← Frontend
```

## Endpoint Parity Checklist (37 total)

### High Priority (Frontend Critical):
- [ ] GET `/api/tokens/history` - Token list
- [ ] GET `/api/tokens/<id>` - Token details
- [ ] GET `/api/tokens/<id>/history` - Analysis history
- [ ] DELETE `/api/tokens/<id>` - Soft delete
- [ ] POST `/api/tokens/<id>/restore` - Restore token
- [ ] DELETE `/api/tokens/<id>/permanent` - Permanent delete
- [ ] GET `/api/tokens/trash` - Trash list
- [ ] GET `/multi-token-wallets` - Multi-token wallets
- [ ] POST `/wallets/refresh-balances` - Balance refresh
- [ ] GET `/wallets/<address>/tags` - Get tags
- [ ] POST `/wallets/<address>/tags` - Add tag
- [ ] DELETE `/wallets/<address>/tags` - Remove tag
- [ ] GET `/tags` - All tags
- [ ] GET `/codex` - Codex data

### Medium Priority (Analysis):
- [ ] POST `/analyze/token` - Start analysis
- [ ] GET `/analysis/<job_id>` - Job status
- [ ] GET `/analysis/<job_id>/csv` - Download CSV
- [ ] GET `/analysis/<job_id>/axiom` - Axiom export
- [ ] GET `/analysis` - List analyses

### Low Priority (Legacy/Debug):
- [ ] POST `/register` - Register address
- [ ] GET `/addresses` - List addresses
- [ ] GET `/address/<address>` - Get address
- [ ] DELETE `/address/<address>` - Delete address
- [ ] PUT `/address/<address>/note` - Update note
- [ ] POST `/import` - Import addresses
- [ ] POST `/clear` - Clear addresses
- [ ] GET `/health` - Health check
- [ ] GET `/api/debug-mode` - Debug status
- [ ] GET `/` - Root endpoint
- [ ] GET `/api/debug/config` - Debug config
- [ ] GET `/api/settings` - Get settings
- [ ] POST `/api/settings` - Update settings

### Webhook Endpoints:
- [ ] POST `/webhooks/create` - Create webhook
- [ ] GET `/webhooks/list` - List webhooks
- [ ] GET `/webhooks/<id>` - Get webhook
- [ ] DELETE `/webhooks/<id>` - Delete webhook
- [ ] POST `/webhooks/callback` - Webhook callback

### WebSocket:
- [ ] WebSocket `/ws` - Unified notifications

## Implementation Steps

1. **Phase 1: Core FastAPI Setup** ✓
   - Install dependencies
   - Create main.py structure
   - Setup CORS and middleware

2. **Phase 2: High Priority Endpoints**
   - Token management (7 endpoints)
   - Wallet operations (6 endpoints)
   - Add response caching

3. **Phase 3: Analysis Endpoints**
   - Token analysis queue
   - Background task workers
   - Job status tracking

4. **Phase 4: WebSocket Unification**
   - Implement /ws endpoint
   - Migrate notification logic
   - Test with frontend

5. **Phase 5: Migration & Cleanup**
   - Update start.bat
   - Test parity
   - Retire Flask & old WebSocket server

## Performance Optimizations

### Database:
- Use aiosqlite for async queries
- Add connection pooling
- Implement query result caching

### JSON:
- Use orjson for 5-10x faster serialization
- Add ETag headers for caching

### Concurrency:
- Async Helius API calls
- Background task queue
- Connection reuse

## Rollback Plan
- Keep Flask files as `.bak` until tested
- Frontend can switch between ports via env var
- Database remains unchanged (compatible)

## Testing Checklist
- [ ] All 37 endpoints return correct responses
- [ ] WebSocket notifications work
- [ ] Analysis queue functions
- [ ] Frontend loads faster
- [ ] No regressions in features
