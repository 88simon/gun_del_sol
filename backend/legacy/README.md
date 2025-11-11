# Legacy Backend Files

This folder contains archived backend implementations that have been replaced by the unified FastAPI service.

## Archived Files

### `api_service.py` (Flask REST API)
- **Status**: Deprecated (replaced by `fastapi_main.py`)
- **Original port**: 5001
- **Reason for archival**: FastAPI now handles all REST endpoints with better performance
- **Migration date**: 2025-11-11
- **Notes**: This Flask service was the original REST API. All endpoints have been migrated to FastAPI (port 5003) with improved performance, caching, and async support.

## Migration History

### Phase 1: Flask → FastAPI REST Migration
- Migrated all REST endpoints from Flask to FastAPI
- Added response caching, ETags, and request deduplication
- Implemented async database queries with aiosqlite
- Added GZip compression and HTTP/2 connection pooling

### Phase 2: WebSocket Unification
- Integrated WebSocket support directly into FastAPI
- Removed separate WebSocket server (`websocket_server.py`) on port 5002
- WebSocket now available at `ws://localhost:5003/ws`
- Real-time analysis notifications broadcast via ConnectionManager

## Current Architecture

**Active Services:**
- FastAPI (port 5003): REST API + WebSocket unified
- Next.js (port 3000): Frontend dashboard

**Retired Services:**
- Flask (port 5001): ❌ Deprecated
- WebSocket server (port 5002): ❌ Deprecated

## Reference

These files are kept for reference purposes only. The current production backend is `fastapi_main.py` which includes:
- All REST endpoints (tokens, analysis, webhooks, settings, etc.)
- WebSocket support for real-time notifications
- Production-grade performance optimizations
- Comprehensive error handling and logging
